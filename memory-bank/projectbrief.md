# Project Brief: AI Study Companion

## Core Definition

**AI Study Companion** is a web-based AI learning assistant that keeps K-12 and college students engaged between tutoring sessions, reduces churn by 52%, and drives measurable learning improvements through Socratic dialogue, adaptive practice, and intelligent recommendations.

## Business Problem

- 52% of students churn after achieving initial goal (lack of next steps)
- Students disengage between tutoring sessions
- Low early engagement (Days 1-7) predicts higher churn
- Students don't discover related learning paths naturally

## Solution Overview

Persistent AI companion that:

- Remembers what students learned (RAG with session transcripts)
- Answers questions with context (GPT-4o + LangChain)
- Generates adaptive practice (quizzes with difficulty adjustment)
- Recommends next subjects (LLM-based personalized suggestions)
- Sends smart nudges (Day 7 engagement, inactivity alerts, goal completion)

## Success Metrics

- Daily engagement: ≥2 interactions per student
- Retention: ≥40% goal completion → new subject conversion
- Early engagement: ≥40% Day 7 nudge → session booking
- Learning: ≥20% quiz score improvement
- Technical: <2s response latency (P95)

## Team & Timeline

- Solo developer: Ankit
- Sprint: 48 hours (Phase 0-9)
- MVP: Full-stack auth + 6 features deployed
- Future: Phase 2 integration with Nerdy systems

## Deliverables by Hour 48

✅ Authentication (JWT + email/password)
✅ Chat with RAG (context-aware responses)
✅ Adaptive quizzes (auto-complete at 85%)
✅ Progress dashboard (real-time)
✅ Personalized recommendations
✅ Email nudges (SendGrid)
✅ Deployed to Vercel + Render
✅ Complete documentation

## Key Decisions

1. **Tech Stack**: React + FastAPI + GPT-4o + ChromaDB (cost-optimized)
2. **Mocked Integration**: All Nerdy systems mocked for Phase 0 (Phase 2 integration planned)
3. **LLM Model**: GPT-4o (30-40% cheaper than GPT-4 Turbo, vision-ready)
4. **Real Email**: SendGrid API for nudges (+ console logging for dev)
5. **Data**: Mock transcripts + 5 test students (realistic scenarios)

## Cost Impact

- Dev sprint: $10-22
- Production monthly: $420 (1000 students = $0.42/student)
- 90-day ROI: $36K+ (projected)
