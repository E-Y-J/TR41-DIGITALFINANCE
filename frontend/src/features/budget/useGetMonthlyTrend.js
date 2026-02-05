import { useQuery } from "@tanstack/react-query";
import { getMonthlyTrend } from "../../api/transactions";
import { useAxios } from "../../hooks/useAxios";

export const useGetMonthlyTrend = (params = {}, options = {}) => {
  const apiClient = useAxios();

  return useQuery({
    queryKey: ["monthlyTrend", params],
    queryFn: () => getMonthlyTrend(apiClient, params),
    ...options,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    refetchOnWindowFocus: false,
    placeholderData: (previousData) => previousData,
  });
};
