#!/bin/sh
set -e
cd /app
# alembic: 실패해도 uvicorn 실행 (DB connect_timeout 15초로 블로킹 방지)
python -m alembic upgrade head 2>&1 || true
echo "Starting uvicorn on port ${PORT:-8001}"
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8001}"
