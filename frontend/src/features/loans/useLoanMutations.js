import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createLoan, updateLoan, deleteLoan } from "../../api/loans";
import { useAxios } from "../../hooks/useAxios";

export const useCreateLoan = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (newLoan) => createLoan(apiClient, newLoan),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["loans"] });
    },
    onError: (error) => {
      console.error("Error creating loan:", error);
    },
  });
};

export const useUpdateLoan = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ loanId, data }) => updateLoan(apiClient, loanId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["loans"] });
    },
    onError: (error) => {
      console.error("Error updating loan:", error);
    },
  });
};

export const useDeleteLoan = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (loanId) => deleteLoan(apiClient, loanId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["loans"] });
    },
    onError: (error) => {
      console.error("Error deleting loan:", error);
    },
  });
};
