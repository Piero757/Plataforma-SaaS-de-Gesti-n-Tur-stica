import axios from 'axios';
import { useAuthStore } from '@/store/authStore';

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/api` : '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 and refresh token logic
api.interceptors.response.use(
  (response) => response.data, // extract data automatically for success responses
  async (error) => {
    const originalRequest = error.config;

    // Fix infinite loop if refresh token call fails
    if (originalRequest.url === '/auth/refresh') {
      useAuthStore.getState().logout();
      window.location.href = '/login';
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = useAuthStore.getState().refreshToken;

      if (refreshToken) {
        try {
          // Attempt to refresh token
          const res = await axios.post(`${api.defaults.baseURL}/auth/refresh`, { refreshToken });
          const { accessToken, refreshToken: newRefresh } = res.data.data;
          
          const currentState = useAuthStore.getState();
          if (currentState.usuario && currentState.empresa) {
              currentState.setAuth(accessToken, newRefresh, currentState.usuario, currentState.empresa);
          }

          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${accessToken}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh totally failed, logout
          useAuthStore.getState().logout();
          window.location.href = '/login';
        }
      } else {
         useAuthStore.getState().logout();
         window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);
