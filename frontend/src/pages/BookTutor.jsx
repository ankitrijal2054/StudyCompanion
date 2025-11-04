import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import {
  Calendar,
  Clock,
  User,
  CheckCircle,
  ArrowLeft,
  Sparkles,
} from "lucide-react";

export default function BookTutor() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const studentId = searchParams.get("student_id") || "S001";
  const subject = searchParams.get("subject") || "General";

  const [formData, setFormData] = useState({
    studentName: "",
    subject: subject,
    topic: "",
    description: "",
    selectedTutor: null,
    selectedTime: null,
  });

  const [submitted, setSubmitted] = useState(false);

  // Mock tutors list
  const mockTutors = [
    {
      id: 1,
      name: "Dr. Sarah Chen",
      subject: "Chemistry",
      rating: 4.9,
      experience: "8 years",
      availability: ["Today 2:00 PM", "Tomorrow 10:00 AM", "Tomorrow 3:00 PM"],
    },
    {
      id: 2,
      name: "Prof. Michael Rodriguez",
      subject: "Mathematics",
      rating: 4.8,
      experience: "12 years",
      availability: ["Today 4:00 PM", "Tomorrow 11:00 AM", "Tomorrow 5:00 PM"],
    },
    {
      id: 3,
      name: "Ms. Emily Johnson",
      subject: "Physics",
      rating: 4.9,
      experience: "6 years",
      availability: ["Today 3:00 PM", "Tomorrow 2:00 PM", "Tomorrow 4:00 PM"],
    },
    {
      id: 4,
      name: "Dr. James Wilson",
      subject: "General",
      rating: 4.7,
      experience: "10 years",
      availability: ["Today 5:00 PM", "Tomorrow 9:00 AM", "Tomorrow 1:00 PM"],
    },
  ];

  const availableTutors = mockTutors.filter(
    (tutor) => tutor.subject === subject || tutor.subject === "General"
  );

  useEffect(() => {
    const studentNames = {
      S001: "Ava Johnson",
      S002: "Marcus Lee",
      S003: "Priya Sharma",
      S004: "Jordan Taylor",
      S005: "Sofia Martinez",
    };
    setFormData((prev) => ({
      ...prev,
      studentName: studentNames[studentId] || "Student",
    }));
  }, [studentId]);

  const handleSubmit = (e) => {
    e.preventDefault();

    console.log("Booking Details:", {
      studentId,
      ...formData,
      bookedAt: new Date().toISOString(),
    });

    setSubmitted(true);

    setTimeout(() => {
      navigate(`/chat?student_id=${studentId}&subject=${subject}`);
    }, 2000);
  };

  if (submitted) {
    return (
      <div className="h-full bg-white flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="w-16 h-16 rounded-2xl bg-emerald-50 flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-emerald-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Booking Confirmed! 🎉
          </h2>
          <p className="text-gray-600 mb-2">
            Your session with{" "}
            <span className="font-semibold">
              {formData.selectedTutor?.name}
            </span>{" "}
            is scheduled.
          </p>
          <p className="text-sm text-gray-500">
            Redirecting you back to chat...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-gray-50 overflow-hidden">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white sticky top-0">
        <div className="px-6 py-4 max-w-5xl mx-auto">
          <button
            onClick={() =>
              navigate(`/chat?student_id=${studentId}&subject=${subject}`)
            }
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft size={18} />
            <span className="text-sm font-medium">Back to Chat</span>
          </button>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-indigo-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">
                Book a Tutoring Session
              </h1>
              <p className="text-xs text-gray-500">
                Connect with an expert tutor for personalized help
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto py-8 px-6 max-w-5xl mx-auto w-full">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Student Info */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Student Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Student Name
                </label>
                <input
                  type="text"
                  value={formData.studentName}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      studentName: e.target.value,
                    }))
                  }
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Subject
                </label>
                <input
                  type="text"
                  value={formData.subject}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      subject: e.target.value,
                    }))
                  }
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  required
                />
              </div>
            </div>
          </div>

          {/* Session Details */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Session Details
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Topic or Area of Focus
                </label>
                <input
                  type="text"
                  value={formData.topic}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, topic: e.target.value }))
                  }
                  placeholder="e.g., Ionic bonding, Quadratic equations..."
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Additional Notes (optional)
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }))
                  }
                  placeholder="Tell us more about what you need help with..."
                  rows={3}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                />
              </div>
            </div>
          </div>

          {/* Available Tutors */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Available Tutors
            </h2>
            <div className="space-y-3">
              {availableTutors.map((tutor) => (
                <div
                  key={tutor.id}
                  className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                    formData.selectedTutor?.id === tutor.id
                      ? "border-indigo-600 bg-indigo-50"
                      : "border-gray-200 hover:border-gray-300 bg-white"
                  }`}
                  onClick={() =>
                    setFormData((prev) => ({ ...prev, selectedTutor: tutor }))
                  }
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start gap-3">
                      <div className="w-11 h-11 rounded-lg bg-indigo-100 flex items-center justify-center flex-shrink-0">
                        <User className="w-5 h-5 text-indigo-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {tutor.name}
                        </h3>
                        <p className="text-xs text-gray-600 mt-0.5">
                          {tutor.subject} • {tutor.experience}
                        </p>
                        <div className="flex items-center gap-1 mt-1.5">
                          <span className="text-yellow-500 text-sm">★</span>
                          <span className="text-xs text-gray-700 font-medium">
                            {tutor.rating}
                          </span>
                        </div>
                      </div>
                    </div>
                    {formData.selectedTutor?.id === tutor.id && (
                      <CheckCircle className="w-5 h-5 text-indigo-600 flex-shrink-0" />
                    )}
                  </div>

                  {formData.selectedTutor?.id === tutor.id && (
                    <div className="mt-3 pt-3 border-t border-indigo-200">
                      <p className="text-xs font-medium text-gray-700 mb-2">
                        Available Times:
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {tutor.availability.map((time, idx) => (
                          <button
                            key={idx}
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              setFormData((prev) => ({
                                ...prev,
                                selectedTime: time,
                              }));
                            }}
                            className={`px-3 py-1.5 rounded-lg text-xs border transition-colors ${
                              formData.selectedTime === time
                                ? "bg-indigo-600 text-white border-indigo-600"
                                : "bg-white text-gray-700 border-gray-300 hover:border-indigo-300"
                            }`}
                          >
                            <Clock size={12} className="inline mr-1" />
                            {time}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() =>
                navigate(`/chat?student_id=${studentId}&subject=${subject}`)
              }
              className="px-6 py-2.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!formData.selectedTutor || !formData.selectedTime}
              className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium text-sm flex items-center gap-2"
            >
              <Calendar size={16} />
              Confirm Booking
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
