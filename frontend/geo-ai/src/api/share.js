import { apiFetch } from './client';

export const getSharedChat = (token) => apiFetch(`/api/v1/share/${token}`);
