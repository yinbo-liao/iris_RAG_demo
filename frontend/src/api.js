import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

function errorMessage(detail, fallback) {
  // FastAPI validation errors (422) return a list of {loc, msg, type} objects.
  if (Array.isArray(detail)) {
    const messages = detail.map((item) => item?.msg || JSON.stringify(item));
    if (messages.length) return messages.join('; ');
  }
  if (typeof detail === 'string' && detail) return detail;
  if (detail && typeof detail === 'object') return JSON.stringify(detail);
  return fallback || 'An unexpected error occurred';
}

api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(
    new Error(errorMessage(error.response?.data?.detail, error.message))
  )
);

export async function queryIris(query, approach) {
  const { data } = await api.post('/api/query', { query, approach });
  return data;
}

export async function compareApproaches(query) {
  const { data } = await api.get('/api/compare', { params: { query } });
  return data;
}

export async function getTools() {
  const { data } = await api.get('/api/tools');
  return data;
}

export async function getKnowledge() {
  const { data } = await api.get('/api/knowledge');
  return data;
}

export async function getStats() {
  const { data } = await api.get('/api/stats');
  return data;
}

export async function getHistory(limit = 20) {
  const { data } = await api.get('/api/history', { params: { limit } });
  return data;
}

export async function clearHistory() {
  const { data } = await api.delete('/api/history');
  return data;
}

export async function runMultiAgent(query) {
  const { data } = await api.post('/api/agents/analyze', { query });
  return data;
}

export async function getAgentRegistry() {
  const { data } = await api.get('/api/agents/registry');
  return data;
}

export default api;
