"""SQLAlchemy models: User (auth) and QALog (exchange logging)."""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class QALog(Base):
    __tablename__ = "qa_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    search_query = Column(Text)
    answer = Column(Text)
    sources = Column(Text)
    similarity = Column(Float)
    latency_ms = Column(Integer)
    feedback = Column(String(10))
    created_at = Column(DateTime, server_default=func.now())
