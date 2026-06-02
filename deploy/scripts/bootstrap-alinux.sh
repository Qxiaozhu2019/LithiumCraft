#!/usr/bin/env bash
set -euo pipefail

SWAP_SIZE="${SWAP_SIZE:-2G}"
SWAP_FILE="${SWAP_FILE:-/swapfile}"

if [ "$(id -u)" -eq 0 ]; then
  SUDO=""
else
  SUDO="sudo"
fi

if command -v dnf >/dev/null 2>&1; then
  PKG=dnf
elif command -v yum >/dev/null 2>&1; then
  PKG=yum
else
  echo "Neither dnf nor yum was found. This script targets Alibaba Cloud Linux/CentOS-like systems." >&2
  exit 1
fi

echo "Installing base packages with ${PKG}..."
${SUDO} "${PKG}" update -y
${SUDO} "${PKG}" install -y git curl vim unzip ca-certificates

if ! command -v docker >/dev/null 2>&1; then
  echo "Installing Docker Engine..."
  curl -fsSL https://get.docker.com | ${SUDO} sh
else
  echo "Docker is already installed."
fi

${SUDO} systemctl enable docker
${SUDO} systemctl start docker

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose plugin is not available. Install docker-compose-plugin, then rerun this script." >&2
  exit 1
fi

if [ "$(free -m | awk '/^Swap:/ {print $2}')" -eq 0 ]; then
  echo "Creating ${SWAP_SIZE} swap file at ${SWAP_FILE}..."
  ${SUDO} fallocate -l "${SWAP_SIZE}" "${SWAP_FILE}"
  ${SUDO} chmod 600 "${SWAP_FILE}"
  ${SUDO} mkswap "${SWAP_FILE}"
  ${SUDO} swapon "${SWAP_FILE}"
  if ! grep -q "^${SWAP_FILE} " /etc/fstab; then
    echo "${SWAP_FILE} none swap sw 0 0" | ${SUDO} tee -a /etc/fstab >/dev/null
  fi
else
  echo "Swap already exists; skipping swap creation."
fi

echo "Bootstrap complete."
docker version
docker compose version
free -h
