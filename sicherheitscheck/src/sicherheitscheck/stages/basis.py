"""Stufe "basis": eigene, schnelle Grundprüfung ohne Fremdprogramm.

Sie ersetzt TruffleHog nicht. Sie fängt nur die gröbsten Fälle ab, damit auch ohne
installierte Werkzeuge etwas geprüft wird: bekannte Schlüsselformate im Klartext,
Schlüsseldateien und .env-Dateien, die nicht von Git ignoriert werden.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import List

from .base import Fund, StufenErgebnis, dateien_durchlaufen, schwaerzen

NAME = "basis"

MUSTER = [
    ("AWS-Zugangsschlüssel", "kritisch", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub-Token", "kritisch", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("Anthropic-API-Schlüssel", "kritisch", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}")),
    ("OpenAI-API-Schlüssel", "kritisch", re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_\-]{32,}")),
    ("Stripe-Live-Schlüssel", "kritisch", re.compile(r"\bsk_live_[0-9a-zA-Z]{24,}\b")),
    ("Slack-Token", "hoch", re.compile(r"\bxox[baprs]-[0-9A-Za-z\-]{10,}")),
    ("Google-API-Schlüssel", "hoch", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Privater Schlüssel (PEM)", "kritisch",
     re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY(?: BLOCK)?-----")),
]

SCHLUESSELDATEIEN = {"id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"}
SCHLUESSEL_ENDUNGEN = (".pem", ".key", ".p12", ".pfx")
ENV_AUSNAHMEN = (".example", ".sample", ".template", ".dist")


def _git_ignoriert(wurzel: Path, datei: Path) -> bool | None:
    """True/False, wenn Git entscheiden kann; None, wenn kein Git-Repo oder Git fehlt."""
    try:
        r = subprocess.run(
            ["git", "-C", str(wurzel), "check-ignore", "-q", str(datei)],
            capture_output=True, timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode == 0:
        return True
    if r.returncode == 1:
        return False
    return None


def _ist_env(name: str) -> bool:
    if name == ".env":
        return True
    return name.startswith(".env.") and not name.endswith(ENV_AUSNAHMEN)


def pruefen(wurzel: Path) -> StufenErgebnis:
    funde: List[Fund] = []
    for datei in dateien_durchlaufen(wurzel):
        rel = datei.relative_to(wurzel).as_posix()
        name = datei.name

        if _ist_env(name):
            ign = _git_ignoriert(wurzel, datei)
            if ign is True:
                funde.append(Fund(NAME, "info", ".env-Datei vorhanden, aber von Git ignoriert", rel))
            else:
                funde.append(Fund(
                    NAME, "hoch", ".env-Datei ist nicht von Git ausgeschlossen" if ign is False
                    else ".env-Datei vorhanden (Git-Status unbekannt)", rel,
                    "Sie kann Zugangsdaten enthalten. In .gitignore eintragen und Inhalt prüfen.",
                ))

        if name in SCHLUESSELDATEIEN or name.endswith(SCHLUESSEL_ENDUNGEN):
            funde.append(Fund(NAME, "hoch", "Mögliche Schlüsseldatei im Projekt", rel,
                              "Private Schlüssel gehören nicht in ein Projektverzeichnis."))

        try:
            text = datei.read_text(encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, OSError):
            continue  # Binärdatei oder nicht lesbar
        for bezeichnung, schwere, muster in MUSTER:
            for treffer in muster.finditer(text):
                zeile = text.count("\n", 0, treffer.start()) + 1
                funde.append(Fund(
                    NAME, schwere, "%s im Klartext" % bezeichnung, "%s:%d" % (rel, zeile),
                    "Fund: " + schwaerzen(treffer.group(0)),
                ))
    status = "funde" if any(f.schwere != "info" for f in funde) else "ok"
    return StufenErgebnis(NAME, status, funde, "Eigene Grundprüfung (ersetzt TruffleHog nicht).")
