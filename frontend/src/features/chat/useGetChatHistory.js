import { useQuery } from "@tanstack/react-query";
import { chatHistory } from "../../api/user";
import { useAxios } from "../../hooks/useAxios";

export const useGetChatHistory = () => {
  const apiClient = useAxios();

  return useQuery({
    queryKey: ["chatHistory"],
    queryFn: () => chatHistory(apiClient),
    refetchOnWindowFocus: false,
    select: (response) => {
      const serverData = response.data;
      console.log("Raw Chat History Response:", serverData);

      if (!serverData) {
        return [];
      }

      return serverData;
    },
    placeholderData: (previousData) => previousData,
  });
};
