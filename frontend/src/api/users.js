import api from "./axios";

export async function listUsers() {
  const { data } = await api.get("/users");
  return data;
}

export async function listRoles() {
  const { data } = await api.get("/users/roles");
  return data.roles || [];
}

export async function createUser(payload) {
  const { data } = await api.post("/users", payload);
  return data;
}

export async function updateUser(id, payload) {
  const { data } = await api.put(`/users/${id}`, payload);
  return data;
}

export async function updateUserStatus(id, status) {
  const { data } = await api.patch(`/users/${id}/status`, { status });
  return data;
}

export async function resetUserPassword(id, temporary_password) {
  const { data } = await api.post(`/users/${id}/reset-password`, {
    temporary_password,
  });
  return data;
}
