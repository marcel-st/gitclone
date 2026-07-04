#!/usr/bin/env bash
# Restore a backup produced by backup.sh. DESTRUCTIVE: overwrites current data.
#
# Usage: scripts/restore.sh /srv/backups/20260704_030000
set -euo pipefail

cd "$(dirname "$0")/.."

SRC="${1:-}"
if [ -z "${SRC}" ] || [ ! -d "${SRC}" ]; then
  echo "Usage: $0 <backup-dir>" >&2
  exit 1
fi

# shellcheck disable=SC1091
set -a; [ -f .env ] && . ./.env; set +a
COMPOSE="docker compose"

echo "!!! This overwrites the Forgejo data volume and both databases from ${SRC}"
read -r -p "Type RESTORE to continue: " confirm
[ "${confirm}" = "RESTORE" ] || { echo "Aborted."; exit 1; }

echo "[restore] verifying checksums"
( cd "${SRC}" && sha256sum -c SHA256SUMS )

echo "[restore] stopping app services"
${COMPOSE} stop orchestrator scheduler forgejo

echo "[restore] restoring databases"
gunzip -c "${SRC}/orchestrator.sql.gz" \
  | ${COMPOSE} exec -T db psql -U "${POSTGRES_SUPERUSER}" -d "${ORCHESTRATOR_DB_NAME}"
gunzip -c "${SRC}/forgejo.sql.gz" \
  | ${COMPOSE} exec -T db psql -U "${POSTGRES_SUPERUSER}" -d "${FORGEJO_DB_NAME}"

echo "[restore] restoring Forgejo data volume"
${COMPOSE} start forgejo
${COMPOSE} exec -T forgejo sh -c 'rm -rf /data/* && tar xzf - -C /data' < "${SRC}/forgejo_data.tar.gz"

echo "[restore] restarting services"
${COMPOSE} up -d

echo "[restore] done."
