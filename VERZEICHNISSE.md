# Verzeichnisse: Eintragstexte und Stand

Alle Texte sind wahrheitsgemäß zum Stand 2026-11-10 (Katalog: DE, LU, EU; kostenlose Beta; kein Konto nötig).

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

## Stand je Verzeichnis (Recherche 2026-11-10, Quellen Dritter, vor dem Einreichen auf der jeweiligen Seite prüfen)

| Verzeichnis | Weg | Konto nötig | Stand |
|---|---|---|---|
| Offizielle MCP-Registry | `server.json` per CI (GitHub OIDC) | nur GitHub | **erledigt**, 0.2.0 aktuell |
| PulseMCP | übernimmt aus der offiziellen Registry (wöchentlich); eigene Einreichung laut Quellen pausiert | nein | **automatisch**, nichts zu tun |
| Glama | indexiert öffentliche GitHub-Server; Eintrag dort beanspruchen/prüfen | GitHub-Login | offen |
| mcp.so | Web-Formular mit Repository-URL | evtl. Login | offen |
| Smithery | CLI/Dashboard; Smithery-Proxy endete laut Quelle 31.10.2026, Verzeichnis läuft weiter | Smithery-Konto (GitHub-Login) | niedrige Priorität |
| Glama (Stand 2026-11-12) | Eintrag **beansprucht** (Ownership verified), Status Healthy | GitHub | **erledigt** |
| mcp.so | Formular bietet nur noch eine bezahlte Einreichung (39 $ einmalig) an; bewusst nicht gebucht | Zahlung | zurückgestellt |
| awesome-mcp-servers | Pull Request per `scripts/awesome-mcp-eintrag.sh` (Fork nötig); Kategorie Legal, Regeln: öffentlicher GitHub-Code zum Selbstbetrieb | GitHub | bereit, Pull Request noch zu stellen |
