"""
Quiz API endpoints for AI Study Companion
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from services.quiz_generator import generate_quiz, score_quiz, check_auto_completion
from database import SessionLocal, QuizResult, Student, Goal
from datetime import datetime
import json

router = APIRouter(prefix="/practice", tags=["practice"])


class QuizGenerationRequest(BaseModel):
    student_id: str
    subject: str
    num_questions: int = 5


class QuestionOption(BaseModel):
    option: str
    is_correct: bool


class Question(BaseModel):
    question_id: int
    question_text: str
    options: List[str]  # ["A. Option 1", "B. Option 2", ...]
    correct_answer: str  # "A", "B", "C", or "D"
    topic: str
    difficulty: str


class QuizResponse(BaseModel):
    quiz_id: str
    subject: str
    questions: List[Question]
    num_questions: int
    difficulty: str
    estimated_time_minutes: int


class QuizSubmissionRequest(BaseModel):
    answers: List[str]  # ["A", "B", "C", ...] in order of question_id


class QuizSubmissionResponse(BaseModel):
    quiz_id: str
    score_percent: float
    correct_count: int
    total_questions: int
    feedback: str
    goal_completed: bool
    goal_id: Optional[str] = None
    celebration_message: Optional[str] = None


@router.post("/", response_model=QuizResponse)
async def generate_quiz_endpoint(request: QuizGenerationRequest):
    """
    Generate an adaptive quiz for a student in a specific subject.
    
    Args:
        request: QuizGenerationRequest with student_id, subject, num_questions
    
    Returns:
        QuizResponse with quiz_id, questions, and metadata
    """
    # Validate student exists
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.student_id == request.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {request.student_id} not found")
    finally:
        db.close()
    
    # Generate quiz using quiz generator service
    try:
        quiz_data = generate_quiz(
            student_id=request.student_id,
            subject=request.subject,
            num_questions=request.num_questions
        )
        return QuizResponse(**quiz_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")


@router.post("/{quiz_id}/submit", response_model=QuizSubmissionResponse)
async def submit_quiz(quiz_id: str, submission: QuizSubmissionRequest):
    """
    Submit quiz answers and get scoring results with auto-goal completion check.
    
    Args:
        quiz_id: The quiz identifier
        submission: QuizSubmissionRequest with answers array
    
    Returns:
        QuizSubmissionResponse with score, feedback, and goal completion status
    """
    db = SessionLocal()
    try:
        # Get quiz from database
        quiz_result = db.query(QuizResult).filter(QuizResult.quiz_id == quiz_id).first()
        if not quiz_result:
            raise HTTPException(status_code=404, detail=f"Quiz {quiz_id} not found")
        
        # Score the quiz
        score_data = score_quiz(quiz_id, submission.answers, db)
        
        # Update quiz result in database
        quiz_result.answers = {"submitted_answers": submission.answers}
        quiz_result.score_percent = score_data["score_percent"]
        quiz_result.correct_answers = score_data["correct_count"]
        quiz_result.total_questions = score_data["total_questions"]
        
        # Check for auto-goal completion
        goal_completed = False
        goal_id = None
        celebration_message = None
        
        auto_completion_result = check_auto_completion(
            student_id=quiz_result.student_id,
            subject=quiz_result.subject,
            db=db
        )
        
        if auto_completion_result["should_complete"]:
            goal_completed = True
            goal_id = auto_completion_result["goal_id"]
            subject_name = quiz_result.subject
            celebration_message = f"🎉 You've mastered {subject_name}! Ready for the next challenge? Check out our personalized recommendations!"
            
            # Mark goal as completed
            goal = db.query(Goal).filter(Goal.id == goal_id).first()
            if goal:
                goal.status = "completed"
                goal.completed_at = datetime.utcnow()
                goal.progress_percent = 100.0
        
        db.commit()
        
        return QuizSubmissionResponse(
            quiz_id=quiz_id,
            score_percent=score_data["score_percent"],
            correct_count=score_data["correct_count"],
            total_questions=score_data["total_questions"],
            feedback=score_data["feedback"],
            goal_completed=goal_completed,
            goal_id=goal_id,
            celebration_message=celebration_message
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting quiz: {str(e)}")
    finally:
        db.close()
