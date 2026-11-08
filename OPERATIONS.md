# DutyKit – Betriebshandbuch für den Betriebsagenten

Ziel: DutyKit soll als verlässliche, ehrlich gekennzeichnete Rechtsquelle für KI-Agenten wachsen. Qualität vor Menge.

## Unverhandelbar
- Ein Eintrag ist nur `belegt`, wenn der Wortlaut der Primärquelle in dieser Sitzung abgerufen und verglichen wurde. Sonst `zu_pruefen` mit Anmerkung, was offen ist. Nie raten, nie Quellen erfinden.
- Keine Rechtsberatung formulieren; keine Eingaben der Nutzer speichern.
- Nichts mit Kosten, Zahlungen, Konten, DNS oder Server-Deploy ohne ausdrückliche Freigabe des Inhabers. Billing bleibt aus.
- Arbeit auf Branch `claude/dutykit-ops`, Änderungen per Pull Request; nie direkt auf `main`.

## Wöchentlicher Lauf (Reihenfolge)
1. **Gesundheit**: `uv run --with "mcp>=2" --with pytest pytest -q` und `python scripts/katalog_pruefen.py` – Fehler zuerst beheben.
2. **Katalog prüfen**: Einträge mit `zu_pruefen` oder ältestem `geprueft` gegen die Primärquelle abgleichen (gesetze-im-internet.de, eur-lex, legilux). Bei Erfolg `belegt` + neues Datum, bei Abweichung Text korrigieren. Pro Lauf höchstens 8 Einträge, dafür gründlich.
3. **Gesetzesänderungen**: Nach relevanten Änderungen suchen (E-Rechnung, AI Act/Digital Omnibus, BFSG, DSGVO-Verfahren, LU-Gesetzgebung) und Katalog anpassen.
4. **Wachstum**: Backlog unten abarbeiten – ein Land oder eine Tätigkeit pro Lauf, jeweils mit Tests.
5. **Sichtbarkeit**: Pro Lauf höchstens ein neuer Leitfaden unter `site/blog/` (nur belegte Inhalte), Sitemap und `llms.txt` aktualisieren.
6. **Bericht**: Kurze Zusammenfassung im Pull Request: was geprüft, was geändert, was der Inhaber entscheiden muss.

## Backlog (nach Wert)
1. LU-Einträge mit gesicherter legilux-Quelle (RCS/RBE, Rechnungsangaben, Datenschutz CNPD).
2. FR und BE (Kataloglücke laut README).
3. `rechnung_vorpruefen` für LU; Kleinbetragsrechnung (§ 33 UStDV) in DE.
4. Stripe-Webhook für Schlüsselvergabe (nur vorbereiten, nicht aktivieren).
5. Tool `katalog_status` (Anzahl belegt/zu_pruefen je Land) für Transparenz.

## Entscheidungen des Inhabers (offen)
- Registry: neue Version 0.1.1 unter `io.github.renschrder-stack/dutykit` veröffentlichen (`mcp-publisher`, GitHub-Login nötig). Aktuell steht dort noch das alte Konto in 0.1.0.
- Deploy der neuen Version auf den Server (`deploy/deploy.sh`).
- Zeitpunkt für Billing und Preise (Entwurf in `angebot.json`: Gratis 20/Tag, Credits 10 € für 1.000, Pro 29 €/Monat für 10.000, jeweils netto).
- Umsatzsteuer: Stripe allein erledigt sie nicht. Entscheiden: Stripe + Stripe Tax + eigene OSS-Meldung (mit Steuerberater) oder Merchant of Record (z. B. Paddle, Lemon Squeezy).
