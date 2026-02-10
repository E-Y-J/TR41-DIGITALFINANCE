export const getLoans = async (apiClient, params = {}) => {
  const data = await apiClient.get("/loans", {
    params: params,
  });
  return data;
};

export const getLoan = async (apiClient, loanId) => {
  const data = await apiClient.get(`/loans/${loanId}`);
  return data;
};

export const createLoan = async (apiClient, loanData) => {
  const data = await apiClient.post("/loans", loanData);
  return data;
};

export const updateLoan = async (apiClient, loanId, loanData) => {
  const data = await apiClient.patch(`/loans/${loanId}`, loanData);
  return data;
};

export const deleteLoan = async (apiClient, loanId) => {
  const data = await apiClient.delete(`/loans/${loanId}`);
  return data;
};
