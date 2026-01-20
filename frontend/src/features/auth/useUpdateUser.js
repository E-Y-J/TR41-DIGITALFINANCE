import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useAxios } from "../../hooks/useAxios";
import { updateUser } from "../../api/user";

export const useUpdateUser = () => {
  const navigate = useNavigate();
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (formData) => updateUser(apiClient, formData),
    onSuccess: async (response) => {
      queryClient.setQueryData(["user"], (oldCache) => {
        return {
          ...oldCache,
          data: response.data,
        };
      });
      navigate("/home", { replace: true });
    },
    select: (data) => data.data,
    onError: (error) => {
      console.error("Update failed:", error);
    },
  });
};
