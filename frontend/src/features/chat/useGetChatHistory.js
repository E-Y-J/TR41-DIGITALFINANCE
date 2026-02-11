import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { chatHistory, deleteChatSession } from "../../api/user";
import { useAxios } from "../../hooks/useAxios";

export const useGetChatHistory = (params = {}) => {
  const apiClient = useAxios();

  return useQuery({
    queryKey: ["chatHistory", params],
    queryFn: () => chatHistory(apiClient, params),
    refetchOnWindowFocus: false,
    select: (response) => {
      const serverData = response.data;

      if (!serverData) {
        return [];
      }

      return serverData;
    },
    placeholderData: (previousData) => previousData,
  });
};

export const useDeleteChatSession = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId) => deleteChatSession(apiClient, sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chatHistory"] });
    },
  });
};
