#!/bin/sh
set -e

echo "[entrypoint] Resolving database connection settings..."

DB_HOST="${POSTGRES_HOST:-}"
DB_PORT="${POSTGRES_PORT:-}"
DB_USER="${POSTGRES_USER:-}"

if [ -n "${DATABASE_URL:-}" ]; then
  if [ -z "$DB_HOST" ]; then
    DB_HOST="$(echo "$DATABASE_URL" | sed -E 's|.*@([^:/?]+).*|\1|')"
  fi
  if [ -z "$DB_PORT" ]; then
    DB_PORT="$(echo "$DATABASE_URL" | sed -E 's|.*:([0-9]+)/.*|\1|')"
  fi
  if [ -z "$DB_USER" ]; then
    DB_USER="$(echo "$DATABASE_URL" | sed -E 's|.*://([^:/]+).*|\1|')"
  fi
fi

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"

echo "[entrypoint] Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
  sleep 2
done

echo "[entrypoint] PostgreSQL is ready. Running Alembic migrations..."
alembic upgrade head

echo "[entrypoint] Running seed data..."
python /app/seed.py

echo "[entrypoint] Starting application..."
exec "$@"