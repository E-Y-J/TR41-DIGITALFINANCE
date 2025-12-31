import axios from "axios";

const apiClient = axios.create({
  baseURL: "/api",
  timeout: 15000,
  withCredentials: true,
});

export default apiClient;
