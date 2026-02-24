"""DB/모델 없이 /api/health만 응답 - 배포 디버깅용"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
@app.get("/health")
def health():
    return {"ok": True}
