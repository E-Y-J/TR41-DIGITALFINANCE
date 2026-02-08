import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createTransaction } from "../../api/transactions";
import { useAxios } from "../../hooks/useAxios";

export const useCreateTransaction = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (newTransaction) =>
      createTransaction(apiClient, newTransaction),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
    },

    onError: (error) => {
      console.error("Error creating transaction:", error);
    },
  });
};
