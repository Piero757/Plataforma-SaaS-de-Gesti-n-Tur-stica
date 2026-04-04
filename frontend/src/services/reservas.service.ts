import { api } from './api';

export const reservasService = {
  listar: async (params?: any) => {
    return api.get('/reservas', { params });
  },
  obtener: async (id: string) => {
    return api.get(`/reservas/${id}`);
  },
  crear: async (data: any) => {
    return api.post('/reservas', data);
  },
  actualizar: async (id: string, data: any) => {
    return api.put(`/reservas/${id}`, data);
  },
  cambiarEstado: async (id: string, estado: 'confirmar' | 'cancelar' | 'completar') => {
    return api.put(`/reservas/${id}/${estado}`);
  }
};
