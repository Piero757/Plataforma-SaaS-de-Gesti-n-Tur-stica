'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import { authService } from '@/services/auth.service';
import type { Metadata } from 'next';

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await authService.login({ email, password });
      setAuth(data.data.accessToken, data.data.refreshToken, data.data.usuario, data.data.empresa);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.message ?? 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Panel izquierdo — branding */}
      <div className="hidden lg:flex lg:w-1/2 auth-gradient flex-col justify-between p-12 text-white">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
              <span className="text-2xl">✈️</span>
            </div>
            <span className="text-xl font-bold tracking-tight">SaaS Turismo</span>
          </div>
        </div>

        <div className="space-y-6">
          <div className="space-y-3">
            <h1 className="text-4xl font-bold leading-tight">
              Gestiona tu empresa turística<br />
              <span className="text-blue-200">de forma inteligente</span>
            </h1>
            <p className="text-blue-100 text-lg leading-relaxed">
              Reservas, clientes, hoteles y paquetes turísticos en una sola plataforma profesional.
            </p>
          </div>

          {/* Features */}
          <div className="space-y-3">
            {[
              { icon: '🏨', text: 'Gestión de hoteles y habitaciones' },
              { icon: '📋', text: 'Reservas en tiempo real' },
              { icon: '👥', text: 'CRM de clientes integrado' },
              { icon: '📊', text: 'Reportes y análisis avanzados' },
            ].map(({ icon, text }) => (
              <div key={text} className="flex items-center gap-3 text-blue-100">
                <span className="text-xl">{icon}</span>
                <span className="text-sm font-medium">{text}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="text-blue-300 text-sm">
          © 2024 Plataforma SaaS de Gestión Turística. Todos los derechos reservados.
        </div>
      </div>

      {/* Panel derecho — formulario */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md space-y-8 animate-enter">
          {/* Logo mobile */}
          <div className="lg:hidden flex items-center gap-2 justify-center">
            <span className="text-3xl">✈️</span>
            <span className="text-xl font-bold text-blue-700">SaaS Turismo</span>
          </div>

          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 space-y-6">
            <div className="space-y-1">
              <h2 className="text-2xl font-bold text-gray-900">Bienvenido de vuelta</h2>
              <p className="text-gray-500 text-sm">Ingresa tus credenciales para continuar</p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2 text-red-700 text-sm">
                <span>⚠️</span>
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label htmlFor="email" className="text-sm font-medium text-gray-700">
                  Correo electrónico
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@empresa.com"
                  required
                  className="w-full px-4 py-2.5 rounded-lg border border-gray-300 text-sm
                    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                    transition-all duration-150 bg-white"
                />
              </div>

              <div className="space-y-1.5">
                <label htmlFor="password" className="text-sm font-medium text-gray-700">
                  Contraseña
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    className="w-full px-4 py-2.5 rounded-lg border border-gray-300 text-sm
                      focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                      transition-all duration-150 pr-10 bg-white"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {showPassword ? '🙈' : '👁️'}
                  </button>
                </div>
              </div>

              <div className="pt-1">
                <button
                  id="btn-login"
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400
                    text-white font-semibold rounded-lg text-sm transition-all duration-150
                    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                    disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-sm"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Iniciando sesión...
                    </>
                  ) : (
                    'Iniciar sesión'
                  )}
                </button>
              </div>
            </form>

            {/* Demo credentials */}
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 text-xs text-blue-700 space-y-1">
              <p className="font-semibold">🔑 Credenciales de demo:</p>
              <p>Email: <span className="font-mono">admin@demotours.com</span></p>
              <p>Password: <span className="font-mono">Admin123!</span></p>
            </div>

            <div className="text-center text-sm text-gray-500">
              ¿No tienes cuenta?{' '}
              <Link href="/register" className="text-blue-600 hover:text-blue-700 font-medium hover:underline">
                Registra tu empresa
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
