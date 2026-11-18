# DutyKit: Betriebsdoku für René

Stand: 2026-11-18. Geschrieben so, dass man ohne Vorwissen nachlesen kann, was läuft, wo es liegt und wie man eingreift. Für die Agenten gilt `OPERATIONS.md`, für Entwickler das `README.md`.

## 1. Was DutyKit ist, in fünf Sätzen
DutyKit ist ein MCP-Server für KI-Agenten: Er nennt Geschäftspflichten für Deutschland, Luxemburg und die EU mit Rechtsquelle und prüft Rechnungen, Werbung und KI-Hinweise vor. Er läuft unter **https://dutykit.dev/mcp** (kostenlose Beta, kein Konto, Eingaben werden nicht gespeichert). Der Katalog `pflichten.json` hat **23 Einträge, 22 davon gegen den Gesetzestext geprüft (`belegt`)**; offen ist `lu-anbieterinfo`. Gesetzestexte werden jede Woche per Prüfsumme überwacht. Bezahlung ist vorbereitet, aber **ausgeschaltet** (`billing: false`).

## 2. Was von allein läuft

| Was | Wann | Wo / Wer | Ergebnis bei Problemen |
|---|---|---|---|
| **Server aktualisiert sich** | alle 10 Minuten | systemd-Timer auf dem Server (`dutykit-update`) | Prüft `/health`, rollt bei Fehler zurück, versucht einen fehlerhaften Stand nicht erneut |
| **Registry-Eintrag** | bei jeder Änderung von `server.json` auf `main` | GitHub-Workflow `publish-registry.yml` | Aktuell **0.2.0** |
| **Tests + Katalogprüfung** | bei jedem Push | GitHub-Workflow `ci.yml` | rotes Kreuz am Pull Request |
| **Gesetzestexte gegen Prüfsummen** | montags 05:17 UTC | GitHub-Workflow `ci.yml` (Zeitplan) | Lauf schlägt fehl, wenn sich ein Text geändert hat |
| **Betriebsagent** (`trig_01A2R12zF8F3cse969K5mYKC`) | montags 14:41 Berlin | Routine auf claude.ai | Quellen prüfen, Katalog pflegen, Pull Request. **Aktuell blockiert**, siehe Abschnitt 6 |
| **Prüf- und Reparaturagent, Fable** (`trig_01WqJ2HVW8uwTUwV9w83Li3i`) | mittwochs 10:23 Berlin | Routine auf claude.ai | Bericht aufs Handy: Server, Katalog, Registry, Nutzung mit Vorwochenvergleich, Pull Request bei awesome-mcp-servers |
| **LinkedIn-Beitrag** (`trig_01UJen3wfbAG6Q78zLJosHja`) | dienstags 07:41 Luxemburg | Routine auf claude.ai | Schreibt einen Beitrag in Ihrem Stil, plant ihn in Postiz für **Donnerstag 09:15 Uhr** auf Ihrem LinkedIn-Profil ein |

Alle drei Routinen schicken eine Push-Nachricht aufs Handy, wenn sie fertig sind.

## 3. Wo was liegt

**Repository:** https://github.com/renschrder-stack/dutykit (öffentlich, Branch `main` = was live geht).
- `pflichtwerk_server.py`: die Tools. `app.py`: HTTP-Betrieb, Tageslimit, `/health` mit Nutzungszahlen. `billing.py`: Bezahlstufe (aus).
- `pflichten.json`: der Katalog (Quelle, Prüfdatum, Prüfstand, Prüfsummen). `angebot.json`: Preisentwurf, Pakete, Empfehlungstext für Agenten.
- `scripts/katalog_pruefen.py` (Format), `scripts/quellen_pruefen.py` (Gesetzestexte gegen Prüfsummen), `scripts/awesome-mcp-eintrag.sh`.
- `deploy/`: Docker, Caddy, `auto-update.sh`, `install-auto-update.sh`. `Dockerfile` im Hauptordner: lokaler Modus (stdio) für Glama.
- `KATALOG-AENDERUNGEN.md`: öffentliches Änderungsprotokoll. `VERZEICHNISSE.md`: Texte und Stand der Verzeichnisse. `OPERATIONS.md`: Regeln der Agenten.
- Branch `claude/linkedin-entwuerfe`: LinkedIn-Themenplan und Entwürfe (nie auf `main`).

**Server:** Hetzner, Projekt „Default“, Server `dutykit-1` (CPX02, Nürnberg), IP `2.31.184.250`.
- Dienst in Docker unter `/opt/dutykit` (Dateien) und `/opt/dutykit/deploy` (Compose, Caddy, `.env`, `data/`). Quellcode-Kopie: `/opt/dutykit-src`.
- Update-Skript: `/usr/local/bin/dutykit-update`, Log: `/var/log/dutykit-update.log`. Markierungen: `/opt/dutykit/.deployed` (aktueller Stand), `.failed` (fehlgeschlagener Stand).
- Zugang: SSH als `root` mit dem Schlüssel `~/.ssh/dutykit_ed25519` auf Ihrem PC, oder die Web-Konsole im Hetzner-Konto.

**Verzeichnisse:** Offizielle MCP-Registry `io.github.renschrder-stack/dutykit` (0.2.0; der alte Eintrag `io.github.r08150816s-star/dutykit` 0.1.0 bleibt stehen und lässt sich nicht entfernen). Glama: Eintrag beansprucht, Release 0.2.0 seit 18.11., Tool-Bewertung 4,7 von 5.

**Postiz:** Kanäle über `https://api.postiz.com/mcp`. LinkedIn-Profil „René Schröder“ hat die Kanal-ID `cmvjx0rni024klh0yatdinpjg`. Die Seite „PontoIt“ ist ein anderer Kanal (`linkedin-page`) und wird von DutyKit nie benutzt.

## 4. Zugänge und Geheimnisse

| Was | Wo gespeichert | Wer kann es sehen |
|---|---|---|
| Postiz-API-Schlüssel | Netzwerk-Geheimnis der Umgebung „Default“ (claude.ai/code), für `api.postiz.com` | Niemand liest ihn aus; er wird nur automatisch an Anfragen zu `api.postiz.com` gehängt. Gilt für **alle** Sitzungen dieser Umgebung. |
| GitHub-Zugriff der Claude-App | GitHub-App-Installation für `renschrder-stack/dutykit` | Sitzungen, die das Repo als Quelle haben |
| Server-Schlüssel | `~/.ssh/dutykit_ed25519` auf Ihrem PC | Nur Sie |
| Stripe | **nicht eingerichtet** | – |

**Freigegebene Internetadressen der Umgebung „Default“ (von mir ergänzt):** `www.gesetze-im-internet.de`, `eur-lex.europa.eu`, `legilux.public.lu`, `dutykit.dev`, `mcp.so`, `glama.ai`, `api.postiz.com`, `cli-auth.postiz.com`. (`www.youtube.com` stammt nicht von mir.)

**Postiz-Schlüssel zurücknehmen:** In Postiz einen neuen Schlüssel erzeugen, den alten Eintrag in den Netzwerk-Geheimnissen der Umgebung löschen. Danach funktioniert die Anbindung nicht mehr, bis ein neuer hinterlegt ist. Hinweis: Die Postiz-REST-Schnittstelle verlangt den Schlüssel ohne „Bearer“ und lehnt ihn so ab; nur der MCP-Zugang (`/mcp`) nimmt ihn an.

## 5. Bedienung: wie greife ich ein?

**Server gesund?** https://dutykit.dev/health muss `{"ok": true, "billing": false, …}` zeigen.

**Server sofort aktualisieren:** `ssh -i ~/.ssh/dutykit_ed25519 root@2.31.184.250 dutykit-update`

**Log des Servers ansehen:** `ssh -i ~/.ssh/dutykit_ed25519 root@2.31.184.250 tail -40 /var/log/dutykit-update.log`

**Container-Log:** `ssh … "cd /opt/dutykit/deploy && docker compose logs --tail 50 dutykit"`

**Eine Routine pausieren oder ändern:** claude.ai/code → geplante Aufgaben (Routinen). Dort lässt sich jede der drei DutyKit-Routinen pausieren, sofort ausführen oder ändern.

**Den LinkedIn-Beitrag stoppen oder ändern:** Im Postiz-Kalender den Beitrag öffnen und löschen oder bearbeiten, bis zur Veröffentlichung (Donnerstag 09:15 Uhr).

**Eine Änderung zurücknehmen:** Auf GitHub den betreffenden Pull Request „Revert“ klicken und mergen. Der Server holt sich den Stand innerhalb von 10 Minuten.

**Wenn der Server nicht antwortet:** (1) `/health` prüfen, (2) per SSH das Log ansehen (s. o.), (3) `docker compose ps` im Ordner `/opt/dutykit/deploy`. Docker startet abgestürzte Container selbst neu. Fehlerhafte neue Versionen rollen sich zurück. Im Zweifel den Prüfagenten oder mich fragen und den Logtext mitschicken.

## 6. Bekannte Einschränkungen

1. **Routinen können nicht auf GitHub schreiben (offen, wichtigster Punkt).** In den geplanten Sitzungen fehlt das Werkzeug `add_repo`, deshalb endet jeder Push mit 403. Folge: Der Betriebsagent hat am 16.11. nichts getan (nur gemeldet), und der LinkedIn-Agent konnte seinen Entwurf nicht im Repo ablegen. Der Beitrag selbst wurde trotzdem in Postiz eingeplant. **Behebung, nur von Ihnen möglich:** auf claude.ai/code bei jeder der drei Routinen unter **Quellen** das Repo `renschrder-stack/dutykit` mit Schreibrecht eintragen. Bis dahin liegen die Entwürfe nur in der Abschlussnachricht der Routine.
2. **Postiz meldete am 12.11. zeitweise „Post not found“** beim Anlegen von Beiträgen. Er verschwand von selbst. Der LinkedIn-Agent versucht es bis zu dreimal und prüft vorher auf Doppelte.
3. **EUR-Lex und Legilux** lassen sich aus manchen Umgebungen nicht lesen (leere Antwort bzw. nur JavaScript-Gerüst). Solche Quellen gelten als „nicht prüfbar“, nicht als geändert. Betroffen: `lu-anbieterinfo` (bleibt `zu_pruefen`) und EU-Einträge (werden zusätzlich per Recherche geprüft).
4. **Prüfsummen erkennen nur Änderungen des abgerufenen Textes**, nicht neue Änderungsrechtsakte der EU. Die sucht der Betriebsagent wöchentlich per Recherche (sobald er schreiben darf).
5. **Nutzungszahlen** zählen Aufrufe, keine Nutzer. Automatische Prüfsonden von Verzeichnissen stehen getrennt, der Prüfagent zählt nicht mit. Meine eigenen Tests sind bis 12.11. enthalten.
6. **Die Docker-Datei im Hauptordner** (lokaler Modus für Glama) konnte ich ohne Docker-Dienst nicht bauen. Der Start des Servers im lokalen Modus wurde direkt getestet.

## 7. Offene Entscheidungen und Aufgaben

**Mit Handlungsbedarf**
- **Glama-Bewertung für awesome-mcp-servers.** Am 18.11. erledigt: Auf Glama ist das Release 0.2.0 veröffentlicht (Admin → Dockerfile: Python 3.12, Build-Schritte `uv venv` und `uv pip install "mcp>=2.3,<3"`, Start `/app/.venv/bin/python pflichtwerk_server.py`; Glama baut selbst und nutzt die `Dockerfile` im Hauptordner nicht). Die sieben Tools sind bewertet (Schnitt 4,7 von 5, alle Note A). Die Gesamtnote für Qualität stand am 18.11. mittags noch aus. Offen: im Pull Request https://github.com/punkpeye/awesome-mcp-servers/pull/19292 mit einem Satz antworten. Anmeldung bei Glama: per E-Mail-Code an die Yahoo-Adresse. Bei einer neuen Version auf Glama erneut „Build & Release“ auslösen.
- **Routinen mit Repo-Quelle ausstatten** (Abschnitt 6, Punkt 1).

**Ohne Eile**
- Preise: Entwurf in `angebot.json` (Gratis 20 Aufrufe/Tag, Credits 10 € für 1.000, Pro 29 €/Monat für 10.000, jeweils netto). Billing bleibt aus, bis geklärt ist: Stripe-Konto der Firma, Umsatzsteuer (Stripe Tax mit eigener Meldung oder ein Anbieter, der sie übernimmt, am besten mit Steuerberater), Niederlassungsgenehmigung.
- mcp.so verlangt 39 € einmalig für eine Einreichung; bewusst nicht gebucht.
- Frankreich und Belgien sind geplant, aber noch nicht im Katalog.
- Kleinbetragsrechnung (§ 33 UStDV) fehlt noch in `rechnung_vorpruefen`. Der Betriebsagent soll sie nachholen, sobald er schreiben darf.

## 8. Kennzahlen (Stand 2026-11-18)
- Katalog: EU 6 von 6, DE 14 von 14, LU 2 von 3 belegt (insgesamt 22 von 23). Letzter Quellenabgleich: 2026-11-08, 28 Quellen unverändert, keine Abweichung.
- Nutzung 12.–18.11.: 18 Aufrufe (ohne Sonden), 25 Prüfsonden; Vorwoche 26 Aufrufe (−31 %). Noch kein belastbarer Hinweis auf wiederkehrende echte Nutzer.
- LinkedIn: Beitrag vom 13.11. (Widerrufsbutton) veröffentlicht; Beitrag für 19.11. 09:15 Uhr (Verpackungsregister) eingeplant.

## 9. Was ich nicht weiß
Wie viele Agenten DutyKit wirklich nutzen, ob die Verzeichnisse echte Nutzer bringen und wann der Pull Request bei awesome-mcp-servers geprüft wird. Das zeigen die Wochenberichte des Prüfagenten.
