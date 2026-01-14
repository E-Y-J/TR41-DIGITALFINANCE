import { useQuery } from "@tanstack/react-query";
import { getUser } from "../../api/user";
import { useAxios } from "../useAxios";

export const useGetUser = () => {
  const apiClient = useAxios();

  return useQuery({
    queryKey: ["user_data"],
    queryFn: () => getUser(apiClient),
    placeholderData: (previousData) => previousData,
  });
};

//enabled: allowing to prevent api from being called automatically
//staleTime: time before data is considered stale and needs refetching
//cacheTime: time data remains in cache before being garbage collected
//refetchOnWindowFocus: whether to refetch data when window regains focus
//retry: number of retry attempts on failure
//select: function to filter
//refectinterval: time interval for automatic refetching
//onSuccess/onError: callbacks for success or error handling
//placeholderData: data to show while loading (used for pagination)
