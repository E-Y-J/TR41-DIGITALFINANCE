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
