import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteTransaction } from "../../api/transactions";
import { useAxios } from "../../hooks/useAxios";

export const useDeleteTransaction = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (transactionId) => deleteTransaction(apiClient, transactionId),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },

    onError: (error) => {
      console.error("Error deleting transaction:", error);
    },
  });
};
