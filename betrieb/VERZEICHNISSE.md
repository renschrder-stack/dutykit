# Verzeichnisse: Eintragstexte und Stand

Alle Texte sind wahrheitsgemäß zum Stand 2026-11-27 (Katalog: DE, LU, EU; kostenlose Beta; kein Konto nötig).

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

## Einreichungen des Agenten
Höchstens eine alle 48 Stunden. Vor jeder Einreichung diese Liste lesen.

| Zeitpunkt (UTC) | Verzeichnis | Weg | Ergebnis |
|---|---|---|---|
| 2026-11-23 06:16 | mcp.directory | Formular `https://mcp.directory/submit` (GitHub-Adresse und Kurzbeschreibung, keine E-Mail angegeben) | Antwort der Seite: „Server submitted for review!“, Veröffentlichung laut Seite binnen 24 Stunden. Vorher geprüft: Suche nach „dutykit“ ergab „No servers found“ |
| 2026-11-25 06:17 | mcpservers.org | Formular `https://mcpservers.org/submit`, kostenlose Variante (Name, Kategorie „Other“, Kurzbeschreibung, GitHub-Adresse, Registry-Name, Endpoint `https://dutykit.dev/mcp` ohne Anmeldung, Kontakt `hallo@dutykit.dev`) | Antwort der Seite: „Submission Successful!“, Prüfung laut Seite binnen 2 Wochen, Nachricht an die Kontaktadresse. Vorher geprüft: Websuche auf mcpservers.org nach „dutykit“ ohne Treffer (die Suche der Seite selbst ist für automatische Abrufe gesperrt) |

**Stand 27.11.:** Keine Einreichung. Die kostenlosen Formulare sind ausgeschöpft. Übrig sind Pull Requests in fremden Repositories (awesome-remote-mcp-servers, Docker MCP Catalog, ToolHive-Katalog). Der GitHub-Zugang des Agenten gilt nur für `renschrder-stack/dutykit`; er kann dort keinen Fork anlegen und keinen Pull Request stellen. Die 48-Stunden-Sperre ist seit 27.11. 06:17 UTC abgelaufen.

## Stand je Verzeichnis (geprüft im Lauf 2026-11-27)

| Verzeichnis | Stand 2026-11-27 |
|---|---|
| Offizielle MCP-Registry | **eingetragen**: `io.github.renschrder-stack/dutykit` 0.2.0 ist `isLatest`. Alter Eintrag `io.github.r08150816s-star/dutykit` 0.1.0 steht weiter |
| Glama | **eingetragen**: Abzeichen zeigt „rated A“. Abzeichen im README, Website verlinkt den Eintrag |
| awesome-mcp-servers | **offen, wartet auf die Antwort des Inhabers**: Betreuer bat am 23.11. um das Glama-Abzeichen im README und eine Erwähnung im Pull Request https://github.com/punkpeye/awesome-mcp-servers/pull/19292. Das Abzeichen ist seit 25.11. da. Am 27.11. keine neue Nachricht im Pull Request |
| mcp.directory | **eingereicht am 23.11.**, am 27.11. noch nicht sichtbar (Suche: „No servers found“) |
| mcpservers.org | **eingereicht am 25.11.**, Prüfung laut Seite binnen 2 Wochen; Sichtbarkeit nicht prüfbar (Suche der Seite ist für automatische Abrufe gesperrt) |
| PulseMCP | **nicht prüfbar**: „Access Denied“ |
| Smithery | **nicht eingetragen**: Suche zeigt „0 servers“ |
| awesome-remote-mcp-servers (jaw9c) | **nicht eingetragen**. Eintragstext unten; Pull Request kann der Agent nicht stellen |
| mcp.so | **zurückgestellt**: nur bezahlte Einreichung (39 $) |

## Weitere Fundstellen (Recherche 2026-11-18, Angaben Dritter, vor dem Einreichen auf der jeweiligen Seite prüfen)

| Verzeichnis | Weg laut Quelle |
|---|---|
| Docker MCP Catalog | Pull Request an `docker/mcp-registry` (dort liegt eine `CONTRIBUTING.md`) |
| ToolHive-Katalog (`stacklok/toolhive-catalog`) | Pull Request |

Für alle passen die fertigen Texte oben unverändert (Name, Endpoint, Kurzbeschreibung, Beschreibung EN).

**Eintrag für awesome-remote-mcp-servers** (Format vor dem Einreichen mit der dortigen README abgleichen):
```
| DutyKit | Legal / Compliance | `https://dutykit.dev/mcp` | Open (no auth) | [renschrder-stack](https://github.com/renschrder-stack/dutykit) |
```

## Wettbewerb (Glama „related“, zuletzt angesehen 2026-11-25)
- `josemvelez78/mcp-europe-business`: 28 Tools, laut Eintrag 18+ Länder, u. a. Prüfung von Steuernummern und IBAN, USt-Sätze, Rechnungsregeln. Noten Lizenz A, Qualität A, Pflege D.
- „EMEA Compliance MCP“: Noten A / A / D; Einzelheiten am 18.11. nicht abrufbar.
- Was DutyKit davon unterscheidet: Prüfstand je Eintrag gegen den Gesetzestext und öffentliches Änderungsprotokoll. Was fehlt: Breite (Länder). Abgeleitete Verbesserung für den nächsten Lauf: keine neue Funktion, sondern FR/BE aus dem Backlog vorziehen, sobald die Primärquellen lesbar sind.
- 25.11.: `closermethod/emea-compliance-mcp` ist ein lokaler Server mit Vertriebshinweisen für Europa (Kategorien CRM, Legal & Compliance, Marketing), kein Pflichtenkatalog. `josemvelez78/mcp-europe-business` steht unter Legal & Compliance und Finance. Abgeleitet: keine Änderung am Server; der neue Leitfaden zu den Anbieterangaben deckt ein Thema ab, das beide nicht haben.
