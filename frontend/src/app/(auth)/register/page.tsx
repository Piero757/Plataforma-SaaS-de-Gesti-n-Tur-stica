'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authService } from '@/services/auth.service';
import { useAuthStore } from '@/store/authStore';

const PLANES = [
  { id: 'basico', nombre: 'Básico', precio: '$49/mes', max: '5 usuarios · 100 reservas', color: 'border-gray-200' },
  { id: 'profesional', nombre: 'Profesional', precio: '$149/mes', max: '20 usuarios · 500 reservas', color: 'border-blue-500', popular: true },
  { id: 'empresarial', nombre: 'Empresarial', precio: '$399/mes', max: 'Ilimitados', color: 'border-purple-500' },
];

export default function RegisterPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [planSeleccionado, setPlanSeleccionado] = useState('profesional');

  const [form, setForm] = useState({
    empresaNombre: '',
    empresaEmail: '',
    empresaTelefono: '',
    empresaPais: '',
    empresaCiudad: '',
    nombre: '',
    email: '',
    password: '',
    confirmarPassword: '',
  });

  const update = (field: string, value: string) => setForm((prev) => ({ ...prev, [field]: value }));

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (form.password !== form.confirmarPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await authService.register({ ...form, planId: planSeleccionado });
      setAuth(data.data.accessToken, data.data.refreshToken, data.data.usuario, data.data.empresa);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.message ?? 'Error al registrar la empresa');
    } finally {
      setLoading(false);
    }
  }

  const inputClass = `w-full px-4 py-2.5 rounded-lg border border-gray-300 text-sm
    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
    transition-all duration-150 bg-white`;

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <div className="w-full max-w-2xl animate-enter">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-3">
            <span className="text-4xl">✈️</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Registra tu empresa</h1>
          <p className="text-gray-500 mt-1">Comienza tu prueba gratuita de 14 días</p>
        </div>

        {/* Steps */}
        <div className="flex items-center justify-center mb-8">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold
                transition-all duration-300 ${step >= s
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-gray-200 text-gray-500'}`}>
                {step > s ? '✓' : s}
              </div>
              {s < 3 && (
                <div className={`w-16 h-0.5 transition-all duration-300 ${step > s ? 'bg-blue-600' : 'bg-gray-200'}`} />
              )}
            </div>
          ))}
        </div>

        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          {error && (
            <div className="mb-5 bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2 text-red-700 text-sm">
              <span>⚠️</span><span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* PASO 1: Datos de la empresa */}
            {step === 1 && (
              <div className="space-y-5 animate-enter">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Datos de la empresa</h2>
                  <p className="text-sm text-gray-500 mt-0.5">Información básica de tu negocio</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="md:col-span-2 space-y-1.5">
                    <label className="text-sm font-medium text-gray-700">Nombre de la empresa *</label>
                    <input className={inputClass} required value={form.empresaNombre}
                      onChange={(e) => update('empresaNombre', e.target.value)}
                      placeholder="Ej: Tropical Tours S.A." />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-gray-700">Email corporativo *</label>
                    <input className={inputClass} type="email" required value={form.empresaEmail}
                      onChange={(e) => update('empresaEmail', e.target.value)}
                      placeholder="info@empresa.com" />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-gray-700">Teléfono</label>
                    <input className={inputClass} value={form.empresaTelefono}
                      onChange={(e) => update('empresaTelefono', e.target.value)}
                      placeholder="+1 555-0100" />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-gray-700">País</label>
                    <input className={inputClass} value={form.empresaPais}
                      onChange={(e) => update('empresaPais', e.target.value)}
                      placeholder="México" />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-gray-700">Ciudad</label>
                    <input className={inputClass} value={form.empresaCiudad}
                      onChange={(e) => update('empresaCiudad', e.target.value)}
                      placeholder="Ciudad de México" />
                  </div>
                </div>
                <button type="button" onClick={() => setStep(2)}
                  disabled={!form.empresaNombre || !form.empresaEmail}
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300
                    text-white font-semibold rounded-lg text-sm transition-all">
                  Continuar →
                </button>
              </div>
            )}

            {/* PASO 2: Usuario administrador */}
            {step === 2 && (
              <div className="space-y-5 animate-enter">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Tu cuenta de administrador</h2>
                  <p className="text-sm text-gray-500 mt-0.5">Credenciales de acceso al sistema</p>
                </div>
                <div className="space-y-4">
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-gray-700">Nombre completo *</label>
                    <input className={inputClass} required value={form.nombre}
                      onChange={(e) => update('nombre', e.target.value)}
                      placeholder="Juan García" />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-gray-700">Email de acceso *</label>
                    <input className={inputClass} type="email" required value={form.email}
                      onChange={(e) => update('email', e.target.value)}
                      placeholder="juan@empresa.com" />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-gray-700">Contraseña *</label>
                    <input className={inputClass} type="password" required value={form.password}
                      onChange={(e) => update('password', e.target.value)}
                      placeholder="Mínimo 8 caracteres" />
                    <p className="text-xs text-gray-400">Mínimo 8 caracteres, una mayúscula y un número</p>
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-gray-700">Confirmar contraseña *</label>
                    <input className={inputClass} type="password" required value={form.confirmarPassword}
                      onChange={(e) => update('confirmarPassword', e.target.value)}
                      placeholder="Repite tu contraseña" />
                  </div>
                </div>
                <div className="flex gap-3">
                  <button type="button" onClick={() => setStep(1)}
                    className="flex-1 py-2.5 border border-gray-300 hover:bg-gray-50 font-medium rounded-lg text-sm transition-all">
                    ← Atrás
                  </button>
                  <button type="button" onClick={() => setStep(3)}
                    disabled={!form.nombre || !form.email || !form.password}
                    className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300
                      text-white font-semibold rounded-lg text-sm transition-all">
                    Continuar →
                  </button>
                </div>
              </div>
            )}

            {/* PASO 3: Selección de plan */}
            {step === 3 && (
              <div className="space-y-5 animate-enter">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Elige tu plan</h2>
                  <p className="text-sm text-gray-500 mt-0.5">Puedes cambiar de plan en cualquier momento</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {PLANES.map((plan) => (
                    <button key={plan.id} type="button" onClick={() => setPlanSeleccionado(plan.id)}
                      className={`relative p-4 rounded-xl border-2 text-left transition-all duration-150 ${
                        planSeleccionado === plan.id
                          ? `${plan.color} shadow-md scale-[1.02]`
                          : 'border-gray-200 hover:border-gray-300'
                      }`}>
                      {plan.popular && (
                        <span className="absolute -top-2 left-1/2 -translate-x-1/2 bg-blue-600 text-white
                          text-xs font-semibold px-2 py-0.5 rounded-full">Popular</span>
                      )}
                      <p className="font-bold text-gray-900">{plan.nombre}</p>
                      <p className="text-blue-700 font-semibold text-lg mt-1">{plan.precio}</p>
                      <p className="text-xs text-gray-500 mt-1">{plan.max}</p>
                    </button>
                  ))}
                </div>
                <div className="flex gap-3">
                  <button type="button" onClick={() => setStep(2)}
                    className="flex-1 py-2.5 border border-gray-300 hover:bg-gray-50 font-medium rounded-lg text-sm transition-all">
                    ← Atrás
                  </button>
                  <button id="btn-register" type="submit" disabled={loading}
                    className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400
                      text-white font-semibold rounded-lg text-sm transition-all flex items-center justify-center gap-2">
                    {loading ? (
                      <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Creando...</>
                    ) : '🚀 Crear mi empresa'}
                  </button>
                </div>
              </div>
            )}
          </form>

          <div className="mt-6 text-center text-sm text-gray-500">
            ¿Ya tienes cuenta?{' '}
            <Link href="/login" className="text-blue-600 hover:underline font-medium">Inicia sesión</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
