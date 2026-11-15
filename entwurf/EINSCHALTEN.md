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

1. **Rechtliches klären.** `billing.py` und das Impressum nennen die Niederlassungsgenehmigung als Voraussetzung
   für den Verkauf. Bei guichet.lu oder einer Steuerberatung bestätigen lassen, ebenso die Umsatzsteuer bei
   Verkäufen an Kunden in anderen EU-Ländern.
2. **Stripe im Testmodus:** Produkt "DutyKit Pro" mit wiederkehrendem Preis anlegen, daraus einen Payment Link
   erzeugen. Im Payment Link unter "Nach der Zahlung" auf diese Adresse weiterleiten:
   `https://dutykit.dev/schluessel?session_id={CHECKOUT_SESSION_ID}`
   Die ID des Links (`plink_...`) notieren.
3. **Stripe-Webhook im Testmodus** anlegen: Endpunkt `https://dutykit.dev/stripe/webhook`, Ereignisse
   `checkout.session.completed`, `checkout.session.async_payment_succeeded`, `customer.subscription.updated`,
   `customer.subscription.deleted`, `charge.refunded`. Das Signaturgeheimnis (`whsec_...`) notieren.
4. **Server:** in `/opt/dutykit/deploy/.env` eintragen:
   `DUTYKIT_BILLING=1`, `STRIPE_WEBHOOK_SECRET=<Test-whsec>`, `DUTYKIT_STRIPE_PAYMENT_LINK=<Test-plink>`,
   `DUTYKIT_BEZAHLT_PRO_TAG=5000`.
   Achtung: Die vorhandene `.env` auf dem Server enthält noch `DUTYKIT_STRIPE_METER=dutykit_calls`
   (`deploy.sh` überschreibt sie nie). Beim Festpreis diese Zeile auf leer setzen; `STRIPE_SECRET_KEY` bleibt leer.
   Dann `bash deploy/deploy.sh <SERVER-IP>`.
5. **Probekauf im Testmodus:** Kauf mit Testkarte → Schlüsselseite zeigt den Schlüssel → Aufruf mit Schlüssel
   klappt → Abo in Stripe kündigen → der Schlüssel liefert HTTP 402. Erscheint kein Schlüssel, in Stripe beim
   Webhook die Zustellung ansehen (400 = falsches Geheimnis; 200 ohne Schlüssel = `plink_...` stimmt nicht).
6. **Auf live umstellen:** Produkt, Payment Link und Webhook im Live-Modus genauso anlegen, in der `.env`
   `STRIPE_WEBHOOK_SECRET` und `DUTYKIT_STRIPE_PAYMENT_LINK` durch die Live-Werte ersetzen, `docker compose up -d`.
7. **Seite:** Abschnitt aus `entwurf/pricing-abschnitt.html` in `site/index.html` einsetzen (Payment-Link eintragen),
   Badge "Public beta · free" und den JSON-LD-Preis anpassen, Impressum-Status und Datenschutzerklärung ergänzen
   (Stripe als Zahlungsdienst; gespeichert werden je Schlüssel Stripe-Kundennummer, Abo-Nummer und Aufrufzähler,
   keine E-Mail-Adresse, keine Eingaben). Dazu AGB bzw. Widerrufshinweise, je nach Auskunft aus Schritt 1.

Kündigung: Schlüsselseite und Preisabschnitt nennen nur den Weg per E-Mail an hallo@dutykit.dev; du kündigst das
Abo dann in Stripe. Wer Selbstkündigung anbieten will, schaltet in Stripe das Kundenportal ein und ergänzt den Link.

## Was der Server tut, wenn der Schalter an ist

| Ereignis | Wirkung |
|---|---|
| Kauf über den eigenen Payment Link, bezahlt | genau ein Schlüssel je Abo, auch wenn Stripe die Meldung wiederholt |
| Kauf eines anderen Produkts im selben Stripe-Konto | kein Schlüssel |
| Käufer landet auf `/schluessel?session_id=…` | sieht seinen Schlüssel; kommt die Meldung später an, hilft Neuladen |
| Abo `unpaid` oder pausiert | Schlüssel aus, Aufrufe liefern 402 |
| Abo wieder `active` | Schlüssel wieder an |
| Abo beendet | Schlüssel endgültig aus, auch wenn später noch eine Meldung "aktiv" eintrifft |
| volle Erstattung | alle Schlüssel dieses Kunden endgültig aus |
| Tageslimit erreicht | 429 bis zum nächsten Tag (UTC) |
| Aufruf ohne Schlüssel | Freistufe wie bisher |

Schlüssel von Hand: `docker compose exec dutykit python -c "import billing; print(billing.schluessel_anlegen('cus_...'))"`
