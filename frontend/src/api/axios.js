import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  headers: { "Content-Type": "application/json" },
  timeout: 120000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("wings_access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("wings_access_token");
      localStorage.removeItem("wings_user");
      if (!window.location.pathname.includes("/login")) window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export default api;
