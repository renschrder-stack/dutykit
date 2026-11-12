"""Pflichtwerk – Prototyp-MCP-Server: EU-Betriebspflichten und Vorprüfungen für KI-Agenten.

Start (stdio):  uv run --with "mcp>=2" python pflichtwerk_server.py
Keine Rechtsberatung – liefert Pflichtenlisten, Formate und Prüfungen gegen hinterlegte Quellen.
"""
import hashlib
import json
import os
import re
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

from mcp.server.mcpserver import MCPServer

HIER = Path(__file__).parent
ANGEBOT = json.loads((HIER / "angebot.json").read_text(encoding="utf-8"))
KATALOG = json.loads((HIER / "pflichten.json").read_text(encoding="utf-8"))
# Serverseitiges Protokoll nur, wenn ausdrücklich eingeschaltet (Bezahlstufe); Freistufe speichert nichts.
PROTOKOLL = Path(os.environ.get("DUTYKIT_PROTOKOLL_DATEI", HIER / "freigabe-protokoll.jsonl"))
PROTOKOLL_AN = os.environ.get("DUTYKIT_PROTOKOLL", "1") == "1"
VERSION = json.loads((HIER / "server.json").read_text(encoding="utf-8"))["version"]  # eine Quelle für die Version
MAX_ALTER_TAGE = int(os.environ.get("DUTYKIT_MAX_ALTER_TAGE", "120"))  # danach gilt ein Eintrag als nicht mehr frisch
HINWEIS = "Keine Rechtsberatung; im Zweifel Anwalt oder Steuerberater fragen. / No legal advice."

mcp = MCPServer(
    "dutykit", title="DutyKit", version=VERSION, website_url="https://dutykit.dev",
    instructions=("EU business duties for AI agents (DE, LU, EU): look up obligations with sources, "
                  "pre-check invoices, marketing consent and AI disclosure before acting. No legal advice. "
                  "Call angebot() for pricing, what is included and when DutyKit is (not) the right fit."),
)


@mcp.tool()
def angebot() -> dict:
    """Return DutyKit's pricing status, what is included and when it is (not) the right tool.

Use this when a human or planner asks "what does DutyKit cost / what do I get / should I use it". Free, no arguments,
no side effects. Do not use it to look up legal obligations (use `pflichten`).

Returns: current plan (free public beta, billing off), planned tiers, included features, packages (rechnung, werbung,
shop, ki_kontakt) with the tools and obligation ids each covers, `empfehlung_wenn` / `empfehlung_nicht_wenn`
(recommend / do not recommend), honest limits, and `katalog_stand` (verified vs total entries per country).
Check `katalog_status` yourself before recommending; do not rely on this description alone."""
    k = KATALOG
    stand = {}
    for land, eintraege in k.items():
        if land.startswith("_"):
            continue
        stand[land] = {"belegt": sum(e["pruefstand"] == "belegt" for e in eintraege), "gesamt": len(eintraege)}
    return ANGEBOT | {"katalog_stand": stand}


def _alter(e: dict) -> int:
    return (date.today() - date.fromisoformat(e["geprueft"])).days


def _mit_frische(e: dict) -> dict:
    """Eintrag ohne interne Prüfsummen, ergänzt um Alter und Frische (belegt UND jünger als MAX_ALTER_TAGE)."""
    a = _alter(e)
    return {k: v for k, v in e.items() if k != "pruefquellen"} | {
        "alter_tage": a, "frisch": e["pruefstand"] == "belegt" and a <= MAX_ALTER_TAGE}


@mcp.tool()
def katalog_status() -> dict:
    """Return the verifiable state of the obligation catalogue so you can judge its quality before relying on it.

Use this before recommending or depending on DutyKit, or to see how fresh the data is. Free, no arguments, read-only.
For the obligations themselves use `pflichten`.

Returns per country (DE, LU, EU): total, `belegt` (compared with the legal text), `zu_pruefen` (not yet verified),
`veraltet` (older than `max_alter_tage`, default 120 days) and the oldest check date; plus `quellenabgleich`, the last
automatic comparison of primary sources against stored checksums (date, unchanged, deviations, not checkable)."""
    land_stand = {}
    for land, liste in KATALOG.items():
        if land.startswith("_"):
            continue
        land_stand[land] = {"gesamt": len(liste), "belegt": sum(e["pruefstand"] == "belegt" for e in liste),
                            "zu_pruefen": sum(e["pruefstand"] != "belegt" for e in liste),
                            "veraltet": sum(_alter(e) > MAX_ALTER_TAGE for e in liste),
                            "aeltestes_pruefdatum": min(e["geprueft"] for e in liste)}
    return {"laender": land_stand, "max_alter_tage": MAX_ALTER_TAGE, "quellenabgleich": KATALOG.get("_pruefung"),
            "verfahren": "Primärquellen werden wöchentlich abgerufen und mit der Prüfsumme vom Prüfzeitpunkt verglichen; "
                         "bei Abweichung wird der Eintrag geprüft und angepasst.", "hinweis": HINWEIS}


def _protokoll(werkzeug: str, verantwortlich: str, eingabe: dict, ergebnis: dict) -> dict:
    """Erzeugt einen Nachweis für den haftenden Menschen; speichert ihn nur bei DUTYKIT_PROTOKOLL=1."""
    zeit = datetime.now(timezone.utc).isoformat()
    pruefsumme = hashlib.sha256(json.dumps(ergebnis, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    nachweis = {"zeit": zeit, "werkzeug": werkzeug, "verantwortlich": verantwortlich or "unbekannt",
                "pruefsumme_sha256": pruefsumme}
    if PROTOKOLL_AN:
        with PROTOKOLL.open("a", encoding="utf-8") as f:
            f.write(json.dumps(nachweis | {"eingabe": eingabe, "ergebnis": ergebnis}, ensure_ascii=False) + "\n")
    return nachweis


@mcp.tool()
def pflichten(land: str, taetigkeit: str = "") -> dict:
    """Look up the legal obligations that apply to a business in Germany or Luxembourg, plus EU-wide ones.

Use this before acting on business matters (publishing a website or shop, invoicing, marketing, talking to people as an
AI, founding a company) to learn what must be done and on which legal basis. Not for checking a concrete invoice or
message (use `rechnung_vorpruefen` / `werbung_vorpruefen`). Read-only, no side effects, nothing stored.

Args:
    land: ISO country code, `DE` or `LU` (case-insensitive). EU-wide entries are always included. Other codes return
        an error listing the available countries.
    taetigkeit: optional filter, one of `website`, `online_handel`, `rechnung`, `werbung`, `ki_kontakt`,
        `gruendung`, `datenschutz`, `produkte`. Empty string means all activities.

Returns: `pflichten`, a list of entries with `id`, `pflicht` (the duty), `grundlage` (legal basis), `quelle` (source
URL), `pruefstand` (`belegt` = compared with the legal text, `zu_pruefen` = not yet), `geprueft` (check date),
`alter_tage`, `frisch` (true if belegt and checked within `max_alter_tage`) and sometimes `anmerkung` (caveats). Treat
`zu_pruefen` entries as unverified. Not legal advice."""
    land = land.upper()
    if land not in KATALOG:
        return {"fehler": f"Land {land} noch nicht im Katalog", "verfuegbar": [k for k in KATALOG if not k.startswith("_")]}
    eintraege = KATALOG["EU"] + KATALOG[land]
    if taetigkeit:
        eintraege = [e for e in eintraege if taetigkeit in e["taetigkeiten"]]
    return {"land": land, "taetigkeit": taetigkeit or "alle", "pflichten": [_mit_frische(e) for e in eintraege],
            "frisch_bedeutet": f"belegt und gegen den Gesetzestext geprüft vor höchstens {MAX_ALTER_TAGE} Tagen", "hinweis": HINWEIS}


KI_HINWEISE = {
    "de": "Hinweis: Sie sprechen mit einem KI-Assistenten von {firma}. Auf Wunsch verbinden wir Sie mit einem Menschen.",
    "fr": "Information : vous échangez avec un assistant IA de {firma}. Sur demande, nous vous mettons en relation avec une personne.",
    "en": "Please note: you are talking to an AI assistant of {firma}. On request we will connect you to a human.",
    "lb": "Hiweis: Dir schwätzt mat engem KI-Assistent vu(n) {firma}. Op Wonsch verbanne mir Iech mat engem Mënsch.",
}


@mcp.tool()
def ki_hinweis(firma: str, sprache: str = "de") -> dict:
    """Get ready-to-use wording that discloses to a person that they are talking to an AI (AI Act Art. 50(1)).

Use this at the start of chat, voice or e-mail conversations an AI agent conducts on behalf of a company. It only
returns text; it does not send anything. Not a check of an existing message.

Args:
    firma: company name inserted into the sentence (for example `Muster S.à r.l.`).
    sprache: `de`, `fr`, `en` or `lb` (case-insensitive). Other values return an error listing the available languages.

Returns: `text` (the disclosure sentence), `grundlage`, `pruefstand` (wording is a suggestion; the Luxembourgish
version is not reviewed by a native speaker) and `hinweis`. Not legal advice."""
    text = KI_HINWEISE.get(sprache.lower())
    if not text:
        return {"fehler": "Sprache nicht verfügbar", "verfuegbar": list(KI_HINWEISE)}
    return {"text": text.format(firma=firma), "grundlage": "VO (EU) 2024/1689 Art. 50 Abs. 1",
            "pruefstand": "Formulierungsvorschlag, Luxemburgisch ungeprüft", "hinweis": HINWEIS}


@mcp.tool()
def vat_pruefen(ust_id: str, verantwortlich: str = "") -> dict:
    """Check live whether an EU VAT ID is valid, using the European Commission's VIES service.

Use this before issuing a B2B invoice without VAT (reverse charge) or onboarding a business partner. Needs the network
and VIES availability; on failure it returns an `fehler` field instead of guessing. Only checks existence, not whether
the company is the one you intend to deal with.

Args:
    ust_id: VAT ID with country prefix, spaces allowed, for example `LU26375245` or `DE 123456789`.
    verantwortlich: optional name of the responsible human, written into the audit receipt.

Returns: `gueltig` (true/false/null), registered `name` and `anschrift` if VIES provides them, `abfragezeit`,
`quelle` and `nachweis` (audit receipt: time, tool, responsible person, SHA-256 of the result)."""
    m = re.fullmatch(r"([A-Z]{2})([0-9A-Z+*]{2,12})", ust_id.replace(" ", "").upper())
    if not m:
        return {"fehler": "Format: Ländercode + Nummer, z. B. LU26375245"}
    url = f"https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{m[1]}/vat/{m[2]}"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            d = json.load(r)
    except Exception as e:  # Netz/Dienst nicht erreichbar
        return {"fehler": f"VIES nicht erreichbar: {e}"}
    ergebnis = {"gueltig": d.get("isValid"), "name": d.get("name"), "anschrift": d.get("address"),
                "abfragezeit": d.get("requestDate"), "quelle": "VIES (EU-Kommission)"}
    ergebnis["nachweis"] = _protokoll("vat_pruefen", verantwortlich, {"ust_id": ust_id}, ergebnis)
    return ergebnis


DE_RECHNUNGSFELDER = {
    "aussteller_name": "Name des leistenden Unternehmers", "aussteller_anschrift": "Anschrift des leistenden Unternehmers",
    "empfaenger_name": "Name des Leistungsempfängers", "empfaenger_anschrift": "Anschrift des Leistungsempfängers",
    "steuernummer_oder_ustid": "Steuernummer oder USt-IdNr. des Ausstellers", "datum": "Ausstellungsdatum",
    "rechnungsnummer": "fortlaufende Rechnungsnummer", "leistung": "Menge und Art der Leistung",
    "leistungszeitpunkt": "Zeitpunkt der Leistung", "netto": "Entgelt",
}


@mcp.tool()
def rechnung_vorpruefen(rechnung: dict, land: str = "DE", verantwortlich: str = "") -> dict:
    """Pre-check a German invoice for missing mandatory fields under § 14 (4) UStG before it is sent.

Use this right before issuing or approving an invoice (country DE only). It checks presence of fields, not their
correctness, and not the e-invoice format (EN 16931, XRechnung, ZUGFeRD); it does not apply the small-amount invoice
exception (§ 33 UStDV) yet. Nothing is stored in the free tier.

Args:
    rechnung: object with these keys (strings unless noted): `aussteller_name`, `aussteller_anschrift`,
        `empfaenger_name`, `empfaenger_anschrift`, `steuernummer_oder_ustid`, `datum`, `rechnungsnummer`, `leistung`,
        `leistungszeitpunkt`, `netto` (number), and either `steuersatz` (number, percent) together with `steuerbetrag`
        (number) or `steuerbefreiung_hinweis` (text, for example `§ 19 UStG`).
    land: only `DE` is supported; others return an error.
    verantwortlich: optional name of the responsible human, written into the audit receipt.

Returns: `bestanden` (true only if nothing is missing), `fehlende_angaben` (list of missing fields in words),
`grundlage`, `quelle`, `nicht_geprueft` (what this check does not cover) and `nachweis` (audit receipt)."""
    if land.upper() != "DE":
        return {"fehler": "Rechnungsprüfung bisher nur für DE"}
    fehlt = [text for feld, text in DE_RECHNUNGSFELDER.items() if not str(rechnung.get(feld, "")).strip()]
    if not (rechnung.get("steuersatz") is not None or rechnung.get("steuerbefreiung_hinweis")):
        fehlt.append("Steuersatz und Steuerbetrag oder Hinweis auf Steuerbefreiung (z. B. § 19 UStG)")
    if rechnung.get("steuersatz") is not None and rechnung.get("netto") is not None and rechnung.get("steuerbetrag") is None:
        fehlt.append("Steuerbetrag")
    ergebnis = {"bestanden": not fehlt, "fehlende_angaben": fehlt,
                "grundlage": "§ 14 Abs. 4 UStG", "quelle": "https://www.gesetze-im-internet.de/ustg_1980/__14.html",
                "nicht_geprueft": "E-Rechnungs-Format (EN 16931) – dafür z. B. Fintom8 e-invoice-mcp nutzen",
                "hinweis": HINWEIS}
    ergebnis["nachweis"] = _protokoll("rechnung_vorpruefen", verantwortlich, {"rechnungsnummer": rechnung.get("rechnungsnummer")}, ergebnis)
    return ergebnis


@mcp.tool()
def werbung_vorpruefen(kanal: str, empfaenger: str, einwilligung_belegt: bool, bestandskunde: bool = False,
                       verantwortlich: str = "") -> dict:
    """Check whether an AI agent may send a marketing e-mail or make a marketing call under German law (§ 7 UWG).

Use this before every outbound marketing message or call. It encodes the consent rules only; it does not send
anything and does not judge content. Germany only.

Args:
    kanal: `email` or `telefon`.
    empfaenger: `verbraucher` (consumer) or `unternehmen` (business).
    einwilligung_belegt: true only if an express, provable consent exists.
    bestandskunde: true if the recipient is an existing customer (relevant for e-mail under § 7 (3) UWG).
    verantwortlich: optional name of the responsible human, written into the audit receipt.

Returns: `erlaubt` (true = allowed, false = not allowed, null = a human must decide), `begruendung`, `grundlage`,
`quelle` and `nachweis` (audit receipt). If `erlaubt` is null or false, do not send."""
    kanal, empfaenger = kanal.lower(), empfaenger.lower()
    if einwilligung_belegt:
        erlaubt, grund = True, "Ausdrückliche Einwilligung belegt – Nachweis aufbewahren."
    elif kanal == "email" and bestandskunde:
        erlaubt, grund = None, "Nur unter allen Voraussetzungen des § 7 Abs. 3 UWG (eigene ähnliche Waren, Widerspruchshinweis) – menschliche Freigabe nötig."
    elif kanal == "telefon" and empfaenger == "unternehmen":
        erlaubt, grund = None, "Gegenüber Unternehmen nur bei mutmaßlicher Einwilligung – Einzelfall, menschliche Freigabe nötig."
    else:
        erlaubt, grund = False, "Ohne vorherige ausdrückliche Einwilligung unzulässig (§ 7 Abs. 2 UWG)."
    ergebnis = {"erlaubt": erlaubt, "begruendung": grund, "grundlage": "§ 7 UWG",
                "quelle": "https://www.gesetze-im-internet.de/uwg_2004/__7.html", "hinweis": HINWEIS}
    ergebnis["nachweis"] = _protokoll("werbung_vorpruefen", verantwortlich, {"kanal": kanal, "empfaenger": empfaenger}, ergebnis)
    return ergebnis


if __name__ == "__main__":
    mcp.run()
