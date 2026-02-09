export const getCategories = async (apiClient, params = {}) => {
  const data = await apiClient.get("/categories", {
    params: params,
  });
  return data;
};
