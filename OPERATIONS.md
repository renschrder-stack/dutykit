# DutyKit – Betriebshandbuch für den Betriebsagenten

Ziel: DutyKit soll als verlässliche, ehrlich gekennzeichnete Rechtsquelle für KI-Agenten wachsen. Qualität vor Menge.

## Unverhandelbar
- Ein Eintrag ist nur `belegt`, wenn der Wortlaut der Primärquelle in dieser Sitzung abgerufen und verglichen wurde. Sonst `zu_pruefen` mit Anmerkung, was offen ist. Nie raten, nie Quellen erfinden.
- Keine Rechtsberatung formulieren; keine Eingaben der Nutzer speichern.
- Nichts mit Kosten, Zahlungen, Konten, DNS oder Server-Deploy ohne ausdrückliche Freigabe des Inhabers. Kein Geld ausgeben (keine bezahlten Einträge, kein Glama Boost, keine Abos); solche Möglichkeiten nur im Wochenbericht vorschlagen.
- Billing bleibt aus (`billing: false`), bis der Inhaber meldet, dass die Niederlassungsgenehmigung in Luxemburg vorliegt. Geld verdienen bleibt das Ziel: Vorarbeiten (Code, Tests, Texte) sind erlaubt, Einschalten nicht.
- Keine Zugangsdaten ins Repo. Keine Behauptungen über Nutzer, Kunden oder Erfolg, die die Zahlen nicht hergeben.
- In fremden Repositories und Konten nur lesen, nie kommentieren oder Anträge stellen.
- Arbeit auf Branch `claude/dutykit-ops`, Änderungen per Pull Request; nie direkt auf `main`.

## Auftrag des Inhabers (18.11.2026)
DutyKit soll ohne Zutun des Inhabers laufen. Ziel: KI-Agenten und deren Entwickler finden und benutzen DutyKit. Der Agent arbeitet innerhalb dieser Regeln selbstständig, stellt keine Rückfragen und berichtet einmal pro Woche. Was ohne den Inhaber nicht geht, steht ausschließlich im Wochenbericht unter „Braucht Sie“ und bleibt dort, bis es erledigt ist.

## Wöchentlicher Lauf (Reihenfolge)
0. **Quellenabgleich**: `python scripts/quellen_pruefen.py`. Bei ABWEICHUNG: neuen Text lesen, Eintrag anpassen (oder bestätigen, dass er unverändert gilt), Eintrag in `KATALOG-AENDERUNGEN.md`, dann `--neu-hashen <ID>`. Nie Prüfsummen neu setzen, ohne den Text gelesen zu haben. Am Ende `--schreiben`.
0b. **EU-Änderungen**: Prüfsummen erfassen spätere Änderungsrechtsakte nicht von selbst. Jede Woche per Suche prüfen: Digital Omnibus (DSGVO, ePrivacy, Data Act), AI Act, PPWR/VerpackDG, E-Rechnung, BFSG, § 356a BGB, LU-Gesetzgebung. Treffer als Änderungsakt in `pruefquellen` aufnehmen.
1. **Gesundheit**: `uv run --with "mcp>=2" --with pytest pytest -q` und `python scripts/katalog_pruefen.py` – Fehler zuerst beheben.
2. **Katalog prüfen**: Einträge mit `zu_pruefen` oder ältestem `geprueft` gegen die Primärquelle abgleichen (gesetze-im-internet.de, eur-lex, legilux). Bei Erfolg `belegt` + neues Datum, bei Abweichung Text korrigieren. Pro Lauf höchstens 8 Einträge, dafür gründlich.
3. **Gesetzesänderungen**: Nach relevanten Änderungen suchen (E-Rechnung, AI Act/Digital Omnibus, BFSG, DSGVO-Verfahren, LU-Gesetzgebung) und Katalog anpassen.
4. **Wachstum**: Backlog unten abarbeiten – ein Land oder eine Tätigkeit pro Lauf, jeweils mit Tests.
5. **Sichtbarkeit** (jede Woche, siehe Abschnitt unten).
6. **Wochenbericht** schreiben und zustellen (siehe Abschnitt unten).

## Sichtbarkeit bei Agenten
Jede Woche prüfen und, wo möglich, selbst verbessern:
- **Verzeichnisse:** Stand je Eintrag in `VERZEICHNISSE.md` fortschreiben: offizielle MCP-Registry (Version = `server.json`), Glama (Release aktuell, Noten, Abzeichen `https://glama.ai/mcp/servers/renschrder-stack/dutykit/badges/score.svg`), PulseMCP, awesome-mcp-servers (enthält `README.md` auf `main` die Zeichenfolge `renschrder-stack/dutykit`?), awesome-remote-mcp-servers, mcp.so, Smithery.
- **Neue Fundstellen:** Pro Lauf nach weiteren Verzeichnissen, Listen und Registern für MCP-Server suchen. Den fertigen Eintragstext in `VERZEICHNISSE.md` ablegen; wo ein Eintrag ein Konto oder einen Pull Request bei Dritten braucht, im Bericht unter „Braucht Sie“ nennen.
- **Auffindbarkeit:** Tool-Beschreibungen, `README.md`, `server.json`, `site/llms.txt`, `site/sitemap.xml` und die Startseite aktuell und für Agenten eindeutig halten. Pro Lauf höchstens ein neuer Leitfaden unter `site/blog/` (nur belegte Inhalte).
- **Wettbewerb:** Zwei bis drei vergleichbare Server (z. B. die bei Glama als verwandt gezeigten) ansehen: Was können sie, wie sind sie bewertet, was fehlt DutyKit? Daraus höchstens eine Verbesserung pro Lauf ableiten.
- **Messung:** Aufrufe aus `/health` (Feld `nutzung`, mit User-Agent `DutyKit-Pruefagent/1.0` abrufen). Seitenaufrufe der Website werden bisher nicht gezählt; ein Zähler ohne IP-Adressen und ohne Cookies ist ein Backlog-Punkt.
- **Glama-Release:** Ändert sich `version` in `server.json`, braucht Glama ein neues Release (Admin → Dockerfile → „Build & Release“, Anmeldung per E-Mail-Code an den Inhaber). Im Bericht unter „Braucht Sie“ nennen.

## Wochenbericht
Datei `berichte/JJJJ-KWnn.md` im Pull Request des Laufs, höchstens eine Bildschirmseite, einfache deutsche Sätze, in dieser Reihenfolge:
1. **Zahlen:** Aufrufe der Woche ohne Prüfsonden, Vergleich zur Vorwoche, Aufrufe je Tool, Prüfsonden getrennt; Stand je Verzeichnis in einer Zeile; LinkedIn-Beitrag der Woche (Thema, eingeplant ja/nein).
2. **Erledigt diese Woche.**
3. **Geplant für nächste Woche.**
4. **Braucht Sie:** nur, was ohne den Inhaber nicht geht, je Punkt ein Satz mit Ort und Wirkung. Im Normalfall leer.

Zustellung: Den Bericht per Mail an die Adresse des Inhabers senden (Mail-Werkzeug per ToolSearch nach `send_email` bzw. `send_message` suchen; nur an den Inhaber selbst, Betreff „DutyKit Wochenbericht KWnn“). Fehlt ein Mail-Werkzeug, genau eine PushNotification mit den drei wichtigsten Zahlen und dem Link zum Pull Request. Den Bericht zusätzlich vollständig als Abschlussnachricht ausgeben.

## Backlog (nach Wert)
1. LU-Einträge mit gesicherter legilux-Quelle (RCS/RBE, Rechnungsangaben, Datenschutz CNPD).
2. FR und BE (Kataloglücke laut README).
3. `rechnung_vorpruefen` für LU; Kleinbetragsrechnung (§ 33 UStDV) in DE.
4. Stripe-Webhook für Schlüsselvergabe (nur vorbereiten, nicht aktivieren).
5. Zähler für Seitenaufrufe der Website ohne IP-Adressen und ohne Cookies, Ausgabe in `/health`.

## Automatische Auslieferung
- Registry: `.github/workflows/publish-registry.yml` veröffentlicht `server.json` bei Änderung auf `main` (GitHub OIDC).
- Server: `deploy/auto-update.sh` läuft per systemd-Timer alle 10 Minuten auf dem Server, holt `main`, liefert aus, prüft `/health` und rollt bei Fehler zurück (Log `/var/log/dutykit-update.log`). Einmalig installiert mit `deploy/install-auto-update.sh`. Heißt: Was auf `main` landet, geht live – deshalb nur nach grüner CI mergen.

## Entscheidungen des Inhabers (offen)
- Zeitpunkt für Billing und Preise (Entwurf in `angebot.json`: Gratis 20/Tag, Credits 10 € für 1.000, Pro 29 €/Monat für 10.000, jeweils netto).
- Umsatzsteuer: Stripe allein erledigt sie nicht. Entscheiden: Stripe + Stripe Tax + eigene OSS-Meldung (mit Steuerberater) oder Merchant of Record (z. B. Paddle, Lemon Squeezy).
