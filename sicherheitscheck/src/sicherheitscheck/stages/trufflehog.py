"""Stufe "trufflehog": sucht Geheimnisse im Dateibestand und in der Git-Historie.

TruffleHog (trufflesecurity/trufflehog, Lizenz AGPL-3.0) wird nur als eigenes Programm
aufgerufen, nicht eingebunden. Ohne --verifizieren läuft es mit --no-verification: dann
werden gefundene Schlüssel NICHT an die ausstellenden Dienste geschickt.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from .base import Fund, StufenErgebnis, programm_finden, schwaerzen

NAME = "trufflehog"
INSTALL_HINWEIS = (
    "TruffleHog nicht gefunden. Windows-Programm von "
    "https://github.com/trufflesecurity/trufflehog/releases laden und entweder in den "
    "Ordner tools\\ neben dieses Tool legen oder den Pfad in der Umgebungsvariable "
    "SICHERHEITSCHECK_TRUFFLEHOG eintragen."
)


def _version(exe: str) -> str:
    try:
        r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=30)
        return (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _ort(eintrag: dict) -> str:
    daten = (eintrag.get("SourceMetadata") or {}).get("Data") or {}
    if "Git" in daten:
        g = daten["Git"]
        return "%s:%s (Commit %s)" % (g.get("file", "?"), g.get("line", "?"), str(g.get("commit", "?"))[:8])
    if "Filesystem" in daten:
        f = daten["Filesystem"]
        return "%s:%s" % (f.get("file", "?"), f.get("line", "?"))
    return ""


def zeilen_auswerten(ausgabe: str, wurzel: Optional[Path] = None) -> List[Fund]:
    """Wandelt JSON-Zeilen von TruffleHog in Funde um. Der Klartext (Raw) wird nie übernommen."""
    funde: List[Fund] = []
    for zeile in ausgabe.splitlines():
        zeile = zeile.strip()
        if not zeile.startswith("{"):
            continue
        try:
            e = json.loads(zeile)
        except ValueError:
            continue
        if "DetectorName" not in e:
            continue
        verifiziert = bool(e.get("Verified"))
        ort = _ort(e)
        if wurzel is not None:
            ort = ort.replace(str(wurzel).rstrip("/\\") + "/", "").replace(str(wurzel).rstrip("/\\") + "\\", "")
        roh = e.get("Raw") or e.get("RawV2") or ""
        funde.append(Fund(
            NAME,
            "kritisch" if verifiziert else "hoch",
            "%s-Geheimnis gefunden%s" % (e.get("DetectorName", "?"), " (als aktiv bestätigt)" if verifiziert else ""),
            ort,
            "Fund: " + schwaerzen(roh),
            verifiziert=verifiziert,
        ))
    return funde


def _lauf(exe: str, argumente: List[str], timeout: int):
    r = subprocess.run([exe] + argumente, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def pruefen(wurzel: Path, verifizieren: bool = False, tools_ordner: Optional[Path] = None,
            timeout: int = 900) -> StufenErgebnis:
    exe = programm_finden("SICHERHEITSCHECK_TRUFFLEHOG", "trufflehog", projekt_tools=tools_ordner)
    if not exe:
        return StufenErgebnis(NAME, "uebersprungen", hinweis=INSTALL_HINWEIS)

    basis = ["--json", "--no-update"]
    if not verifizieren:
        basis.append("--no-verification")

    # Im Dateibestandslauf bleibt .git außen vor: die Historie prüft der git-Lauf,
    # sonst tauchen dieselben Funde doppelt aus Git-Interna auf.
    ausschluss = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    ausschluss.write("(^|[/\\\\])\\.git([/\\\\]|$)\n")
    ausschluss.close()

    aufrufe = [["filesystem", str(wurzel), "--exclude-paths", ausschluss.name] + basis]
    if (wurzel / ".git").exists():
        aufrufe.append(["git", wurzel.as_uri()] + basis)

    try:
        return _lauf_alle(exe, aufrufe, wurzel, timeout, verifizieren)
    finally:
        try:
            os.unlink(ausschluss.name)
        except OSError:
            pass


def _lauf_alle(exe: str, aufrufe: List[List[str]], wurzel: Path, timeout: int, verifizieren: bool) -> StufenErgebnis:
    funde: List[Fund] = []
    for args in aufrufe:
        try:
            rc, out, err = _lauf(exe, args, timeout)
        except subprocess.TimeoutExpired:
            return StufenErgebnis(NAME, "fehler", funde, "Zeitüberschreitung bei: trufflehog " + args[0],
                                  _version(exe))
        except OSError as ex:
            return StufenErgebnis(NAME, "fehler", funde, "Start fehlgeschlagen: %s" % ex)
        funde.extend(zeilen_auswerten(out, wurzel))
        if rc not in (0, 183):  # 183 = "mit --fail Funde gefunden"
            return StufenErgebnis(
                NAME, "fehler", funde,
                "trufflehog %s endete mit Code %d: %s" % (args[0], rc, err.strip()[-300:]), _version(exe))

    hinweis = "Dateibestand" + (" und Git-Historie" if len(aufrufe) > 1 else " (kein Git-Repo, Historie nicht geprüft)")
    hinweis += "; Schlüssel wurden " + ("bei den Diensten auf Aktivität geprüft." if verifizieren
                                       else "nicht an Dienste geschickt (keine Verifikation).")
    return StufenErgebnis(NAME, "funde" if funde else "ok", funde, hinweis, _version(exe))
