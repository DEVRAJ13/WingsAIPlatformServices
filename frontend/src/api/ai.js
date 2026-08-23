import api from "./axios";

export async function chat(message) {
  const { data } = await api.post("/ai/chat", { message });
  return data;
}

export async function ragSearch(question) {
  const { data } = await api.post("/ai/rag/search", { question });
  return data;
}

export async function ragQuery(question) {
  const { data } = await api.post("/ai/rag/query", { question });
  return data;
}
