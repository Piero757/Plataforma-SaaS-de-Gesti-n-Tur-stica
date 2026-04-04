import { api } from './api';

export const authService = {
  login: async (credentials: any) => {
    // using axios directly to bypass standard interceptor data unpacking if needed, or just let interceptor handle it
    // since interceptor unpacks `response.data`, we just return the result
    return api.post('/auth/login', credentials);
  },
  
  register: async (data: any) => {
    return api.post('/auth/register', data);
  },

  logout: async (refreshToken: string) => {
     return api.post('/auth/logout', { refreshToken });
  },

  getMe: async () => {
    return api.get('/auth/me');
  }
};

export const reportesService = {
  getDashboard: async () => {
    return api.get('/reportes/dashboard');
  }
}
