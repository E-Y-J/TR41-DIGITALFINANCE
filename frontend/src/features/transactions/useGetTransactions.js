import { useQuery } from "@tanstack/react-query";
import { getTransactions } from "../../api/transactions";
import { useAxios } from "../../hooks/useAxios";

export const useGetTransactions = (params = {}) => {
  const apiClient = useAxios();
  return useQuery({
    queryKey: ["transactions", params],
    queryFn: getTransactions(apiClient, params),
  });
};
