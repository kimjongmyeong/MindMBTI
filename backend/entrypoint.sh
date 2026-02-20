#!/bin/sh
set -e
cd /app
python -m alembic upgrade head 2>/dev/null || true
exec uvicorn main:app --host 0.0.0.0 --port 8001
