"""Bezahlstufe: Webhook, Schlüsselseite, Limits. Start:  python -m unittest discover tests"""
import asyncio
import hashlib
import hmac
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import app  # noqa: E402
import billing  # noqa: E402

GEHEIM = "whsec_test"


def signiert(ereignis: dict, zeit: int | None = None, geheim: str = GEHEIM) -> tuple[bytes, str]:
    body = json.dumps(ereignis).encode()
    t = str(zeit or int(time.time()))
    v1 = hmac.new(geheim.encode(), t.encode() + b"." + body, hashlib.sha256).hexdigest()
    return body, f"t={t},v1={v1}"


def kauf(sitzung="cs_test_1", abo="sub_1", kunde="cus_1") -> dict:
    return {"type": "checkout.session.completed", "data": {"object": {
        "id": sitzung, "mode": "subscription", "payment_status": "paid", "customer": kunde, "subscription": abo}}}


def aufruf(methode: str, pfad: str, body: bytes = b"", headers=(), query: bytes = b"") -> tuple[int, bytes]:
    """Ruft die ASGI-App direkt auf und liefert (Status, Body)."""
    gesendet = []

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(msg):
        gesendet.append(msg)

    scope = {"type": "http", "method": methode, "path": pfad, "query_string": query,
             "headers": list(headers), "client": ("203.0.113.9", 1)}
    asyncio.run(app.app(scope, receive, send))
    return gesendet[0]["status"], b"".join(m.get("body", b"") for m in gesendet[1:])


WERKZEUG = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "pflichten"}}).encode()


class Bezahlstufe(unittest.TestCase):
    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory()
        billing.KEYS = Path(self.ordner.name) / "keys.json"
        billing.WEBHOOK_GEHEIMNIS = GEHEIM
        billing.BEZAHLT_PRO_TAG = 3
        billing.AKTIV = True
        app.STATISTIK = str(Path(self.ordner.name) / "statistik.json")

    def tearDown(self):
        billing.AKTIV = False
        self.ordner.cleanup()

    def webhook(self, ereignis, **kw):
        body, sig = signiert(ereignis, **kw)
        return aufruf("POST", "/stripe/webhook", body, [(b"stripe-signature", sig.encode())])

    def schluessel(self) -> dict:
        return json.loads(billing.KEYS.read_text()) if billing.KEYS.exists() else {}

    def mcp(self, schluessel: str) -> int:
        return aufruf("POST", "/mcp", WERKZEUG, [(b"authorization", f"Bearer {schluessel}".encode())])[0]

    def test_kauf_erzeugt_genau_einen_schluessel(self):
        self.assertEqual(self.webhook(kauf())[0], 200)
        self.assertEqual(self.webhook(kauf())[0], 200)  # Stripe wiederholt die Meldung
        self.assertEqual(len(self.schluessel()), 1)

    def test_unbezahlt_erzeugt_keinen_schluessel(self):
        ereignis = kauf()
        ereignis["data"]["object"]["payment_status"] = "unpaid"
        self.assertEqual(self.webhook(ereignis)[0], 200)
        self.assertEqual(self.schluessel(), {})

    def test_falsche_signatur_wird_abgelehnt(self):
        self.assertEqual(self.webhook(kauf(), geheim="whsec_falsch")[0], 400)
        self.assertEqual(self.webhook(kauf(), zeit=int(time.time()) - 3600)[0], 400)  # zu alt
        self.assertEqual(aufruf("POST", "/stripe/webhook", json.dumps(kauf()).encode())[0], 400)  # ohne Signatur
        self.assertEqual(self.schluessel(), {})

    def test_ohne_geheimnis_wird_nichts_angenommen(self):
        billing.WEBHOOK_GEHEIMNIS = ""
        self.assertEqual(self.webhook(kauf(), geheim="")[0], 400)

    def test_schluesselseite(self):
        self.webhook(kauf(sitzung="cs_test_abc"))
        status, seite = aufruf("GET", "/schluessel", query=b"session_id=cs_test_abc")
        self.assertEqual(status, 200)
        self.assertIn(next(iter(self.schluessel())).encode(), seite)
        self.assertEqual(aufruf("GET", "/schluessel", query=b"session_id=cs_test_andere")[0], 404)
        self.assertEqual(aufruf("GET", "/schluessel")[0], 404)
        self.assertNotIn("cs_test_abc", billing.KEYS.read_text())  # nur der Hash liegt in der Datei

    def test_kuendigung_und_wiederaufnahme(self):
        self.webhook(kauf())
        k = next(iter(self.schluessel()))
        self.assertEqual(billing.pruefe_und_zaehle(k), 0)
        self.webhook({"type": "customer.subscription.updated", "data": {"object": {"id": "sub_1", "status": "unpaid"}}})
        self.assertEqual(self.mcp(k), 402)
        self.webhook({"type": "customer.subscription.updated", "data": {"object": {"id": "sub_1", "status": "active"}}})
        self.assertEqual(billing.pruefe_und_zaehle(k), 0)
        self.webhook({"type": "customer.subscription.deleted", "data": {"object": {"id": "sub_1"}}})
        self.assertEqual(self.mcp(k), 402)
        self.assertEqual(aufruf("GET", "/schluessel", query=b"session_id=cs_test_1")[0], 404)

    def test_erstattung_schaltet_ab(self):
        self.webhook(kauf())
        k = next(iter(self.schluessel()))
        self.webhook({"type": "charge.refunded", "data": {"object": {"customer": "cus_1", "refunded": False}}})
        self.assertEqual(billing.pruefe_und_zaehle(k), 0)  # Teilerstattung lässt den Schlüssel an
        self.webhook({"type": "charge.refunded", "data": {"object": {"customer": "cus_1", "refunded": True}}})
        self.assertEqual(self.mcp(k), 402)

    def test_tageslimit_je_schluessel(self):
        self.webhook(kauf())
        k = next(iter(self.schluessel()))
        for _ in range(3):
            self.assertEqual(billing.pruefe_und_zaehle(k), 0)
        self.assertEqual(self.mcp(k), 429)
        daten = self.schluessel()
        daten[k]["tag"] = "2000-01-01"  # neuer Tag: Zähler beginnt neu
        billing.KEYS.write_text(json.dumps(daten))
        self.assertEqual(billing.pruefe_und_zaehle(k), 0)

    def test_unbekannter_schluessel(self):
        self.assertEqual(self.mcp("dk_gibt_es_nicht"), 402)

    def test_unbekanntes_ereignis_wird_quittiert(self):
        self.assertEqual(self.webhook({"type": "invoice.paid", "data": {"object": {}}})[0], 200)

    def test_schalter_aus(self):
        billing.AKTIV = False
        self.assertEqual(self.webhook(kauf())[0], 404)
        self.assertEqual(aufruf("GET", "/schluessel", query=b"session_id=cs_test_1")[0], 404)
        self.assertEqual(self.schluessel(), {})
        status, body = aufruf("GET", "/health")
        self.assertEqual((status, json.loads(body)), (200, {"ok": True, "billing": False}))


if __name__ == "__main__":
    unittest.main()
