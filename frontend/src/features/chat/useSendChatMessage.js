import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sendChatMessage } from "../../api/chat";
import { useAxios } from "../../hooks/useAxios";

export const useSendChatMessage = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ message, session_id = null, context = {} }) => {
      const res = await sendChatMessage(apiClient, { message, session_id, context });
      return res;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chat-history"] });
    },
  });
};
