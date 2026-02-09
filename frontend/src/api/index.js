import axios from "axios";

const apiClient = axios.create({
  baseURL: "/api",
  timeout: 15000,
  withCredentials: true,
});

// Response interceptor for centralized error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 errors without triggering logout
    // The app should handle auth state via Auth0, not via API responses
    if (error.response?.status === 401) {
      console.warn("API returned 401 - token may be expired or invalid");
      // Don't trigger logout here - let Auth0 handle session state
      // The AuthenticationGuard will redirect if truly unauthenticated
    }

    // Handle 403 (forbidden) - user is authenticated but lacks permission
    if (error.response?.status === 403) {
      console.warn("API returned 403 - insufficient permissions");
    }

    // Handle network errors
    if (error.code === "ECONNABORTED" || error.message?.includes("timeout")) {
      console.error("Request timeout - server may be slow or unreachable");
    }

    return Promise.reject(error);
  },
);

export default apiClient;
