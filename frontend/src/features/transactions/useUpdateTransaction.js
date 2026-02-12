import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateTransaction } from "../../api/transactions";
import { useAxios } from "../../hooks/useAxios";

export const useUpdateTransaction = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ transactionId, data }) =>
      updateTransaction(apiClient, transactionId, data),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },

    onError: (error) => {
      console.error("Error updating transaction:", error);
    },
  });
};
