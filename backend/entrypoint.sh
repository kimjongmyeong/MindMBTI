#!/bin/sh
set -e
cd /app
# alembic: 실패해도 uvicorn 실행 (DB connect_timeout 15초로 블로킹 방지)
python -m alembic upgrade head 2>&1 || true
echo "Starting uvicorn on port ${PORT:-8001}"
# Railway는 PORT를 주입 (기본 8080)
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8080}"
