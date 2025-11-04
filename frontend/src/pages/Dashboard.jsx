import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { apiCall } from "../services/api";
import Navigation from "../components/Navigation";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import {
  Flame,
  Target,
  TrendingUp,
  Award,
  Clock,
  BookOpen,
  ChevronRight,
  Loader2,
  MessageSquare,
  Zap,
} from "lucide-react";
import "./Dashboard.css";

const Dashboard = () => {
  const [searchParams] = useSearchParams();
  const studentId = searchParams.get("student_id") || "S001";
  const navigate = useNavigate();

  const [stats, setStats] = useState(null);
  const [goals, setGoals] = useState(null);
  const [quizHistory, setQuizHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  // Track window width for responsive design
  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch stats, goals, and quiz history in parallel
        const [statsRes, goalsRes, quizRes] = await Promise.all([
          apiCall(`/dashboard/student/${studentId}/stats`, "GET"),
          apiCall(`/dashboard/student/${studentId}/goals`, "GET"),
          apiCall(`/dashboard/student/${studentId}/quiz-history`, "GET"),
        ]);

        setStats(statsRes);
        setGoals(goalsRes);
        setQuizHistory(quizRes);
      } catch (err) {
        console.error("Error fetching dashboard data:", err);
        setError(err.message || "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();

    // Refresh data every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, [studentId]);

  if (loading) {
    return (
      <div className="dashboard-loading">
        <Loader2 className="spinner" />
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <p className="error-message">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="retry-button"
        >
          Retry
        </button>
      </div>
    );
  }

  // Calculate responsive chart height
  const getChartHeight = () => {
    if (windowWidth < 480) return 250;
    if (windowWidth < 768) return 280;
    return 300;
  };

  const chartData =
    quizHistory?.quiz_history
      ?.slice()
      .reverse()
      .map((q) => ({
        date: new Date(q.created_at).toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        }),
        score: q.score_percent,
        subject: q.subject,
      })) || [];

  const activeGoals = goals?.active_goals || [];
  const completedGoals = goals?.completed_goals || [];

  return (
    <div className="dashboard-container">
      {/* Header Section */}
      <div className="dashboard-header">
        <div className="header-content">
          <h1 className="dashboard-title">Hi there! 👋</h1>
          <p className="dashboard-subtitle">
            Your learning progress is looking great. Keep up the momentum!
          </p>
        </div>
      </div>
      {/* Quick Actions */}
      <div className="quick-actions">
        <button
          className="quick-action-btn chat-btn"
          onClick={() => navigate(`/chat?student_id=${studentId}`)}
        >
          <MessageSquare className="action-icon" />
          <span>Start Chat</span>
        </button>
        <button
          className="quick-action-btn quiz-btn"
          onClick={() => navigate(`/quiz/General?student_id=${studentId}`)}
        >
          <Zap className="action-icon" />
          <span>Take a Quiz</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <StatCard
          icon={<Flame className="stat-icon flame" />}
          label="Session Streak"
          value={stats?.session_streak || 0}
          unit="sessions"
          trend="+2 this week"
          trendPositive={true}
        />
        <StatCard
          icon={<Target className="stat-icon target" />}
          label="Goals Progress"
          value={stats?.goals_progress_percent || 0}
          unit="%"
          trend="3 active goals"
          trendPositive={true}
        />
        <StatCard
          icon={<TrendingUp className="stat-icon trending" />}
          label="Quiz Average"
          value={stats?.avg_quiz_score || 0}
          unit="%"
          trend={`${stats?.total_quizzes || 0} quizzes taken`}
          trendPositive={true}
        />
        <StatCard
          icon={<Award className="stat-icon award" />}
          label="Achievements"
          value={stats?.completed_goals || 0}
          unit="completed"
          trend="Keep learning!"
          trendPositive={true}
        />
      </div>

      {/* Goals and Chart Section */}
      <div className="dashboard-grid">
        {/* Active Goals */}
        <div className="goals-section">
          <h2 className="section-title">
            <BookOpen className="section-icon" />
            Active Learning Goals
          </h2>
          {activeGoals.length > 0 ? (
            <div className="goals-list">
              {activeGoals.map((goal) => (
                <GoalCard key={goal.goal_id} goal={goal} />
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>No active goals yet. Start a new learning journey!</p>
            </div>
          )}
        </div>

        {/* Quiz Performance Chart */}
        <div className="chart-section">
          <h2 className="section-title">
            <TrendingUp className="section-icon" />
            Quiz Performance
          </h2>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={getChartHeight()}>
              <LineChart
                data={chartData}
                margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis dataKey="date" stroke="#666" />
                <YAxis domain={[0, 100]} stroke="#666" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#fff",
                    border: "1px solid #ddd",
                    borderRadius: "8px",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#6366f1"
                  strokeWidth={2}
                  dot={{ fill: "#6366f1", r: 4 }}
                  activeDot={{ r: 6 }}
                  name="Score %"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state">
              <p>No quiz data yet. Complete a quiz to see your performance!</p>
            </div>
          )}
        </div>
      </div>

      {/* Completed Goals */}
      {completedGoals.length > 0 && (
        <div className="completed-section">
          <h2 className="section-title">
            <Award className="section-icon" />
            Completed Goals 🎉
          </h2>
          <div className="completed-goals-grid">
            {completedGoals.map((goal) => (
              <div key={goal.goal_id} className="completed-goal-card">
                <div className="completed-badge">✓ Completed</div>
                <h3 className="goal-subject">{goal.subject}</h3>
                <p className="goal-description">{goal.description}</p>
                {goal.completed_at && (
                  <p className="completed-date">
                    on {new Date(goal.completed_at).toLocaleDateString()}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Activity Feed */}
      <div className="activity-section">
        <h2 className="section-title">
          <Clock className="section-icon" />
          Recent Activity
        </h2>
        {quizHistory?.quiz_history && quizHistory.quiz_history.length > 0 ? (
          <div className="activity-feed">
            {quizHistory.quiz_history.slice(0, 5).map((quiz) => (
              <div key={quiz.quiz_id} className="activity-item">
                <div className="activity-icon">📝</div>
                <div className="activity-content">
                  <p className="activity-title">
                    Completed <strong>{quiz.subject}</strong> quiz
                  </p>
                  <p className="activity-subtitle">
                    Scored <strong>{quiz.score_percent}%</strong> •{" "}
                    {new Date(quiz.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div
                  className={`score-badge ${
                    quiz.score_percent >= 80 ? "excellent" : "good"
                  }`}
                >
                  {quiz.score_percent}%
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>No recent activity. Start a quiz to see your progress here!</p>
          </div>
        )}
      </div>
    </div>
  );
};

// StatCard Component
const StatCard = ({ icon, label, value, unit, trend, trendPositive }) => (
  <div className="stat-card">
    <div className="stat-header">
      <div className="stat-icon-container">{icon}</div>
      <p className="stat-label">{label}</p>
    </div>
    <div className="stat-value">
      <span className="value">{value}</span>
      <span className="unit">{unit}</span>
    </div>
    <p className={`stat-trend ${trendPositive ? "positive" : "neutral"}`}>
      {trend}
    </p>
  </div>
);

// GoalCard Component
const GoalCard = ({ goal }) => {
  const progressPercentage = Math.min(goal.progress_percent, 100);

  return (
    <div className="goal-card">
      <div className="goal-header">
        <h3 className="goal-subject">{goal.subject}</h3>
        <span className="goal-status">{goal.status}</span>
      </div>
      <p className="goal-description">{goal.description}</p>

      {/* Progress Bar */}
      <div className="progress-section">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
        <p className="progress-text">
          {progressPercentage.toFixed(0)}% Complete
        </p>
      </div>

      {/* Days Remaining */}
      <div className="goal-footer">
        <p className="days-remaining">
          <Clock className="clock-icon" />
          {goal.days_remaining} days remaining
        </p>
        <button
          className="continue-button"
          onClick={() =>
            navigate(
              `/chat?student_id=${goal.student_id || studentId}&subject=${
                goal.subject
              }`
            )
          }
        >
          Continue Learning
          <ChevronRight className="button-icon" />
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
