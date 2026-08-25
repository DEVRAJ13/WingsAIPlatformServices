import api from "./axios";

export async function login(email, password) {
  const { data } = await api.post("/auth/login", { email, password });
  return data;
}

export async function register(payload) {
  const { data } = await api.post("/auth/register", payload);
  return data;
}

export async function getCurrentUser() {
  const { data } = await api.get("/users/me");
  return data;
}

export async function changePassword(current_password, new_password) {
  const { data } = await api.post("/auth/change-password", { current_password, new_password });
  return data;
}
