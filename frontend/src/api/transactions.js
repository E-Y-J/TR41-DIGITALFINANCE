export const getTransactions = async (apiClient, params = {}) => {
  const data = await apiClient.get("/transactions", {
    params: params,
  });
  return data;
};
