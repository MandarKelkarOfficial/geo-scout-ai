import { apiFetch } from './client';

export const listSessions = () => apiFetch('/api/v1/sessions');
export const deleteSession = (id) => apiFetch(`/api/v1/sessions/${id}`, { method: 'DELETE' });
export const getHistory = (id) => apiFetch(`/api/v1/sessions/${id}/history`);
export const shareSession = (id) => apiFetch(`/api/v1/sessions/${id}/share`, { method: 'POST' });
export const renameSession = (id, title) => apiFetch(`/api/v1/sessions/${id}/rename`, { method: 'PATCH', body: JSON.stringify({ title }) });
