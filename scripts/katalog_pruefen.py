"""Katalog-Linter: Struktur, Pflichtfelder, Quellen-URLs, Alter der Prüfung.

Aufruf:  python scripts/katalog_pruefen.py [--max-alter-tage 180]
Exit-Code 1 bei Strukturfehlern; veraltete Prüfdaten werden nur gemeldet (Warnung), außer mit --streng.
"""
import json
import sys
from datetime import date
from pathlib import Path

KATALOG = Path(__file__).parent.parent / "pflichten.json"
FELDER = {"id", "taetigkeiten", "pflicht", "grundlage", "quelle", "pruefstand", "geprueft"}
TAETIGKEITEN = {"website", "online_handel", "rechnung", "werbung", "ki_kontakt", "gruendung", "datenschutz", "produkte"}
PRUEFSTAND = {"belegt", "zu_pruefen"}


def pruefen(max_alter: int = 180) -> tuple[list[str], list[str]]:
    fehler, warnungen, ids = [], [], set()
    daten = json.loads(KATALOG.read_text(encoding="utf-8"))
    for land, eintraege in daten.items():
        if land.startswith("_"):
            continue
        for e in eintraege:
            n = e.get("id", "?")
            if fehlt := FELDER - e.keys():
                fehler.append(f"{n}: Felder fehlen: {sorted(fehlt)}")
                continue
            if n in ids:
                fehler.append(f"{n}: doppelte ID")
            ids.add(n)
            if not n.startswith(land.lower() + "-"):
                fehler.append(f"{n}: ID muss mit '{land.lower()}-' beginnen")
            if not set(e["taetigkeiten"]) <= TAETIGKEITEN:
                fehler.append(f"{n}: unbekannte Tätigkeit {sorted(set(e['taetigkeiten']) - TAETIGKEITEN)}")
            if e["pruefstand"] not in PRUEFSTAND:
                fehler.append(f"{n}: pruefstand muss {sorted(PRUEFSTAND)} sein")
            if not e["quelle"].startswith("https://"):
                fehler.append(f"{n}: Quelle muss https-URL sein")
            if e["pruefstand"] == "zu_pruefen" and not e.get("anmerkung"):
                fehler.append(f"{n}: 'zu_pruefen' braucht eine Anmerkung (was ist offen?)")
            try:
                alter = (date.today() - date.fromisoformat(e["geprueft"])).days
            except ValueError:
                fehler.append(f"{n}: geprueft ist kein ISO-Datum")
                continue
            if alter > max_alter:
                warnungen.append(f"{n}: letzte Prüfung vor {alter} Tagen")
    return fehler, warnungen


if __name__ == "__main__":
    args = sys.argv[1:]
    alter = int(args[args.index("--max-alter-tage") + 1]) if "--max-alter-tage" in args else 180
    f, w = pruefen(alter)
    for x in f:
        print("FEHLER ", x)
    for x in w:
        print("WARNUNG", x)
    print(f"{len(f)} Fehler, {len(w)} Warnungen")
    sys.exit(1 if f or (w and "--streng" in args) else 0)
