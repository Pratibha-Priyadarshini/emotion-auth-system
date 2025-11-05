import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DB_PATH = os.environ.get("APP_DB_PATH", os.path.join(os.path.dirname(__file__), "storage", "app.db"))
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    passphrase = Column(String)  # stored in plain for demo; DO NOT in production
    kd_model_path = Column(String, nullable=True)
    kd_enroll_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class EventLog(Base):
    __tablename__ = "event_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    decision = Column(String)  # permit/delay/deny/escalate
    confidence = Column(Float)
    reason = Column(Text)
    facial = Column(JSON)
    voice = Column(JSON)
    keystroke = Column(JSON)
    env = Column(JSON)
    fusion = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_session():
    return SessionLocal()
