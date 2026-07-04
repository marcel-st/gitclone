#!/usr/bin/env bash
# Nightly backup: dumps both Postgres databases and the Forgejo data volume.
# Writes a timestamped directory under BACKUP_DIR and prunes old ones.
#
# Usage: BACKUP_DIR=/srv/backups scripts/backup.sh
# Cron:  0 3 * * *  cd /path/to/gitclone && BACKUP_DIR=/srv/backups scripts/backup.sh >> /var/log/gitclone-backup.log 2>&1
set -euo pipefail

cd "$(dirname "$0")/.."

# shellcheck disable=SC1091
set -a; [ -f .env ] && . ./.env; set +a

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION="${BACKUP_RETENTION:-14}"
STAMP="$(date +%Y%m%d_%H%M%S)"
DEST="${BACKUP_DIR}/${STAMP}"
COMPOSE="docker compose"

mkdir -p "${DEST}"
echo "[backup] writing to ${DEST}"

echo "[backup] dumping ${ORCHESTRATOR_DB_NAME}"
${COMPOSE} exec -T db pg_dump -U "${POSTGRES_SUPERUSER}" -d "${ORCHESTRATOR_DB_NAME}" \
  | gzip > "${DEST}/orchestrator.sql.gz"

echo "[backup] dumping ${FORGEJO_DB_NAME}"
${COMPOSE} exec -T db pg_dump -U "${POSTGRES_SUPERUSER}" -d "${FORGEJO_DB_NAME}" \
  | gzip > "${DEST}/forgejo.sql.gz"

echo "[backup] archiving Forgejo data volume"
${COMPOSE} exec -T forgejo tar czf - -C /data . > "${DEST}/forgejo_data.tar.gz"

sha256sum "${DEST}"/* > "${DEST}/SHA256SUMS"

echo "[backup] pruning to last ${RETENTION} snapshots"
ls -1dt "${BACKUP_DIR}"/*/ 2>/dev/null | tail -n +$((RETENTION + 1)) | xargs -r rm -rf

echo "[backup] done: ${DEST}"
echo "[backup] REMINDER: copy ${DEST} off-host (3-2-1 rule)."
