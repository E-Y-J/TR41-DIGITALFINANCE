export const getTransactions = async (apiClient, params = {}) => {
  const data = await apiClient.get("/transactions", {
    params: params,
  });
  return data;
};

export const createTransaction = async (apiClient, transactionData) => {
  const data = await apiClient.post("/transactions", transactionData);
  return data;
};

export const updateTransaction = async (apiClient, transactionId, transactionData) => {
  const data = await apiClient.put(`/transactions/${transactionId}`, transactionData);
  return data;
};

export const deleteTransaction = async (apiClient, transactionId) => {
  const data = await apiClient.delete(`/transactions/${transactionId}`);
  return data;
};

export const getSummary = async (apiClient, params = {}) => {
  const data = await apiClient.get("/transactions/summary", {
    params: params,
  });
  return data;
};

export const getMonthlyTrend = async (apiClient, params = {}) => {
  const data = await apiClient.get("/transactions/trend", {
    params: params,
  });
  return data;
};

export const getSuggestions = async (apiClient, months = 3) => {
  const data = await apiClient.get("/budgets/suggestions", {
    params: { months },
  });
  return data;
};
