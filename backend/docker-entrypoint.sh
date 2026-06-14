#!/bin/sh
# docker-entrypoint.sh — runs when the backend container starts.
#
# 1. If the database file doesn't exist yet, seed it once (first run).
# 2. Start the API server.
#
# DATABASE_URL (set in docker-compose.yml) points at /data/support.db, which lives on a
# named volume so the data survives container restarts.
set -e

DB_FILE="/data/support.db"

if [ ! -f "$DB_FILE" ]; then
  echo "No database found at $DB_FILE — seeding sample data..."
  python -m backend.seed
else
  echo "Database found at $DB_FILE — skipping seed."
fi

# exec replaces this shell with uvicorn so signals (Ctrl+C) reach the server.
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
