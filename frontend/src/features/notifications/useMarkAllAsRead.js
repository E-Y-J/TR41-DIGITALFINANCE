import { useMutation, useQueryClient } from "@tanstack/react-query";
import { markAllAsRead } from "../../api/notifications";
import { useAxios } from "../../hooks/useAxios";

export const useMarkAllAsRead = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => markAllAsRead(apiClient),
    onSuccess: () => {
      // Invalidate notifications queries to refresh the list and count
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
};
