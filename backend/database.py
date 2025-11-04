from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    name = Column(String)
    grade = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    student_id = Column(String, unique=True, index=True)
    engagement_stats = Column(JSON, default={})

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    subject = Column(String)
    messages = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    goal_id = Column(String, unique=True, index=True)
    subject = Column(String)
    description = Column(String)
    progress = Column(Float, default=0.0)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class QuizResult(Base):
    __tablename__ = "quiz_results"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    quiz_id = Column(String, unique=True, index=True)
    subject = Column(String)
    score = Column(Float)
    questions = Column(JSON)
    answers = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class NudgeLog(Base):
    __tablename__ = "nudge_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    nudge_type = Column(String)
    status = Column(String, default="sent")
    sent_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized successfully!")
    print(f"📁 Database created at: {DATABASE_URL}")
