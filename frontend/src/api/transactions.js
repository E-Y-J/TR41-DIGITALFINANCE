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
