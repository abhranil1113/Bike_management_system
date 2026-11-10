// Frontend/shared/api.ts
import axios from 'axios';

export const getBackendBaseUrl = (): string => {
  if (typeof window !== 'undefined' && window.location) {
    const host = window.location.hostname || 'localhost';
    const protocol = window.location.protocol || 'http:';
    return `${protocol}//${host}:8000`;
  }
  return 'http://localhost:8000';
};

export const getPortalUrl = (port: number): string => {
  if (typeof window !== 'undefined' && window.location) {
    const host = window.location.hostname || 'localhost';
    const protocol = window.location.protocol || 'http:';
    return `${protocol}//${host}:${port}`;
  }
  return `http://localhost:${port}`;
};

export const apiClient = axios.create({
  baseURL: getBackendBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

apiClient.interceptors.request.use((config) => {
  config.baseURL = getBackendBaseUrl();
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn('[API 401] Unauthorized - Token may be expired.');
    }
    return Promise.reject(error);
  }
);
