import { useSearchParams, useNavigate } from "react-router-dom";
import "./Navigation.css";

const Navigation = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const studentId = searchParams.get("student_id") || "S001";

  return (
    <nav className="navigation-bar">
      <div className="nav-container">
        <button
          className="nav-brand"
          onClick={() => navigate(`/dashboard?student_id=${studentId}`)}
          title="Go to Dashboard"
        >
          <div className="brand-icon">🎓</div>
          <span className="brand-text">Study Companion</span>
        </button>
      </div>
    </nav>
  );
};

export default Navigation;
