#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
COMPOSE_FILE="${COMPOSE_FILE:-deploy/docker-compose.yml}"
ENV_FILE="${ENV_FILE:-.env}"

cd "${APP_DIR}"

if [ ! -f "${ENV_FILE}" ]; then
  echo "Missing ${ENV_FILE}. Copy deploy/env.production.example to .env and replace all secrets first." >&2
  exit 1
fi

if grep -Eq 'change-this-in-production|ChangeMe123!|replace-with-' "${ENV_FILE}"; then
  echo "${ENV_FILE} still contains default placeholder secrets. Replace them before deploying." >&2
  exit 1
fi

docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" up -d --build
docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" ps

echo "Deployment command completed. Run deploy/scripts/verify.sh to validate HTTP and API access."
