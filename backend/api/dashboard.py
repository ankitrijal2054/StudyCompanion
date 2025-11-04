from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from database import SessionLocal, Student, Goal, QuizResult, Conversation
import json

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/student/{student_id}/stats")
def get_student_stats(student_id: str):
    """Get student statistics: session count, goals progress, quiz average"""
    db = SessionLocal()
    try:
        # Find student by student_id
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Count total sessions (conversations)
        total_sessions = db.query(func.count(Conversation.id)).filter(
            Conversation.student_id == student.id
        ).scalar() or 0
        
        # Calculate goals progress
        goals = db.query(Goal).filter(Goal.student_id == student.id).all()
        active_goals = [g for g in goals if g.status == "active"]
        completed_goals = [g for g in goals if g.status == "completed"]
        
        avg_goal_progress = 0
        if active_goals:
            avg_goal_progress = sum(g.progress_percent for g in active_goals) / len(active_goals)
        
        # Calculate average quiz score
        quiz_results = db.query(QuizResult).filter(
            QuizResult.student_id == student.id
        ).all()
        
        avg_quiz_score = 0
        if quiz_results:
            avg_quiz_score = sum(q.score_percent for q in quiz_results) / len(quiz_results)
        
        # Get last 7 days of sessions for streak
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        recent_sessions = db.query(func.count(Conversation.id)).filter(
            Conversation.student_id == student.id,
            Conversation.created_at >= one_week_ago
        ).scalar() or 0
        
        return {
            "student_id": student_id,
            "total_sessions": total_sessions,
            "session_streak": recent_sessions,  # Sessions in last 7 days
            "goals_progress_percent": round(avg_goal_progress, 1),
            "active_goals": len(active_goals),
            "completed_goals": len(completed_goals),
            "avg_quiz_score": round(avg_quiz_score, 1),
            "total_quizzes": len(quiz_results),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/student/{student_id}/goals")
def get_student_goals(student_id: str):
    """Get student's active and completed goals"""
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        goals = db.query(Goal).filter(Goal.student_id == student.id).all()
        
        goal_list = []
        for goal in goals:
            days_remaining = 0
            if goal.target_completion:
                delta = goal.target_completion - datetime.utcnow()
                days_remaining = max(0, delta.days)
            
            goal_list.append({
                "goal_id": goal.goal_id,
                "subject": goal.subject,
                "description": goal.description,
                "progress_percent": goal.progress_percent,
                "status": goal.status,
                "days_remaining": days_remaining,
                "created_at": goal.created_at.isoformat() if goal.created_at else None,
                "target_completion": goal.target_completion.isoformat() if goal.target_completion else None,
                "completed_at": goal.completed_at.isoformat() if goal.completed_at else None,
            })
        
        # Separate active and completed
        active = [g for g in goal_list if g["status"] == "active"]
        completed = [g for g in goal_list if g["status"] == "completed"]
        
        return {
            "student_id": student_id,
            "active_goals": active,
            "completed_goals": completed,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/student/{student_id}/quiz-history")
def get_quiz_history(student_id: str, limit: int = 10):
    """Get student's recent quiz history with scores and dates"""
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get recent quizzes, ordered by creation date descending
        quiz_results = db.query(QuizResult).filter(
            QuizResult.student_id == student.id
        ).order_by(desc(QuizResult.created_at)).limit(limit).all()
        
        history = []
        for quiz in quiz_results:
            history.append({
                "quiz_id": quiz.quiz_id,
                "subject": quiz.subject,
                "topic": quiz.topic,
                "score_percent": quiz.score_percent,
                "correct_answers": quiz.correct_answers,
                "total_questions": quiz.total_questions,
                "difficulty": quiz.difficulty,
                "created_at": quiz.created_at.isoformat() if quiz.created_at else None,
            })
        
        return {
            "student_id": student_id,
            "quiz_history": history,
            "total_quizzes": len(quiz_results),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
