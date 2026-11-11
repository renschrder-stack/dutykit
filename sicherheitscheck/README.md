# Sicherheitscheck

Prüft einen Projektordner mit mehreren Sicherheitswerkzeugen und schreibt **einen** Bericht
(`bericht.md` und `bericht.json`). Läuft lokal. Ausnahme: SkillSpector kann Paketnamen und Versionen aus Abhängigkeitslisten von Skills
an `api.osv.dev` schicken (siehe Datenschutz). Sonst gehen keine Projektdaten an Dienste.

Entstanden aus dem Video "5 Security Plugins" (Kanal Worth Making). Das Video beschreibt fünf
getrennte Werkzeuge, kein fertiges Gesamtprogramm. Diese Version Stufe 1 deckt die Werkzeuge ab,
die ohne KI-Schlüssel und ohne Docker laufen.

## Stufen

| Stufe | Was sie prüft | Werkzeug | Braucht |
|---|---|---|---|
| `basis` | Schlüssel im Klartext, Schlüsseldateien, `.env` ohne `.gitignore` | eigener Code | nichts |
| `trufflehog` | Geheimnisse im Dateibestand **und in der Git-Historie** (auch gelöschte) | [TruffleHog](https://github.com/trufflesecurity/trufflehog) (AGPL-3.0, wird nur aufgerufen) | `trufflehog`-Programm |
| `skillspector` | Skills (`SKILL.md`) im Projekt auf Schadmuster, ohne KI-Auswertung | [SkillSpector](https://github.com/NVIDIA/skillspector) von NVIDIA (Apache-2.0) | `skillspector`, Python 3.12+ |

Fehlt ein Programm, steht im Bericht **"NICHT geprüft"**. "Keine Funde" bei fehlenden Stufen ist kein Freispruch.

## Nicht enthalten (Stufe 2, nur auf Wunsch)

- Anthropic-Plugin `security-guidance`: läuft innerhalb von Claude Code beim Bauen, nicht von außen aufrufbar.
- [Cloudflare security-audit-skill](https://github.com/cloudflare/security-audit-skill) und [Strix](https://github.com/usestrix/strix): KI-Agenten, kosten Tokens. Strix braucht einen KI-Schlüssel und meist Docker.

## Benutzen

**Windows:** `starten.bat` doppelklicken, Ordner wählen, Bericht öffnet sich.
(Auf Windows noch nicht getestet, siehe unten.)

**Kommandozeile:**

```
pip install -e .
sicherheitscheck C:\pfad\zum\projekt
```

Rückgabecodes: `0` alles geprüft, keine Funde | `1` Funde | `2` Bedienfehler | `3` keine Funde, aber Stufen liefen nicht.

Berichte landen standardmäßig in `~/.sicherheitscheck/berichte/<Projekt>-<Zeit>/`, nicht im Projekt.

**Mit Claude:** `.claude/skills/sicherheitscheck/` in `%USERPROFILE%\.claude\skills\` kopieren.
Dann reicht in Claude Code der Satz "Sicherheitscheck". Claude führt das Kommando aus und fasst den Bericht zusammen.

## Programme einrichten

- **TruffleHog:** Windows-Programm von den [Releases](https://github.com/trufflesecurity/trufflehog/releases) in den Ordner `tools\` legen
  oder `SICHERHEITSCHECK_TRUFFLEHOG` auf den Pfad setzen.
- **SkillSpector:** `uv tool install git+https://github.com/NVIDIA/skillspector.git`
  (oder `SICHERHEITSCHECK_SKILLSPECTOR`).

## Datenschutz

- Geheimnisse stehen im Bericht nie im Klartext, nur Länge und Prüfsumme.
- **SkillSpector** fragt für Abhängigkeiten in Skills (z. B. `requirements.txt`) die Datenbank `api.osv.dev` ab, auch mit `--no-llm`. Es gehen Paketnamen und Versionen hinaus, kein Skill-Text. Bei Netzfehler nutzt es eine kleine eingebaute Liste. Quelle: `osv_client.py` im SkillSpector-Quelltext (Stand 11.11.2026). Ein Schalter zum Abschalten ist mir nicht bekannt, muss geprüft werden.
- Standardmäßig läuft TruffleHog mit `--no-verification`: gefundene Schlüssel werden **nicht** an die ausstellenden Dienste geschickt.
  Mit `--verifizieren` prüft TruffleHog, ob ein Schlüssel noch aktiv ist, und sendet ihn dafür dorthin.
- Ein gefundener Schlüssel gilt als kompromittiert. Beim Aussteller widerrufen. Löschen aus dem Code reicht nicht, die Git-Historie behält ihn.

## Grenzen (ehrlich)

- Getestet unter Linux. Die `starten.bat` und die Windows-Programme sind **nicht** getestet.
- TruffleHog und SkillSpector finden bekannte Muster. Keine Funde heißt nicht, dass das Projekt sicher ist.
- Die Grundprüfung ist bewusst klein und ersetzt TruffleHog nicht.
- Kein Angriffstest gegen eine laufende App (das wäre Strix, Stufe 2).

## Tests

```
python -m unittest discover -s tests -v
```

Der Test mit dem echten TruffleHog wird übersprungen, wenn das Programm fehlt.
