import { useState, useRef, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { sendChatMessage } from "../services/api";
import {
  MessageCircle,
  Send,
  Loader2,
  AlertCircle,
  BookOpen,
  Sparkles,
} from "lucide-react";

export default function Chat() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const studentId = searchParams.get("student_id") || "S001";
  const subject = searchParams.get("subject") || "General";

  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: "user",
      content: inputMessage.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);
    setError(null);

    try {
      const history = messages.slice(-10).map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await sendChatMessage(
        studentId,
        userMessage.content,
        history
      );

      const aiMessage = {
        role: "assistant",
        content: response.response,
        timestamp: new Date().toISOString(),
        confidence_score: response.confidence_score,
        should_handoff: response.should_handoff,
        handoff_message: response.handoff_message,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      setError(err.message || "Failed to get response. Please try again.");
      const errorMessage = {
        role: "assistant",
        content:
          "I'm sorry, I'm having trouble right now. Please try again in a moment.",
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleBookSession = () => {
    navigate(`/book-tutor?student_id=${studentId}&subject=${subject}`);
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white">
        <div className="px-6 py-4 max-w-5xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-indigo-600 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">
                  AI Study Companion
                </h1>
                <p className="text-xs text-gray-500">
                  {studentId} • {subject}
                </p>
              </div>
            </div>
            <button
              onClick={handleBookSession}
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 transition-colors font-medium text-sm border border-indigo-200"
            >
              <BookOpen size={16} />
              Book Tutor
            </button>
          </div>
        </div>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-6 py-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full py-20 text-center">
              <div className="w-16 h-16 rounded-2xl bg-indigo-50 flex items-center justify-center mb-4">
                <MessageCircle className="w-8 h-8 text-indigo-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Welcome to your study session
              </h2>
              <p className="text-gray-600 max-w-md">
                Ask me anything about your studies! I remember your learning
                history and will guide you with thoughtful questions.
              </p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-2xl rounded-2xl px-5 py-3 text-left ${
                  message.role === "user"
                    ? "bg-indigo-600 text-white"
                    : message.isError
                    ? "bg-red-50 text-red-800 border border-red-200"
                    : "bg-gray-50 text-gray-900 border border-gray-200"
                }`}
              >
                <p className="whitespace-pre-wrap text-sm leading-relaxed">
                  {message.content}
                </p>

                {message.should_handoff && message.handoff_message && (
                  <button
                    onClick={handleBookSession}
                    className="mt-3 w-full px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 transition-colors font-medium"
                  >
                    Book a Session
                  </button>
                )}

                <p
                  className={`text-xs mt-2 ${
                    message.role === "user"
                      ? "text-indigo-100"
                      : "text-gray-500"
                  }`}
                >
                  {new Date(message.timestamp).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-50 border border-gray-200 rounded-2xl px-5 py-3 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
                <span className="text-sm text-gray-600">Thinking...</span>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <span className="text-red-800 text-sm">{error}</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <footer className="border-t border-gray-100 bg-white">
        <div className="px-6 py-4 max-w-4xl mx-auto">
          <div className="flex items-end gap-3">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question or describe what you're working on..."
              className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              rows={1}
              disabled={isLoading}
              style={{ maxHeight: "120px" }}
            />
            <button
              onClick={handleSend}
              disabled={!inputMessage.trim() || isLoading}
              className="px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2 font-medium text-sm flex-shrink-0"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <Send size={16} />
                  Send
                </>
              )}
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}
