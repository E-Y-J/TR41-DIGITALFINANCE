import { useQuery } from "@tanstack/react-query";
import { getNotifications } from "../../api/notifications";
import { useAxios } from "../../hooks/useAxios";

export const useGetNotifications = (params = {}) => {
  const apiClient = useAxios();

  return useQuery({
    queryKey: ["notifications", params],
    queryFn: () => getNotifications(apiClient, params),
    refetchOnWindowFocus: false,
    // Refetch every 30 seconds to keep notifications fresh
    refetchInterval: 30000,
    select: (response) => {
      const serverData = response.data;

      if (!serverData || !serverData.data) {
        return { items: [], total: 0 };
      }

      return {
        items: serverData.data,
        total: serverData.meta?.total ?? serverData.data.length,
        meta: serverData.meta,
      };
    },
    placeholderData: (previousData) => previousData,
  });
};
