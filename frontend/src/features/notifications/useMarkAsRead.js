import { useMutation, useQueryClient } from "@tanstack/react-query";
import { markAsRead } from "../../api/notifications";
import { useAxios } from "../../hooks/useAxios";

export const useMarkAsRead = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificationId) => markAsRead(apiClient, notificationId),
    onSuccess: () => {
      // Invalidate notifications queries to refresh the list
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
};
