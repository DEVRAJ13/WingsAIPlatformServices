import api from "./axios";

export async function listApprovals() {
  const { data } = await api.get("/approvals");
  return data;
}

export async function createApproval(payload) {
  const { data } = await api.post("/approvals", payload);
  return data;
}

export async function createAIApproval(payload) {
  const { data } = await api.post("/approvals/from-ai", payload);
  return data;
}

export async function decideApproval(id, payload) {
  const { data } = await api.post(`/approvals/${id}/decide`, {
    decision: payload.decision,
    decision_comment: payload.comment ?? payload.decision_comment ?? null,
  });
  return data;
}

export async function executeApproval(id) {
  const { data } = await api.post(`/approvals/${id}/execute`);
  return data;
}
