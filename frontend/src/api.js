import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An unexpected error occurred';
    return Promise.reject(new Error(message));
  }
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

export default api;
