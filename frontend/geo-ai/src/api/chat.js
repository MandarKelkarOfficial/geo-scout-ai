import { apiFetch } from './client';

export const sendMessage = (query, session_token = null) =>
  apiFetch('/api/v1/query', {
    method: 'POST',
    body: JSON.stringify({ query, session_token }),
  });
