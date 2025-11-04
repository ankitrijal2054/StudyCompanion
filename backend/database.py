from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Use absolute path for database
db_path = os.path.join(os.path.dirname(__file__), "app.db")
# SQLite URL: sqlite followed by absolute path (already has leading slash on macOS)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")

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
    engagement_level = Column(String, default="moderate")
    learning_pace = Column(String, default="moderate")
    total_sessions = Column(Integer, default=0)
    avg_quiz_score = Column(Float, default=0.0)
    preferred_time = Column(String, default="afternoon")
    engagement_stats = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, nullable=True)

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)  # Foreign key to Student.id
    subject = Column(String)
    topic = Column(String, nullable=True)
    tutor_name = Column(String, nullable=True)
    session_date = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    transcript_reference = Column(String, nullable=True)
    messages = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)  # Foreign key to Student.id
    goal_id = Column(String, unique=True, index=True)
    subject = Column(String)
    description = Column(String)
    progress_percent = Column(Float, default=0.0)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    target_completion = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

class QuizResult(Base):
    __tablename__ = "quiz_results"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)  # Foreign key to Student.id
    quiz_id = Column(String, unique=True, index=True)
    subject = Column(String)
    topic = Column(String, nullable=True)
    score_percent = Column(Float)
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    difficulty = Column(String, default="intermediate")
    time_taken_minutes = Column(Integer, default=0)
    quiz_date = Column(DateTime, nullable=True)
    questions = Column(JSON, default={})
    answers = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

class NudgeLog(Base):
    __tablename__ = "nudge_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)  # Foreign key to Student.id
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
