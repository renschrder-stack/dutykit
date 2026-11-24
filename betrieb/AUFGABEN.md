# DutyKit: Aufgaben des Agenten

Ein Agent pflegt DutyKit allein. Er läuft **Montag, Mittwoch, Freitag um 07:13 Uhr** (Luxemburg).
Regeln und Grenzen: `betrieb/REGELN.md` (verbindlich, vor jedem Lauf frisch lesen).
Er stellt keine Rückfragen. Was nur der Inhaber kann, steht im Wochenbericht unter „Braucht Sie“.

## Jeder Lauf (Mo, Mi, Fr)
1. **Prüfen:** Server gesund? (`/health`, Startseite, MCP `tools/list`, je ein Aufruf von `katalog_status`, `pflichten`, `rechnung_vorpruefen`). User-Agent `DutyKit-Pruefagent/1.0`.
2. **Reparieren:** Fehler im Repo sofort beheben (Test dazu, Pull Request, selbst mergen). Liegt der Fehler außerhalb des Repos: eine Push-Nachricht.
3. **Einreichen:** höchstens eine Einreichung bei einem Verzeichnis, frühestens 48 Stunden nach der letzten (Regeln: `REGELN.md`, Abschnitt „Sichtbarkeit: selbstständig mehr Nutzer gewinnen“).
4. **Verzeichnisse prüfen:** Stand in `betrieb/VERZEICHNISSE.md` nachtragen.
5. **Stand schreiben:** `betrieb/STAND.md` neu schreiben (Vorlage dort beibehalten, kurze Sätze).

## Zusätzlich montags
6. **Katalog:** Quellenabgleich, EU-Änderungen suchen, bis zu 8 Einträge am Gesetzestext prüfen.
7. **LinkedIn:** einen Beitrag schreiben und dem Inhaber mailen, nicht einplanen (Postiz gekündigt, Veröffentlichung von Hand über die Seite PontoIt; Ablauf: `betrieb/linkedin/ABLAUF.md`).
8. **Wochenbericht:** `betrieb/berichte/JJJJ-KWnn.md` schreiben und per Mail an den Inhaber senden. Danach prüfen, dass die Mail wirklich raus ist (Antwort des Mail-Werkzeugs lesen). Im Bericht und in `STAND.md` steht nur dann „gemailt“, wenn das Werkzeug den Versand bestätigt hat; sonst steht dort „Mail nicht gesendet“ mit dem Fehler, und es geht eine Push-Nachricht raus.

## Zusätzlich mittwochs: Sichtbarkeit (Pflicht, nicht verschieben)
9. **Neue Seite:** genau einen neuen Leitfaden unter `site/blog/` veröffentlichen, zu einer Frage, die Agenten oder Entwickler wirklich stellen. Nur belegte Inhalte. Mit Zählbild, Eintrag in `site/blog/index.html`, `site/sitemap.xml` und `site/llms.txt`.
10. **Verlinken:** die neue Seite von mindestens zwei bestehenden Seiten aus verlinken (Startseite, verwandte Leitfäden, README).
11. **Auswerten:** aus `/health` lesen, welche Seiten und Werkzeuge aufgerufen wurden. Eine Sache nachbessern, die das nahelegt (Titel, Beschreibung, Tool-Beschreibung, Beispiel).
12. **Wettbewerb:** zwei vergleichbare Server ansehen, höchstens eine Verbesserung ableiten.

## Zusätzlich freitags: Weiterentwickeln (Pflicht, nicht verschieben)
13. **Backlog:** genau einen Punkt aus dem Backlog in `REGELN.md` fertig umsetzen, mit Tests. Ist der oberste Punkt blockiert, den nächsten nehmen und den Grund in `STAND.md` nennen.

## Immer am Ende
- In `STAND.md` unter „Nicht geschafft“ jede Aufgabe dieses Tages nennen, die nicht erledigt wurde, mit einem Satz Grund. Ist alles erledigt, steht dort „Nichts“.
- Tests grün, Pull Request von `claude/dutykit-ops` nach `main`, selbst mergen nach `REGELN.md`.
- Zwischen den Wochenberichten keine Nachricht an den Inhaber. Ausnahme: Server bleibt krank.

## Was der Agent nie tut
Geld ausgeben. Billing einschalten. Preise, DNS, Konten, Server per SSH ändern. Recht ohne Quelle behaupten. In Foren oder Chats posten.
