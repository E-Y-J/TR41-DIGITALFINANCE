import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateBudget } from "../../api/budgets";
import { useAxios } from "../../hooks/useAxios";

export const useUpdateBudget = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ budgetId, data }) => updateBudget(apiClient, budgetId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
    },
    onError: (error) => {
      console.error("Error updating budget:", error);
    },
  });
};
