import api from "./axios";

export async function createDocument(payload) {
  const { data } = await api.post("/documents", payload);
  return data;
}

export async function searchKnowledge(question) {
  const { data } = await api.post("/ai/rag/search", { question });
  return data;
}

export async function queryKnowledge(question) {
  const { data } = await api.post("/ai/rag/query", { question });
  return data;
}
