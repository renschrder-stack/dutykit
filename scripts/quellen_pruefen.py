"""Quellenüberwachung: ruft die Primärquellen ab und vergleicht sie mit der Prüfsumme vom Prüfzeitpunkt.

  python scripts/quellen_pruefen.py                 Abgleich; Exit 1 bei Abweichung (Gesetzestext hat sich geändert)
  python scripts/quellen_pruefen.py --schreiben     zusätzlich Zeitstempel/Ergebnis in pflichten.json (_pruefung)
  python scripts/quellen_pruefen.py --neu-hashen ID [ID...]
        Prüfsummen NEU setzen – nur nachdem der geänderte Text gelesen und der Eintrag angepasst wurde.

Pro Eintrag steht unter "pruefquellen" eine Liste {url, anker?, ende?, laenge?, sha256}. Abrufprobleme sind Warnungen,
keine Abweichungen. Hinweis: eur-lex-Adressen mit CELEX liefern die Urfassung; spätere Änderungen von EU-Rechtsakten
erkennt dieser Abgleich nur, wenn der ändernde Rechtsakt selbst als Quelle eingetragen ist (siehe OPERATIONS.md).
"""
import hashlib
import html
import json
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

KATALOG = Path(__file__).parent.parent / "pflichten.json"
UA = "DutyKit-Quellenpruefung/1.0 (+https://github.com/renschrder-stack/dutykit)"


def normalisieren(roh: str, anker: str = "", ende: str = "", laenge: int = 0, url: str = "") -> str:
    t = re.sub(r"(?s)<(script|style).*?</\1>", " ", roh)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"\s+", " ", t).strip()
    if "gesetze-im-internet.de" in url and not anker:
        a, b = t.find("Nichtamtliches Inhaltsverzeichnis"), t.find("zum Seitenanfang")
        if a != -1:
            t = t[a:b if b > a else None]
    if anker:
        i = t.find(anker)
        if i == -1:
            raise ValueError(f"Anker nicht gefunden: {anker!r}")
        t = t[i:]
        if ende:
            j = t.find(ende, len(anker))
            t = t[:j] if j != -1 else t
        if laenge:
            t = t[:laenge]
    return t


def abrufen(url: str) -> str:
    letzter = None
    for versuch in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", errors="ignore")
        except Exception as e:  # Netz/Dienst
            letzter = e
            time.sleep(2 * (versuch + 1))
    raise OSError(str(letzter))


def pruefsumme(q: dict, roh: str | None = None) -> str:
    text = normalisieren(roh if roh is not None else abrufen(q["url"]), q.get("anker", ""), q.get("ende", ""),
                         q.get("laenge", 0), q["url"])
    return hashlib.sha256(text.encode()).hexdigest()


def alle_eintraege(daten: dict):
    for land, liste in daten.items():
        if isinstance(liste, list):
            yield from liste


def abgleichen(daten: dict, abruf=abrufen) -> dict:
    ok, abweichungen, warnungen = 0, [], []
    for e in alle_eintraege(daten):
        for q in e.get("pruefquellen", []):
            try:
                neu = pruefsumme(q, abruf(q["url"]))
            except (OSError, ValueError) as ex:
                warnungen.append(f"{e['id']}: {q['url']} nicht prüfbar ({ex})")
                continue
            if neu == q["sha256"]:
                ok += 1
            else:
                abweichungen.append(f"{e['id']}: Text geändert seit {e['geprueft']} – {q['url']}")
    return {"unveraendert": ok, "abweichungen": abweichungen, "warnungen": warnungen}


if __name__ == "__main__":
    args = sys.argv[1:]
    daten = json.loads(KATALOG.read_text(encoding="utf-8"))
    if "--neu-hashen" in args:
        ids = set(args[args.index("--neu-hashen") + 1:])
        for e in alle_eintraege(daten):
            if not ids or e["id"] in ids:
                for q in e.get("pruefquellen", []):
                    q["sha256"] = pruefsumme(q)
                    print("gesetzt", e["id"], q["url"])
        KATALOG.write_text(json.dumps(daten, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        sys.exit(0)
    erg = abgleichen(daten)
    for x in erg["abweichungen"]:
        print("ABWEICHUNG", x)
    for x in erg["warnungen"]:
        print("WARNUNG   ", x)
    print(f"{erg['unveraendert']} Quellen unverändert, {len(erg['abweichungen'])} Abweichungen, {len(erg['warnungen'])} Warnungen")
    if "--schreiben" in args:
        daten["_pruefung"] = {"zuletzt_abgeglichen": date.today().isoformat(), "quellen_unveraendert": erg["unveraendert"],
                              "abweichungen": len(erg["abweichungen"]), "nicht_pruefbar": len(erg["warnungen"])}
        KATALOG.write_text(json.dumps(daten, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sys.exit(1 if erg["abweichungen"] else 0)
