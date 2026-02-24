#!/bin/sh
set -e
cd /app
python -m alembic upgrade head 2>&1 || true
echo "Starting main:app on port ${PORT:-8080}"
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8080}"
