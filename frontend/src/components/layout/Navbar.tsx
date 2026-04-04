'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { api } from '@/services/api';

export default function Navbar() {
  const router = useRouter();
  const { usuario, empresa, logout } = useAuthStore();
  const [noLeidas, setNoLeidas] = useState(0);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    api.get('/notificaciones?pendientes=true&limit=1')
      .then((r) => setNoLeidas(r.data?.noLeidas ?? 0))
      .catch(() => {});
  }, []);

  function handleLogout() {
    logout();
    router.replace('/login');
  }

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shrink-0">
      {/* Breadcrumb / Título */}
      <div className="flex items-center gap-2">
        <div className="lg:hidden w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center">
          <span className="text-lg">✈️</span>
        </div>
        <div>
          <p className="text-sm text-gray-400 hidden sm:block">
            {empresa?.nombre ?? 'SaaS Turismo'}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        {/* Notificaciones */}
        <button
          onClick={() => router.push('/notificaciones')}
          className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
          title="Notificaciones"
        >
          <span className="text-xl">🔔</span>
          {noLeidas > 0 && (
            <span className="absolute -top-0.5 -right-0.5 w-5 h-5 bg-red-500 text-white
              text-xs font-bold rounded-full flex items-center justify-center">
              {noLeidas > 9 ? '9+' : noLeidas}
            </span>
          )}
        </button>

        {/* Menú de usuario */}
        <div className="relative">
          <button
            id="user-menu-btn"
            onClick={() => setMenuOpen((v) => !v)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-gray-100
              transition-colors text-sm font-medium text-gray-700"
          >
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center
              text-white text-xs font-bold">
              {usuario?.nombre?.[0]?.toUpperCase() ?? 'U'}
            </div>
            <span className="hidden sm:block max-w-24 truncate">{usuario?.nombre}</span>
            <span className="text-gray-400 text-xs">▾</span>
          </button>

          {menuOpen && (
            <div className="absolute right-0 top-full mt-1 w-48 bg-white rounded-xl
              shadow-lg border border-gray-100 py-1 z-50 animate-enter">
              <div className="px-3 py-2 border-b border-gray-100">
                <p className="text-sm font-medium text-gray-900">{usuario?.nombre}</p>
                <p className="text-xs text-gray-400 capitalize">{usuario?.rol}</p>
              </div>
              <button onClick={() => { setMenuOpen(false); router.push('/configuracion'); }}
                className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2">
                <span>⚙️</span> Configuración
              </button>
              <button onClick={handleLogout}
                className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2">
                <span>🚪</span> Cerrar sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
