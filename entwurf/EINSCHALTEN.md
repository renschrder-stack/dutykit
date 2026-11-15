# Bezahlstufe einschalten

Stand: Code fertig und getestet, Schalter AUS (`DUTYKIT_BILLING=0`). Dieser Ordner wird nicht auf den Server
übertragen (`deploy.sh` kopiert nur `site/`, die vier Python-/JSON-Dateien und `deploy/`).

Gegen das echte Stripe ist nichts getestet. Geprüft ist mit nachgebauten, korrekt signierten Meldungen
(`python -m unittest discover tests`) und einem lokalen Serverlauf.

## Angebot (Vorschlag, Preis entscheidest du)

- DutyKit Pro: 19 € im Monat, 5.000 Werkzeugaufrufe pro Tag je Schlüssel, monatlich kündbar.
- Freistufe bleibt: 200 Aufrufe pro Tag je IP, ohne Konto.
- Das serverseitige Prüfprotokoll ("audit log") ist noch nicht gebaut. Nicht bewerben, bis es existiert.
  Der Satz dazu auf der Startseite ("…and a server-side audit log will follow") passt als Ankündigung weiter.

## Deine Schritte, in dieser Reihenfolge

1. **Rechtliches klären.** `billing.py` und das Impressum sagen beide: erst Niederlassungsgenehmigung, dann Verkauf.
   Ob das bei kleinen Umsätzen entfallen kann, kann ich nicht beurteilen. Bitte bei guichet.lu oder einer
   Steuerberatung bestätigen lassen, ebenso die Umsatzsteuer bei Verkäufen an Kunden in anderen EU-Ländern.
2. **Stripe:** Produkt "DutyKit Pro" mit wiederkehrendem Preis anlegen, daraus einen Payment Link erzeugen.
   Im Payment Link unter "Nach der Zahlung" auf diese Adresse weiterleiten:
   `https://dutykit.dev/schluessel?session_id={CHECKOUT_SESSION_ID}`
3. **Stripe-Webhook** anlegen: Endpunkt `https://dutykit.dev/stripe/webhook`, Ereignisse
   `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `charge.refunded`.
   Das Signaturgeheimnis (`whsec_...`) notieren.
4. **Server:** in `/opt/dutykit/deploy/.env` eintragen: `DUTYKIT_BILLING=1`, `STRIPE_WEBHOOK_SECRET=whsec_...`,
   `DUTYKIT_BEZAHLT_PRO_TAG=5000`. `STRIPE_SECRET_KEY` und `DUTYKIT_STRIPE_METER` bleiben beim Festpreis leer.
   Dann `bash deploy/deploy.sh <SERVER-IP>`.
5. **Probekauf im Stripe-Testmodus** (eigener Test-Payment-Link und Test-Webhook): Kauf, Schlüsselseite,
   Aufruf mit Schlüssel, Kündigung → der Schlüssel muss danach HTTP 402 liefern.
6. **Seite:** Abschnitt aus `entwurf/pricing-abschnitt.html` in `site/index.html` einsetzen (Payment-Link eintragen),
   Badge "Public beta · free" und den JSON-LD-Preis anpassen, Impressum-Status und Datenschutzerklärung ergänzen
   (Stripe als Zahlungsdienst; gespeichert werden je Schlüssel Stripe-Kundennummer, Abo-Nummer und Aufrufzähler,
   keine E-Mail-Adresse, keine Eingaben). Dazu Kündigungsweg und AGB bzw. Widerrufshinweise, je nach Auskunft aus Schritt 1.

## Was der Server tut, wenn der Schalter an ist

| Ereignis | Wirkung |
|---|---|
| Kauf abgeschlossen und bezahlt | genau ein Schlüssel je Abo, auch wenn Stripe die Meldung wiederholt |
| Käufer landet auf `/schluessel?session_id=…` | sieht seinen Schlüssel; kommt die Meldung später an, hilft Neuladen |
| Abo `unpaid`, `canceled`, pausiert oder gelöscht | Schlüssel aus, Aufrufe liefern 402 |
| Abo wieder `active` | Schlüssel wieder an |
| volle Erstattung | alle Schlüssel dieses Kunden aus |
| Tageslimit erreicht | 429 bis zum nächsten Tag (UTC) |
| Aufruf ohne Schlüssel | Freistufe wie bisher |

Schlüssel von Hand: `docker compose exec dutykit python -c "import billing; print(billing.schluessel_anlegen('cus_...'))"`
