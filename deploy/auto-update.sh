#!/usr/bin/env bash
# Läuft auf dem Server (per systemd-Timer): holt main von GitHub und liefert aus, wenn es etwas Neues gibt.
# Behält .env und data/, prüft nach dem Start den Gesundheitsstatus und rollt bei Fehler zurück.
set -euo pipefail
REPO_URL="${REPO_URL:-https://github.com/renschrder-stack/dutykit.git}"
SRC_DIR="${SRC_DIR:-/opt/dutykit-src}"
APP_DIR="${APP_DIR:-/opt/dutykit}"
LOG="${LOG:-/var/log/dutykit-update.log}"
log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$LOG"; }

[ -d "$SRC_DIR/.git" ] || git clone --quiet "$REPO_URL" "$SRC_DIR"
cd "$SRC_DIR"
git fetch --quiet origin main
NEU=$(git rev-parse origin/main)
ALT=$(cat "$APP_DIR/.deployed" 2>/dev/null || echo none)
[ "$NEU" = "$ALT" ] && exit 0
[ "$NEU" = "$(cat "$APP_DIR/.failed" 2>/dev/null || true)" ] && exit 0   # fehlgeschlagenen Stand nicht alle 10 Minuten neu versuchen

liefern() {  # $1 = Commit; jeder Schritt muss gelingen (set -e gilt innerhalb von "if" nicht)
  git checkout --quiet --force "$1" || return 1
  mkdir -p "$APP_DIR/deploy/data" "$APP_DIR/site" || return 1
  cp pflichtwerk_server.py app.py billing.py pflichten.json angebot.json server.json "$APP_DIR/" || return 1
  cp deploy/Dockerfile deploy/docker-compose.yml deploy/Caddyfile "$APP_DIR/deploy/" || return 1
  cp -r site/. "$APP_DIR/site/" || return 1
  [ -f "$APP_DIR/deploy/.env" ] || cp deploy/.env.example "$APP_DIR/deploy/.env" || return 1
  (cd "$APP_DIR/deploy" && docker compose up -d --build) || return 1
}
gesund() {
  for _ in 1 2 3 4 5 6; do
    sleep 5
    (cd "$APP_DIR/deploy" && docker compose exec -T dutykit python -c \
      "import urllib.request,sys;sys.exit(0 if b'\"ok\"' in urllib.request.urlopen('http://localhost:8080/health',timeout=5).read() else 1)") && return 0
  done
  return 1
}

log "Auslieferung ${NEU:0:7} (vorher ${ALT:0:7})"
if liefern "$NEU" && gesund; then
  echo "$NEU" > "$APP_DIR/.deployed"; log "OK ${NEU:0:7}"
else
  echo "$NEU" > "$APP_DIR/.failed"; log "FEHLER – Rollback auf ${ALT:0:7}"
  [ "$ALT" != none ] && liefern "$ALT" && gesund && log "Rollback OK" || log "Rollback fehlgeschlagen"
  git checkout --quiet --force origin/main
  exit 1
fi
