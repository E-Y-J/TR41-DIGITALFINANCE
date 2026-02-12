import { useQuery } from "@tanstack/react-query";
import { getLoans } from "../../api/loans";
import { useAxios } from "../../hooks/useAxios";

export const useGetLoans = (params = {}) => {
  const apiClient = useAxios();

  return useQuery({
    queryKey: ["loans", params],
    queryFn: () => getLoans(apiClient, params),
    refetchOnWindowFocus: false,
    select: (response) => {
      const serverData = response?.data.data;
      if (serverData.items && Array.isArray(serverData.items)) {
        return {
          items: serverData.items || [],
          totalPages: serverData.pages || 1,
        };
      }

      if (Array.isArray(serverData)) {
        return {
          items: serverData,
          totalPages: 1,
        };
      }

      return { items: [], totalPages: 1 };
    },
    placeholderData: (previousData) => previousData,
  });
};
