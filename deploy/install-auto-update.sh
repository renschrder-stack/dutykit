#!/usr/bin/env bash
# Einmal auf dem Server als root ausführen (z. B. in der Hetzner-Web-Konsole). Danach aktualisiert sich der Server selbst.
set -euo pipefail
command -v git >/dev/null || { apt-get update -qq && apt-get install -y -qq git; }
command -v docker >/dev/null || { echo "Docker fehlt"; exit 1; }
SRC=/opt/dutykit-src
[ -d "$SRC/.git" ] || git clone --quiet https://github.com/renschrder-stack/dutykit.git "$SRC"
git -C "$SRC" fetch --quiet origin main && git -C "$SRC" checkout --quiet --force origin/main
install -m 755 "$SRC/deploy/auto-update.sh" /usr/local/bin/dutykit-update
cat > /etc/systemd/system/dutykit-update.service <<'U'
[Unit]
Description=DutyKit automatisch aktualisieren
[Service]
Type=oneshot
ExecStart=/usr/local/bin/dutykit-update
U
cat > /etc/systemd/system/dutykit-update.timer <<'U'
[Unit]
Description=DutyKit Aktualisierung alle 10 Minuten
[Timer]
OnBootSec=2min
OnUnitActiveSec=10min
[Install]
WantedBy=timers.target
U
systemctl daemon-reload && systemctl enable --now dutykit-update.timer
/usr/local/bin/dutykit-update && echo "Fertig: Server aktualisiert sich ab jetzt selbst (Log: /var/log/dutykit-update.log)"
