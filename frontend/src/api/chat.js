export const sendChatMessage = async (apiClient, { message, context = {} }) => {
  const data = await apiClient.post("/v1/ai/chat", {
    message,
    context,
  });
  return data;
};
