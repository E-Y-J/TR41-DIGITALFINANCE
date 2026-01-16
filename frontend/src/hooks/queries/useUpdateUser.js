import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useAxios } from "../useAxios";
import { updateUser } from "../../api/user";

export const useUpdateUser = () => {
  const navigate = useNavigate();
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (formData) => updateUser(apiClient, formData),

    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["user"] });
      navigate("/home", { replace: true });
    },

    onError: (error) => {
      console.error("Update failed:", error);
    },
  });
};
