export const getTransactions = async (apiClient, params = {}) => {
  const data = await apiClient.get("/api/transactions", {
    params: params,
  });
  return data;
};
