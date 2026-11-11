"""Kommandozeile: sicherheitscheck <Projektordner>"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from . import __version__, report
from .stages import basis, skillspector, trufflehog

STUFEN = ("basis", "trufflehog", "skillspector")
TOOLS_ORDNER = Path(__file__).resolve().parents[2] / "tools"


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sicherheitscheck",
        description="Prüft einen Projektordner mit mehreren Sicherheitswerkzeugen und schreibt einen Bericht.",
        epilog="Rückgabecodes: 0 alles geprüft, keine Funde | 1 Funde | 2 Bedienfehler | "
               "3 keine Funde, aber Stufen liefen nicht",
    )
    p.add_argument("projekt", nargs="?", help="Ordner des Projekts")
    p.add_argument("--bericht-ordner", help="Wohin der Bericht geschrieben wird (Standard: ~/.sicherheitscheck/berichte/...)")
    p.add_argument("--stufen", default=",".join(STUFEN), help="Kommagetrennt, Standard: alle (%s)" % ", ".join(STUFEN))
    p.add_argument("--verifizieren", action="store_true",
                   help="TruffleHog darf gefundene Schlüssel bei den Diensten auf Aktivität prüfen "
                        "(sendet sie dorthin). Standard: aus.")
    p.add_argument("--version", action="store_true")
    return p


def _name_fuer_ordner(wurzel: Path) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", wurzel.name) or "projekt"


def main(argv: Optional[List[str]] = None) -> int:
    args = _parser().parse_args(argv)
    if args.version:
        print("sicherheitscheck", __version__)
        return 0
    if not args.projekt:
        print("Fehler: Projektordner fehlt.", file=sys.stderr)
        return 2
    wurzel = Path(args.projekt).expanduser().resolve()
    if not wurzel.is_dir():
        print("Fehler: Ordner nicht gefunden: %s" % wurzel, file=sys.stderr)
        return 2

    gewaehlt = [s.strip() for s in args.stufen.split(",") if s.strip()]
    unbekannt = [s for s in gewaehlt if s not in STUFEN]
    if unbekannt:
        print("Fehler: unbekannte Stufe(n): %s" % ", ".join(unbekannt), file=sys.stderr)
        return 2

    ergebnisse = []
    for stufe in gewaehlt:
        print("… Stufe %s" % stufe, file=sys.stderr)
        if stufe == "basis":
            ergebnisse.append(basis.pruefen(wurzel))
        elif stufe == "trufflehog":
            ergebnisse.append(trufflehog.pruefen(wurzel, args.verifizieren, TOOLS_ORDNER))
        elif stufe == "skillspector":
            ergebnisse.append(skillspector.pruefen(wurzel, TOOLS_ORDNER))

    jetzt = datetime.now()
    if args.bericht_ordner:
        ziel = Path(args.bericht_ordner).expanduser()
    else:
        ziel = Path.home() / ".sicherheitscheck" / "berichte" / ("%s-%s" % (_name_fuer_ordner(wurzel), jetzt.strftime("%Y%m%d-%H%M%S")))
    md = report.schreiben(ziel, wurzel.name, ergebnisse, jetzt)

    print(report.gesamturteil(ergebnisse))
    for e in ergebnisse:
        print("  %-13s %-15s %d Fund(e)" % (e.name, report.STATUS_TEXT.get(e.status, e.status).split(" (")[0], len(e.funde)))
    print("Bericht: %s" % md)
    return report.exit_code(ergebnisse)


if __name__ == "__main__":
    sys.exit(main())
