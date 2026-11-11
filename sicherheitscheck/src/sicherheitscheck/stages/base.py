"""Gemeinsame Typen und Hilfen für alle Prüfstufen."""
from __future__ import annotations

import hashlib
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

SCHWEREGRADE = ("kritisch", "hoch", "mittel", "niedrig", "info")

# Ordner, die nie durchsucht werden (Abhängigkeiten, Build-Ausgaben, Versionsverwaltung).
IGNORIERTE_ORDNER = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
    "target", ".next", ".svelte-kit", ".tox", ".mypy_cache", ".pytest_cache",
}


@dataclass
class Fund:
    stufe: str
    schwere: str
    titel: str
    ort: str = ""
    detail: str = ""
    verifiziert: Optional[bool] = None  # nur bei Geheimnissen: wurde der Schlüssel als aktiv bestätigt?

    def als_dict(self) -> dict:
        return {
            "stufe": self.stufe, "schwere": self.schwere, "titel": self.titel,
            "ort": self.ort, "detail": self.detail, "verifiziert": self.verifiziert,
        }


@dataclass
class StufenErgebnis:
    name: str
    status: str  # "ok" | "funde" | "uebersprungen" | "fehler"
    funde: List[Fund] = field(default_factory=list)
    hinweis: str = ""
    werkzeug_version: str = ""

    def als_dict(self) -> dict:
        return {
            "name": self.name, "status": self.status, "hinweis": self.hinweis,
            "werkzeug_version": self.werkzeug_version,
            "funde": [f.als_dict() for f in self.funde],
        }


def schwaerzen(geheimnis: str) -> str:
    """Geheimnisse nie im Klartext in Berichte schreiben: nur Länge und kurzer Fingerabdruck."""
    if not geheimnis:
        return "(leer)"
    fp = hashlib.sha256(geheimnis.encode("utf-8", "replace")).hexdigest()[:8]
    return "[geschwärzt, %d Zeichen, Prüfsumme %s]" % (len(geheimnis), fp)


def programm_finden(env_name: str, *namen: str, projekt_tools: Optional[Path] = None) -> Optional[str]:
    """Sucht ein Programm: 1. Umgebungsvariable, 2. tools-Ordner neben dem Tool, 3. PATH."""
    explizit = os.environ.get(env_name)
    if explizit and Path(explizit).exists():
        return explizit
    if projekt_tools:
        for n in namen:
            for endung in ("", ".exe"):
                kandidat = projekt_tools / (n + endung)
                if kandidat.is_file():
                    return str(kandidat)
    for n in namen:
        gefunden = shutil.which(n)
        if gefunden:
            return gefunden
    return None


def dateien_durchlaufen(wurzel: Path, max_bytes: int = 1_000_000):
    """Liefert Textdatei-Kandidaten unterhalb von wurzel, ohne ignorierte Ordner und ohne große Dateien."""
    for ordner, unterordner, dateien in os.walk(wurzel):
        unterordner[:] = [d for d in unterordner if d not in IGNORIERTE_ORDNER]
        for name in dateien:
            pfad = Path(ordner) / name
            try:
                if pfad.is_symlink() or pfad.stat().st_size > max_bytes:
                    continue
            except OSError:
                continue
            yield pfad
