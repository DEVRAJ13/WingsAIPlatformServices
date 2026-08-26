import api from "./axios";

export async function getMonitoringOverview() {
  const { data } = await api.get("/monitoring/overview");
  return data;
}

export async function getMonitoringHealth() {
  const { data } = await api.get("/monitoring/health");
  return data;
}

export async function getMonitoringAgents() {
  const { data } = await api.get("/monitoring/agents");
  return data;
}

export async function listWorkflowRuns(limit = 50) {
  const { data } = await api.get("/monitoring/workflows", {
    params: { limit },
  });
  return data;
}

export async function getWorkflowDetail(workflowId) {
  const { data } = await api.get(`/monitoring/workflows/${encodeURIComponent(workflowId)}`);
  return data;
}
