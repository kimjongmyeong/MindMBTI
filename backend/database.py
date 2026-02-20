"""
DB 연결 및 세션 관리
DATABASE_URL 미설정 시 SQLite 사용 (로컬/테스트)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# Render 등에서 postgres:// 사용 시 postgresql://로 변환
_url = os.getenv("DATABASE_URL", "sqlite:///./mindmbti.db")
DATABASE_URL = _url.replace("postgres://", "postgresql://", 1) if _url.startswith("postgres://") else _url
# SQLite용 connect_args
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from models import User, MbtiSession, Share, UserResult
    Base.metadata.create_all(bind=engine)
