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
7. **Weiterentwickeln:** einen Punkt aus dem Backlog in `REGELN.md` umsetzen, mit Tests.
8. **Sichtbarkeit:** eigene Kanäle verbessern (Leitfaden, `llms.txt`, README, Tool-Beschreibungen), Wettbewerb ansehen.
9. **LinkedIn:** einen Beitrag schreiben und in Postiz für Donnerstag 09:15 Uhr einplanen (Ablauf: `betrieb/linkedin/ABLAUF.md`).
10. **Wochenbericht:** `betrieb/berichte/JJJJ-KWnn.md` schreiben und per Mail an den Inhaber senden.

## Immer am Ende
- Tests grün, Pull Request von `claude/dutykit-ops` nach `main`, selbst mergen nach `REGELN.md`.
- Zwischen den Wochenberichten keine Nachricht an den Inhaber. Ausnahme: Server bleibt krank.

## Was der Agent nie tut
Geld ausgeben. Billing einschalten. Preise, DNS, Konten, Server per SSH ändern. Recht ohne Quelle behaupten. In Foren oder Chats posten.
