"""
Chat API endpoints for AI Study Companion
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from services.ai_agent import generate_chat_response
from database import SessionLocal, Conversation, Student
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    student_id: str
    message: str
    history: Optional[List[Dict]] = None


class ChatResponse(BaseModel):
    response: str
    confidence_score: float
    should_handoff: bool
    handoff_message: Optional[str] = None


@router.post("/", response_model=ChatResponse)
async def chat(message_data: ChatMessage):
    """
    Chat endpoint for AI Study Companion
    
    Args:
        message_data: Chat message with student_id, message, and optional history
    
    Returns:
        AI response with confidence score and handoff detection
    """
    # Validate student exists
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.student_id == message_data.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {message_data.student_id} not found")
    finally:
        db.close()
    
    # Generate AI response
    try:
        result = generate_chat_response(
            student_id=message_data.student_id,
            message=message_data.message,
            history=message_data.history or []
        )
        
        # Save conversation to database (optional - for tracking)
        db = SessionLocal()
        try:
            # Find or create conversation record
            conversation = db.query(Conversation).filter(
                Conversation.student_id == student.id
            ).order_by(Conversation.created_at.desc()).first()
            
            if not conversation:
                conversation = Conversation(
                    student_id=student.id,
                    subject="General",
                    message_count=0,
                    messages=[]
                )
                db.add(conversation)
            
            # Add new messages to conversation
            messages = conversation.messages or []
            messages.append({
                "role": "user",
                "content": message_data.message,
                "timestamp": datetime.utcnow().isoformat()
            })
            messages.append({
                "role": "assistant",
                "content": result["response"],
                "timestamp": datetime.utcnow().isoformat(),
                "confidence_score": result["confidence_score"],
                "should_handoff": result["should_handoff"]
            })
            
            conversation.messages = messages
            conversation.message_count = len(messages)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Warning: Failed to save conversation: {e}")
        finally:
            db.close()
        
        return ChatResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

