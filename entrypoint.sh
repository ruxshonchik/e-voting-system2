#!/bin/bash
set -e

echo ">>> Running Alembic migrations..."
if ! alembic upgrade head; then
    echo "ERROR: Alembic migration failed! Exiting."
    exit 1
fi
echo ">>> Migrations complete."

echo ">>> Starting server..."
exec gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind "0.0.0.0:${PORT:-8000}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
