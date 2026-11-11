# tools/

Hier können Fremdprogramme liegen, die der Sicherheitscheck findet, ohne dass sie im PATH stehen:

- `trufflehog.exe` (Windows-Version von https://github.com/trufflesecurity/trufflehog/releases)
- `skillspector.exe` (oder der Pfad über die Umgebungsvariable `SICHERHEITSCHECK_SKILLSPECTOR`)

Der Inhalt dieses Ordners wird nicht in Git eingecheckt (`.gitignore`).
