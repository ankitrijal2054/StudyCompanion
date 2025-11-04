# AI Study Companion - Product Requirements Document

## Executive Summary

**Product**: AI Study Companion  
**Timeline**: 48-hour Sprint  
**Goal**: Build a persistent AI learning assistant that keeps students engaged between tutoring sessions, reduces churn, and drives measurable learning improvements.

**Business Impact**:

- Reduce 52% "goal achieved" churn via intelligent cross-subject recommendations
- Increase Day 7 session booking rate through proactive nudges
- Improve student retention and learning outcomes through personalized practice

---

## Problem Statement

Nerdy faces critical retention challenges:

- **52% of students churn** after achieving their initial goal (lack of next steps)
- **Students disengage** between tutoring sessions (no continuous learning support)
- **Low early engagement**: Students with <3 sessions by Day 7 have higher churn risk
- **Single-subject focus**: Students don't discover related subjects naturally

**Solution**: An AI companion that maintains engagement 24/7, personalizes learning paths, and intelligently guides students to their next learning journey.

---

## Product Overview

### Core Value Proposition

A conversational AI that acts as a personal study partner between tutoring sessions - remembering what students learned, generating adaptive practice, answering questions, and recommending next subjects at the right moment.

### Target Users

- **Primary**: K-12 and college students actively enrolled in Nerdy tutoring
- **Secondary**: Students who completed initial goals (churn risk)

---

## Success Metrics

| Category             | Metric                                   | Target         | Measurement Method             |
| -------------------- | ---------------------------------------- | -------------- | ------------------------------ |
| **Engagement**       | Daily active interactions                | ≥2 per student | Chat message count             |
| **Retention**        | Goal completion → new subject conversion | ≥40%           | Recommendation acceptance rate |
| **Early Engagement** | Day 7 nudge → session booking            | ≥40%           | Email CTR → booking conversion |
| **Learning**         | Quiz score improvement                   | ≥20%           | Pre/post assessment delta      |
| **Technical**        | Response latency                         | <2s            | P95 response time              |

---

## Core Features (MVP - 48 Hours)

### 0. 🔐 Authentication System

**Priority**: P0 (Gate-keeping)

**Functionality**:

- User registration (email + password)
- User login with email/password
- Session persistence (JWT tokens)
- Logout functionality
- Profile creation on signup (name, email, grade level)

**Technical Implementation**:

```
- Backend: FastAPI with JWT authentication
- Password hashing: bcrypt
- Token storage: Secure HTTP-only cookies (frontend) + DB
- Database: SQLite for user credentials and profiles
```

**Data Structure (users table)**:

```json
{
  "user_id": "U001",
  "email": "ava@example.com",
  "password_hash": "bcrypt_hash_here",
  "name": "Ava Johnson",
  "grade": 11,
  "created_at": "2025-11-04T10:00:00Z",
  "last_login": "2025-11-04T14:30:00Z"
}
```

**Auth Flow**:

1. User registers with email/password
2. Backend validates, hashes password, creates user profile
3. User logs in → receives JWT token
4. Token included in all API requests (Authorization header)
5. Backend validates token before processing requests
6. Token refresh mechanism (24-hour expiry, refresh token for longer sessions)

---

### 1. 🧠 Student Memory System

**Priority**: P0 (Foundation)

**Functionality**:

- Stores student profile (name, subjects, goals, progress)
- Ingests and vectorizes tutoring session transcripts
- Maintains conversation history and learning context
- Tracks quiz performance and knowledge gaps

**Technical Implementation**:

```
- RAG Pipeline: LangChain + ChromaDB
- Embedding Model: OpenAI text-embedding-3-small
- Storage: ChromaDB (local) + SQLite (metadata)
```

**Mock Data Structure**:

```json
{
  "student_id": "S001",
  "name": "Ava Johnson",
  "subjects": ["Chemistry", "Math"],
  "current_goals": [
    {
      "subject": "Chemistry",
      "goal": "Master VSEPR theory",
      "progress": 0.75,
      "started": "2025-10-15",
      "target_date": "2025-11-01"
    }
  ],
  "completed_goals": [
    {
      "subject": "SAT Math",
      "goal": "Score 700+",
      "completed": "2025-10-10"
    }
  ],
  "session_history": [
    {
      "date": "2025-10-28",
      "subject": "Chemistry",
      "topics": ["Ionic bonds", "Covalent bonds", "Electronegativity"],
      "transcript": "Tutor: Today we covered...",
      "tutor_notes": "Student struggled with polarity concept"
    }
  ],
  "last_active": "2025-11-03",
  "engagement_stats": {
    "sessions_last_7_days": 2,
    "chat_interactions_last_7_days": 5
  }
}
```

---

### 2. 💬 Conversational AI Agent

**Priority**: P0 (Core Experience)

**Functionality**:

- Answer questions about previous lessons with context
- Explain concepts conversationally (ELI5 style)
- Suggest next study steps based on progress
- Detect when to escalate to human tutor

**Conversation Modes**:

1. **Question Answering**: "What did we learn about ionic bonds?"
2. **Concept Explanation**: "I still don't understand electronegativity"
3. **Study Guidance**: "What should I focus on next?"
4. **Practice Request**: "Can you quiz me on chemistry?"

**Human Handoff Triggers**:

- Student explicitly asks for tutor ("I need help from my tutor")
- AI confidence score <0.6 on response
- Student expresses frustration (3+ clarification requests)
- Complex multi-step problem solving needed
- Student requests to book session

**Technical Implementation**:

```
- LLM: GPT-4 Turbo (gpt-4-turbo-preview)
- Framework: LangChain with custom prompt templates
- Context Window: Last 10 messages + relevant transcript chunks
- Retrieval: Top 5 most relevant session excerpts via semantic search
```

**Prompt Template Example**:

```
You are a friendly AI study companion for {student_name}.

CONTEXT FROM PREVIOUS SESSIONS:
{retrieved_transcript_chunks}

STUDENT'S CURRENT GOALS:
{current_goals}

CONVERSATION HISTORY:
{chat_history}

STUDENT QUESTION: {user_input}

Respond conversationally and helpfully. If the question is beyond your knowledge or requires human expertise, suggest booking a session with their tutor. Keep responses concise (2-3 paragraphs max).
```

---

### 3. 📚 Adaptive Practice Generator

**Priority**: P0 (Learning Impact)

**Functionality**:

- Generate quizzes based on recent session topics
- Adapt difficulty based on student performance
- Provide immediate feedback with explanations
- Track improvement over time

**Practice Types**:

1. **Quick Check** (5 questions): Review recent lesson
2. **Mastery Quiz** (10 questions): Comprehensive topic assessment
3. **Weak Spot Practice** (3-7 questions): Target identified gaps

**Question Generation Strategy**:

```
Prompt: "Generate {n} {difficulty} multiple-choice questions about {topic}
for a {grade_level} student. Focus on concepts from this lesson: {transcript}.
Include one question targeting this weak area: {weak_concept}.

Format as JSON:
{
  "questions": [
    {
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "B",
      "explanation": "...",
      "difficulty": "medium"
    }
  ]
}"
```

**Adaptive Logic**:

- Score ≥80%: Increase difficulty or move to next topic
- Score 60-79%: Maintain difficulty, reinforce concepts
- Score <60%: Decrease difficulty, focus on fundamentals

**Technical Implementation**:

```
- LLM: GPT-4 Turbo with structured output
- Storage: SQLite (quiz results)
- Analytics: Simple Python logic for performance tracking
```

---

### 4. 🎯 Progress Dashboard

**Priority**: P0 (Visibility)

**Functionality**:

- Visual progress bars for each goal
- Quiz score trends over time
- Session frequency calendar heatmap
- Multi-goal tracking (not just single subject)

**Dashboard Components**:

1. **Goal Progress Cards**

   - Subject name
   - Progress percentage (0-100%)
   - Days until target completion
   - "Continue Learning" CTA

2. **Learning Analytics**

   - Quiz performance chart (line graph)
   - Topics mastered (badge display)
   - Session streak counter

3. **Activity Feed**
   - Recent quiz results
   - Upcoming session reminders
   - Achievement unlocks

**Technical Implementation**:

```
- Frontend: React + Recharts/Chart.js
- Data Source: SQLite queries aggregated by backend
- Update Frequency: Real-time (after each interaction)
```

---

### 5. 🔔 Smart Nudge System

**Priority**: P0 (Retention)

**Functionality**:

- Detect low engagement (<3 sessions in 7 days from goal start)
- Send personalized email nudge
- Track nudge effectiveness

**Nudge Triggers & Logic**:

| Trigger            | Condition             | Timing           | Message Type                              |
| ------------------ | --------------------- | ---------------- | ----------------------------------------- |
| Early Engagement   | Day 7, <3 sessions    | Day 7 9am local  | Motivational + booking CTA                |
| Practice Reminder  | No activity in 3 days | 3 days 6pm local | "Your AI companion misses you"            |
| Goal Near Complete | Progress ≥85%         | Immediately      | "You're almost there! Book final session" |

**Email Template (Day 7 Nudge)**:

```
Subject: {Student Name}, let's keep the momentum going! 🚀

Hi {Student Name},

You started strong with {session_count} sessions on {subject}!
Your AI Study Companion noticed you haven't checked in lately.

Quick wins waiting for you:
- 5 practice questions on {recent_topic}
- Chat about anything you're stuck on
- See your progress toward {goal}

[Continue Learning] [Book Next Session]

Your progress shouldn't pause between sessions!
- Your AI Study Companion
```

**Technical Implementation**:

```
- Trigger: CRON job (hourly check) or Firebase Cloud Functions
- Email Service: SendGrid API (mock with console logs for sprint)
- Database: SQLite flag for "nudge_sent" to avoid duplicates
```

---

### 6. 🧭 Recommendation Engine

**Priority**: P0 (Churn Prevention)

**Functionality**:

- Suggest related subjects when goal completed
- Personalize recommendations based on student history and learning style
- Show clear value proposition for next subject
- Adapt suggestions based on grade level and academic goals

**LLM-Based Recommendation Logic**:

The recommendation engine uses GPT-4 to generate highly personalized, context-aware subject suggestions that consider:

- Completed goal details
- Student's complete learning history
- Grade level and academic trajectory
- Learning patterns and preferences
- Natural subject progressions

**Implementation**:

```python
# backend/recommendations.py
from openai import OpenAI
import json

client = OpenAI()

RECOMMENDATION_PROMPT = """You are an expert academic advisor for K-12 and college prep students.

STUDENT PROFILE:
Name: {student_name}
Grade: {grade}
Completed Goal: {completed_goal}
All Completed Subjects: {completed_subjects}
Current Subjects: {current_subjects}

LEARNING HISTORY:
{learning_summary}

TASK:
Suggest 3 related subjects this student should study next. Consider:
1. Natural academic progressions (e.g., Algebra → Geometry → Trigonometry)
2. Related skill areas (e.g., Chemistry → Physics for STEM)
3. College prep needs (e.g., SAT complete → College Essays)
4. Student's demonstrated interests and strengths
5. Grade-appropriate recommendations

For each recommendation:
- Choose subjects that build on completed work
- Provide compelling, personalized reasons
- List 3-4 specific skills they'll develop
- Suggest an appropriate difficulty level

IMPORTANT:
- DO NOT suggest subjects they're already studying or have completed
- Prioritize high-value subjects for college applications if student is grades 10-12
- Consider interdisciplinary connections
- Make recommendations exciting and achievable

OUTPUT FORMAT (strict JSON):
{{
  "recommendations": [
    {{
      "subject": "Physics",
      "reason": "Your chemistry foundation makes physics a natural next step - you'll see how the concepts connect in exciting ways",
      "related_skills": ["Forces and motion", "Energy conservation", "Electricity and magnetism", "Problem-solving"],
      "difficulty": "medium",
      "college_value": "high",
      "icon": "⚡"
    }},
    {{
      "subject": "AP Chemistry",
      "reason": "Take your chemistry knowledge to college level and earn potential college credit",
      "related_skills": ["Thermodynamics", "Chemical kinetics", "Equilibrium", "Advanced lab techniques"],
      "difficulty": "hard",
      "college_value": "very high",
      "icon": "🧪"
    }},
    {{
      "subject": "Biology",
      "reason": "Explore life sciences and see chemistry in action at the molecular level",
      "related_skills": ["Cell biology", "Genetics", "Biochemistry", "Evolution"],
      "difficulty": "medium",
      "college_value": "high",
      "icon": "🧬"
    }}
  ],
  "reasoning": "Brief explanation of why these three subjects make sense for this student"
}}"""

def get_recommendations(student):
    """Generate personalized recommendations using LLM"""

    # Check if student has completed goals
    if not student['completed_goals']:
        return {"recommendations": [], "reasoning": "No completed goals yet"}

    # Get most recent completed goal
    last_completed = student['completed_goals'][-1]

    # Build learning summary from session history
    learning_summary = build_learning_summary(student)

    # Prepare completed and current subjects lists
    completed_subjects = [g['subject'] for g in student['completed_goals']]
    current_subjects = [g['subject'] for g in student.get('current_goals', [])]

    # Format the prompt
    prompt = RECOMMENDATION_PROMPT.format(
        student_name=student['name'],
        grade=student['grade'],
        completed_goal=f"{last_completed['subject']}: {last_completed.get('description', 'Goal completed')}",
        completed_subjects=", ".join(completed_subjects) if completed_subjects else "None",
        current_subjects=", ".join(current_subjects) if current_subjects else "None",
        learning_summary=learning_summary
    )

    try:
        # Generate recommendations using GPT-4
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert academic advisor. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Filter out any subjects already in student's profile (safety check)
        all_student_subjects = set(completed_subjects + current_subjects)
        filtered_recs = [
            rec for rec in result['recommendations']
            if rec['subject'] not in all_student_subjects
        ]

        # Log recommendations for analytics
        log_recommendation_event(
            student_id=student['student_id'],
            completed_goal=last_completed['subject'],
            recommendations=[r['subject'] for r in filtered_recs]
        )

        return {
            "recommendations": filtered_recs[:3],  # Top 3
            "reasoning": result.get('reasoning', '')
        }

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        # Fallback to basic suggestions if LLM fails
        return get_fallback_recommendations(last_completed['subject'])

def build_learning_summary(student):
    """Create a concise summary of student's learning history"""

    summaries = []

    # Summarize quiz performance
    if 'quiz_history' in student and student['quiz_history']:
        avg_score = sum(q['percentage'] for q in student['quiz_history']) / len(student['quiz_history'])
        summaries.append(f"Average quiz performance: {avg_score:.0f}%")

    # Summarize engagement
    if 'engagement' in student:
        summaries.append(f"Recent engagement: {student['engagement']['sessions_last_7_days']} sessions in last 7 days")

    # Summarize completed goals
    if student['completed_goals']:
        completed = ", ".join([g['subject'] for g in student['completed_goals'][-3:]])
        summaries.append(f"Recently mastered: {completed}")

    return " | ".join(summaries) if summaries else "New student, building learning history"

def get_fallback_recommendations(subject):
    """Simple fallback if LLM fails"""
    FALLBACK_MAP = {
        "SAT Math": ["SAT Reading & Writing", "AP Calculus", "College Essays"],
        "Chemistry": ["Physics", "AP Chemistry", "Biology"],
        "Algebra": ["Geometry", "Trigonometry", "Pre-Calculus"],
        "default": ["Study Skills", "Test Prep", "Time Management"]
    }

    subjects = FALLBACK_MAP.get(subject, FALLBACK_MAP["default"])

    return {
        "recommendations": [
            {
                "subject": s,
                "reason": f"Recommended based on completing {subject}",
                "related_skills": ["Core concepts", "Advanced techniques"],
                "difficulty": "medium",
                "college_value": "high",
                "icon": "📚"
            }
            for s in subjects
        ],
        "reasoning": "Using default recommendations"
    }

def log_recommendation_event(student_id, completed_goal, recommendations):
    """Track recommendations for analytics"""
    # Store in database for later analysis
    # This helps measure conversion rates and improve prompts
    pass
```

**Recommendation Display**:

- Shown immediately when goal marked complete with personalized message
- Card UI with subject icon, title, personalized benefit statement
- Shows difficulty level and college application value
- "Start Learning" CTA → creates new goal
- AI-generated reasoning displayed to build trust

**Technical Implementation**:

```
- Primary: GPT-4 Turbo for intelligent suggestions
- Fallback: Simple rule-based system if API fails
- Storage: Log all recommendations and student responses for continuous improvement
- Cost: ~$0.01 per recommendation generation
```

**Why LLM-Based is Superior**:

1. **Personalization**: Considers full student context, not just completed subject
2. **Adaptability**: Works for any subject combination, even unusual paths
3. **Compelling Copy**: Generates unique, motivating reasons for each student
4. **Smart Filtering**: Understands nuanced relationships between subjects
5. **Continuous Improvement**: Can refine prompt based on conversion data

---

## Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     STUDENT (Web Browser)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FRONTEND (React.js)                         │
│  • Chat Interface (conversational UI)                        │
│  • Progress Dashboard (charts, goal cards)                   │
│  • Practice Quiz UI (interactive questions)                  │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Routes                                           │  │
│  │  • /chat (POST) - conversational agent                │  │
│  │  • /practice (POST) - generate quiz                   │  │
│  │  • /progress (GET) - fetch dashboard data             │  │
│  │  • /recommendations (GET) - suggest subjects          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  AI Engine (LangChain)                                │  │
│  │  • RAG Pipeline - retrieve relevant session context   │  │
│  │  • LLM Orchestration - GPT-4 with prompt templates    │  │
│  │  • Memory Manager - conversation history              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────┬───────────────────────┬────────────────────────┬──────┘
      │                       │                        │
      ▼                       ▼                        ▼
┌───────────┐       ┌──────────────────┐    ┌─────────────────┐
│ ChromaDB  │       │  SQLite          │    │  OpenAI API     │
│ (Vectors) │       │  (Metadata)      │    │  (GPT-4)        │
│           │       │                  │    │                 │
│ • Session │       │ • Student data   │    │ • Chat          │
│   embeds  │       │ • Quiz results   │    │ • Quiz gen      │
│ • Chat    │       │ • Progress       │    │ • Summaries     │
│   history │       │ • Nudge logs     │    │                 │
└───────────┘       └──────────────────┘    └─────────────────┘
```

### Technology Stack

| Layer             | Technology                         | Justification                                          |
| ----------------- | ---------------------------------- | ------------------------------------------------------ |
| **Frontend**      | React.js + Vite                    | Fast dev setup, component reusability                  |
| **UI Components** | Tailwind CSS + shadcn/ui           | Rapid styling, pre-built components                    |
| **Charts**        | Recharts                           | React-native, lightweight                              |
| **Backend**       | FastAPI (Python)                   | Fast API development, async support                    |
| **Auth**          | FastAPI-JWT + bcrypt               | Secure token-based authentication                      |
| **AI Framework**  | LangChain                          | RAG pipeline, LLM orchestration                        |
| **LLM**           | GPT-4o                             | Balanced cost/quality, structured output, vision-ready |
| **Embeddings**    | text-embedding-3-small             | Fast, cost-effective                                   |
| **Vector DB**     | ChromaDB                           | Local, no setup, persistent                            |
| **Metadata DB**   | SQLite                             | Lightweight, file-based, auth storage                  |
| **Email**         | SendGrid API (real) + mock console | Real email delivery + development logging              |
| **Hosting**       | Vercel (FE) + Render (BE)          | Free tier, fast deployment                             |

**Integration Notes (MVP Phase)**:

- ✅ **Authentication**: Native JWT system (not integrated with Nerdy yet)
- ✅ **Tutoring Sessions**: Mock transcripts stored in `/data/transcripts/`
- ✅ **Subject List**: Generic subjects for MVP (e.g., Chemistry, Algebra, SAT Math, Spanish)
- ✅ **Tutor Booking**: Mock booking page with form pre-filled with student/subject info
- ✅ **Session History**: Mocked from local data (not pulling from Nerdy's tutoring system yet)
- 📋 **Phase 2 Integration**: Connect to real Nerdy booking system, subject taxonomy, session data

---

### Data Flow Examples

**Chat Interaction**:

```
1. User sends message → Frontend POST /chat
2. Backend retrieves conversation history (SQLite)
3. Backend performs semantic search on transcripts (ChromaDB)
4. Backend constructs prompt with context
5. LLM generates response (OpenAI API)
6. Backend stores exchange (SQLite)
7. Response returned to frontend
```

**Practice Quiz Generation**:

```
1. User clicks "Practice Chemistry" → Frontend POST /practice
2. Backend fetches recent chemistry sessions (ChromaDB)
3. Backend identifies weak concepts from quiz history (SQLite)
4. LLM generates 5 adaptive questions (OpenAI API)
5. Questions stored with quiz_id (SQLite)
6. Questions returned to frontend
7. User completes quiz → POST /practice/submit
8. Backend scores, updates progress (SQLite)
```

---

## Mock Data Specification

### Student Profiles (5 personas)

```json
[
  {
    "student_id": "S001",
    "name": "Ava Johnson",
    "email": "ava.johnson@example.com",
    "grade": 11,
    "subjects": ["Chemistry", "Math"],
    "current_goals": [
      {
        "goal_id": "G001",
        "subject": "Chemistry",
        "description": "Master VSEPR theory and molecular geometry",
        "progress": 0.75,
        "started": "2025-10-15",
        "target_date": "2025-11-10"
      }
    ],
    "completed_goals": [
      {
        "subject": "SAT Math",
        "description": "Score 700+",
        "completed": "2025-10-01"
      }
    ],
    "engagement": {
      "sessions_last_7_days": 2,
      "last_active": "2025-11-03",
      "total_chat_messages": 47
    }
  },
  {
    "student_id": "S002",
    "name": "Marcus Lee",
    "email": "marcus.lee@example.com",
    "grade": 9,
    "subjects": ["Algebra", "English"],
    "current_goals": [
      {
        "goal_id": "G002",
        "subject": "Algebra",
        "description": "Understand quadratic equations",
        "progress": 0.3,
        "started": "2025-10-28",
        "target_date": "2025-11-15"
      }
    ],
    "completed_goals": [],
    "engagement": {
      "sessions_last_7_days": 1,
      "last_active": "2025-10-29",
      "total_chat_messages": 8
    }
  },
  {
    "student_id": "S003",
    "name": "Priya Sharma",
    "email": "priya.sharma@example.com",
    "grade": 12,
    "subjects": ["AP Chemistry", "Physics"],
    "current_goals": [
      {
        "goal_id": "G003",
        "subject": "AP Chemistry",
        "description": "Complete thermodynamics unit",
        "progress": 0.9,
        "started": "2025-09-20",
        "target_date": "2025-11-05"
      }
    ],
    "completed_goals": [
      {
        "subject": "SAT Chemistry",
        "description": "Score 750+",
        "completed": "2025-10-20"
      }
    ],
    "engagement": {
      "sessions_last_7_days": 5,
      "last_active": "2025-11-04",
      "total_chat_messages": 112
    }
  },
  {
    "student_id": "S004",
    "name": "Jordan Taylor",
    "email": "jordan.taylor@example.com",
    "grade": 10,
    "subjects": ["Geometry"],
    "current_goals": [
      {
        "goal_id": "G004",
        "subject": "Geometry",
        "description": "Master triangle proofs",
        "progress": 0.15,
        "started": "2025-11-01",
        "target_date": "2025-11-30"
      }
    ],
    "completed_goals": [],
    "engagement": {
      "sessions_last_7_days": 0,
      "last_active": "2025-11-01",
      "total_chat_messages": 3
    }
  },
  {
    "student_id": "S005",
    "name": "Sofia Martinez",
    "email": "sofia.martinez@example.com",
    "grade": 11,
    "subjects": ["Spanish", "History"],
    "current_goals": [],
    "completed_goals": [
      {
        "subject": "Spanish I",
        "description": "Complete introductory course",
        "completed": "2025-11-02"
      }
    ],
    "engagement": {
      "sessions_last_7_days": 3,
      "last_active": "2025-11-02",
      "total_chat_messages": 34
    }
  }
]
```

### Session Transcripts (3 examples per student)

**Example - Ava's Chemistry Session**:

```
Date: 2025-10-28
Subject: Chemistry
Topics: Ionic bonds, Covalent bonds, Electronegativity

Transcript:
Tutor: Hi Ava! Today we're going to dive into chemical bonding. Let's start with ionic bonds. Can you tell me what you remember about ions?

Student: Ions are atoms that have gained or lost electrons, right?

Tutor: Exactly! When an atom loses electrons, it becomes positively charged, and we call it a cation. When it gains electrons, it becomes negatively charged—an anion. Ionic bonds form between cations and anions. The classic example is table salt, NaCl. Sodium gives up an electron to chlorine.

Student: Got it. So what about covalent bonds?

Tutor: Great question. Covalent bonds are when atoms share electrons instead of transferring them. This usually happens between nonmetals. For example, in a water molecule, H₂O, oxygen shares electrons with two hydrogen atoms.

Student: Okay, but I'm confused about when a bond is polar. Like, how do I know?

Tutor: That's where electronegativity comes in! It's a measure of how strongly an atom attracts electrons in a bond. If two atoms have very different electronegativities—say, a difference greater than 0.5—the bond becomes polar. The more electronegative atom pulls the electrons closer, creating a partial negative charge, while the other atom gets a partial positive charge.

Student: Oh! So in water, oxygen is more electronegative than hydrogen?

Tutor: Exactly! Oxygen has an electronegativity of about 3.5, and hydrogen is around 2.1. That difference makes the O-H bonds polar, and that's why water is a polar molecule. This polarity is actually why water has such unique properties, like being a great solvent.

Student: That makes sense now. So if I see a bond between two atoms with similar electronegativities, it's nonpolar?

Tutor: Bingo! Like in O₂ or N₂, where both atoms are the same, the electronegativity difference is zero, so the bond is perfectly nonpolar. You're getting this!

Tutor Notes: Ava grasped ionic vs. covalent quickly but needed extra time on polarity. She should practice identifying polar vs. nonpolar bonds using electronegativity values. Consider assigning practice problems on molecular geometry and VSEPR theory next.
```

### Quiz Performance Data

```json
{
  "student_id": "S001",
  "quiz_history": [
    {
      "quiz_id": "Q001",
      "date": "2025-10-20",
      "subject": "Chemistry",
      "topic": "Ionic Bonding",
      "score": 4,
      "total": 5,
      "percentage": 80,
      "time_spent_seconds": 320
    },
    {
      "quiz_id": "Q002",
      "date": "2025-10-25",
      "subject": "Chemistry",
      "topic": "Covalent Bonding",
      "score": 3,
      "total": 5,
      "percentage": 60,
      "time_spent_seconds": 420
    },
    {
      "quiz_id": "Q003",
      "date": "2025-11-01",
      "subject": "Chemistry",
      "topic": "Electronegativity & Polarity",
      "score": 4,
      "total": 5,
      "percentage": 80,
      "time_spent_seconds": 280
    }
  ]
}
```

### Performance Metrics (Before/After Mock)

| Metric               | Before AI Companion | After AI Companion | Improvement |
| -------------------- | ------------------- | ------------------ | ----------- |
| Avg Quiz Score       | 68%                 | 84%                | +23.5%      |
| Sessions per Week    | 2.1                 | 3.8                | +81%        |
| Day 7 Retention      | 54%                 | 73%                | +35%        |
| Goal Completion Rate | 61%                 | 78%                | +28%        |
| Avg Response Time    | N/A                 | 1.4s               | N/A         |
| Student Satisfaction | 3.8/5               | 4.6/5              | +21%        |

---

## 48-Hour Sprint Breakdown

### Phase 0: Setup & Planning (0-2 hours)

**Human Tasks**:

- Review PRD and prioritize features
- Set up GitHub repo
- Initialize frontend (Vite + React) and backend (FastAPI)
- Configure OpenAI API keys and SendGrid API keys
- Create mock student accounts with test emails

**AI-Assisted**:

- Generate project scaffolding prompts
- Create folder structure (including `/data/transcripts/`, `/data/students.json`)
- Set up dependencies (package.json, requirements.txt)
- Create authentication boilerplate (FastAPI-JWT setup)

**Deliverables**:

- GitHub repo initialized
- Frontend and backend running locally
- `/data/` folder with mock student profiles
- SQLite schema for users, students, conversations, quiz results, goals
- SendGrid API key configured (ready for Phase 7)

---

### Phase 1: Mock Data Creation (2-6 hours)

**AI Tools**: ChatGPT, Claude, GPT-4

**Tasks**:

1. Generate 5 diverse student profiles (JSON)
2. Create 15 session transcripts (3 per student, various subjects)
3. Generate quiz performance history
4. Create mock improvement metrics

**Prompts**:

```
"Generate 5 realistic student profiles for a tutoring platform. Include:
- Student ID, name, grade level
- 1-2 current subjects
- Current learning goals with progress percentages
- Completed goals
- Engagement metrics (sessions last 7 days, last active date)
Format as JSON array."

"Write a realistic tutoring session transcript between a chemistry tutor
and an 11th grade student named Ava. The session covers ionic bonds,
covalent bonds, and electronegativity. The student is initially confused
about polarity. Include tutor notes at the end. ~400 words."
```

**Deliverable**: `/data` folder with `students.json`, `transcripts/`, `quiz_results.json`

---

### Phase 2: RAG Pipeline Setup (6-12 hours)

**AI Tools**: Cursor, GitHub Copilot, ChatGPT

**Tasks**:

1. Initialize ChromaDB and create collections
2. Embed session transcripts using OpenAI embeddings
3. Implement semantic search function
4. Test retrieval quality with sample queries

**Key Code (AI-generated)**:

```python
# backend/rag_engine.py
import chromadb
from openai import OpenAI

client = OpenAI()
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("session_transcripts")

def embed_transcripts(transcripts):
    """Embed and store session transcripts"""
    for t in transcripts:
        embedding = client.embeddings.create(
            input=t['content'],
            model="text-embedding-3-small"
        ).data[0].embedding

        collection.add(
            ids=[t['session_id']],
            embeddings=[embedding],
            metadatas=[{
                "student_id": t['student_id'],
                "subject": t['subject'],
                "date": t['date']
            }],
            documents=[t['content']]
        )

def retrieve_context(query, student_id, top_k=3):
    """Retrieve relevant transcript chunks"""
    query_embedding = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    ).data[0].embedding

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"student_id": student_id}
    )

    return results['documents'][0]
```

**Validation**:

- Query: "What did we learn about ionic bonds?" → Should return relevant chemistry session
- Query: "How do I solve quadratic equations?" → Should return algebra session

---

### Phase 3: Conversational Agent (12-20 hours)

**AI Tools**: Cursor, ChatGPT, LangChain docs

**Tasks**:

1. Create chat API endpoint (`/chat`)
2. Implement LangChain conversation chain
3. Design prompt templates with context injection
4. Add human handoff detection logic
5. Build chat UI component (React)

**Key Implementation**:

```python
# backend/ai_agent.py
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough

llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.7)

SYSTEM_PROMPT = """You are a friendly AI study companion for {student_name}, a grade {grade} student.

RECENT LESSONS:
{retrieved_context}

CURRENT GOALS:
{current_goals}

CONVERSATION HISTORY:
{chat_history}

Guidelines:
- Be encouraging and supportive
- Refer to specific lessons when relevant
- If you're unsure or the question is complex, suggest: "This might be a great question for your tutor! Want to book a session?"
- Keep responses 2-3 paragraphs max
- Use examples and analogies

STUDENT: {user_input}
AI COMPANION:"""

def generate_response(student_id, user_input, chat_history):
    # Retrieve context
    context = retrieve_context(user_input, student_id)

    # Get student data
    student = get_student(student_id)

    # Build prompt
    prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)

    # Generate response
    chain = (
        {
            "student_name": lambda x: student['name'],
            "grade": lambda x: student['grade'],
            "retrieved_context": lambda x: "\n".join(context),
            "current_goals": lambda x: format_goals(student['current_goals']),
            "chat_history": lambda x: format_history(chat_history[-10:]),
            "user_input": RunnablePassthrough()
        }
        | prompt
        | llm
    )

    response = chain.invoke(user_input)

    # Check for handoff triggers
    if should_handoff(response, user_input):
        response += "\n\n💡 This might be a great topic for your next tutoring session! [Book Now]"

    return response.content
```

**Frontend (React)**:

```jsx
// components/ChatInterface.jsx
import { useState, useEffect, useRef } from "react";
import { Send } from "lucide-react";

export function ChatInterface({ studentId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: studentId,
          message: input,
          history: messages,
        }),
      });

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                msg.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-100 text-gray-900"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && <div className="text-gray-500">AI is thinking...</div>}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask me anything about your lessons..."
          className="flex-1 rounded-lg border border-gray-300 p-3"
        />
        <button
          onClick={sendMessage}
          className="bg-blue-500 text-white rounded-lg px-6 hover:bg-blue-600"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
}
```

**Testing Scenarios**:

1. "What did we learn about chemical bonds?"
2. "I'm still confused about electronegativity"
3. "Can you help me with my homework?"
4. "What should I study next?"

**Human Handoff UI**:

When handoff conditions are met, the chat shows a message like:

```
"This is a great question for your tutor! Would you like to book a session?"
[Book Session Button]
```

Clicking "Book Session" opens a mock tutor booking page (`/book-tutor`) pre-filled with:

- Student name (from profile)
- Current subject
- Brief description of the topic
- Available tutor slots (mocked)
- CTA to confirm booking (mocked - doesn't actually book)

**Note**: Phase 2 integration will connect this to Nerdy's real booking system.

---

### Phase 4: Practice Quiz Generator (20-28 hours)

**AI Tools**: Cursor, ChatGPT

**Tasks**:

1. Create quiz generation endpoint (`/practice`)
2. Implement adaptive difficulty logic
3. Build quiz UI with immediate feedback
4. Store and analyze quiz results

**Quiz Generation Logic**:

```python
# backend/quiz_generator.py
import json

QUIZ_PROMPT = """Generate {num_questions} multiple-choice questions for a grade {grade} student studying {subject}.

Context from recent lesson:
{lesson_context}

Difficulty level: {difficulty}

Student's weak areas:
{weak_concepts}

Requirements:
- Focus on conceptual understanding, not just memorization
- Include 1-2 questions targeting weak areas
- Provide clear explanations for correct answers
- Match difficulty to student's current level

Format as JSON:
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": "B",
      "explanation": "Why B is correct...",
      "topic": "Specific topic",
      "difficulty": "easy|medium|hard"
    }}
  ]
}}"""

def generate_quiz(student_id, subject, num_questions=5):
    student = get_student(student_id)

    # Get recent lessons
    lesson_context = retrieve_context(
        f"recent lessons about {subject}",
        student_id,
        top_k=2
    )

    # Analyze quiz history for weak spots
    weak_concepts = identify_weak_areas(student_id, subject)

    # Determine difficulty
    avg_score = calculate_avg_score(student_id, subject)
    difficulty = "easy" if avg_score < 60 else "medium" if avg_score < 80 else "hard"

    # Generate questions
    prompt = QUIZ_PROMPT.format(
        num_questions=num_questions,
        grade=student['grade'],
        subject=subject,
        lesson_context="\n".join(lesson_context),
        difficulty=difficulty,
        weak_concepts=", ".join(weak_concepts) if weak_concepts else "None identified"
    )

    response = llm.invoke(prompt)
    quiz_data = json.loads(response.content)

    # Store quiz in DB
    quiz_id = store_quiz(student_id, subject, quiz_data)

    return {
        "quiz_id": quiz_id,
        "questions": quiz_data['questions']
    }

def submit_quiz(quiz_id, answers):
    quiz = get_quiz(quiz_id)
    correct = sum(1 for q, a in zip(quiz['questions'], answers)
                  if q['correct_answer'] == a)
    score = (correct / len(answers)) * 100

    # Store results
    store_quiz_result(quiz_id, score, answers)

    # Update progress
    update_student_progress(quiz['student_id'], quiz['subject'], score)

    return {
        "score": score,
        "correct": correct,
        "total": len(answers),
        "feedback": generate_feedback(score)
    }
```

**Auto-Goal Completion Logic**:

```python
def check_goal_completion(student_id, subject):
    """Check if student should complete goal based on quiz performance"""

    # Get recent quizzes for this subject (last 5)
    recent_quizzes = get_recent_quizzes(student_id, subject, limit=5)

    if len(recent_quizzes) < 2:
        return False  # Need at least 2 quizzes

    # Calculate average score
    avg_score = sum(q['score'] for q in recent_quizzes) / len(recent_quizzes)

    # Auto-complete if average score ≥ 85%
    if avg_score >= 85:
        goal = get_active_goal(student_id, subject)
        if goal:
            complete_goal(goal['goal_id'])
            # Trigger recommendation engine immediately (Phase 6)
            trigger_recommendations(student_id, goal)
            return True

    return False
```

**Immediate Recommendation Display**:

When a goal is auto-completed, the UI shows:

1. Celebration message ("🎉 You've mastered {subject}!")
2. Recommendation cards appear immediately (via WebSocket or polling)
3. Student can click "Start Learning" to create new goal from recommendation

---

**Frontend Quiz UI**:

```jsx
// components/QuizInterface.jsx
import { useState } from "react";

export function QuizInterface({ studentId, subject }) {
  const [quiz, setQuiz] = useState(null);
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [results, setResults] = useState(null);

  const startQuiz = async () => {
    const res = await fetch("/api/practice", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: studentId, subject }),
    });
    const data = await res.json();
    setQuiz(data);
  };

  const submitQuiz = async () => {
    const res = await fetch(`/api/practice/${quiz.quiz_id}/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers: Object.values(answers) }),
    });
    const data = await res.json();
    setResults(data);
    setSubmitted(true);
  };

  if (!quiz) {
    return (
      <div className="text-center p-8">
        <h2 className="text-2xl font-bold mb-4">
          Ready to practice {subject}?
        </h2>
        <button
          onClick={startQuiz}
          className="bg-blue-500 text-white px-6 py-3 rounded-lg"
        >
          Start Quiz
        </button>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="max-w-2xl mx-auto p-8">
        <h2 className="text-3xl font-bold mb-4">Quiz Results</h2>
        <div className="text-6xl font-bold text-blue-500 mb-4">
          {results.score}%
        </div>
        <p className="text-xl mb-6">
          You got {results.correct} out of {results.total} correct!
        </p>
        <p className="text-gray-700 mb-8">{results.feedback}</p>
        <button
          onClick={() => window.location.reload()}
          className="bg-blue-500 text-white px-6 py-3 rounded-lg"
        >
          Practice Again
        </button>
      </div>
    );
  }

  const question = quiz.questions[currentQ];

  return (
    <div className="max-w-2xl mx-auto p-8">
      <div className="mb-4 text-sm text-gray-500">
        Question {currentQ + 1} of {quiz.questions.length}
      </div>

      <h3 className="text-xl font-bold mb-6">{question.question}</h3>

      <div className="space-y-3 mb-6">
        {question.options.map((opt, i) => (
          <button
            key={i}
            onClick={() => setAnswers({ ...answers, [currentQ]: opt[0] })}
            className={`w-full text-left p-4 rounded-lg border-2 transition ${
              answers[currentQ] === opt[0]
                ? "border-blue-500 bg-blue-50"
                : "border-gray-200 hover:border-gray-300"
            }`}
          >
            {opt}
          </button>
        ))}
      </div>

      <div className="flex justify-between">
        <button
          onClick={() => setCurrentQ(Math.max(0, currentQ - 1))}
          disabled={currentQ === 0}
          className="px-4 py-2 rounded-lg border disabled:opacity-50"
        >
          Previous
        </button>

        {currentQ === quiz.questions.length - 1 ? (
          <button
            onClick={submitQuiz}
            disabled={Object.keys(answers).length !== quiz.questions.length}
            className="px-6 py-2 bg-green-500 text-white rounded-lg disabled:opacity-50"
          >
            Submit Quiz
          </button>
        ) : (
          <button
            onClick={() => setCurrentQ(currentQ + 1)}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
}
```

---

### Phase 5: Progress Dashboard (28-36 hours)

**AI Tools**: v0.dev (UI generation), Cursor

**Tasks**:

1. Create dashboard layout
2. Implement progress charts (Recharts)
3. Build goal cards with progress bars
4. Add activity feed

**Dashboard Components**:

```jsx
// components/Dashboard.jsx
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { TrendingUp, Target, Award } from "lucide-react";

export function Dashboard({ student }) {
  const quizData = transformQuizHistory(student.quiz_history);

  return (
    <div className="max-w-6xl mx-auto p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Hi {student.name}! 👋</h1>
        <p className="text-gray-600">Here's your learning journey</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-3 gap-6">
        <StatCard
          icon={<TrendingUp />}
          label="Session Streak"
          value={`${student.engagement.sessions_last_7_days} this week`}
          trend="+2 from last week"
        />
        <StatCard
          icon={<Target />}
          label="Goals Progress"
          value={`${calculateAvgProgress(student.current_goals)}%`}
          trend="On track"
        />
        <StatCard
          icon={<Award />}
          label="Quiz Average"
          value={`${calculateQuizAvg(student.quiz_history)}%`}
          trend="+12% improvement"
        />
      </div>

      {/* Current Goals */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Your Goals</h2>
        <div className="space-y-4">
          {student.current_goals.map((goal) => (
            <GoalCard key={goal.goal_id} goal={goal} />
          ))}
        </div>
      </div>

      {/* Quiz Performance Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Quiz Performance Trend</h2>
        <LineChart width={800} height={300} data={quizData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#3B82F6"
            strokeWidth={2}
          />
        </LineChart>
      </div>

      {/* Recommended Next Steps */}
      {student.completed_goals.length > 0 && (
        <RecommendationSection student={student} />
      )}
    </div>
  );
}

function GoalCard({ goal }) {
  const daysLeft = calculateDaysLeft(goal.target_date);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="font-bold text-lg">{goal.subject}</h3>
          <p className="text-gray-600">{goal.description}</p>
        </div>
        <span className="text-sm text-gray-500">{daysLeft} days left</span>
      </div>

      <div className="mb-2">
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500 transition-all"
            style={{ width: `${goal.progress * 100}%` }}
          />
        </div>
      </div>

      <div className="flex justify-between items-center text-sm">
        <span className="text-gray-600">
          {Math.round(goal.progress * 100)}% complete
        </span>
        <button className="text-blue-500 font-medium hover:underline">
          Continue Learning →
        </button>
      </div>
    </div>
  );
}
```

---

### Phase 6: Recommendation Engine (36-40 hours)

**AI Tools**: GPT-4 API, Cursor, ChatGPT (prompt engineering)

**Tasks**:

1. Implement LLM-based recommendation generation
2. Create recommendation display UI with rich context
3. Add goal creation flow from recommendations
4. Test conversion tracking and prompt effectiveness

**Implementation**:

```python
# backend/recommendations.py
from openai import OpenAI
import json

client = OpenAI()

RECOMMENDATION_PROMPT = """You are an expert academic advisor for K-12 and college prep students.

STUDENT PROFILE:
Name: {student_name}
Grade: {grade}
Completed Goal: {completed_goal}
All Completed Subjects: {completed_subjects}
Current Subjects: {current_subjects}

LEARNING HISTORY:
{learning_summary}

TASK:
Suggest 3 related subjects this student should study next. Consider:
1. Natural academic progressions (e.g., Algebra → Geometry)
2. Related skill areas (e.g., Chemistry → Physics)
3. College prep needs (e.g., SAT complete → College Essays)
4. Student's demonstrated interests and strengths
5. Grade-appropriate recommendations

For each recommendation:
- Choose subjects that build on completed work
- Provide compelling, personalized reasons
- List 3-4 specific skills they'll develop

DO NOT suggest subjects they're already studying or have completed.

OUTPUT FORMAT (strict JSON):
{{
  "recommendations": [
    {{
      "subject": "Physics",
      "reason": "Your chemistry foundation makes physics a natural next step",
      "related_skills": ["Forces", "Energy", "Electricity", "Problem-solving"],
      "difficulty": "medium",
      "college_value": "high",
      "icon": "⚡"
    }}
  ],
  "reasoning": "Brief explanation of why these three subjects make sense"
}}"""

def get_recommendations(student):
    """Generate personalized recommendations using LLM"""

    if not student['completed_goals']:
        return {"recommendations": [], "reasoning": "No completed goals yet"}

    last_completed = student['completed_goals'][-1]
    learning_summary = build_learning_summary(student)

    completed_subjects = [g['subject'] for g in student['completed_goals']]
    current_subjects = [g['subject'] for g in student.get('current_goals', [])]

    prompt = RECOMMENDATION_PROMPT.format(
        student_name=student['name'],
        grade=student['grade'],
        completed_goal=f"{last_completed['subject']}: {last_completed.get('description', 'Goal completed')}",
        completed_subjects=", ".join(completed_subjects) if completed_subjects else "None",
        current_subjects=", ".join(current_subjects) if current_subjects else "None",
        learning_summary=learning_summary
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert academic advisor. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Filter out subjects already in student's profile (safety check)
        all_student_subjects = set(completed_subjects + current_subjects)
        filtered_recs = [
            rec for rec in result['recommendations']
            if rec['subject'] not in all_student_subjects
        ]

        log_recommendation_event(student['student_id'], last_completed['subject'],
                                 [r['subject'] for r in filtered_recs])

        return {
            "recommendations": filtered_recs[:3],
            "reasoning": result.get('reasoning', '')
        }

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return get_fallback_recommendations(last_completed['subject'])

def build_learning_summary(student):
    """Create a concise summary of student's learning history"""
    summaries = []

    if 'quiz_history' in student and student['quiz_history']:
        avg_score = sum(q['percentage'] for q in student['quiz_history']) / len(student['quiz_history'])
        summaries.append(f"Average quiz performance: {avg_score:.0f}%")

    if 'engagement' in student:
        summaries.append(f"Recent engagement: {student['engagement']['sessions_last_7_days']} sessions in last 7 days")

    if student['completed_goals']:
        completed = ", ".join([g['subject'] for g in student['completed_goals'][-3:]])
        summaries.append(f"Recently mastered: {completed}")

    return " | ".join(summaries) if summaries else "New student, building learning history"
```

**Frontend**:

```jsx
// components/RecommendationSection.jsx
import { useState, useEffect } from "react";
import { Sparkles, TrendingUp, Award } from "lucide-react";

function RecommendationSection({ student }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecommendations();
  }, [student]);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `/api/recommendations?student_id=${student.student_id}`
      );
      const result = await res.json();
      setData(result);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoading(false);
    }
  };

  const createGoal = async (subject) => {
    try {
      await fetch("/api/goals", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: student.student_id,
          subject: subject,
          source: "ai_recommendation",
        }),
      });
      // Refresh page or update state
      window.location.reload();
    } catch (error) {
      console.error("Error creating goal:", error);
    }
  };

  if (loading) {
    return (
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-8">
        <div className="flex items-center gap-2 text-gray-600">
          <Sparkles className="animate-pulse" />
          <span>Generating personalized recommendations...</span>
        </div>
      </div>
    );
  }

  if (!data || data.recommendations.length === 0) return null;

  return (
    <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-8">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-3xl">🎉</span>
        <h2 className="text-2xl font-bold">
          Congratulations on completing your goal!
        </h2>
      </div>

      <p className="text-gray-700 mb-2">
        Ready for your next challenge? Based on your progress and interests,
        here are some subjects you might love:
      </p>

      {data.reasoning && (
        <p className="text-sm text-gray-600 italic mb-6">💡 {data.reasoning}</p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {data.recommendations.map((rec, i) => (
          <div
            key={i}
            className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition border-2 border-transparent hover:border-purple-200"
          >
            {/* Icon and Badges */}
            <div className="flex items-start justify-between mb-3">
              <div className="text-4xl">{rec.icon || "📚"}</div>
              <div className="flex flex-col gap-1">
                <span
                  className={`text-xs px-2 py-1 rounded-full ${
                    rec.difficulty === "easy"
                      ? "bg-green-100 text-green-700"
                      : rec.difficulty === "medium"
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-red-100 text-red-700"
                  }`}
                >
                  {rec.difficulty || "medium"}
                </span>
                {rec.college_value && (
                  <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700 flex items-center gap-1">
                    <Award size={10} />
                    {rec.college_value}
                  </span>
                )}
              </div>
            </div>

            {/* Subject Title */}
            <h3 className="font-bold text-lg mb-2">{rec.subject}</h3>

            {/* Personalized Reason */}
            <p className="text-gray-700 text-sm mb-4 leading-relaxed">
              {rec.reason}
            </p>

            {/* Skills */}
            <div className="mb-4">
              <p className="text-xs font-semibold text-gray-500 mb-2">
                You'll learn:
              </p>
              <div className="flex flex-wrap gap-1">
                {rec.related_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* CTA */}
            <button
              onClick={() => createGoal(rec.subject)}
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-2.5 rounded-lg hover:from-purple-600 hover:to-pink-600 transition font-medium flex items-center justify-center gap-2"
            >
              <Sparkles size={16} />
              Start Learning
            </button>
          </div>
        ))}
      </div>

      {/* Alternative Action */}
      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600">
          Not sure yet?{" "}
          <button
            onClick={() => {
              /* Open chat */
            }}
            className="text-purple-600 hover:underline font-medium"
          >
            Chat with your AI companion
          </button>{" "}
          about your options
        </p>
      </div>
    </div>
  );
}

export default RecommendationSection;
```

**Testing Scenarios**:

1. Student completes "SAT Math" → Should recommend SAT Reading, College Essays, AP Calc with personalized reasons
2. Student completes "Chemistry" → Should recommend Physics, AP Chemistry, Biology with STEM-focused messaging
3. Student in grade 9 vs grade 12 → Should receive age-appropriate recommendations
4. Student with high quiz scores → Should receive harder difficulty recommendations

---

### Phase 7: Nudge System (40-44 hours)

**AI Tools**: ChatGPT (email copy), Cursor

**Tasks**:

1. Create nudge detection logic
2. Implement email template system with real SendGrid integration
3. Add console logging for development/testing
4. Add nudge tracking in database

**Backend Logic**:

```python
# backend/nudge_system.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime, timedelta
import os

# Initialize SendGrid
sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))

def check_and_send_nudges():
    """Run this hourly via CRON or scheduler"""
    students = get_all_students()

    for student in students:
        # Day 7 Nudge: <3 sessions since goal started
        if should_send_day7_nudge(student):
            send_day7_nudge(student)

        # Inactivity Nudge: No activity in 3 days
        elif should_send_inactivity_nudge(student):
            send_inactivity_nudge(student)

        # Goal Near Complete: Progress ≥85%
        elif should_send_goal_completion_nudge(student):
            send_goal_completion_nudge(student)

def send_day7_nudge(student):
    subject = f"{student['name']}, let's keep the momentum going! 🚀"

    goal = student['current_goals'][0]
    sessions = student['engagement']['sessions_last_7_days']

    body = f"""
    Hi {student['name']},

    You started strong with {sessions} session{'s' if sessions != 1 else ''} on {goal['subject']}!
    Your AI Study Companion noticed you haven't checked in lately.

    Quick wins waiting for you:
    • 5 practice questions on {goal['description']}
    • Chat about anything you're stuck on
    • See your progress toward your goal

    [Continue Learning] [Book Next Session]

    Your progress shouldn't pause between sessions!

    — Your AI Study Companion
    """

    # Send via SendGrid
    try:
        message = Mail(
            from_email='study-companion@nerdy.com',
            to_emails=student['email'],
            subject=subject,
            plain_text_content=body
        )
        response = sg.send(message)
        print(f"✅ Email sent to {student['email']} (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error sending email to {student['email']}: {e}")

    # Mock console log for development
    print(f"\n📧 NUDGE EMAIL (CONSOLE LOG)")
    print(f"To: {student['email']}")
    print(f"Subject: {subject}")
    print(body)

    # Log nudge in DB
    log_nudge(student['student_id'], 'day7', 'sent')

def should_send_day7_nudge(student):
    if not student['current_goals']:
        return False

    goal = student['current_goals'][0]
    goal_started = datetime.fromisoformat(goal['started'])
    days_since_start = (datetime.now() - goal_started).days

    sessions_count = student['engagement']['sessions_last_7_days']

    # Check if already sent nudge
    nudge_sent = check_nudge_log(student['student_id'], 'day7')

    return (days_since_start == 7 and
            sessions_count < 3 and
            not nudge_sent)

def send_inactivity_nudge(student):
    # Similar implementation...
    pass

def send_goal_completion_nudge(student):
    # Similar implementation...
    pass
```

**CRON Setup (mock)**:

```python
# backend/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        check_and_send_nudges,
        'interval',
        hours=1,
        id='nudge_checker'
    )
    scheduler.start()
```

**Email Configuration**:

- **From Address**: `study-companion@nerdy.com` (update with real Nerdy domain post-launch)
- **SendGrid API Key**: Stored in `.env` file (backend only)
- **Real Emails**: Nudges sent to student email addresses from database
- **Console Logging**: All emails also logged to console for development/debugging
- **Testing**: Use test email accounts (e.g., your own email + temp email services)

---

### Phase 8: Integration & Testing (44-46 hours)

**Tasks**:

1. Connect all components (frontend ↔ backend)
2. End-to-end testing of user flows
3. Performance optimization (caching, lazy loading)
4. Bug fixes

**Critical User Flows to Test**:

1. **New student onboarding** → Chat → Practice → Dashboard
2. **Goal completion** → Recommendations → New goal creation
3. **Low engagement** → Nudge trigger → Re-engagement
4. **Chat handoff** → Tutor booking suggestion

---

### Phase 9: Deployment & Documentation (46-48 hours)

**Tasks**:

1. Deploy frontend to Vercel
2. Deploy backend to Render
3. Create demo video (5 min)
4. Write documentation

**Deployment Steps**:

**Frontend (Vercel)**:

```bash
# Push to GitHub
git add .
git commit -m "Complete AI Study Companion MVP"
git push origin main

# Deploy via Vercel CLI or GitHub integration
vercel --prod
```

**Backend (Render)**:

```yaml
# render.yaml
services:
  - type: web
    name: ai-study-companion-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: OPENAI_API_KEY
        sync: false
```

**Demo Video Script** (5 minutes):

1. **Intro** (30s): Problem statement, solution overview
2. **Chat Demo** (90s): Ask questions, show context retrieval
3. **Practice Quiz** (60s): Generate quiz, take quiz, see results
4. **Dashboard** (60s): Show progress, goals, charts
5. **Recommendations** (45s): Complete goal, see suggestions
6. **Technical Walkthrough** (45s): Show RAG pipeline, AI tools used
7. **Outro** (30s): ROI projection, next steps

---

## AI Tools & Prompting Strategy

### Tool Usage by Phase

| Phase           | Primary Tool     | Prompting Strategy                               | Output                     |
| --------------- | ---------------- | ------------------------------------------------ | -------------------------- |
| Mock Data       | ChatGPT/Claude   | "Generate 5 realistic student profiles..."       | JSON files                 |
| RAG Setup       | Cursor + Copilot | Code completion for ChromaDB setup               | Python code                |
| Chat Agent      | Cursor + ChatGPT | "Build LangChain conversation chain with RAG..." | Backend + prompt templates |
| Quiz Gen        | GPT-4 API        | Structured output with JSON schema               | Quiz questions             |
| Dashboard       | v0.dev + Cursor  | "Create React dashboard with progress charts..." | React components           |
| Recommendations | ChatGPT          | "Generate subject recommendation mapping..."     | Python logic               |
| Email Copy      | ChatGPT          | "Write encouraging nudge email for students..."  | Email templates            |
| Deployment      | GitHub Copilot   | Infrastructure as code suggestions               | Config files               |

### Key Prompts

**Student Profile Generation**:

```
Generate 5 diverse student profiles for a tutoring platform. Include:
- Realistic names (varied backgrounds)
- Grade levels 9-12
- 1-2 subjects (mix STEM and humanities)
- Current goals with 15-90% progress
- 0-5 completed goals
- Engagement metrics: sessions_last_7_days (0-5), last_active (recent dates)

Make one student high-engagement, one at-risk (low sessions), and one who just completed a goal.
Format as JSON array.
```

**Session Transcript Generation**:

```
Write a realistic 400-word tutoring session transcript:
- Subject: {subject}
- Student: {name}, grade {grade}
- Topics: {topics}
- Student starts slightly confused, tutor explains clearly, student shows understanding by end
- Include tutor notes at end identifying student's weak area

Format as plain text with clear speaker labels (Tutor: / Student:).
```

**Chat Response Prompt** (system):

```
You are a friendly, encouraging AI study companion for {student_name}, a grade {grade} student studying {subjects}.

WHAT YOU KNOW:
{retrieved_session_context}

STUDENT'S GOALS:
{current_goals}

YOUR ROLE:
- Answer questions about previous lessons using specific examples
- Explain concepts clearly (use analogies and examples)
- Encourage the student and celebrate progress
- Suggest next study steps
- If the question is complex or beyond your knowledge, say: "This is a great question for your tutor! Want to book a session?"

TONE: Supportive, clear, concise (2-3 paragraphs max)

STUDENT: {user_input}
YOU:
```

**Quiz Generation Prompt**:

```
Generate {num_questions} multiple-choice questions for a grade {grade} {subject} student.

RECENT LESSON CONTEXT:
{session_transcript_excerpt}

STUDENT'S WEAK AREAS (prioritize these):
{identified_weak_concepts}

DIFFICULTY: {easy/medium/hard}

REQUIREMENTS:
- Test conceptual understanding, not memorization
- Include at least one question on weak areas
- Provide detailed explanations for correct answers
- Match difficulty to student level

OUTPUT FORMAT (strict JSON):
{
  "questions": [
    {
      "question": "Clear, specific question text ending with ?",
      "options": ["A) option", "B) option", "C) option", "D) option"],
      "correct_answer": "B",
      "explanation": "2-3 sentence explanation of why B is correct and others are wrong",
      "topic": "Specific subtopic being tested",
      "difficulty": "easy"
    }
  ]
}
```

**Recommendation Prompt** (LLM fallback):

```
A student just completed this goal:
Subject: {subject}
Description: {goal_description}
Grade: {grade}

Suggest 3 related subjects they should study next. Consider:
- Natural academic progressions (Algebra → Geometry)
- Related skills (Chemistry → Physics)
- College prep needs (SAT complete → Essays)

For each recommendation, provide:
- Subject name
- One sentence explaining why it's a good next step
- 3 related skills they'll learn

Format as JSON:
{
  "recommendations": [
    {
      "subject": "Physics",
      "reason": "Natural next step in STEM that builds on chemistry concepts",
      "related_skills": ["Forces", "Energy", "Motion"]
    }
  ]
}
```

---

## Cost Analysis

### Development Costs (48 hours)

| Resource            | Cost        | Notes                               |
| ------------------- | ----------- | ----------------------------------- |
| OpenAI API (GPT-4o) | ~$8         | 300K tokens for development/testing |
| OpenAI Embeddings   | ~$2         | 1M tokens for transcript embedding  |
| SendGrid            | $0          | Free tier (up to 100 emails/day)    |
| Vercel (Frontend)   | $0          | Free hobby plan                     |
| Render (Backend)    | $0          | Free tier (512MB RAM)               |
| Domain (optional)   | $12/yr      | Optional for demo                   |
| **Total**           | **~$10-22** | One-time sprint cost                |

### Production Costs (Monthly, 1000 Active Students)

| Component          | Usage                   | Cost         | Calculation                                                                             |
| ------------------ | ----------------------- | ------------ | --------------------------------------------------------------------------------------- |
| **OpenAI API**     |
| Chat (GPT-4o)      | 10 msgs/student/day     | $300         | 10 msgs × 1000 students × 30 days × 150 tokens avg × $0.005/1K input + $0.015/1K output |
| Quiz Generation    | 2 quizzes/student/week  | $40          | 2 quizzes × 1000 × 4 weeks × 500 tokens × $0.005/1K                                     |
| Recommendations    | 0.5 recs/student/month  | $10          | 500 recs × 800 tokens × $0.005/1K input + $0.015/1K output                              |
| Embeddings         | 3 sessions/student/week | $5           | 3 × 1000 × 4 × 1000 tokens × $0.00013/1K                                                |
| **Infrastructure** |
| Vercel Pro         | Static + serverless     | $20          | Pro plan for custom domain                                                              |
| Render (Backend)   | 2GB RAM instance        | $25          | Standard plan                                                                           |
| ChromaDB Cloud     | 10M vectors             | $0           | Self-hosted initially, $29/mo when scaling                                              |
| SendGrid           | 40K emails/mo           | $20          | Email delivery                                                                          |
| **Total**          |                         | **~$420/mo** | For 1000 students                                                                       |

**Per-Student Monthly Cost**: $0.42 (30% cheaper than GPT-4 Turbo)

**GPT-4o Benefits vs GPT-4 Turbo**:

- ✅ 30-40% cost reduction
- ✅ Faster response times
- ✅ Vision capabilities built-in (future image upload support)
- ✅ Multimodal support (text + image in single API call)
- ✅ Structured output (JSON mode for quizzes)
- ⚠️ Slightly lower reasoning on complex math (mitigated by RAG context)

---

## Success Criteria

### Technical Success

- [ ] All API endpoints respond in <2s (P95)
- [ ] RAG retrieval accuracy ≥80% (relevant context returned)
- [ ] Zero critical bugs in core flows
- [ ] Successfully deployed and accessible via public URLs
- [ ] Handles 10 concurrent users without degradation

### Product Success

- [ ] Chat provides contextually relevant responses in >90% of test cases
- [ ] Quiz questions are appropriate difficulty and topic-relevant
- [ ] Progress dashboard updates in real-time
- [ ] Recommendations shown immediately upon goal completion
- [ ] Nudges sent at correct triggers with <5 min delay

### Business Success (Mock Data Validation)

- [ ] Mock quiz scores show ≥20% improvement over time
- [ ] Recommendation acceptance rate ≥40% (simulated)
- [ ] Day 7 nudge → engagement rate ≥40% (simulated)
- [ ] Clear path to production deployment within 2 weeks
- [ ] Projected ROI ≥500% within 90 days

### AI Sophistication

- [ ] RAG pipeline successfully retrieves relevant session context
- [ ] LLM generates personalized, on-topic responses
- [ ] Adaptive quiz difficulty adjusts based on performance
- [ ] Human handoff triggers work correctly
- [ ] Recommendation logic balances rules and AI flexibility

---

**Success Metrics to Track**:

- Churn rate reduction (target: -10 percentage points)
- Session frequency increase (target: +30%)
- Goal completion rate (target: +20%)
- Student satisfaction score (target: 4.5+/5)
- Tutor satisfaction (target: 80% positive feedback)

---

## Risk Mitigation

| Risk                           | Probability | Impact   | Mitigation                                        |
| ------------------------------ | ----------- | -------- | ------------------------------------------------- |
| **AI response quality issues** | Medium      | High     | Extensive prompt testing, fallback to human tutor |
| **High API costs**             | Medium      | Medium   | Implement caching, optimize context window        |
| **Low student adoption**       | Medium      | High     | User testing, onboarding optimization             |
| **Scalability bottlenecks**    | Low         | High     | Load testing, infrastructure planning             |
| **Data privacy concerns**      | Low         | Critical | FERPA compliance, encryption, audit trail         |
| **Integration complexity**     | Medium      | Medium   | API-first design, incremental rollout             |

---

## Appendix

### Glossary

- **RAG (Retrieval-Augmented Generation)**: AI technique combining semantic search with LLM generation for contextually relevant responses
- **Embeddings**: Numerical vector representations of text enabling semantic similarity search
- **Churn**: Student stopping use of tutoring services
- **Day 7 Engagement**: Critical early retention metric (students with <3 sessions by Day 7 have higher churn)
- **FERPA**: Family Educational Rights and Privacy Act (US student data privacy law)

### References

- LangChain Documentation: https://docs.langchain.com
- ChromaDB Guide: https://docs.trychroma.com
- OpenAI API Reference: https://platform.openai.com/docs
- FastAPI Tutorial: https://fastapi.tiangolo.com
- React + Vite Setup: https://vitejs.dev/guide

---

**Document Version**: 1.0  
**Last Updated**: November 4, 2025  
**Author**: Product Team  
**Status**: Ready for Sprint Kickoff 🚀

---

## MVP Scope & Phase 2 Integration Plan

### What's Mocked in MVP (48-Hour Sprint)

| Component               | MVP Status | Implementation             | Phase 2 Plan                               |
| ----------------------- | ---------- | -------------------------- | ------------------------------------------ |
| **Authentication**      | ✅ Native  | JWT + bcrypt (new system)  | SSO integration with Nerdy accounts        |
| **Session Transcripts** | ✅ Mocked  | Local JSON files           | API pull from Nerdy tutoring sessions      |
| **Subject List**        | ✅ Generic | Hardcoded subjects         | Connect to Nerdy's subject taxonomy        |
| **Tutor Booking**       | ✅ Mocked  | Mock page, form pre-fill   | Integrate with Nerdy's real booking system |
| **Student Database**    | ✅ Mocked  | Local SQLite               | Sync with Nerdy's student master data      |
| **Tutor Profiles**      | ✅ Mocked  | Generic "Available tutors" | Pull real tutor availability and rates     |
| **Payment Integration** | ❌ N/A     | Not in scope               | Phase 3 (post-MVP review)                  |
| **Video Sessions**      | ❌ N/A     | Not in scope               | Phase 3 (post-MVP review)                  |
| **OCR/Image Upload**    | ❌ N/A     | Not in scope               | Phase 2 (if time permits)                  |

### Data Flow: MVP vs Production

**MVP (Current 48-Hour Sprint)**:

```
Student Login
  ↓
[Auth System] (Native JWT)
  ↓
[Mock Student Data] (SQLite local)
  ↓
[Mock Session Transcripts] (/data/transcripts/)
  ↓
[RAG Engine] (ChromaDB + LangChain)
  ↓
[GPT-4o Chat] → Student
  ↓
[Quiz Generation] → Store locally
  ↓
[Recommendations] (LLM-based, stored locally)
  ↓
[Mock Tutor Booking] → Form shows student info + subject
```

**Phase 2 Integration (After MVP Validation)**:

```
Student Login
  ↓
[Nerdy SSO] ← Connect to Nerdy auth
  ↓
[Nerdy Student DB] ← Sync student profiles
  ↓
[Nerdy Session API] ← Pull real tutoring transcripts
  ↓
[RAG Engine] (ChromaDB + LangChain)
  ↓
[GPT-4o Chat] → Student
  ↓
[Quiz Generation] → Store in Nerdy DB
  ↓
[Recommendations] (LLM-based, evaluated against Nerdy subjects)
  ↓
[Nerdy Booking System] ← Real bookings, real tutor assignment
```

### Testing Strategy for MVP

**Mock Data Testing**:

1. Create 5 test student accounts with pre-loaded data
2. Simulate engagement patterns (chat, quizzes, goal completion)
3. Manually trigger nudge system (adjust timestamps for testing)
4. Monitor console logs + real emails to test inbox

**Mocked Integrations Testing**:

1. **Tutor Booking Page**: Verify form pre-fills correctly with student name/subject
2. **Session Transcripts**: Manually add/edit transcripts in `/data/transcripts/`, verify RAG retrieves them
3. **Subject List**: Confirm recommendations stay within generic subject list
4. **Email Sending**: Verify both SendGrid delivery + console logging work

**Phase 2 Readiness**:

- Document all API contracts (input/output formats)
- List all fields that will need to map to Nerdy systems
- Identify custom fields that only exist in AI Companion (mark for future deprecation)
- Create integration checklist for Phase 2 handoff

---

## Prompts for Each AI Tool

### LLM Prompt for Chat (GPT-4o)

```
You are a friendly AI study companion for {student_name}, a grade {grade} student.

STUDENT'S LEARNING CONTEXT:
{retrieved_transcript_chunks}

STUDENT'S CURRENT GOALS:
{current_goals}

RECENT CONVERSATION:
{chat_history_last_10}

STUDENT: {user_message}

Guidelines:
- Reference specific topics from their lessons when relevant
- Explain concepts clearly with examples
- Encourage progress and celebrate achievements
- If unsure or question is complex: "This is a great question for your tutor! Want to book a session?"
- Keep responses 2-3 paragraphs max
- Use warm, supportive tone

RESPONSE:
```

### LLM Prompt for Quiz Generation (GPT-4o)

```
Generate {num_questions} multiple-choice questions for a grade {grade} {subject} student.

RECENT LESSON CONTEXT:
{session_transcript}

STUDENT'S WEAK AREAS (prioritize):
{weak_concepts}

DIFFICULTY: {easy|medium|hard}

Requirements:
- Test conceptual understanding, not memorization
- Include ≥1 question on weak areas
- Provide detailed explanations for correct answers
- Match difficulty to student's recent performance

OUTPUT (strict JSON):
{
  "questions": [
    {
      "question": "Question text ending with ?",
      "options": ["A) option", "B) option", "C) option", "D) option"],
      "correct_answer": "B",
      "explanation": "Why B is correct...",
      "topic": "Specific topic",
      "difficulty": "medium"
    }
  ]
}
```

### LLM Prompt for Recommendations (GPT-4o)

```
You are an expert academic advisor. Suggest 3 related subjects for this student's next learning goal.

STUDENT PROFILE:
- Name: {student_name}
- Grade: {grade}
- Just completed: {completed_goal_subject}
- Past subjects: {completed_subjects_list}
- Currently studying: {current_subjects_list}
- Performance: {avg_quiz_score}% average quiz score

LEARNING HISTORY:
{learning_summary}

TASK:
Suggest 3 subjects that:
1. Build on {completed_goal_subject}
2. Are achievable and exciting for a grade {grade} student
3. Support college/academic goals
4. Are NOT already completed or in progress

For each recommendation:
- Subject name
- Personalized reason why it's perfect for them
- 3-4 specific skills they'll gain
- Difficulty level (easy/medium/hard)
- College prep value (low/medium/high)

OUTPUT (strict JSON):
{
  "recommendations": [
    {
      "subject": "Physics",
      "reason": "Your chemistry foundation makes physics a natural next step",
      "related_skills": ["Forces and motion", "Energy", "Electricity"],
      "difficulty": "medium",
      "college_value": "high",
      "icon": "⚡"
    }
  ],
  "reasoning": "Why these three recommendations make sense"
}
```

---
