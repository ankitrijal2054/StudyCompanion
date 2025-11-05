import { Routes, Route, Navigate } from "react-router-dom";
import Navigation from "./components/Navigation";
import Chat from "./pages/Chat";
import BookTutor from "./pages/BookTutor";
import Quiz from "./pages/Quiz";
import Dashboard from "./pages/Dashboard";
import "./App.css";

function App() {
  return (
    <>
      <Navigation />
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/book-tutor" element={<BookTutor />} />
        <Route path="/quiz/:subject" element={<Quiz />} />
        <Route path="/quiz/:subject/:quizId" element={<Quiz />} />
        <Route
          path="/"
          element={<Navigate to="/dashboard?student_id=S001" replace />}
        />
      </Routes>
    </>
  );
}

export default App;
