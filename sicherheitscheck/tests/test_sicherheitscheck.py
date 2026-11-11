import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sicherheitscheck import cli, report  # noqa: E402
from sicherheitscheck.stages import basis, skillspector, trufflehog  # noqa: E402
from sicherheitscheck.stages.base import Fund, StufenErgebnis, schwaerzen  # noqa: E402

# Test-Schlüssel werden zur Laufzeit zusammengesetzt, damit das Repo selbst keine Treffer erzeugt.
FALSCHER_AWS = "AKIA" + "IOSFODNN7EXAMPLE"
FALSCHER_GH = "ghp_" + "a" * 36
PEM_KOPF = "-----BEGIN " + "RSA PRIVATE KEY-----"


def projekt_mit_funden(tmp: Path) -> Path:
    (tmp / "app.py").write_text('KEY = "%s"\n' % FALSCHER_AWS, encoding="utf-8")
    (tmp / "config.txt").write_text("token=%s\n" % FALSCHER_GH, encoding="utf-8")
    (tmp / ".env").write_text("A=1\n", encoding="utf-8")
    (tmp / "server.pem").write_text(PEM_KOPF + "\nxx\n", encoding="utf-8")
    (tmp / "node_modules").mkdir()
    (tmp / "node_modules" / "x.py").write_text('K="%s"\n' % FALSCHER_AWS, encoding="utf-8")
    return tmp


class BasisTests(unittest.TestCase):
    def test_findet_schluessel_und_schwaerzt(self):
        with tempfile.TemporaryDirectory() as t:
            e = basis.pruefen(projekt_mit_funden(Path(t)))
        self.assertEqual(e.status, "funde")
        titel = " ".join(f.titel for f in e.funde)
        self.assertIn("AWS", titel)
        self.assertIn("GitHub", titel)
        self.assertIn("PEM", titel)
        roh = json.dumps([f.als_dict() for f in e.funde])
        self.assertNotIn(FALSCHER_AWS, roh)
        self.assertNotIn(FALSCHER_GH, roh)

    def test_ignoriert_node_modules(self):
        with tempfile.TemporaryDirectory() as t:
            e = basis.pruefen(projekt_mit_funden(Path(t)))
        self.assertFalse(any("node_modules" in f.ort for f in e.funde))

    def test_sauberes_projekt(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "a.py").write_text("print('hallo')\n", encoding="utf-8")
            e = basis.pruefen(Path(t))
        self.assertEqual(e.status, "ok")


class TruffleHogTests(unittest.TestCase):
    def test_ohne_programm_uebersprungen(self):
        with mock.patch.dict(os.environ, {"SICHERHEITSCHECK_TRUFFLEHOG": "/gibt/es/nicht", "PATH": ""}):
            with tempfile.TemporaryDirectory() as t:
                e = trufflehog.pruefen(Path(t), tools_ordner=Path(t) / "leer")
        self.assertEqual(e.status, "uebersprungen")
        self.assertIn("github.com/trufflesecurity", e.hinweis)

    def test_auswertung_ohne_klartext(self):
        zeilen = "\n".join([
            json.dumps({"DetectorName": "AWS", "Verified": True, "Raw": FALSCHER_AWS,
                        "SourceMetadata": {"Data": {"Git": {"file": "a.py", "line": 3, "commit": "abcdef1234"}}}}),
            json.dumps({"DetectorName": "Github", "Verified": False, "Raw": FALSCHER_GH,
                        "SourceMetadata": {"Data": {"Filesystem": {"file": "/p/b.txt", "line": 1}}}}),
            "kein json",
            json.dumps({"level": "info-0", "msg": "scan"}),
        ])
        funde = trufflehog.zeilen_auswerten(zeilen)
        self.assertEqual([f.schwere for f in funde], ["kritisch", "hoch"])
        self.assertTrue(funde[0].verifiziert)
        self.assertIn("a.py:3", funde[0].ort)
        roh = json.dumps([f.als_dict() for f in funde])
        self.assertNotIn(FALSCHER_AWS, roh)
        self.assertNotIn(FALSCHER_GH, roh)


class TruffleHogEchtTests(unittest.TestCase):
    """Lauf mit dem echten Programm; wird übersprungen, wenn es nicht installiert ist."""

    @unittest.skipUnless(trufflehog.programm_finden("SICHERHEITSCHECK_TRUFFLEHOG", "trufflehog"),
                         "trufflehog nicht installiert")
    def test_findet_geloeschtes_geheimnis_in_historie(self):
        import random
        import string
        import subprocess
        zufall = random.Random(7)
        w = lambda n, al=string.ascii_letters + string.digits: "".join(zufall.choice(al) for _ in range(n))
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)
            def git(*a):
                subprocess.run(["git", "-C", t, "-c", "user.email=t@t", "-c", "user.name=t"] + list(a),
                               check=True, capture_output=True)
            git("init", "-q", "-b", "main")
            (p / "config.py").write_text(
                'AWS_ACCESS_KEY_ID = "AKIA%s"\nAWS_SECRET_ACCESS_KEY = "%s"\n'
                % (w(16, string.ascii_uppercase + string.digits), w(40, string.ascii_letters + string.digits + "+/")),
                encoding="utf-8")
            git("add", "."); git("commit", "-qm", "v1")
            git("rm", "-q", "config.py"); (p / "a.txt").write_text("sauber\n"); git("add", "."); git("commit", "-qm", "v2")
            e = trufflehog.pruefen(p)
        self.assertEqual(e.status, "funde", e.hinweis)
        self.assertTrue(any("config.py" in f.ort and "Commit" in f.ort for f in e.funde))
        self.assertFalse(any(".git/" in f.ort for f in e.funde))


class SkillSpectorTests(unittest.TestCase):
    def test_skill_ordner_finden(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t) / ".claude" / "skills" / "x"
            d.mkdir(parents=True)
            (d / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8")
            (Path(t) / "node_modules" / "y").mkdir(parents=True)
            (Path(t) / "node_modules" / "y" / "SKILL.md").write_text("x", encoding="utf-8")
            self.assertEqual(skillspector.skill_ordner_finden(Path(t)), [d])

    def test_keine_skills_ist_ok(self):
        with tempfile.TemporaryDirectory() as t:
            e = skillspector.pruefen(Path(t))
        self.assertEqual(e.status, "ok")

    def test_bericht_auswerten(self):
        daten = {"issues": [{
            "category": "Prompt Injection", "pattern": "Instruction Override", "severity": "HIGH",
            "location": {"file": "SKILL.md", "start_line": 3}, "explanation": "E.", "remediation": "R."}]}
        funde = skillspector.bericht_auswerten(daten, "wasch")
        self.assertEqual(funde[0].schwere, "hoch")
        self.assertIn("SKILL.md:3", funde[0].ort)


class BerichtTests(unittest.TestCase):
    def test_luecke_ist_kein_freispruch(self):
        erg = [StufenErgebnis("basis", "ok"), StufenErgebnis("trufflehog", "uebersprungen", hinweis="fehlt")]
        self.assertIn("UNVOLLSTÄNDIG", report.gesamturteil(erg))
        self.assertEqual(report.exit_code(erg), 3)

    def test_funde_haben_vorrang(self):
        erg = [StufenErgebnis("basis", "funde", [Fund("basis", "hoch", "x")])]
        self.assertEqual(report.exit_code(erg), 1)

    def test_schwaerzen(self):
        s = schwaerzen("geheim123")
        self.assertNotIn("geheim", s)
        self.assertIn("9 Zeichen", s)

    def test_markdown_zeigt_nicht_geprueft(self):
        md = report.markdown("p", [StufenErgebnis("trufflehog", "uebersprungen", hinweis="x")], datetime(2026, 1, 1))
        self.assertIn("NICHT geprüft", md)


class CliTests(unittest.TestCase):
    def test_fehlender_ordner(self):
        self.assertEqual(cli.main(["/gibt/es/nicht"]), 2)

    def test_unbekannte_stufe(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(cli.main([t, "--stufen", "quatsch"]), 2)

    def test_ende_zu_ende_basis(self):
        with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as b:
            p = projekt_mit_funden(Path(t))
            rc = cli.main([str(p), "--stufen", "basis", "--bericht-ordner", b])
            self.assertEqual(rc, 1)
            md = (Path(b) / "bericht.md").read_text(encoding="utf-8")
            self.assertIn("AWS-Zugangsschlüssel", md)
            self.assertNotIn(FALSCHER_AWS, md)
            self.assertTrue((Path(b) / "bericht.json").exists())


if __name__ == "__main__":
    unittest.main()
