export const getTransactions = async (apiClient, params = {}) => {
  const data = await apiClient.get("/transactions", {
    params: params,
  });
  console.log("Fetched transactions:", data);
  return data;
};
