import { Routes, Route, Navigate } from "react-router-dom";
import Chat from "./pages/Chat";
import BookTutor from "./pages/BookTutor";
import "./App.css";

function App() {
  return (
    <Routes>
      <Route path="/chat" element={<Chat />} />
      <Route path="/book-tutor" element={<BookTutor />} />
      <Route
        path="/"
        element={
          <Navigate to="/chat?student_id=S001&subject=General" replace />
        }
      />
    </Routes>
  );
}

export default App;
