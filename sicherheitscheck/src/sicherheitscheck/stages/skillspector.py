"""Stufe "skillspector": prüft Claude-Skills im Projekt, bevor man ihnen vertraut.

SkillSpector (NVIDIA/SkillSpector, Apache-2.0) ist ein Programm für Skills, nicht für
Anwendungscode. Es läuft hier mit --no-llm: nur statische Muster, ohne KI-Schlüssel. Skill-Text
verlässt den Rechner nicht. Ausnahme: Paketnamen und Versionen aus Abhängigkeitslisten fragt
SkillSpector bei api.osv.dev ab. Gesucht werden Ordner mit SKILL.md.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from .base import IGNORIERTE_ORDNER, Fund, StufenErgebnis, programm_finden

NAME = "skillspector"
MAX_SKILLS = 20
INSTALL_HINWEIS = (
    "SkillSpector nicht gefunden. Installation: uv tool install "
    "git+https://github.com/NVIDIA/skillspector.git (braucht Python 3.12 oder neuer). "
    "Oder Pfad in der Umgebungsvariable SICHERHEITSCHECK_SKILLSPECTOR eintragen."
)
SCHWERE = {"CRITICAL": "kritisch", "HIGH": "hoch", "MEDIUM": "mittel", "LOW": "niedrig"}


def skill_ordner_finden(wurzel: Path) -> List[Path]:
    gefunden: List[Path] = []
    for ordner, unterordner, dateien in os.walk(wurzel):
        # .claude bleibt erlaubt: dort liegen Projekt-Skills.
        unterordner[:] = [d for d in unterordner if d not in IGNORIERTE_ORDNER]
        if "SKILL.md" in dateien:
            gefunden.append(Path(ordner))
    return sorted(gefunden)


def bericht_auswerten(daten: dict, skill_ordner: str) -> List[Fund]:
    """Wandelt den JSON-Bericht eines einzelnen Skills in Funde um."""
    funde: List[Fund] = []
    for i in daten.get("issues", []):
        loc = i.get("location") or {}
        ort = "%s:%s" % (loc.get("file", "?"), loc.get("start_line", "?"))
        funde.append(Fund(
            NAME,
            SCHWERE.get(str(i.get("severity", "")).upper(), "info"),
            "%s: %s" % (i.get("category", "?"), i.get("pattern", "?")),
            "%s → %s" % (skill_ordner, ort),
            "%s Empfehlung: %s" % (i.get("explanation", ""), i.get("remediation", "")),
        ))
    return funde


def _version(exe: str) -> str:
    try:
        r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=60)
        return (r.stdout or r.stderr).strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def pruefen(wurzel: Path, tools_ordner: Optional[Path] = None, timeout: int = 300) -> StufenErgebnis:
    skills = skill_ordner_finden(wurzel)
    if not skills:
        return StufenErgebnis(NAME, "ok", hinweis="Keine Skills (SKILL.md) im Projekt gefunden, nichts zu prüfen.")

    exe = programm_finden("SICHERHEITSCHECK_SKILLSPECTOR", "skillspector", projekt_tools=tools_ordner)
    if not exe:
        return StufenErgebnis(NAME, "uebersprungen",
                              hinweis="%d Skills gefunden, aber %s" % (len(skills), INSTALL_HINWEIS))

    funde: List[Fund] = []
    notizen: List[str] = []
    if len(skills) > MAX_SKILLS:
        notizen.append("Nur die ersten %d von %d Skills geprüft." % (MAX_SKILLS, len(skills)))
        skills = skills[:MAX_SKILLS]

    for ordner in skills:
        rel = ordner.relative_to(wurzel).as_posix() or "."
        with tempfile.TemporaryDirectory() as tmp:
            ausgabe = os.path.join(tmp, "bericht.json")
            try:
                r = subprocess.run(
                    [exe, "scan", str(ordner), "--no-llm", "--format", "json", "--output", ausgabe],
                    capture_output=True, text=True, timeout=timeout,
                )
            except subprocess.TimeoutExpired:
                return StufenErgebnis(NAME, "fehler", funde, "Zeitüberschreitung bei Skill " + rel)
            except OSError as ex:
                return StufenErgebnis(NAME, "fehler", funde, "Start fehlgeschlagen: %s" % ex)
            # Rückgabecode 1 bedeutet bei SkillSpector: Funde vorhanden, kein Fehler.
            if r.returncode not in (0, 1) or not os.path.exists(ausgabe):
                return StufenErgebnis(NAME, "fehler", funde,
                                      "SkillSpector Code %d bei %s: %s" % (r.returncode, rel, (r.stderr or "")[-300:]))
            try:
                with open(ausgabe, encoding="utf-8") as f:
                    daten = json.load(f)
            except (OSError, ValueError) as ex:
                return StufenErgebnis(NAME, "fehler", funde, "Bericht unlesbar bei %s: %s" % (rel, ex))
        funde.extend(bericht_auswerten(daten, rel))

    notizen.insert(0, "%d Skill(s) statisch geprüft (ohne KI-Auswertung)." % len(skills))
    return StufenErgebnis(NAME, "funde" if funde else "ok", funde, " ".join(notizen), _version(exe))
