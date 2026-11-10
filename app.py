"""DutyKit – Online-Betrieb: MCP über Streamable HTTP unter /mcp.

Freistufe: ohne Konto, Tageslimit pro IP (DUTYKIT_FREI_PRO_TAG, Standard 200 Aufrufe).
Bezahlstufe: liegt fertig in billing.py, bleibt aus, solange DUTYKIT_BILLING=0 („Schalter").

Start lokal:  uv run --with "mcp>=2" --with uvicorn uvicorn app:app --port 8080
"""
import json
import os
import time
from collections import defaultdict

import pflichtwerk_server  # registriert die Werkzeuge
import billing
from mcp.server.transport_security import TransportSecuritySettings

FREI_PRO_TAG = int(os.environ.get("DUTYKIT_FREI_PRO_TAG", "200"))
ERLAUBTE_HOSTS = [h.strip() for h in os.environ.get("DUTYKIT_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]

os.environ.setdefault("DUTYKIT_PROTOKOLL", "0")  # Freistufe: nichts serverseitig speichern
pflichtwerk_server.PROTOKOLL_AN = os.environ["DUTYKIT_PROTOKOLL"] == "1"

_mcp_app = pflichtwerk_server.mcp.streamable_http_app(
    stateless_http=True, json_response=False, host="0.0.0.0",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=ERLAUBTE_HOSTS + [h + ":*" for h in ERLAUBTE_HOSTS],
        allowed_origins=["https://" + h for h in ERLAUBTE_HOSTS] + ["http://localhost:*"],
    ),
)

_zaehler: dict[tuple[str, str], int] = defaultdict(int)
STATISTIK = os.environ.get("DUTYKIT_STATISTIK_DATEI", "/data/statistik.json")


def _statistik(body: bytes) -> None:
    """Anonyme Tageszählung je Werkzeug (keine IP, keine Eingaben) für den Wochenbericht."""
    try:
        name = json.loads(body).get("params", {}).get("name", "?")
    except Exception:
        name = "?"
    tag = time.strftime("%Y-%m-%d", time.gmtime())
    try:
        with open(STATISTIK, encoding="utf-8") as f:
            daten = json.load(f)
    except Exception:
        daten = {}
    daten.setdefault(tag, {}).setdefault(name, 0)
    daten[tag][name] += 1
    try:
        with open(STATISTIK, "w", encoding="utf-8") as f:
            json.dump(daten, f)
    except OSError:
        pass  # Statistik darf den Dienst nie stören


def _ist_sonde(werkzeug: str) -> bool:
    """Automatische Prüfdienste (z. B. Verzeichnisse) rufen Werkzeuge mit Namen wie __verifymcp_auth_probe_… auf."""
    return werkzeug.startswith("__")


def _eigene_pruefung(scope) -> bool:
    """Eigene Prüfläufe (Prüfagent) kennzeichnen sich per User-Agent und zählen nicht in die Nutzungsstatistik."""
    for k, v in scope.get("headers", []):
        if k == b"user-agent" and b"dutykit-pruefagent" in v.lower():
            return True
    return False


def statistik_zusammenfassung(heute: str | None = None, datei: str | None = None) -> dict:
    """Anonyme Nutzung: letzte 7 Tage gegen die 7 Tage davor, Prüfsonden getrennt (keine IP, keine Eingaben)."""
    from datetime import date, timedelta
    try:
        with open(datei or STATISTIK, encoding="utf-8") as f:
            daten = json.load(f)
    except Exception:
        daten = {}
    tag0 = date.fromisoformat(heute) if heute else date.today()

    def woche(ende_offset: int) -> dict:
        tage = [(tag0 - timedelta(days=ende_offset + i)).isoformat() for i in range(7)]
        je: dict[str, int] = {}
        sonden = 0
        for t in tage:
            for werkzeug, n in daten.get(t, {}).items():
                if _ist_sonde(werkzeug):
                    sonden += n
                else:
                    je[werkzeug] = je.get(werkzeug, 0) + n
        return {"von": tage[-1], "bis": tage[0], "aufrufe": sum(je.values()), "je_werkzeug": je, "pruefsonden": sonden}

    jetzt, vorher = woche(0), woche(7)
    ver = None if vorher["aufrufe"] == 0 else round((jetzt["aufrufe"] - vorher["aufrufe"]) * 100 / vorher["aufrufe"])
    return {"woche_aktuell": jetzt, "woche_vorher": vorher, "veraenderung_prozent": ver,
            "hinweis": "Zählt Werkzeugaufrufe, keine Nutzer. Automatische Prüfsonden sind getrennt ausgewiesen, Prüfläufe "
                       "des Prüfagenten (User-Agent DutyKit-Pruefagent) werden nicht gezählt. Alle Zeiten UTC."}


def _client_ip(scope) -> str:
    for k, v in scope.get("headers", []):
        if k == b"x-forwarded-for":  # gesetzt vom Reverse-Proxy (Caddy)
            return v.decode().split(",")[0].strip()
    return (scope.get("client") or ("?", 0))[0]


async def _antwort(send, status: int, daten: dict) -> None:
    body = json.dumps(daten, ensure_ascii=False).encode()
    await send({"type": "http.response.start", "status": status,
                "headers": [(b"content-type", b"application/json; charset=utf-8")]})
    await send({"type": "http.response.body", "body": body})


async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        return await _mcp_app(scope, receive, send)
    if scope["type"] == "http" and scope["path"] == "/health":
        return await _antwort(send, 200, {"ok": True, "billing": billing.AKTIV,
                                           "nutzung": statistik_zusammenfassung()})
    if scope["type"] == "http" and scope["path"].startswith("/mcp") and scope["method"] == "POST":
        # Body puffern: nur echte Werkzeugaufrufe (tools/call) zählen, nicht Handshake/Listen.
        teile, mehr = [], True
        while mehr:
            msg = await receive()
            teile.append(msg.get("body", b""))
            mehr = msg.get("more_body", False)
        body = b"".join(teile)
        geliefert = False
        original = receive

        async def receive():  # noqa: F811 – liefert den gepufferten Body erneut aus
            nonlocal geliefert
            if not geliefert:
                geliefert = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await original()  # danach echte Ereignisse (z. B. Verbindungsabbruch)

        if b'"tools/call"' not in body:
            return await _mcp_app(scope, receive, send)
        if not _eigene_pruefung(scope):
            _statistik(body)
        if billing.AKTIV:
            schluessel = billing.schluessel_aus_headern(scope.get("headers", []))
            if schluessel:
                if not billing.pruefe_und_zaehle(schluessel):
                    return await _antwort(send, 402, {"fehler": "API-Schlüssel ungültig oder Abo inaktiv"})
                return await _mcp_app(scope, receive, send)
        tag = time.strftime("%Y-%m-%d", time.gmtime())
        key = (_client_ip(scope), tag)
        if _zaehler[key] >= FREI_PRO_TAG:
            return await _antwort(send, 429, {"fehler": f"Freikontingent ({FREI_PRO_TAG}/Tag) erschöpft",
                                              "info": "https://dutykit.dev"})
        _zaehler[key] += 1
        if len(_zaehler) > 50000:  # alte Tage verwerfen
            for k in [k for k in _zaehler if k[1] != tag]:
                del _zaehler[k]
    return await _mcp_app(scope, receive, send)
