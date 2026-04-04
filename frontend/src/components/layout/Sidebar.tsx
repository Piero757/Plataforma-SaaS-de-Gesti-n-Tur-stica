'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/dashboard',       label: 'Dashboard',        icon: '📊' },
  { href: '/reservas',        label: 'Reservas',         icon: '📋' },
  { href: '/clientes',        label: 'Clientes',         icon: '👥' },
  { href: '/hoteles',         label: 'Hoteles',          icon: '🏨' },
  { href: '/paquetes',        label: 'Paquetes',         icon: '✈️' },
  { href: '/pagos',           label: 'Pagos',            icon: '💳' },
  { href: '/empleados',       label: 'Empleados',        icon: '👔' },
  { href: '/reportes',        label: 'Reportes',         icon: '📈' },
];

const adminItems = [
  { href: '/usuarios',        label: 'Usuarios',         icon: '🔐' },
  { href: '/configuracion',   label: 'Configuración',    icon: '⚙️' },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { empresa, usuario } = useAuthStore();

  return (
    <aside className="hidden lg:flex w-64 flex-col bg-white border-r border-gray-200 h-full">
      {/* Logo / Empresa */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-gray-100">
        <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center shadow-sm shrink-0">
          <span className="text-lg">✈️</span>
        </div>
        <div className="overflow-hidden">
          <p className="text-sm font-bold text-gray-900 truncate">{empresa?.nombre ?? 'SaaS Turismo'}</p>
          <p className="text-xs text-gray-400">Panel de Control</p>
        </div>
      </div>

      {/* Navegación principal */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 mb-2">Principal</p>
        {navItems.map(({ href, label, icon }) => {
          const isActive = pathname === href || (href !== '/dashboard' && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'nav-link',
                isActive && 'active'
              )}
            >
              <span className="text-base w-5 text-center shrink-0">{icon}</span>
              <span>{label}</span>
              {isActive && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-white/70" />
              )}
            </Link>
          );
        })}

        <div className="pt-4">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 mb-2">Administración</p>
          {adminItems.map(({ href, label, icon }) => {
            const isActive = pathname === href || pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={cn('nav-link', isActive && 'active')}
              >
                <span className="text-base w-5 text-center shrink-0">{icon}</span>
                <span>{label}</span>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Plan actual */}
      <div className="px-3 py-3 border-t border-gray-100">
        <div className="bg-blue-50 rounded-xl p-3 border border-blue-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-semibold text-blue-700">Plan Profesional</span>
            <span className="text-xs text-blue-500">$149/mes</span>
          </div>
          <div className="w-full bg-blue-100 rounded-full h-1.5 mb-1">
            <div className="bg-blue-600 h-1.5 rounded-full" style={{ width: '45%' }} />
          </div>
          <p className="text-xs text-blue-600">225 / 500 reservas</p>
        </div>
      </div>

      {/* Usuario */}
      <div className="px-4 py-3 border-t border-gray-100 flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-bold shrink-0">
          {usuario?.nombre?.[0]?.toUpperCase() ?? 'U'}
        </div>
        <div className="overflow-hidden flex-1">
          <p className="text-sm font-medium text-gray-900 truncate">{usuario?.nombre}</p>
          <p className="text-xs text-gray-400 truncate capitalize">{usuario?.rol}</p>
        </div>
      </div>
    </aside>
  );
}
