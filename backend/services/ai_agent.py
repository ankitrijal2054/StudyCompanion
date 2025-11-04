"""
AI Agent service using LangChain for conversational AI with context retrieval
"""
import os
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv
from services.rag_engine import retrieve_context
from database import SessionLocal, Student, Goal, Conversation, User

load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable must be set")
openai_client = OpenAI(api_key=api_key)

# Model configuration
MODEL_NAME = "gpt-4o"
MAX_HISTORY_LENGTH = 10  # Store last 10 messages


def get_student_info(student_id: str) -> Optional[Dict]:
    """Retrieve student information from database"""
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return None
        
        # Get user info
        user = db.query(User).filter(User.id == student.user_id).first()
        
        # Get current goals
        goals = db.query(Goal).filter(
            Goal.student_id == student.id,
            Goal.status == "active"
        ).all()
        
        return {
            "student_id": student.student_id,
            "name": user.name if user else "Student",
            "grade": user.grade if user else None,
            "engagement_level": student.engagement_level,
            "avg_quiz_score": student.avg_quiz_score,
            "current_goals": [
                {
                    "subject": goal.subject,
                    "description": goal.description,
                    "progress_percent": goal.progress_percent
                }
                for goal in goals
            ]
        }
    finally:
        db.close()


def build_prompt_template(
    student_info: Dict,
    query: str,
    context: List[Dict],
    history: List[Dict]
) -> str:
    """Build comprehensive prompt with student context, RAG results, and conversation history"""
    
    # Student information section
    student_section = f"""
Student Information:
- Name: {student_info.get('name', 'Student')}
- Grade: {student_info.get('grade', 'N/A')}
- Engagement Level: {student_info.get('engagement_level', 'moderate')}
- Average Quiz Score: {student_info.get('avg_quiz_score', 0):.1f}%
"""
    
    # Current goals section
    goals = student_info.get('current_goals', [])
    if goals:
        goals_section = "\nCurrent Learning Goals:\n"
        for goal in goals:
            goals_section += f"- {goal['subject']}: {goal['description']} ({goal['progress_percent']:.0f}% complete)\n"
    else:
        goals_section = "\nCurrent Learning Goals: None set\n"
    
    # RAG context section
    if context:
        context_section = "\nRelevant Previous Session Context:\n"
        for i, ctx in enumerate(context[:3], 1):  # Top 3 results
            metadata = ctx.get('metadata', {})
            context_section += f"\n{i}. Subject: {metadata.get('subject', 'N/A')}, Topic: {metadata.get('topic', 'N/A')}\n"
            context_section += f"   Summary: {ctx.get('document', '')[:300]}...\n"
    else:
        context_section = "\nRelevant Previous Session Context: None found\n"
    
    # Conversation history section
    if history:
        history_section = "\nRecent Conversation History:\n"
        for msg in history[-MAX_HISTORY_LENGTH:]:  # Last 10 messages
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            history_section += f"{role.title()}: {content}\n"
    else:
        history_section = "\nRecent Conversation History: This is the start of the conversation.\n"
    
    # System prompt
    system_prompt = """You are an AI Study Companion, a supportive tutoring assistant that helps students learn through Socratic dialogue and guided questions.

Your role:
- Remember what the student has learned from previous sessions (using the context provided)
- Ask leading questions to guide understanding rather than giving direct answers
- Provide hints and encouragement when students are struggling
- Reference previous learning when relevant
- Keep responses concise and engaging (2-3 sentences typically)
- If the student seems frustrated or explicitly requests human help, acknowledge this and suggest booking a session

Tone: Friendly, encouraging, and patient. Use emojis sparingly (1-2 per response max)."""
    
    # Combine into full prompt
    full_prompt = f"""{system_prompt}

{student_section}
{goals_section}
{context_section}
{history_section}

Current Student Question: {query}

Please provide a helpful, contextual response that:
1. References relevant previous learning if applicable
2. Guides the student with questions rather than giving direct answers
3. Relates to their current goals if relevant
4. Keeps the response concise and encouraging

Response:"""
    
    return full_prompt


def calculate_confidence_score(response: str, context: List[Dict]) -> float:
    """Calculate confidence score based on response quality and context availability"""
    # Base confidence
    confidence = 0.7
    
    # Boost if we have relevant context
    if context and len(context) > 0:
        confidence += 0.15
    
    # Boost if response is substantial (not too short)
    if len(response) > 50:
        confidence += 0.1
    
    # Penalize if response is too generic or uncertain
    uncertainty_phrases = ["I'm not sure", "I don't know", "I'm uncertain", "I can't help"]
    if any(phrase.lower() in response.lower() for phrase in uncertainty_phrases):
        confidence -= 0.3
    
    return min(1.0, max(0.0, confidence))


def detect_handoff_trigger(
    message: str,
    history: List[Dict],
    confidence: float
) -> Tuple[bool, str]:
    """
    Detect if human handoff should be triggered
    
    Returns:
        (should_handoff: bool, reason: str)
    """
    # Low confidence trigger
    if confidence < 0.6:
        return True, "I'm not completely confident in my answer. Let me connect you with a human tutor who can provide more detailed help."
    
    # Explicit booking requests
    booking_keywords = [
        "book a session", "book session", "schedule a tutor", "schedule tutor",
        "need a tutor", "want a tutor", "human tutor", "book me", "schedule me"
    ]
    message_lower = message.lower()
    if any(keyword in message_lower for keyword in booking_keywords):
        return True, "I'd be happy to help you book a session with a tutor! Let me connect you."
    
    # Frustration detection (3+ "confused" or "don't understand" in recent history)
    if len(history) >= 3:
        recent_messages = history[-5:]  # Last 5 messages
        confusion_count = 0
        for msg in recent_messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '').lower()
                if any(phrase in content for phrase in ["confused", "don't understand", "don't get it", "not getting it", "stuck"]):
                    confusion_count += 1
        
        if confusion_count >= 3:
            return True, "I notice you've been feeling confused. Let me connect you with a human tutor who can provide more personalized guidance."
    
    return False, ""


def generate_chat_response(
    student_id: str,
    message: str,
    history: Optional[List[Dict]] = None
) -> Dict:
    """
    Generate AI chat response with context retrieval and handoff detection
    
    Args:
        student_id: Student ID
        message: User message
        history: Optional conversation history (list of {role, content} dicts)
    
    Returns:
        {
            "response": str,
            "confidence_score": float,
            "should_handoff": bool,
            "handoff_message": str (if should_handoff is True)
        }
    """
    if history is None:
        history = []
    
    # Step 1: Get student information
    student_info = get_student_info(student_id)
    if not student_info:
        return {
            "response": "I couldn't find your student profile. Please contact support.",
            "confidence_score": 0.0,
            "should_handoff": True,
            "handoff_message": "Unable to locate student profile"
        }
    
    # Step 2: Retrieve relevant context using RAG
    context = retrieve_context(message, student_id, top_k=3)
    
    # Step 3: Build prompt with all context
    prompt = build_prompt_template(student_info, message, context, history)
    
    # Step 4: Generate response using OpenAI
    try:
        response = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an AI Study Companion, a supportive tutoring assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Step 5: Calculate confidence score
        confidence = calculate_confidence_score(ai_response, context)
        
        # Step 6: Detect handoff triggers
        should_handoff, handoff_message = detect_handoff_trigger(message, history, confidence)
        
        # Step 7: Combine response with handoff if needed
        if should_handoff:
            final_response = f"{ai_response}\n\n{handoff_message}"
        else:
            final_response = ai_response
        
        return {
            "response": final_response,
            "confidence_score": confidence,
            "should_handoff": should_handoff,
            "handoff_message": handoff_message if should_handoff else None
        }
    
    except Exception as e:
        return {
            "response": "I apologize, but I'm having trouble processing your request right now. Please try again in a moment.",
            "confidence_score": 0.0,
            "should_handoff": True,
            "handoff_message": f"Error: {str(e)}"
        }

