#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
ENV_FILE="${SUPABASE_ENV_FILE:-$ROOT_DIR/.env.supabase.local}"

if [ ! -s "$ENV_FILE" ]; then
  echo "Missing $ENV_FILE"
  echo "Add DATABASE_URL=<Supabase Session pooler URL> before running this command."
  exit 1
fi

DATABASE_URL=$(sed -n 's/^DATABASE_URL=//p' "$ENV_FILE")
if [ -z "$DATABASE_URL" ]; then
  echo "DATABASE_URL is missing from $ENV_FILE"
  exit 1
fi

export DATABASE_MODE=postgres
export DATABASE_URL
export PYTHONPATH="$ROOT_DIR/backend"

exec "$ROOT_DIR/backend/.venv/bin/python" -m uvicorn app.main:app \
  --host 127.0.0.1 \
  --port "${PORT:-8000}"
