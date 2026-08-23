import api from "./axios";

export async function listIncidents() {
  const { data } = await api.get("/incidents");
  return data;
}

export async function getIncident(id) {
  const { data } = await api.get(`/incidents/${id}`);
  return data;
}

export async function createIncident(payload) {
  const { data } = await api.post("/incidents", payload);
  return data;
}
