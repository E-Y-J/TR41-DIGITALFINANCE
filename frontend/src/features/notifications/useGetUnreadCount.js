import { useQuery } from "@tanstack/react-query";
import { getUnreadCount } from "../../api/notifications";
import { useAxios } from "../../hooks/useAxios";

export const useGetUnreadCount = () => {
  const apiClient = useAxios();

  return useQuery({
    queryKey: ["notifications", "unread-count"],
    queryFn: () => getUnreadCount(apiClient),
    refetchOnWindowFocus: false,
    // Refetch every 30 seconds to keep badge current
    refetchInterval: 30000,
    select: (response) => {
      return response.data?.data?.unread_count ?? 0;
    },
  });
};
