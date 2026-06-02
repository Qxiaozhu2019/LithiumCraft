#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
COMPOSE_FILE="${COMPOSE_FILE:-deploy/docker-compose.yml}"
ENV_FILE="${ENV_FILE:-.env}"
BASE_URL="${BASE_URL:-http://127.0.0.1}"

cd "${APP_DIR}"

echo "Checking container status..."
docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" ps

echo "Checking API health at ${BASE_URL}/health..."
curl -fsS "${BASE_URL}/health"
echo

echo "Checking public API at ${BASE_URL}/api/v1/categories..."
curl -fsS "${BASE_URL}/api/v1/categories"
echo

echo "Checking frontend at ${BASE_URL}/..."
curl -fsSI "${BASE_URL}/" | sed -n '1,5p'

echo "Verification complete."
