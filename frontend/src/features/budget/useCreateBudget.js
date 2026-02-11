import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createBudget } from "../../api/budgets";
import { useAxios } from "../../hooks/useAxios";

export const useCreateBudget = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => createBudget(apiClient, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
    },
    onError: (error) => {
      console.error("Error creating budget:", error);
    },
  });
};
