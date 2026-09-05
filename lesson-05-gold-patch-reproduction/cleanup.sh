#!/usr/bin/env bash
# Stop this lesson's containers and reclaim unused Docker resources.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "== Stopping lesson compose stack =="
if [ -f docker/compose.yaml ]; then
  docker compose -f docker/compose.yaml down --remove-orphans || true
elif [ -f docker/compose.yml ]; then
  docker compose -f docker/compose.yml down --remove-orphans || true
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker not found; nothing else to clean."
  exit 0
fi

echo
echo "== Removing unused Docker resources =="
docker container prune -f || true
docker network prune -f || true
docker image prune -f || true
docker volume prune -f || true
docker builder prune -f || true

echo
echo "== Docker disk usage =="
docker system df || true

echo
echo "Done. Local junk (.venv, .apr, __pycache__) is gitignored — remove with: make clean"
