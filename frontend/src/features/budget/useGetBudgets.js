import { useQuery } from "@tanstack/react-query";
import { getBudgets } from "../../api/budgets";
import { useAxios } from "../../hooks/useAxios";

export const useGetBudgets = (params = {}) => {
  const apiClient = useAxios();

  return useQuery({
    queryKey: ["budgets", params],
    queryFn: () => getBudgets(apiClient, params),
    refetchOnWindowFocus: false,
    select: (response) => {
      const serverData = response.data;

      if (!serverData || !serverData.data) {
        return { items: [], meta: {} };
      }

      return {
        items: serverData.data,
        meta: serverData.meta || {},
      };
    },
    placeholderData: (previousData) => previousData,
  });
};
