import { useQuery } from "@tanstack/react-query";
import { getTransactions } from "../../api/transactions";
import { useAxios } from "../../hooks/useAxios";

export const useGetTransactions = (params = {}) => {
  const apiClient = useAxios();

  return useQuery({
    queryKey: ["transactions", params],
    queryFn: () => getTransactions(apiClient, params),
    select: (response) => {
      const serverData = response.data;
      if (serverData.data) {
        return {
          items: serverData.data,
          total: serverData.total || serverData.count || serverData.data.length,
        };
      }

      return { items: [], total: 0 };
    },
  });
};
