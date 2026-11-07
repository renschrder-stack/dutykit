#!/usr/bin/env bash
# Überträgt DutyKit auf den Server und startet ihn neu.
# Aufruf (Git Bash, aus dem Ordner prototyp):  bash deploy/deploy.sh <SERVER-IP>
set -euo pipefail
IP="${1:?Server-IP angeben}"
KEY="$HOME/.ssh/dutykit_ed25519"
SSH="ssh -i $KEY -o StrictHostKeyChecking=accept-new root@$IP"
$SSH "mkdir -p /opt/dutykit/deploy /opt/dutykit/site /opt/dutykit/deploy/data"
scp -i "$KEY" pflichtwerk_server.py app.py billing.py pflichten.json "root@$IP:/opt/dutykit/"
scp -i "$KEY" deploy/Dockerfile deploy/docker-compose.yml deploy/Caddyfile "root@$IP:/opt/dutykit/deploy/"
scp -i "$KEY" -r site/. "root@$IP:/opt/dutykit/site/"
$SSH "test -f /opt/dutykit/deploy/.env" || scp -i "$KEY" deploy/.env.example "root@$IP:/opt/dutykit/deploy/.env"
$SSH "chown -R 10001 /opt/dutykit/deploy/data && cd /opt/dutykit/deploy && docker compose up -d --build && sleep 5 && curl -s http://localhost/health -H 'Host: dutykit.dev' -k || true"
echo "Fertig. Test: curl https://dutykit.dev/health"
