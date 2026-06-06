#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

unset DATABASE_URL
export DATABASE_MODE=sqlite
export PYTHONPATH="$ROOT_DIR/backend"

exec "$ROOT_DIR/backend/.venv/bin/python" -m uvicorn app.main:app \
  --host 127.0.0.1 \
  --port "${PORT:-8000}"
