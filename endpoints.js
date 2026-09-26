import client from "./client";

export const authApi = {
  register: (payload) => client.post("/auth/register", payload),
  login: (payload) => client.post("/auth/login", payload),
  me: () => client.get("/auth/me"),
};

export const purifierApi = {
  list: () => client.get("/purifiers"),
  get: (id) => client.get(`/purifiers/${id}`),
  create: (payload) => client.post("/purifiers", payload),
  update: (id, payload) => client.patch(`/purifiers/${id}`, payload),
  remove: (id) => client.delete(`/purifiers/${id}`),
  logFilterReplacement: (id) => client.post(`/purifiers/${id}/replace-filter`),
};

export const readingApi = {
  list: (purifierId, limit = 50) => client.get("/readings", { params: { purifier_id: purifierId, limit } }),
  create: (payload) => client.post("/readings", payload),
  remove: (id) => client.delete(`/readings/${id}`),
};

export const predictionApi = {
  run: (purifierId) => client.post(`/predictions/run/${purifierId}`),
  latest: (purifierId) => client.get(`/predictions/latest/${purifierId}`),
  history: (purifierId, limit = 30) => client.get(`/predictions/history/${purifierId}`, { params: { limit } }),
};

export const analyticsApi = {
  summary: (purifierId) => client.get(`/analytics/summary/${purifierId}`),
  overview: () => client.get("/analytics/overview"),
};
