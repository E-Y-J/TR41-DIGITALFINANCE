export const getLoans = async (apiClient, params = {}) => {
  const data = await apiClient.get("/loans", {
    params: params,
  });
  return data;
};
