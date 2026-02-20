"""
SQLAlchemy 모델
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=False)
    gender = Column(String(50), nullable=True)
    age_range = Column(String(20), nullable=True)
    profile_image_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MbtiSession(Base):
    __tablename__ = "mbti_sessions"
    id = Column(String(36), primary_key=True)
    answers = Column(JSON, nullable=False)  # {question_id: value}
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Share(Base):
    __tablename__ = "shares"
    id = Column(String(36), primary_key=True)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserResult(Base):
    __tablename__ = "user_results"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    session_id = Column(String(36), nullable=False)
    mbti_type = Column(String(4), nullable=False)
    percentages = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
