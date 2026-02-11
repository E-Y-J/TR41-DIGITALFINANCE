/**
 * Budget API functions
 * Endpoints for budget management
 */

export const getBudgets = async (apiClient, params = {}) => {
  const data = await apiClient.get("/budgets", { params });
  return data;
};

export const getBudget = async (apiClient, budgetId) => {
  const data = await apiClient.get(`/budgets/${budgetId}`);
  return data;
};

export const createBudget = async (apiClient, budgetData) => {
  const data = await apiClient.post("/budgets", budgetData);
  return data;
};

export const updateBudget = async (apiClient, budgetId, budgetData) => {
  const data = await apiClient.put(`/budgets/${budgetId}`, budgetData);
  return data;
};

export const deleteBudget = async (apiClient, budgetId) => {
  const data = await apiClient.delete(`/budgets/${budgetId}`);
  return data;
};

export const getBudgetStatus = async (apiClient) => {
  const data = await apiClient.get("/budgets/status");
  return data;
};

export const getBudgetSuggestions = async (apiClient) => {
  const data = await apiClient.get("/budgets/suggestions");
  return data;
};
