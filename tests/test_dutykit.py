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


def test_angebot_ehrlich_und_konsistent():
    a = s.angebot()
    assert a["gratis"]["aufrufe_pro_tag_pro_ip"] == 200
    assert a["bezahlstufe"]["verfuegbar"] is False
    assert [x["id"] for x in a["bezahlstufe"]["stufen"]] == ["gratis", "credits", "pro"]
    assert {e["id"] for e in a["enthalten"]} >= {"nachweis", "vies_live", "quelle_und_pruefstand"}
    assert a["katalog_stand"]["DE"]["gesamt"] >= a["katalog_stand"]["DE"]["belegt"] > 0
    assert "Frankreich" in " ".join(a["nicht_enthalten"])


import quellen_pruefen as qp


def test_pflichten_hat_frische_und_keine_pruefsummen():
    for e in s.pflichten("DE")["pflichten"]:
        assert "alter_tage" in e and isinstance(e["frisch"], bool) and "pruefquellen" not in e


def test_katalog_status():
    st = s.katalog_status()
    de = st["laender"]["DE"]
    assert de["gesamt"] == de["belegt"] + de["zu_pruefen"]
    assert st["quellenabgleich"]["abweichungen"] == 0


def test_normalisieren_gesetzesseite():
    html = "<html>kopf Nichtamtliches Inhaltsverzeichnis <b>§ 1</b> Text&nbsp;hier zum Seitenanfang fuss</html>"
    assert qp.normalisieren(html, url="https://www.gesetze-im-internet.de/x/__1.html") == "Nichtamtliches Inhaltsverzeichnis § 1 Text hier "


def test_normalisieren_anker_ende():
    assert qp.normalisieren("a Artikel 13 Text Artikel 14 mehr", "Artikel 13", "Artikel 14") == "Artikel 13 Text "


def test_abweichung_wird_erkannt():
    q = {"url": "https://x.test/", "anker": "A", "ende": "B"}
    q["sha256"] = qp.pruefsumme(q, "<p>A alt B</p>")
    daten = {"DE": [{"id": "de-x", "geprueft": "2026-01-01", "pruefquellen": [q]}]}
    assert qp.abgleichen(daten, lambda u: "<p>A alt B</p>")["abweichungen"] == []
    assert len(qp.abgleichen(daten, lambda u: "<p>A neu B</p>")["abweichungen"]) == 1
    assert len(qp.abgleichen(daten, lambda u: "<p>kein anker</p>")["warnungen"]) == 1


def test_alle_belegten_gesetzesquellen_ueberwacht():
    import json
    d = json.loads((s.HIER / "pflichten.json").read_text(encoding="utf-8"))
    ohne = [e["id"] for e in qp.alle_eintraege(d)
            if e["pruefstand"] == "belegt" and "gesetze-im-internet.de" in e["quelle"] and not e.get("pruefquellen")]
    assert ohne == []


def test_pakete_verweisen_auf_existierende_eintraege():
    ids = {e["id"] for e in qp.alle_eintraege(s.KATALOG)}
    pakete = s.angebot()["pakete"]["liste"]
    assert [p["id"] for p in pakete] == ["rechnung", "werbung", "shop", "ki_kontakt"]
    for p in pakete:
        assert set(p["pflichten"]) <= ids, p["id"]
        for tool in p["tools"]:
            assert callable(getattr(s, tool.split("(")[0])), tool


def test_docker_image_enthaelt_alle_dateien_die_der_server_beim_start_liest():
    """Regression: fehlte server.json im Image, startete der Container in einer Endlosschleife."""
    import re, subprocess, sys, tempfile, shutil
    dockerfile = (s.HIER / "deploy" / "Dockerfile").read_text()
    kopiert = re.search(r"^COPY (.+) \./$", dockerfile, re.M).group(1).split()
    with tempfile.TemporaryDirectory() as t:
        for f in kopiert:
            shutil.copy(s.HIER / f, t)
        r = subprocess.run([sys.executable, "-c", "import app"], cwd=t, capture_output=True, text=True,
                           env={**__import__("os").environ, "PYTHONPATH": ""})
        assert r.returncode == 0, r.stderr[-500:]


def test_nutzungsstatistik_wochenvergleich_ohne_sonden(tmp_path):
    import app as a
    f = tmp_path / "st.json"
    f.write_text(json.dumps({
        "2026-11-02": {"pflichten": 4},                                   # Vorwoche (28.10.-03.11.)
        "2026-11-09": {"pflichten": 6, "__verifymcp_auth_probe_x__": 3},  # aktuelle Woche (04.-10.11.)
        "2026-11-10": {"vat_pruefen": 2}}))
    z = a.statistik_zusammenfassung("2026-11-10", str(f))
    assert z["woche_aktuell"]["aufrufe"] == 8 and z["woche_aktuell"]["pruefsonden"] == 3
    assert z["woche_vorher"]["aufrufe"] == 4 and z["veraenderung_prozent"] == 100
    assert "ip" not in json.dumps(z).lower().replace("pruefsonden", "")
    leer = a.statistik_zusammenfassung("2026-11-10", str(tmp_path / "gibt-es-nicht.json"))
    assert leer["woche_aktuell"]["aufrufe"] == 0 and leer["veraenderung_prozent"] is None


def test_eigene_pruefung_wird_erkannt():
    import app as a
    assert a._eigene_pruefung({"headers": [(b"user-agent", b"DutyKit-Pruefagent/1.0")]})
    assert not a._eigene_pruefung({"headers": [(b"user-agent", b"curl/8")]})
