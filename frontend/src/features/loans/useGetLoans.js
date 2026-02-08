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
      const serverData = response?.data;

      if (!serverData?.data) {
        return { items: [], total: 0 };
      }

      const totalCount =
        serverData.meta?.total ??
        serverData.total ??
        serverData.count ??
        serverData.data.length;

      return {
        items: serverData.data,
        total: totalCount,
      };
    },
    placeholderData: (previousData) => previousData,
  });
};
