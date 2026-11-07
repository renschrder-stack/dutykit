"""DutyKit – Bezahlstufe (vorbereitet, standardmäßig AUS).

Einschalten = Schalter umlegen: in /opt/dutykit/.env  DUTYKIT_BILLING=1  und  STRIPE_SECRET_KEY=sk_live_...
setzen, dann `docker compose up -d`. Vorher: Niederlassungsgenehmigung + Stripe-Konto der Firma.

Ablauf bei AN:
- Kunde kauft über einen Stripe Payment Link (Abo). Stripe-Webhook → /opt/dutykit/data/keys.json
  (Skript `schluessel_anlegen` unten, bis der Webhook gebaut ist manuell).
- Agent sendet Header  Authorization: Bearer dk_...
- Jeder Aufruf wird gezählt und als Stripe Meter Event „dutykit_calls“ gemeldet (nutzungsbasiert).
Ohne Schlüssel gilt weiter die Freistufe.
"""
import json
import os
import secrets
import threading
import urllib.parse
import urllib.request
from pathlib import Path

AKTIV = os.environ.get("DUTYKIT_BILLING", "0") == "1"
STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
METER = os.environ.get("DUTYKIT_STRIPE_METER", "dutykit_calls")
KEYS = Path(os.environ.get("DUTYKIT_KEYS_DATEI", "/data/keys.json"))
_lock = threading.Lock()


def _laden() -> dict:
    return json.loads(KEYS.read_text(encoding="utf-8")) if KEYS.exists() else {}


def schluessel_aus_headern(headers) -> str:
    for k, v in headers:
        if k == b"authorization" and v.lower().startswith(b"bearer dk_"):
            return v.decode()[7:]
    return ""


def _stripe_meter(kunde: str) -> None:
    if not STRIPE_KEY:
        return
    daten = urllib.parse.urlencode({"event_name": METER, "payload[stripe_customer_id]": kunde,
                                    "payload[value]": "1"}).encode()
    req = urllib.request.Request("https://api.stripe.com/v1/billing/meter_events", data=daten,
                                 headers={"Authorization": f"Bearer {STRIPE_KEY}"})
    try:
        urllib.request.urlopen(req, timeout=10).read()
    except Exception:
        pass  # Zählung darf den Aufruf nie blockieren; Abgleich über lokale Zähler


def pruefe_und_zaehle(schluessel: str) -> bool:
    with _lock:
        keys = _laden()
        eintrag = keys.get(schluessel)
        if not eintrag or not eintrag.get("aktiv"):
            return False
        eintrag["aufrufe"] = eintrag.get("aufrufe", 0) + 1
        KEYS.write_text(json.dumps(keys, indent=2), encoding="utf-8")
    threading.Thread(target=_stripe_meter, args=(eintrag["stripe_kunde"],), daemon=True).start()
    return True


def schluessel_anlegen(stripe_kunde: str, notiz: str = "") -> str:
    """Manuell: docker compose exec dutykit python -c "import billing; print(billing.schluessel_anlegen('cus_...'))" """
    with _lock:
        keys = _laden()
        neu = "dk_" + secrets.token_urlsafe(24)
        keys[neu] = {"stripe_kunde": stripe_kunde, "aktiv": True, "aufrufe": 0, "notiz": notiz}
        KEYS.parent.mkdir(parents=True, exist_ok=True)
        KEYS.write_text(json.dumps(keys, indent=2), encoding="utf-8")
    return neu
