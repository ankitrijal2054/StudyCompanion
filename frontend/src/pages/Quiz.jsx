import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { apiCall } from "../services/api";
import "./Quiz.css";

const Quiz = () => {
  const { quizId, subject } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const studentId = searchParams.get("student_id") || "S001";

  const [quiz, setQuiz] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [submitted, setSubmitted] = useState(false);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCelebration, setShowCelebration] = useState(false);

  // Load quiz
  useEffect(() => {
    const loadQuiz = async () => {
      try {
        setLoading(true);

        // Validate required parameters
        if (!studentId) {
          setError("Student ID is required");
          setLoading(false);
          return;
        }

        if (!subject) {
          setError("Subject is required");
          setLoading(false);
          return;
        }

        // In a real app, we'd fetch the quiz from /practice/{quizId}
        // For now, we'll generate a new one
        if (quizId === "new") {
          await generateNewQuiz();
        } else {
          // Fetch existing quiz from database
          const response = await apiCall("/practice", "POST", {
            student_id: studentId,
            subject: subject,
            num_questions: 5,
          });
          setQuiz(response);
          setAnswers(new Array(response.num_questions).fill(""));
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadQuiz();
  }, [quizId, subject, studentId]);

  const generateNewQuiz = async () => {
    try {
      const response = await apiCall("/practice", "POST", {
        student_id: studentId,
        subject: subject || "General",
        num_questions: 5,
      });
      setQuiz(response);
      setAnswers(new Array(response.num_questions).fill(""));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleAnswerSelect = (questionIndex, answer) => {
    const newAnswers = [...answers];
    newAnswers[questionIndex] = answer;
    setAnswers(newAnswers);
  };

  const handleNext = () => {
    if (currentQuestion < quiz.num_questions - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      // Filter out empty answers
      const validAnswers = answers.filter((a) => a !== "");

      if (validAnswers.length !== quiz.num_questions) {
        setError("Please answer all questions before submitting");
        setLoading(false);
        return;
      }

      const response = await apiCall(
        `/practice/${quiz.quiz_id}/submit`,
        "POST",
        {
          answers: answers,
        }
      );

      setResults(response);
      setSubmitted(true);

      // Show celebration if goal was completed
      if (response.goal_completed) {
        setShowCelebration(true);
        // Auto-trigger recommendations after celebration
        setTimeout(() => {
          navigate(`/recommendations?goalId=${response.goal_id}`);
        }, 3000);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !quiz) {
    return (
      <div className="quiz-container">
        <div className="loading">Loading quiz...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="quiz-container">
        <div className="error-message">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={() => navigate("/dashboard")}>
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!quiz) {
    return (
      <div className="quiz-container">
        <div className="error-message">
          <h2>Quiz not found</h2>
          <button onClick={() => navigate("/dashboard")}>
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (submitted && results) {
    return (
      <div className="quiz-container">
        {showCelebration && (
          <div className="celebration-overlay">
            <div className="celebration-content">
              <div className="celebration-emoji">🎉</div>
              <h1>{results.celebration_message}</h1>
              <p>Redirecting to personalized recommendations...</p>
            </div>
          </div>
        )}

        {!showCelebration && (
          <div className="results-container">
            <div className="results-header">
              <h1>Quiz Results</h1>
              <p className="subject-label">{quiz.subject}</p>
            </div>

            <div className="score-display">
              <div className="score-circle">
                <div className="score-number">
                  {results.score_percent.toFixed(0)}%
                </div>
              </div>
              <div className="score-details">
                <p className="score-correct">
                  {results.correct_count} out of {results.total_questions}{" "}
                  correct
                </p>
                <p className="score-feedback">{results.feedback}</p>
              </div>
            </div>

            <div className="results-actions">
              <button
                className="btn-primary"
                onClick={() => navigate("/dashboard")}
              >
                Back to Dashboard
              </button>
              <button className="btn-secondary" onClick={generateNewQuiz}>
                Try Another Quiz
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Quiz display
  const question = quiz.questions[currentQuestion];
  const isAnswered = answers[currentQuestion] !== "";

  return (
    <div className="quiz-container">
      <div className="quiz-header">
        <div className="quiz-info">
          <h1>{quiz.subject}</h1>
          <p className="difficulty-badge">{quiz.difficulty.toUpperCase()}</p>
        </div>
        <div className="progress-indicator">
          <span>
            Question {currentQuestion + 1} of {quiz.num_questions}
          </span>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{
                width: `${((currentQuestion + 1) / quiz.num_questions) * 100}%`,
              }}
            ></div>
          </div>
        </div>
      </div>

      <div className="quiz-content">
        <div className="question-container">
          <h2>{question.question_text}</h2>
          <p className="topic-label">Topic: {question.topic}</p>

          <div className="options-container">
            {question.options.map((option, index) => {
              const optionLetter = String.fromCharCode(65 + index); // A, B, C, D
              const isSelected = answers[currentQuestion] === optionLetter;

              return (
                <label
                  key={index}
                  className={`option ${isSelected ? "selected" : ""}`}
                >
                  <input
                    type="radio"
                    name="answer"
                    value={optionLetter}
                    checked={isSelected}
                    onChange={() =>
                      handleAnswerSelect(currentQuestion, optionLetter)
                    }
                  />
                  <span className="option-label">
                    <span className="option-letter">{optionLetter}</span>
                    <span className="option-text">{option}</span>
                  </span>
                </label>
              );
            })}
          </div>
        </div>

        <div className="quiz-navigation">
          <button
            className="btn-secondary"
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
          >
            ← Previous
          </button>

          <div className="question-counter">
            {answers.filter((a) => a !== "").length} / {quiz.num_questions}{" "}
            answered
          </div>

          {currentQuestion === quiz.num_questions - 1 ? (
            <button
              className="btn-primary"
              onClick={handleSubmit}
              disabled={!isAnswered}
            >
              Submit Quiz
            </button>
          ) : (
            <button
              className="btn-secondary"
              onClick={handleNext}
              disabled={!isAnswered}
            >
              Next →
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Quiz;
