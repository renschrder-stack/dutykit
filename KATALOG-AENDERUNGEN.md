# Änderungsprotokoll des Katalogs

Öffentlich geführt, damit nachvollziehbar ist, wann und warum sich Aussagen geändert haben. Neueste zuerst.

## 2026-11-25
- **Präzisierung `de-impressum`:** § 5 Abs. 1 DDG am Wortlaut geprüft. Der Eintrag sprach von „ladungsfähiger Anschrift“; im Gesetz steht „Anschrift, unter der sie niedergelassen sind“. Der Eintrag folgt jetzt dem Wortlaut und nennt zusätzlich Rechtsform und Vertretungsberechtigten, Aufsichtsbehörde und Wirtschafts-Identifikationsnummer. Prüfsumme unverändert.

## 2026-11-23
- **`lu-anbieterinfo` jetzt belegt:** Art. 5 der Loi du 14 août 2000 relative au commerce électronique am Wortlaut der Urfassung im Journal officiel geprüft (Name, Anschrift, Kontaktdaten mit E-Mail, gegebenenfalls Berufsangaben, Handelsregisternummer, TVA-Nummer, Genehmigung). Spätere Änderungen des Gesetzes sind nicht geprüft; das steht in der Anmerkung des Eintrags.
- **Gegenprüfung `eu-anbieterinfo`:** Art. 5 der Richtlinie 2000/31/EG am Wortlaut geprüft, Inhalt unverändert. Der Eintrag hat jetzt eine Prüfsumme.
- **Gegenprüfung `de-werbung`:** § 7 Abs. 2 und 3 UWG am Wortlaut geprüft, Inhalt unverändert.
- **Quellenabgleich:** 18 Quellen unverändert, 0 Abweichungen, 13 nicht prüfbar (gesetze-im-internet.de antwortete nur auf einen Teil der Abrufe).
- **Gegenprüfung `eu-ki-hinweis`:** Art. 50 Abs. 1 der VO (EU) 2024/1689 am Wortlaut geprüft, Inhalt unverändert. Der Eintrag hat jetzt eine Prüfsumme.

## 2026-11-18
- **Gegenprüfung `de-e-rechnung`:** Die Prüfsumme der Seite zu § 27 UStG wich ab. Der Eintrag stützt sich nur auf Absatz 38; dessen Wortlaut wurde am 18.11. abgerufen und stimmt mit dem Eintrag überein (Fristen 31.12.2026 und 31.12.2027, Umsatzgrenze 800 000 Euro). Ebenfalls am Wortlaut geprüft: § 14 Abs. 1 und 2 UStG, § 33 und § 34a UStDV. Welcher andere Absatz von § 27 sich geändert hat, ließ sich nicht feststellen, weil der frühere Text nicht gespeichert ist. Die Prüfsumme überwacht jetzt nur noch Absatz 38. Inhalt des Eintrags unverändert, Prüfdatum 2026-11-18.
- **Neu in `rechnung_vorpruefen`:** Kleinbetragsrechnung nach § 33 UStDV (Gesamtbetrag bis 250 Euro), gegen den am 18.11. abgerufenen Wortlaut umgesetzt.
- **Quellenabgleich:** 22 Quellen unverändert, 6 nicht prüfbar (EUR-Lex viermal leere Antwort, § 5 DDG und § 257 HGB nicht abrufbar).

## 2026-11-08
- **Korrektur `de-verpackungsregister`:** Der Eintrag nannte § 9 VerpackG. Das Verpackungsgesetz wurde nach Sekundärquellen zum 12.08.2026 durch das Verpackungsrecht-Durchführungsgesetz (VerpackDG) abgelöst. Eintrag jetzt auf §§ 6, 7, 9 VerpackDG gegen den Gesetzestext geprüft.
- **Korrektur `eu-ki-kompetenz`:** Art. 4 AI Act verpflichtete zum „Sicherstellen“ von KI-Kompetenz. Die VO (EU) 2026/1744 (Digital Omnibus on AI) ersetzt das durch „Maßnahmen zur Unterstützung der Entwicklung“ ohne garantiertes Niveau. Gegen den Wortlaut der Änderungsverordnung geprüft.
- **Gegenprüfung `eu-ki-hinweis`:** Art. 50 Abs. 1 AI Act durch die VO (EU) 2026/1744 nicht geändert; Übergangsfrist bis 02.12.2026 gilt nur für Abs. 2.
- **Neu:** `de-widerrufsfunktion` (§ 356a BGB). 10 Einträge von „zu_pruefen“ auf „belegt“.
- **Neu:** automatischer Quellenabgleich per Prüfsumme (`scripts/quellen_pruefen.py`), Tool `katalog_status`.
