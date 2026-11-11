"""Bericht als Markdown und JSON. Enthält nie Klartext-Geheimnisse."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

from .stages.base import SCHWEREGRADE, Fund, StufenErgebnis

STATUS_TEXT = {
    "ok": "geprüft, keine Funde",
    "funde": "geprüft, Funde",
    "uebersprungen": "NICHT geprüft (Werkzeug fehlt oder nichts zu prüfen)",
    "fehler": "FEHLGESCHLAGEN",
}


def alle_funde(ergebnisse: List[StufenErgebnis]) -> List[Fund]:
    funde = [f for e in ergebnisse for f in e.funde]
    return sorted(funde, key=lambda f: SCHWEREGRADE.index(f.schwere) if f.schwere in SCHWEREGRADE else 99)


def gesamturteil(ergebnisse: List[StufenErgebnis]) -> str:
    relevant = [f for f in alle_funde(ergebnisse) if f.schwere != "info"]
    luecken = [e for e in ergebnisse if e.status in ("uebersprungen", "fehler")]
    if relevant:
        return "FUNDE: %d Fund(e) brauchen Aufmerksamkeit." % len(relevant)
    if luecken:
        return "UNVOLLSTÄNDIG: keine Funde, aber %d Stufe(n) liefen nicht. Das ist kein Freispruch." % len(luecken)
    return "Keine Funde in den gelaufenen Stufen. Das beweist nicht, dass das Projekt sicher ist."


def exit_code(ergebnisse: List[StufenErgebnis]) -> int:
    if any(f.schwere != "info" for f in alle_funde(ergebnisse)):
        return 1
    if any(e.status in ("uebersprungen", "fehler") for e in ergebnisse):
        return 3
    return 0


def markdown(projekt: str, ergebnisse: List[StufenErgebnis], zeit: datetime) -> str:
    z = ["# Sicherheitscheck: %s" % projekt, "",
         "Zeitpunkt: %s" % zeit.strftime("%d.%m.%Y %H:%M"), "",
         "**%s**" % gesamturteil(ergebnisse), "", "## Stufen", "",
         "| Stufe | Ergebnis | Funde | Hinweis |", "|---|---|---|---|"]
    for e in ergebnisse:
        hinweis = e.hinweis.replace("|", "/").replace("\n", " ")
        z.append("| %s | %s | %d | %s |" % (e.name, STATUS_TEXT.get(e.status, e.status), len(e.funde), hinweis))
    funde = alle_funde(ergebnisse)
    z += ["", "## Funde", ""]
    if not funde:
        z.append("Keine.")
    for f in funde:
        z.append("- **[%s]** %s (%s)" % (f.schwere, f.titel, f.stufe))
        if f.ort:
            z.append("  - Ort: `%s`" % f.ort)
        if f.detail:
            z.append("  - %s" % f.detail)
        if f.verifiziert is not None:
            z.append("  - Als aktiv bestätigt: %s" % ("ja" if f.verifiziert else "nein/unbekannt"))
    z += ["", "---", "Geheimnisse stehen in diesem Bericht nie im Klartext.", ""]
    return "\n".join(z)


def schreiben(ordner: Path, projekt: str, ergebnisse: List[StufenErgebnis], zeit: datetime) -> Path:
    ordner.mkdir(parents=True, exist_ok=True)
    md = ordner / "bericht.md"
    md.write_text(markdown(projekt, ergebnisse, zeit), encoding="utf-8")
    (ordner / "bericht.json").write_text(json.dumps({
        "projekt": projekt, "zeit": zeit.isoformat(timespec="seconds"),
        "urteil": gesamturteil(ergebnisse), "exit_code": exit_code(ergebnisse),
        "stufen": [e.als_dict() for e in ergebnisse],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return md
