import axios from "axios";

// In production, VITE_API_URL points to VPS backend (e.g., https://securebankai.mysticdatanode.net)
// In development, falls back to "/api" which Vite proxies to localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api` 
  : "/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
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
