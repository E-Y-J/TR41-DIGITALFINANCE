export const sendChatMessage = async (apiClient, { message, session_id = null, context = {} }) => {
  const data = await apiClient.post("/v1/ai/chat", {
    message,
    context,
    session_id,
  });
  return data;
};
