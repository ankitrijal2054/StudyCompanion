from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from database import init_db
from api.chat import router as chat_router
from api.quiz import router as quiz_router
from api.dashboard import router as dashboard_router

# Load environment variables
load_dotenv()

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="AI Study Companion API",
    description="API for AI-powered tutoring companion",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(quiz_router)
app.include_router(dashboard_router)

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "AI Study Companion API is running",
        "environment": "development"
    }

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to AI Study Companion API",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Study Companion API...")
    print("📍 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
