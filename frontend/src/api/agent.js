import api from "./axios";

function extractIncidentId(question) {
  const match = String(question || "").match(/\b(?:INC[-_ ]?)?(\d+)\b/i);
  return match ? Number(match[1]) : null;
}

export async function askAgent(question, incidentId = null) {
  const id = incidentId ?? extractIncidentId(question);
  const payload = { question };
  if (id) payload.incident_id = id;

  const { data } = await api.post("/ai/agent/query", payload);
  return data;
}

export async function diagnoseIncident(incidentId) {
  const id = Number(incidentId);
  if (!Number.isInteger(id) || id <= 0) {
    throw new Error("A valid incident ID is required.");
  }
  return askAgent(`Diagnose incident ${id}`, id);
}
