import { useEffect } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { apiClient } from "../api/index.js";

const useAxios = () => {
  const { getAccessTokenSilently } = useAuth0();

  useEffect(() => {
    const requestInterceptor = apiClient.interceptors.request.use(
      async (config) => {
        try {
          const token = await getAccessTokenSilently({
            audience: import.meta.env.VITE_AUTH0_AUDIENCE,
            scope: "openid profile email",
          });

          config.headers.Authorization = `Bearer ${token}`;
        } catch (error) {
          console.error("Failed to attach token:", error);
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    return () => {
      apiClient.interceptors.request.eject(requestInterceptor);
    };
  }, [getAccessTokenSilently]);

  return apiClient;
};

export default useAxios;
