"""DutyKit – Bezahlstufe (standardmäßig AUS).

Einschalten = Schalter umlegen: in /opt/dutykit/deploy/.env  DUTYKIT_BILLING=1,  STRIPE_WEBHOOK_SECRET=whsec_...
setzen, dann `docker compose up -d`. Vorher: Niederlassungsgenehmigung + Stripe-Konto der Firma.
Schritt-für-Schritt: entwurf/EINSCHALTEN.md

Ablauf bei AN (Festpreis-Abo, höheres Tageslimit je Schlüssel):
- Kunde kauft über einen Stripe Payment Link (Abo). Stripe leitet danach weiter auf
  https://dutykit.dev/schluessel?session_id={CHECKOUT_SESSION_ID}
- Stripe meldet den Kauf an  POST /stripe/webhook  (Signatur geprüft). Daraus entsteht genau ein Schlüssel je Abo.
- /schluessel zeigt dem Käufer seinen Schlüssel (die session_id ist das Geheimnis).
- Agent sendet Header  Authorization: Bearer dk_...
- Kündigung, Zahlungsausfall oder Erstattung schalten den Schlüssel ab (HTTP 402).
Ohne Schlüssel gilt weiter die Freistufe. Gespeichert wird je Schlüssel nur: Stripe-Kunde, Abo, Zähler.
Keine E-Mail-Adresse, keine Eingaben.
"""
import hashlib
import hmac
import html
import json
import os
import secrets
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path

AKTIV = os.environ.get("DUTYKIT_BILLING", "0") == "1"
STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY", "")  # nur für nutzungsbasierte Abrechnung (METER) nötig
WEBHOOK_GEHEIMNIS = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
METER = os.environ.get("DUTYKIT_STRIPE_METER", "")  # leer = Festpreis, keine Meter-Ereignisse
BEZAHLT_PRO_TAG = int(os.environ.get("DUTYKIT_BEZAHLT_PRO_TAG", "5000"))
KEYS = Path(os.environ.get("DUTYKIT_KEYS_DATEI", "/data/keys.json"))
TOLERANZ_S = 300  # maximales Alter eines Webhook-Zeitstempels
ABO_AKTIV = {"active", "trialing", "past_due"}  # past_due: Stripe versucht die Zahlung noch erneut
_lock = threading.Lock()


def _laden() -> dict:
    return json.loads(KEYS.read_text(encoding="utf-8")) if KEYS.exists() else {}


def _speichern(keys: dict) -> None:
    """Erst in eine Nebendatei schreiben, dann tauschen: nie eine halb geschriebene keys.json."""
    KEYS.parent.mkdir(parents=True, exist_ok=True)
    tmp = KEYS.with_name(KEYS.name + ".tmp")
    tmp.write_text(json.dumps(keys, indent=2), encoding="utf-8")
    os.replace(tmp, KEYS)


def _heute() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


def schluessel_aus_headern(headers) -> str:
    for k, v in headers:
        if k == b"authorization" and v.lower().startswith(b"bearer dk_"):
            return v.decode()[7:]
    return ""


def _stripe_meter(kunde: str) -> None:
    if not (STRIPE_KEY and METER):
        return
    daten = urllib.parse.urlencode({"event_name": METER, "payload[stripe_customer_id]": kunde,
                                    "payload[value]": "1"}).encode()
    req = urllib.request.Request("https://api.stripe.com/v1/billing/meter_events", data=daten,
                                 headers={"Authorization": f"Bearer {STRIPE_KEY}"})
    try:
        urllib.request.urlopen(req, timeout=10).read()
    except Exception:
        pass  # Zählung darf den Aufruf nie blockieren; Abgleich über lokale Zähler


def pruefe_und_zaehle(schluessel: str) -> int:
    """0 = Aufruf erlaubt, 402 = Schlüssel ungültig oder Abo inaktiv, 429 = Tageslimit des Schlüssels erreicht."""
    with _lock:
        keys = _laden()
        eintrag = keys.get(schluessel)
        if not eintrag or not eintrag.get("aktiv"):
            return 402
        if eintrag.get("tag") != _heute():
            eintrag["tag"], eintrag["heute"] = _heute(), 0
        if eintrag["heute"] >= BEZAHLT_PRO_TAG:
            return 429
        eintrag["heute"] += 1
        eintrag["aufrufe"] = eintrag.get("aufrufe", 0) + 1
        _speichern(keys)
    if STRIPE_KEY and METER:
        threading.Thread(target=_stripe_meter, args=(eintrag["stripe_kunde"],), daemon=True).start()
    return 0


def schluessel_anlegen(stripe_kunde: str, notiz: str = "", abo: str = "", sitzung: str = "") -> str:
    """Legt einen Schlüssel an; je Abo höchstens einen (Stripe wiederholt Meldungen).

    Manuell: docker compose exec dutykit python -c "import billing; print(billing.schluessel_anlegen('cus_...'))"
    """
    with _lock:
        keys = _laden()
        if abo:
            for vorhanden, e in keys.items():
                if e.get("abo") == abo:
                    return vorhanden
        neu = "dk_" + secrets.token_urlsafe(24)
        keys[neu] = {"stripe_kunde": stripe_kunde, "abo": abo, "sitzung": _sitzung_hash(sitzung) if sitzung else "",
                     "aktiv": True, "aufrufe": 0, "notiz": notiz}
        _speichern(keys)
    return neu


def _sitzung_hash(sitzung: str) -> str:
    return hashlib.sha256(sitzung.encode()).hexdigest()


def _setze_aktiv(feld: str, wert: str, aktiv: bool) -> int:
    """Schaltet alle Schlüssel mit eintrag[feld] == wert an oder ab; liefert die Anzahl."""
    if not wert:
        return 0
    with _lock:
        keys = _laden()
        treffer = [e for e in keys.values() if e.get(feld) == wert]
        for e in treffer:
            e["aktiv"] = aktiv
        if treffer:
            _speichern(keys)
    return len(treffer)


def signatur_gueltig(body: bytes, kopfzeile: str, jetzt: float | None = None) -> bool:
    """Prüft den Header Stripe-Signature: t=<Zeit>,v1=<HMAC-SHA256 über "<Zeit>.<Body>">."""
    if not WEBHOOK_GEHEIMNIS:
        return False
    teile = [p.split("=", 1) for p in kopfzeile.split(",") if "=" in p]
    zeit = next((v for k, v in teile if k.strip() == "t"), "")
    signaturen = [v for k, v in teile if k.strip() == "v1"]
    if not zeit.isdigit() or abs((jetzt or time.time()) - int(zeit)) > TOLERANZ_S:
        return False
    erwartet = hmac.new(WEBHOOK_GEHEIMNIS.encode(), zeit.encode() + b"." + body, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(erwartet, s) for s in signaturen)


def webhook(body: bytes, kopfzeile: str) -> tuple[int, dict]:
    """Verarbeitet eine Stripe-Meldung. Unbekannte Ereignisse werden mit 200 quittiert (sonst wiederholt Stripe)."""
    if not signatur_gueltig(body, kopfzeile):
        return 400, {"fehler": "Signatur ungültig"}
    try:
        ereignis = json.loads(body)
        art, obj = ereignis["type"], ereignis["data"]["object"]
    except (ValueError, KeyError, TypeError):
        return 400, {"fehler": "Meldung nicht lesbar"}
    if art == "checkout.session.completed":
        if obj.get("mode") == "subscription" and obj.get("payment_status") in ("paid", "no_payment_required"):
            schluessel_anlegen(obj.get("customer") or "", abo=obj.get("subscription") or "", sitzung=obj.get("id") or "")
    elif art == "customer.subscription.updated":
        _setze_aktiv("abo", obj.get("id", ""), obj.get("status") in ABO_AKTIV)
    elif art == "customer.subscription.deleted":
        _setze_aktiv("abo", obj.get("id", ""), False)
    elif art == "charge.refunded" and obj.get("refunded"):  # nur volle Erstattung
        _setze_aktiv("stripe_kunde", obj.get("customer") or "", False)
    return 200, {"ok": True}


def schluessel_seite(query: str) -> tuple[int, str]:
    """Seite nach dem Kauf: zeigt den Schlüssel zur session_id aus der Stripe-Weiterleitung."""
    sitzung = urllib.parse.parse_qs(query).get("session_id", [""])[0]
    gefunden = ""
    if sitzung.startswith("cs_"):
        h = _sitzung_hash(sitzung)
        with _lock:
            gefunden = next((k for k, e in _laden().items() if e.get("sitzung") == h and e.get("aktiv")), "")
    if gefunden:
        return 200, _SEITE.format(titel="Your DutyKit API key", text=(
            "<p>Send it with every request as a header:</p>"
            f"<pre>Authorization: Bearer {html.escape(gefunden)}</pre>"
            "<p>Claude Code:</p>"
            "<pre>claude mcp add --transport http dutykit https://dutykit.dev/mcp "
            f"--header \"Authorization: Bearer {html.escape(gefunden)}\"</pre>"
            f"<p>Limit: {BEZAHLT_PRO_TAG} tool calls per day. Keep this page's address private; it shows your key "
            "again. To cancel, use the link in your Stripe receipt or write to hallo@dutykit.dev.</p>"))
    return 404, _SEITE.format(titel="Key not ready yet", text=(
        "<p>We could not find a key for this purchase yet. Payment confirmation can take a minute: "
        "please reload this page. If it still fails, write to hallo@dutykit.dev.</p>"))


_SEITE = ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"robots\" content=\"noindex\">"
          "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{titel} – DutyKit</title>"
          "<style>body{{font:17px/1.6 system-ui,sans-serif;max-width:760px;margin:0 auto;padding:48px 16px}}"
          "pre{{overflow-x:auto;padding:12px;border:1px solid #8884;border-radius:6px}}</style></head>"
          "<body><h1>{titel}</h1>{text}<p><a href=\"/\">← DutyKit</a></p></body></html>")
