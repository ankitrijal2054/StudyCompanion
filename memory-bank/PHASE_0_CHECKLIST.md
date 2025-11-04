# 🚀 PHASE 0: Setup & Planning (Hours 0-2)

**Status**: ✅ IN PROGRESS

**Goal**: Initialize full-stack development environment

**Time**: 0-2 hours

**Deliverables**: Frontend ready, Backend ready, Database schema, Environment variables, GitHub initialized

---

## ✅ CHECKLIST

### 1️⃣ Initialize Frontend (30 min)

```bash
cd /Users/ankit/Desktop/GauntletAI/StudyCompanion
npm create vite@latest frontend -- --template react
cd frontend
npm install react-router-dom recharts lucide-react
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm run dev
```

**Expected**: Frontend running on `http://localhost:5173`

Tasks:

- [ ] Run `npm create vite` command
- [ ] Install dependencies (React Router, Recharts, lucide-react)
- [ ] Install Tailwind CSS
- [ ] Verify `npm run dev` works
- [ ] Test: Open http://localhost:5173 in browser

---

### 2️⃣ Initialize Backend (30 min)

```bash
cd /Users/ankit/Desktop/GauntletAI/StudyCompanion
mkdir backend
cd backend
python3 -m venv venv
source venv/bin/activate
```

**Create requirements.txt**:

```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pyjwt==2.8.1
python-dotenv==1.0.0
openai==1.3.8
chromadb==0.4.21
langchain==0.1.0
sendgrid==6.11.0
bcrypt==4.1.1
python-multipart==0.0.6
apscheduler==3.10.4
```

```bash
pip install -r requirements.txt
```

Tasks:

- [ ] Create `backend/` folder
- [ ] Create Python virtual environment
- [ ] Create `requirements.txt` with all dependencies
- [ ] Run `pip install -r requirements.txt`

---

### 3️⃣ Create Database Schema (30 min)

Create `backend/database.py` with SQLite tables:

- users (email, password_hash, name, grade)
- students (student_id, engagement_stats)
- conversations (student_id, subject, messages)
- goals (student_id, subject, progress, status)
- quiz_results (student_id, quiz_id, score, questions, answers)
- nudge_logs (student_id, nudge_type, status)

Tasks:

- [ ] Create `backend/database.py` with SQLAlchemy models
- [ ] Run script to create database
- [ ] Verify: `app.db` file created in `backend/` folder

---

### 4️⃣ Create Configuration Files (15 min)

**backend/.env**:

```
OPENAI_API_KEY=your_openai_key
SENDGRID_API_KEY=your_sendgrid_key
DATABASE_URL=sqlite:///./app.db
JWT_SECRET=your_jwt_secret
```

**frontend/.env.local**:

```
VITE_API_BASE_URL=http://localhost:8000
```

**.gitignore** (root):

```
node_modules/
__pycache__/
.env
.env.local
venv/
app.db
```

Tasks:

- [ ] Create `backend/.env` with API keys
- [ ] Create `frontend/.env.local` with API URL
- [ ] Create `.gitignore` at project root

---

### 5️⃣ Initialize Git (10 min)

```bash
cd /Users/ankit/Desktop/GauntletAI/StudyCompanion
git init
git add .
git commit -m "docs: Initial PRD and project structure"
```

Tasks:

- [ ] Run `git init`
- [ ] Run `git add .`
- [ ] Run `git commit`
- [ ] Test: `git log` should show initial commit

---

### 6️⃣ Create Basic Backend Server (10 min)

**backend/main.py**:

Create FastAPI app with:

- CORS middleware enabled
- `/health` endpoint for testing
- Connection to SQLite database
- Ready for API routes

```bash
python backend/main.py
```

Test: http://localhost:8000/health

Tasks:

- [ ] Create `backend/main.py` with FastAPI app
- [ ] Run uvicorn server
- [ ] Test `/health` endpoint returns 200

---

## 🎯 SUCCESS CRITERIA

By end of Phase 0:

✅ Frontend running on `http://localhost:5173`
✅ Backend running on `http://localhost:8000`
✅ `/health` endpoint responds
✅ SQLite database created (`app.db`)
✅ 6 database tables created
✅ Environment variables configured
✅ `.gitignore` created
✅ Git repository initialized
✅ Project folder structure complete

---

## ⏱️ TIME TRACKING

- Frontend setup: 30 min
- Backend setup: 30 min
- Database schema: 30 min
- Configuration: 15 min
- Git setup: 10 min
- Basic server: 10 min
- **Total**: ~2 hours

---

## 📋 FOLDER STRUCTURE

After Phase 0, you should have:

```
StudyCompanion/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── venv/
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── schemas/
│   ├── main.py
│   ├── database.py
│   ├── requirements.txt
│   └── .env
├── data/
├── AI Docs/
│   ├── PRD.md
│   ├── TaskList.md
│   └── README.md
├── .env
├── .env.local
├── .gitignore
└── README.md
```

---

## 🚀 NEXT STEPS

When Phase 0 is complete:

1. Mark Phase 0 as COMPLETED in TODO
2. Commit: `git commit -m "Phase 0: Setup & Planning complete"`
3. Start Phase 1: Mock Data Creation

---

**Ready? Let's go! 💪**
