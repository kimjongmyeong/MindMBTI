#!/bin/sh
set -e
cd /app
# 1단계: 최소 앱으로 배포 성공 확인 (DB 없음)
# 2단계: 성공하면 USE_MAIN_APP=1로 main 앱 복귀
if [ "$USE_MAIN_APP" != "1" ]; then
  echo "Starting minimal_app on port ${PORT:-8080}"
  exec uvicorn minimal_app:app --host 0.0.0.0 --port "${PORT:-8080}"
fi
python -m alembic upgrade head 2>&1 || true
echo "Starting main:app on port ${PORT:-8080}"
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8080}"
