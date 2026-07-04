#!/usr/bin/env bash
# Health + disk monitor. Prints status and exits non-zero if anything is wrong,
# so it can drive a cron alert (mail on failure) or an uptime check.
#
# Usage: scripts/monitor.sh
set -uo pipefail

cd "$(dirname "$0")/.."

# shellcheck disable=SC1091
set -a; [ -f .env ] && . ./.env; set +a

THRESHOLD="${DISK_PAUSE_THRESHOLD_PERCENT:-90}"
COMPOSE="docker compose"
status=0

echo "== container health =="
for svc in db forgejo orchestrator scheduler frontend caddy; do
  cid="$(${COMPOSE} ps -q "${svc}" 2>/dev/null)"
  if [ -z "${cid}" ]; then
    echo "  ${svc}: NOT RUNNING"; status=1; continue
  fi
  health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "${cid}")"
  echo "  ${svc}: ${health}"
  case "${health}" in
    healthy|running) ;;
    *) status=1 ;;
  esac
done

echo "== Forgejo data disk =="
usage="$(${COMPOSE} exec -T forgejo sh -c "df -P /data | awk 'NR==2 {gsub(/%/,\"\",\$5); print \$5}'" 2>/dev/null)"
if [ -n "${usage}" ]; then
  echo "  /data usage: ${usage}% (threshold ${THRESHOLD}%)"
  if [ "${usage}" -ge "${THRESHOLD}" ]; then
    echo "  ALERT: disk usage at/over threshold — pause new mirrors and expand storage."
    status=1
  fi
else
  echo "  could not read disk usage"; status=1
fi

exit "${status}"
