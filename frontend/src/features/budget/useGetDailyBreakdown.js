import { useQuery } from "@tanstack/react-query";
import { getSummary } from "../../api/transactions";
import { useAxios } from "../../hooks/useAxios";

export const useGetDailyBreakdown = (params = {}, options = {}) => {
  const apiClient = useAxios();

  return useQuery({
    queryKey: ["transactions", params],
    queryFn: () => getSummary(apiClient, params),
    ...options,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    refetchOnWindowFocus: false,
    placeholderData: (previousData) => previousData,
  });
};
