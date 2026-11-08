import json
import os
import sys
from pathlib import Path

os.environ["DUTYKIT_PROTOKOLL"] = "0"
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import katalog_pruefen
import pflichtwerk_server as s


def test_katalog_ist_gueltig():
    fehler, _ = katalog_pruefen.pruefen(max_alter=100000)
    assert fehler == []


def test_version_stimmt_mit_server_json():
    assert s.VERSION == json.loads((s.HIER / "server.json").read_text())["version"]


def test_pflichten_filtert_nach_taetigkeit():
    r = s.pflichten("de", "rechnung")
    assert r["pflichten"] and all("rechnung" in e["taetigkeiten"] for e in r["pflichten"])


def test_pflichten_unbekanntes_land():
    assert "fehler" in s.pflichten("XX")


def test_rechnung_unvollstaendig():
    r = s.rechnung_vorpruefen({"aussteller_name": "A"})
    assert r["bestanden"] is False and len(r["fehlende_angaben"]) >= 8


def test_rechnung_vollstaendig():
    r = s.rechnung_vorpruefen({
        "aussteller_name": "A GmbH", "aussteller_anschrift": "Str 1, 10115 Berlin", "empfaenger_name": "B",
        "empfaenger_anschrift": "Weg 2, 50667 Köln", "steuernummer_oder_ustid": "DE123456789",
        "datum": "2026-11-01", "rechnungsnummer": "R-1", "leistung": "10 Std Beratung",
        "leistungszeitpunkt": "2026-10", "netto": 100, "steuersatz": 19, "steuerbetrag": 19})
    assert r["bestanden"] is True and r["nachweis"]["pruefsumme_sha256"]


def test_rechnung_steuerbetrag_fehlt():
    r = s.rechnung_vorpruefen({"netto": 100, "steuersatz": 19})
    assert "Steuerbetrag" in r["fehlende_angaben"]


def test_rechnung_nur_de():
    assert "fehler" in s.rechnung_vorpruefen({}, land="LU")


def test_werbung_regeln():
    assert s.werbung_vorpruefen("email", "verbraucher", False)["erlaubt"] is False
    assert s.werbung_vorpruefen("email", "verbraucher", True)["erlaubt"] is True
    assert s.werbung_vorpruefen("email", "verbraucher", False, bestandskunde=True)["erlaubt"] is None
    assert s.werbung_vorpruefen("telefon", "unternehmen", False)["erlaubt"] is None
    assert s.werbung_vorpruefen("telefon", "verbraucher", False, bestandskunde=True)["erlaubt"] is False


def test_ki_hinweis_sprachen():
    for sprache in ("de", "fr", "en", "lb"):
        assert "Muster" in s.ki_hinweis("Muster", sprache)["text"]
    assert "fehler" in s.ki_hinweis("X", "xx")


def test_vat_format():
    assert "fehler" in s.vat_pruefen("!!")
