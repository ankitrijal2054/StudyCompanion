/**
 * API service for communicating with backend
 */
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Generic API call function
 * @param {string} endpoint - API endpoint path
 * @param {string} method - HTTP method (GET, POST, etc.)
 * @param {Object} body - Request body (optional)
 * @returns {Promise} Response from API
 */
export async function apiCall(endpoint, method = "GET", body = null) {
  try {
    const options = {
      method: method,
      headers: {
        "Content-Type": "application/json",
      },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `API Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API call error:", error);
    throw error;
  }
}

/**
 * Send a chat message to the AI
 * @param {string} studentId - Student ID
 * @param {string} message - User message
 * @param {Array} history - Optional conversation history
 * @returns {Promise} Response from API
 */
export async function sendChatMessage(studentId, message, history = []) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        student_id: studentId,
        message: message,
        history: history,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to send message");
    }

    return await response.json();
  } catch (error) {
    console.error("Chat API error:", error);
    throw error;
  }
}
