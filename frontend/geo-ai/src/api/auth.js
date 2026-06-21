import { apiFetch } from './client';

export const getMe = () => apiFetch('/api/v1/auth/me');
export const login = (email, password) => apiFetch('/api/v1/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
export const register = (email, password, full_name) => apiFetch('/api/v1/auth/register', { method: 'POST', body: JSON.stringify({ email, password, full_name }) });
export const logout = () => apiFetch('/api/v1/auth/logout', { method: 'POST' });
export const updateMe = (full_name) => apiFetch('/api/v1/auth/me', { method: 'PATCH', body: JSON.stringify({ full_name }) });
