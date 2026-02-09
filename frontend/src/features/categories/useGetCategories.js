import { useQuery } from "@tanstack/react-query";
import { getCategories } from "../../api/categories";
import { useAxios } from "../../hooks/useAxios";

export const useGetCategories = (params = {}) => {
  const apiClient = useAxios();

  return useQuery({
    queryKey: ["categories", params],
    queryFn: () => getCategories(apiClient, params),
    staleTime: 1000 * 60 * 10, // Cache for 10 minutes
    select: (response) => {
      const serverData = response?.data;

      if (!serverData?.data) {
        return [];
      }

      return serverData.data;
    },
  });
};
