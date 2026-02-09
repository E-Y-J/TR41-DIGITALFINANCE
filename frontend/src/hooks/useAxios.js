import { useEffect, useRef, useCallback } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import apiClient from "../api/index.js";

export const useAxios = () => {
  const { getAccessTokenSilently, isAuthenticated } = useAuth0();
  const interceptorRef = useRef(null);

  // Memoize getAccessTokenSilently to prevent interceptor churn
  const getToken = useCallback(async () => {
    if (!isAuthenticated) {
      return null;
    }

    try {
      const token = await getAccessTokenSilently({
        audience: import.meta.env.VITE_AUTH0_AUDIENCE,
        scope: "openid profile email",
        // Don't throw on recoverable errors - just return cached token if available
        cacheMode: "cache-first",
      });
      return token;
    } catch (error) {
      // Handle specific Auth0 errors gracefully
      if (error.error === "login_required" || error.error === "consent_required") {
        // Don't propagate - this would trigger logout
        // The user is still authenticated, just can't refresh silently
        console.warn("Silent token refresh failed (expected in some scenarios):", error.error);
        return null;
      }

      // For network errors, don't crash the app
      if (error.message?.includes("network") || error.message?.includes("timeout")) {
        console.warn("Network error during token fetch:", error.message);
        return null;
      }

      console.error("Unexpected token error:", error);
      return null;
    }
  }, [getAccessTokenSilently, isAuthenticated]);

  useEffect(() => {
    // Only set up interceptor once
    if (interceptorRef.current !== null) {
      apiClient.interceptors.request.eject(interceptorRef.current);
    }

    interceptorRef.current = apiClient.interceptors.request.use(
      async (config) => {
        const token = await getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error),
    );

    return () => {
      if (interceptorRef.current !== null) {
        apiClient.interceptors.request.eject(interceptorRef.current);
        interceptorRef.current = null;
      }
    };
  }, [getToken]);

  return apiClient;
};
