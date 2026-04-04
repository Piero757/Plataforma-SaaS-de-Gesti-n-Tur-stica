import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Usuario {
  id: string;
  nombre: string;
  email: string;
  rol: string;
}

interface Empresa {
  id: string;
  nombre: string;
  slug: string;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  usuario: Usuario | null;
  empresa: Empresa | null;
  isAuthenticated: boolean;
  setAuth: (access: string, refresh: string, user: Usuario, company: Empresa) => void;
  logout: () => void;
  updateUser: (user: Partial<Usuario>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      usuario: null,
      empresa: null,
      isAuthenticated: false,

      setAuth: (access, refresh, user, company) =>
        set({
          accessToken: access,
          refreshToken: refresh,
          usuario: user,
          empresa: company,
          isAuthenticated: true,
        }),

      logout: () =>
        set({
          accessToken: null,
          refreshToken: null,
          usuario: null,
          empresa: null,
          isAuthenticated: false,
        }),

      updateUser: (userUpdates) =>
        set((state) => ({
          usuario: state.usuario ? { ...state.usuario, ...userUpdates } : null,
        })),
    }),
    {
      name: 'saas-auth-storage', // name of the item in the storage (must be unique)
    }
  )
);
