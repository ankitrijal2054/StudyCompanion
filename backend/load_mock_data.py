import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, User, Student, Conversation, Goal, QuizResult, NudgeLog, engine, Base
import bcrypt

# Initialize database
Base.metadata.create_all(bind=engine)

def load_students():
    """Load student profiles from students.json"""
    students_path = Path(__file__).parent.parent / "data" / "students.json"
    
    with open(students_path, 'r') as f:
        students_data = json.load(f)
    
    session = SessionLocal()
    
    for student_data in students_data:
        # Check if user already exists
        existing_user = session.query(User).filter_by(email=student_data['email']).first()
        if existing_user:
            print(f"⏭️  User {student_data['email']} already exists, skipping...")
            continue
        
        # Create user account
        password_hash = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode()
        user = User(
            email=student_data['email'],
            password_hash=password_hash,
            name=student_data['name'],
            grade=student_data['grade']
        )
        session.add(user)
        session.flush()
        
        # Create student profile
        student = Student(
            student_id=student_data['student_id'],
            user_id=user.id,
            engagement_level=student_data.get('engagement_level', 'moderate'),
            learning_pace=student_data.get('learning_pace', 'moderate'),
            total_sessions=student_data.get('total_sessions', 0),
            avg_quiz_score=student_data.get('avg_quiz_score', 0),
            preferred_time=student_data.get('preferred_time', 'afternoon'),
            created_at=datetime.fromisoformat(student_data['created_at'].replace('Z', '+00:00')),
            last_active=datetime.fromisoformat(student_data['last_active'].replace('Z', '+00:00'))
        )
        session.add(student)
        session.flush()
        
        # Add current goals
        for goal_data in student_data.get('current_goals', []):
            goal = Goal(
                goal_id=goal_data['goal_id'],
                student_id=student.id,
                subject=goal_data['subject'],
                description=goal_data['description'],
                status=goal_data['status'],
                progress_percent=goal_data.get('progress_percent', 0),
                created_at=datetime.fromisoformat(goal_data['created_at'].replace('Z', '+00:00')),
                target_completion=datetime.fromisoformat(goal_data['target_completion'].replace('Z', '+00:00')) if goal_data.get('target_completion') else None
            )
            session.add(goal)
        
        # Add completed goals
        for goal_data in student_data.get('completed_goals', []):
            goal = Goal(
                goal_id=goal_data['goal_id'],
                student_id=student.id,
                subject=goal_data['subject'],
                description=goal_data['description'],
                status='completed',
                progress_percent=100,
                created_at=datetime.now(),
                completed_at=datetime.fromisoformat(goal_data['completed_at'].replace('Z', '+00:00')) if goal_data.get('completed_at') else None
            )
            session.add(goal)
        
        print(f"✅ Loaded student: {student_data['name']} ({student_data['student_id']})")
    
    session.commit()
    session.close()

def load_quiz_results():
    """Load quiz results from quiz_results.json"""
    quiz_path = Path(__file__).parent.parent / "data" / "quiz_results.json"
    
    with open(quiz_path, 'r') as f:
        quiz_data = json.load(f)
    
    session = SessionLocal()
    
    for quiz in quiz_data:
        # Get student
        student = session.query(Student).filter_by(student_id=quiz['student_id']).first()
        if not student:
            print(f"⚠️  Student {quiz['student_id']} not found, skipping quiz...")
            continue
        
        # Check if quiz result already exists
        existing_quiz = session.query(QuizResult).filter_by(quiz_id=quiz['quiz_id']).first()
        if existing_quiz:
            continue
        
        quiz_result = QuizResult(
            quiz_id=quiz['quiz_id'],
            student_id=student.id,
            subject=quiz['subject'],
            topic=quiz['topic'],
            quiz_date=datetime.fromisoformat(quiz['quiz_date'].replace('Z', '+00:00')),
            total_questions=quiz['total_questions'],
            correct_answers=quiz['correct_answers'],
            score_percent=quiz['score_percent'],
            difficulty=quiz.get('difficulty', 'intermediate'),
            time_taken_minutes=quiz.get('time_taken_minutes', 0)
        )
        session.add(quiz_result)
    
    session.commit()
    print(f"✅ Loaded {len(quiz_data)} quiz results")
    session.close()

def load_transcripts():
    """Load transcript references into conversations table"""
    transcripts_dir = Path(__file__).parent.parent / "data" / "transcripts"
    session = SessionLocal()
    
    transcript_count = 0
    for transcript_file in transcripts_dir.glob("*.json"):
        with open(transcript_file, 'r') as f:
            transcript_data = json.load(f)
        
        # Get student
        student = session.query(Student).filter_by(student_id=transcript_data['student_id']).first()
        if not student:
            continue
        
        # Check if conversation already exists
        existing = session.query(Conversation).filter_by(
            student_id=student.id,
            subject=transcript_data['subject'],
            topic=transcript_data.get('topic', '')
        ).first()
        if existing:
            continue
        
        conversation = Conversation(
            student_id=student.id,
            subject=transcript_data['subject'],
            topic=transcript_data.get('topic', ''),
            tutor_name=transcript_data.get('tutor_name', 'Tutor'),
            session_date=datetime.fromisoformat(transcript_data['session_date'].replace('Z', '+00:00')),
            duration_minutes=transcript_data.get('duration_minutes', 0),
            message_count=len(transcript_data.get('dialogue', [])),
            transcript_reference=transcript_file.name
        )
        session.add(conversation)
        transcript_count += 1
    
    session.commit()
    print(f"✅ Loaded {transcript_count} conversation records (15 transcripts)")
    session.close()

def verify_data():
    """Verify data was loaded correctly"""
    session = SessionLocal()
    
    user_count = session.query(User).count()
    student_count = session.query(Student).count()
    goal_count = session.query(Goal).count()
    quiz_count = session.query(QuizResult).count()
    conversation_count = session.query(Conversation).count()
    
    print("\n📊 DATABASE VERIFICATION:")
    print(f"   Users: {user_count}")
    print(f"   Students: {student_count}")
    print(f"   Goals: {goal_count}")
    print(f"   Quiz Results: {quiz_count}")
    print(f"   Conversations: {conversation_count}")
    
    session.close()

if __name__ == "__main__":
    print("🚀 Loading mock data into database...\n")
    
    print("📋 Step 1: Loading student profiles...")
    load_students()
    
    print("\n📚 Step 2: Loading quiz results...")
    load_quiz_results()
    
    print("\n💬 Step 3: Loading transcript references...")
    load_transcripts()
    
    print("\n")
    verify_data()
    
    print("\n✅ Mock data loading complete!")
