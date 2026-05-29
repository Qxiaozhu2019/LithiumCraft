#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-deploy/docker-compose.yml}"
ENV_FILE="${ENV_FILE:-.env}"
BACKUP_DIR="${BACKUP_DIR:-deploy/backups}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_PATH="${BACKUP_DIR}/lithiumcraft-postgres-${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

compose_args=(-f "${COMPOSE_FILE}")
if [ -f "${ENV_FILE}" ]; then
  compose_args=(--env-file "${ENV_FILE}" "${compose_args[@]}")
fi

docker compose "${compose_args[@]}" exec -T postgres \
  sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' \
  | gzip > "${BACKUP_PATH}"

echo "PostgreSQL backup written to ${BACKUP_PATH}"
