#!/bin/sh
set -e
cd /app
# alembic: 최대 120초, 실패해도 uvicorn은 실행 (DB 연결 불가 시 로그 확인)
timeout 120 python -m alembic upgrade head 2>&1 || true
echo "Starting uvicorn on port ${PORT:-8001}"
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8001}"
