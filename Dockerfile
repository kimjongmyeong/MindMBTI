# 백엔드 빌드 (Root Directory 미설정 시 repo root에서 사용)
FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
RUN mkdir -p /app/data

EXPOSE 8080
# 직접 uvicorn 실행 (entrypoint 우회 - healthcheck 디버깅)
# Railway PORT는 런타임에 주입됨
CMD sh -c 'uvicorn minimal_app:app --host 0.0.0.0 --port ${PORT:-8080}'
