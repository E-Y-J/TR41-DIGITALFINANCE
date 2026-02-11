export const getUser = async (client) => {
  const { data } = await client.post("/auth/callback");
  return data;
};

export const updateUser = async (client, userData) => {
  const { data } = await client.patch("/users/me", userData);
  return data;
};

export const chatHistory = async (client, params = {}) => {
  const { data } = await client.get("/v1/ai/chat/history", {
    params: {
      include_inactive: true,
      ...params,
    },
  });
  return data;
};

export const sendChatMessage = async (
  client,
  message,
  { sessionId = null, ...context } = {},
) => {
  const { data } = await client.post("/v1/ai/chat", {
    message,
    context,
    session_id: sessionId,
  });
  return data;
};
