import { api } from './api';

export const clientesService = {
  listar: async (params?: any) => {
    return api.get('/clientes', { params });
  },
  obtener: async (id: string) => {
    return api.get(`/clientes/${id}`);
  },
  crear: async (data: any) => {
    return api.post('/clientes', data);
  },
  actualizar: async (id: string, data: any) => {
    return api.put(`/clientes/${id}`, data);
  },
  eliminar: async (id: string) => {
    return api.delete(`/clientes/${id}`);
  }
};
