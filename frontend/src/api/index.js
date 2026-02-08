import axios from "axios";

// In production (Vercel), use VITE_API_URL environment variable
// In development, Vite proxy handles /api -> backend
const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  withCredentials: true,
});

export default apiClient;
