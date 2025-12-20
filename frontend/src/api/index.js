import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 15000,
  withCredentials: true,
});

export default apiClient;
