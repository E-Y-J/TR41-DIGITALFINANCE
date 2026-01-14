import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useAxios } from "../useAxios";
import { updateUser } from "../../api/user";

export const useUpdateUser = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (formData) => updateUser(apiClient, formData),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user"] });
    },
    onError: (error) => {
      console.error("Update failed:", error);
    },
  });
};
