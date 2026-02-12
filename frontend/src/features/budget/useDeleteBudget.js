import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteBudget } from "../../api/budgets";
import { useAxios } from "../../hooks/useAxios";

export const useDeleteBudget = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (budgetId) => deleteBudget(apiClient, budgetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
    },
    onError: (error) => {
      console.error("Error deleting budget:", error);
    },
  });
};
