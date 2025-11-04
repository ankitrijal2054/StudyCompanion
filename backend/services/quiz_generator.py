"""
Quiz Generation Service with Adaptive Difficulty and Auto-Goal Completion
"""
import os
import json
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from database import SessionLocal, Student, QuizResult, Goal
from services.rag_engine import retrieve_context

load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable must be set")
openai_client = OpenAI(api_key=api_key)

MODEL_NAME = "gpt-4o-mini"


def calculate_difficulty_level(student_id: str) -> Tuple[str, Dict]:
    """
    Calculate adaptive difficulty based on recent quiz performance.
    
    Strategy:
    - Easy: Last 3 quizzes avg <60%
    - Medium: Last 3 quizzes avg 60-79%
    - Hard: Last 3 quizzes avg ≥80%
    
    Args:
        student_id: Student identifier
    
    Returns:
        Tuple of (difficulty_string, performance_dict)
    """
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return "medium", {"avg_score": 0, "quiz_count": 0}
        
        # Get last 5 quiz results for this student
        recent_quizzes = db.query(QuizResult).filter(
            QuizResult.student_id == student.id
        ).order_by(QuizResult.created_at.desc()).limit(5).all()
        
        if not recent_quizzes:
            return "medium", {"avg_score": 0, "quiz_count": 0}
        
        avg_score = sum(q.score_percent for q in recent_quizzes) / len(recent_quizzes)
        
        if avg_score < 60:
            difficulty = "easy"
        elif avg_score < 80:
            difficulty = "medium"
        else:
            difficulty = "hard"
        
        return difficulty, {
            "avg_score": avg_score,
            "quiz_count": len(recent_quizzes),
            "recent_scores": [q.score_percent for q in recent_quizzes]
        }
    finally:
        db.close()


def generate_quiz(
    student_id: str,
    subject: str,
    num_questions: int = 5
) -> Dict:
    """
    Generate an adaptive quiz for a student using GPT-4o.
    
    Args:
        student_id: Student identifier
        subject: Subject for quiz (e.g., "Chemistry", "Algebra")
        num_questions: Number of questions to generate (default 5)
    
    Returns:
        Dictionary with quiz_id, subject, questions list, difficulty, estimated_time
    """
    # Calculate adaptive difficulty
    difficulty, performance = calculate_difficulty_level(student_id)
    
    # Retrieve relevant context from RAG engine
    context = retrieve_context(
        query=f"Key concepts in {subject}",
        student_id=student_id,
        top_k=3
    )
    
    context_text = "\n".join([doc.get("content", "") for doc in context]) if context else ""
    
    # Create prompt for GPT-4o to generate questions
    system_prompt = f"""You are an expert tutor creating adaptive quiz questions.
Generate {num_questions} multiple-choice questions for {subject} at {difficulty} difficulty level.

Context from student's previous learning:
{context_text if context_text else "No previous context available"}

Return ONLY valid JSON (no markdown, no code blocks) with this exact structure:
{{
    "questions": [
        {{
            "id": 1,
            "question": "Question text here?",
            "options": [
                "A. First option",
                "B. Second option",
                "C. Third option",
                "D. Fourth option"
            ],
            "correct_answer": "A",
            "topic": "Specific topic within {subject}",
            "explanation": "Brief explanation of correct answer"
        }}
    ]
}}

Rules:
- For EASY difficulty: Focus on fundamental concepts, definitions, basic applications
- For MEDIUM difficulty: Mix of concepts and basic application problems
- For HARD difficulty: Complex scenarios, multi-step problems, deep understanding required
- Each option must be realistic and plausible
- Avoid trick questions, focus on learning
- Ensure options are roughly same length
- Correct answer should be randomly distributed (not always same position)"""
    
    user_prompt = f"Generate {num_questions} {difficulty} difficulty multiple-choice questions for {subject}."
    
    try:
        # Call GPT-4o to generate questions
        response = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        quiz_json = json.loads(response_text)
        
        # Generate quiz_id
        quiz_id = f"quiz_{uuid.uuid4().hex[:8]}"
        
        # Transform questions to match Question model
        questions = []
        for i, q in enumerate(quiz_json.get("questions", [])[:num_questions]):
            questions.append({
                "question_id": i + 1,
                "question_text": q.get("question", ""),
                "options": q.get("options", []),
                "correct_answer": q.get("correct_answer", "A"),
                "topic": q.get("topic", subject),
                "difficulty": difficulty
            })
        
        # Store quiz in database
        db = SessionLocal()
        try:
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if student:
                quiz_record = QuizResult(
                    student_id=student.id,
                    quiz_id=quiz_id,
                    subject=subject,
                    difficulty=difficulty,
                    total_questions=len(questions),
                    questions={"questions": questions}  # Store full questions for later use
                )
                db.add(quiz_record)
                db.commit()
        finally:
            db.close()
        
        # Calculate estimated time (1 minute per question on average)
        estimated_time = num_questions
        
        return {
            "quiz_id": quiz_id,
            "subject": subject,
            "questions": questions,
            "num_questions": len(questions),
            "difficulty": difficulty,
            "estimated_time_minutes": estimated_time
        }
    
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse GPT-4o response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Error generating quiz with GPT-4o: {str(e)}")


def score_quiz(quiz_id: str, submitted_answers: List[str], db=None) -> Dict:
    """
    Score a submitted quiz and return results.
    
    Args:
        quiz_id: Quiz identifier
        submitted_answers: List of submitted answers (["A", "B", "C", ...])
        db: Optional database session
    
    Returns:
        Dictionary with score_percent, correct_count, total_questions, feedback
    """
    should_close_db = False
    if db is None:
        db = SessionLocal()
        should_close_db = True
    
    try:
        # Get quiz from database
        quiz_record = db.query(QuizResult).filter(QuizResult.quiz_id == quiz_id).first()
        if not quiz_record:
            raise Exception(f"Quiz {quiz_id} not found")
        
        # Get correct answers
        questions_data = quiz_record.questions.get("questions", [])
        correct_answers = [q.get("correct_answer", "A") for q in questions_data]
        
        # Score the quiz
        correct_count = sum(
            1 for i, answer in enumerate(submitted_answers)
            if i < len(correct_answers) and answer.upper() == correct_answers[i].upper()
        )
        
        total_questions = len(correct_answers)
        score_percent = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # Generate feedback based on score
        if score_percent >= 85:
            feedback = f"Excellent work! You scored {score_percent:.0f}% and truly mastered this material. Ready for a challenge?"
        elif score_percent >= 70:
            feedback = f"Great job! You scored {score_percent:.0f}% and have a solid understanding. Keep practicing!"
        elif score_percent >= 60:
            feedback = f"Good effort! You scored {score_percent:.0f}% and got the basics down. Review the topics you missed and try again."
        else:
            feedback = f"You scored {score_percent:.0f}%. Let's focus on the fundamentals. Review the learning materials and practice more."
        
        return {
            "score_percent": round(score_percent, 1),
            "correct_count": correct_count,
            "total_questions": total_questions,
            "feedback": feedback
        }
    finally:
        if should_close_db:
            db.close()


def check_auto_completion(student_id: int, subject: str, db=None) -> Dict:
    """
    Check if a student should have their goal auto-completed based on quiz performance.
    
    Criteria:
    - Last 5 quizzes with avg score ≥85%
    - Minimum 2 quizzes completed (for learning purposes)
    
    Args:
        student_id: Student database ID (integer)
        subject: Subject to check
        db: Optional database session
    
    Returns:
        Dictionary with should_complete (bool) and goal_id if applicable
    """
    should_close_db = False
    if db is None:
        db = SessionLocal()
        should_close_db = True
    
    try:
        # Get last 5 quizzes for this student in this subject
        recent_quizzes = db.query(QuizResult).filter(
            QuizResult.student_id == student_id,
            QuizResult.subject == subject
        ).order_by(QuizResult.created_at.desc()).limit(5).all()
        
        # Need at least 2 quizzes to auto-complete
        if len(recent_quizzes) < 2:
            return {"should_complete": False, "goal_id": None}
        
        # Calculate average score
        avg_score = sum(q.score_percent for q in recent_quizzes) / len(recent_quizzes)
        
        if avg_score >= 85:
            # Find the goal to complete
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                goal = db.query(Goal).filter(
                    Goal.student_id == student_id,
                    Goal.subject == subject,
                    Goal.status == "active"
                ).first()
                
                if goal:
                    return {
                        "should_complete": True,
                        "goal_id": goal.id,
                        "avg_score": avg_score,
                        "quiz_count": len(recent_quizzes)
                    }
        
        return {"should_complete": False, "goal_id": None}
    
    finally:
        if should_close_db:
            db.close()
