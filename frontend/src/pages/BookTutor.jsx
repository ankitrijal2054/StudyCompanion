import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Calendar, Clock, User, CheckCircle, ArrowLeft } from "lucide-react";

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

  // Filter tutors by subject
  const availableTutors = mockTutors.filter(
    (tutor) => tutor.subject === subject || tutor.subject === "General"
  );

  useEffect(() => {
    // Pre-fill student name (in real app, fetch from API)
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

    // Log booking (mock implementation)
    console.log("Booking Details:", {
      studentId,
      ...formData,
      bookedAt: new Date().toISOString(),
    });

    // Show success message
    setSubmitted(true);

    // In production, this would call an API endpoint
    setTimeout(() => {
      // Navigate back to chat after 2 seconds
      navigate(`/chat?student_id=${studentId}&subject=${subject}`);
    }, 2000);
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Booking Confirmed! 🎉
          </h2>
          <p className="text-gray-600 mb-6">
            Your session with {formData.selectedTutor?.name} has been scheduled.
          </p>
          <p className="text-sm text-gray-500">
            Redirecting you back to chat...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() =>
              navigate(`/chat?student_id=${studentId}&subject=${subject}`)
            }
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft size={20} />
            Back to Chat
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            Book a Tutoring Session
          </h1>
          <p className="text-gray-600 mt-2">
            Schedule a one-on-one session with an expert tutor
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Student Info */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
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
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
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
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>
            </div>
          </div>

          {/* Topic Description */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
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
                  placeholder="e.g., Ionic bonding, Quadratic equations, etc."
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description (optional)
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }))
                  }
                  placeholder="Describe what you'd like help with..."
                  rows={4}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>

          {/* Available Tutors */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Available Tutors
            </h2>
            <div className="space-y-4">
              {availableTutors.map((tutor) => (
                <div
                  key={tutor.id}
                  className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                    formData.selectedTutor?.id === tutor.id
                      ? "border-indigo-600 bg-indigo-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() =>
                    setFormData((prev) => ({ ...prev, selectedTutor: tutor }))
                  }
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
                        <User className="w-6 h-6 text-indigo-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {tutor.name}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {tutor.subject} • {tutor.experience}
                        </p>
                        <div className="flex items-center gap-1 mt-1">
                          <span className="text-yellow-500">★</span>
                          <span className="text-sm text-gray-700">
                            {tutor.rating}
                          </span>
                        </div>
                      </div>
                    </div>
                    {formData.selectedTutor?.id === tutor.id && (
                      <CheckCircle className="w-6 h-6 text-indigo-600" />
                    )}
                  </div>

                  {formData.selectedTutor?.id === tutor.id && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <p className="text-sm font-medium text-gray-700 mb-2">
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
                            className={`px-3 py-1 rounded-lg text-sm border transition-colors ${
                              formData.selectedTime === time
                                ? "bg-indigo-600 text-white border-indigo-600"
                                : "bg-white text-gray-700 border-gray-300 hover:border-indigo-300"
                            }`}
                          >
                            <Clock size={14} className="inline mr-1" />
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

          {/* Submit Button */}
          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={() =>
                navigate(`/chat?student_id=${studentId}&subject=${subject}`)
              }
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!formData.selectedTutor || !formData.selectedTime}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <Calendar size={18} />
              Confirm Booking
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
