#!/usr/bin/env bash
# Trägt DutyKit in eine Kopie (Fork) von punkpeye/awesome-mcp-servers ein und schiebt den Branch hoch.
# Voraussetzung: Der Fork https://github.com/renschrder-stack/awesome-mcp-servers existiert (Knopf "Fork" auf GitHub).
# Danach nur noch den ausgegebenen Link öffnen und "Create pull request" klicken.
set -euo pipefail
FORK_OWNER="${FORK_OWNER:-renschrder-stack}"
LINE='- [renschrder-stack/dutykit](https://github.com/renschrder-stack/dutykit) [![renschrder-stack/dutykit MCP server](https://glama.ai/mcp/servers/renschrder-stack/dutykit/badges/score.svg)](https://glama.ai/mcp/servers/renschrder-stack/dutykit) 🐍 ☁️ - EU business duties for AI agents (DE, LU, EU): obligations with legal sources and verification status, pre-checks for invoices and marketing consent, AI Act disclosure wording and live VAT ID check.'
cd "$(mktemp -d)"
git clone --quiet "https://github.com/${FORK_OWNER}/awesome-mcp-servers.git"
cd awesome-mcp-servers
grep -q 'renschrder-stack/dutykit' README.md && { echo "Eintrag ist schon vorhanden."; exit 0; }
git remote add upstream https://github.com/punkpeye/awesome-mcp-servers.git
git fetch --quiet upstream main && git checkout --quiet -B add-dutykit upstream/main
# Einfügen im Abschnitt "Legal", alphabetisch zwischen ptrinh/... und sebastianfoerste/...
ZIEL=$(grep -n -F -- '- [sebastianfoerste/eu-reg-mcp]' README.md | head -1 | cut -d: -f1)
[ -n "$ZIEL" ] || { echo "Einfügestelle nicht gefunden – bitte Bescheid sagen."; exit 1; }
printf '%s\n' "$LINE" > /tmp/dutykit-zeile.txt
sed -i "$((ZIEL-1))r /tmp/dutykit-zeile.txt" README.md
[ "$(grep -c 'renschrder-stack/dutykit' README.md)" -ge 1 ] || { echo "Einfügen fehlgeschlagen."; exit 1; }
git add README.md
git -c user.name="renschrder-stack" -c user.email="renschrder-stack@users.noreply.github.com" commit --quiet -m "Add renschrder-stack/dutykit (Legal)"
git push --quiet -u origin add-dutykit
echo
echo "Fertig. Jetzt diesen Link öffnen und 'Create pull request' klicken:"
echo "https://github.com/punkpeye/awesome-mcp-servers/compare/main...${FORK_OWNER}:add-dutykit?expand=1"
echo
echo "Titel:  Add renschrder-stack/dutykit (Legal)"
echo "Text:   Adds DutyKit to the Legal section: EU business duties for AI agents (DE, LU, EU) with legal sources and verification status, pre-checks for invoices and marketing consent, AI Act disclosure wording and a live VAT ID check. Python, self-hostable (see deploy/), also available as a hosted endpoint. Glama listing is claimed."
