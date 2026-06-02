#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
CRON_SCHEDULE="${CRON_SCHEDULE:-30 2 * * *}"
LOG_FILE="${LOG_FILE:-/var/log/lithiumcraft-backup.log}"
CRON_LINE="${CRON_SCHEDULE} cd ${APP_DIR} && bash deploy/scripts/backup-postgres.sh >> ${LOG_FILE} 2>&1"

current_cron="$(mktemp)"
new_cron="$(mktemp)"
trap 'rm -f "${current_cron}" "${new_cron}"' EXIT

crontab -l >"${current_cron}" 2>/dev/null || true
grep -v 'deploy/scripts/backup-postgres.sh' "${current_cron}" >"${new_cron}" || true
printf '%s\n' "${CRON_LINE}" >>"${new_cron}"
crontab "${new_cron}"

echo "Installed PostgreSQL backup cron:"
echo "${CRON_LINE}"
