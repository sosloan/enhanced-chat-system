from sqlalchemy import create_engine, Column, String, Boolean, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./callcenter.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(String, primary_key=True)
    successfulCall = Column(Boolean, nullable=False)
    classification = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    evaluations = relationship("Evaluation", back_populates="transcription", cascade="all, delete-orphan")

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String, primary_key=True)
    transcription_id = Column(String, ForeignKey("transcriptions.id"))
    status = Column(String, nullable=False)
    criteria = Column(JSON, nullable=False)
    improvementSuggestion = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    transcription = relationship("Transcription", back_populates="evaluations")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine) 