# Verzeichnisse: Eintragstexte und Stand

Alle Texte sind wahrheitsgemäß zum Stand 2026-11-18 (Katalog: DE, LU, EU; kostenlose Beta; kein Konto nötig).

## Fertige Texte (zum Einfügen)

**Name:** DutyKit  
**Endpoint (Streamable HTTP, ohne Konto):** https://dutykit.dev/mcp  
**Repository:** https://github.com/renschrder-stack/dutykit  
**Webseite / llms.txt:** https://dutykit.dev · https://dutykit.dev/llms.txt  
**Registry-Name:** io.github.renschrder-stack/dutykit  
**Lizenz:** Code MIT, Katalog CC BY 4.0  
**Kategorie / Tags:** Legal, Compliance, EU, Germany, Luxembourg, VAT, invoicing, GDPR, AI Act

**Kurzbeschreibung (EN, ≤ 100 Zeichen):**
EU business duties for AI agents: legal obligations with sources and pre-checks (DE, LU, EU)

**Beschreibung (EN):**
DutyKit tells an AI agent which business rules apply in Germany, Luxembourg and the EU, with the legal source, check date and verification status (verified against the legal text or not yet) for every obligation. It pre-checks invoices (mandatory fields, § 14 UStG), marketing messages (§ 7 UWG), returns AI-disclosure wording under AI Act Art. 50(1) in de/fr/en/lb and checks EU VAT IDs live via VIES. Every pre-check returns an audit receipt (timestamp, tool, responsible person, SHA-256). Source texts are monitored automatically; corrections are logged publicly. Free public beta, no account, no inputs stored. Not legal advice.

**Beschreibung (DE):**
DutyKit sagt KI-Agenten, welche geschäftlichen Pflichten in Deutschland, Luxemburg und der EU gelten, jeweils mit Rechtsquelle, Prüfdatum und Prüfstand (gegen den Gesetzestext geprüft oder noch nicht). Dazu Vorprüfungen für Rechnungen (§ 14 UStG) und Werbung (§ 7 UWG), KI-Hinweis nach AI Act Art. 50 Abs. 1 in vier Sprachen und Live-Prüfung von USt-IdNr. über VIES. Jede Prüfung liefert einen Nachweis mit SHA-256. Quellen werden automatisch überwacht, Korrekturen sind öffentlich protokolliert. Kostenlose Beta, kein Konto, keine Speicherung von Eingaben. Keine Rechtsberatung.

**Eintrag für awesome-mcp-servers** (Format vor dem Einreichen mit der aktuellen CONTRIBUTING.md abgleichen):
```
- [renschrder-stack/dutykit](https://github.com/renschrder-stack/dutykit) 🐍 ☁️ - EU business duties for AI agents (DE, LU, EU): obligations with legal sources and verification status, pre-checks for invoices and marketing consent, AI Act disclosure wording, live VAT ID check.
```

## Stand je Verzeichnis (geprüft im Wochenlauf 2026-11-18)

| Verzeichnis | Weg | Konto nötig | Stand 2026-11-18 |
|---|---|---|---|
| Offizielle MCP-Registry | `server.json` per CI (GitHub OIDC) | nur GitHub | **erledigt**: `io.github.renschrder-stack/dutykit` 0.2.0 ist `isLatest`, gleich `server.json`. Alter Eintrag `io.github.r08150816s-star/dutykit` 0.1.0 steht weiter |
| Glama | Eintrag beansprucht; Auto-Release über GitHub-Release | E-Mail-Code | **erledigt**: Abzeichen zeigt „rated A“, 7 Tools je Note A, Tool-Bewertung 4,7 von 5. GitHub-Release `v0.2.0` vom 18.11. vorhanden. Die Versionsnummer zeigt die Glama-Seite nicht an (nicht prüfbar) |
| awesome-mcp-servers | Pull Request https://github.com/punkpeye/awesome-mcp-servers/pull/19292 (vom Inhaber, 12.11.) | GitHub | **offen**: Betreuer verlangte am 17.11. eine Glama-Note, Inhaber hat am 18.11. geantwortet. `README.md` auf `main` enthält `renschrder-stack/dutykit` noch nicht |
| PulseMCP | übernimmt aus der offiziellen Registry; eigene Einreichung laut Quellen pausiert | nein | **nicht prüfbar** (`www.pulsemcp.com` ist in der Umgebung nicht freigegeben) |
| awesome-remote-mcp-servers (jaw9c) | Pull Request im fremden Repo | GitHub | **nicht eingetragen** (README enthält „dutykit“ nicht). Eintragstext unten |
| mcp.so | Formular bietet nur noch eine bezahlte Einreichung (39 $ einmalig) an; bewusst nicht gebucht | Zahlung | zurückgestellt; `https://mcp.so/server/dutykit` liefert 404 |
| Smithery | Verzeichnis läuft laut Quellen weiter, Proxy eingestellt | Smithery-Konto | **nicht prüfbar** (`smithery.ai` nicht freigegeben), niedrige Priorität |

## Neue Fundstellen (Recherche 2026-11-18, Angaben Dritter, vor dem Einreichen auf der jeweiligen Seite prüfen)

| Verzeichnis | Weg laut Quelle | Braucht |
|---|---|---|
| Docker MCP Catalog | Pull Request an `docker/mcp-registry` (dort liegt eine `CONTRIBUTING.md`) | GitHub-Konto des Inhabers |
| mcp.directory | Formular `https://mcp.directory/submit`, liest Angaben von GitHub | Formular durch den Inhaber |
| mcpservers.org | Web-Formular unter `/submit` | Formular durch den Inhaber |
| ToolHive-Katalog (`stacklok/toolhive-catalog`) | Pull Request | GitHub-Konto des Inhabers |

Für alle vier passen die fertigen Texte oben unverändert (Name, Endpoint, Kurzbeschreibung, Beschreibung EN).

**Eintrag für awesome-remote-mcp-servers** (Format vor dem Einreichen mit der dortigen README abgleichen):
```
| DutyKit | Legal / Compliance | `https://dutykit.dev/mcp` | Open (no auth) | [renschrder-stack](https://github.com/renschrder-stack/dutykit) |
```

## Wettbewerb (Glama „related“, 2026-11-18)
- `josemvelez78/mcp-europe-business`: 28 Tools, laut Eintrag 18+ Länder, u. a. Prüfung von Steuernummern und IBAN, USt-Sätze, Rechnungsregeln. Noten Lizenz A, Qualität A, Pflege D.
- „EMEA Compliance MCP“: Noten A / A / D; Einzelheiten am 18.11. nicht abrufbar.
- Was DutyKit davon unterscheidet: Prüfstand je Eintrag gegen den Gesetzestext und öffentliches Änderungsprotokoll. Was fehlt: Breite (Länder). Abgeleitete Verbesserung für den nächsten Lauf: keine neue Funktion, sondern FR/BE aus dem Backlog vorziehen, sobald die Primärquellen lesbar sind.
