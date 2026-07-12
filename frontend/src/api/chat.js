import { apiClient } from "./client";

export async function askQuestion({ sessionId, question }) {
  const { data } = await apiClient.post("/chat/ask", {
    session_id: sessionId || null,
    question,
  });
  return data;
}

export async function getSessionMessages(sessionId) {
  const { data } = await apiClient.get(`/chat/sessions/${sessionId}/messages`);
  return data;
}
