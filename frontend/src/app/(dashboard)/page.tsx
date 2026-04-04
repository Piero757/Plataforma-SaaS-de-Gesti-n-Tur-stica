'use client';

import { useEffect, useState } from 'react';
import { reportesService } from '@/services/auth.service';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { SalesChart } from '@/components/dashboard/Charts';
import Link from 'next/link';

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reportesService.getDashboard()
      .then((res: any) => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // Mock data for chart right now as the backend endpoint might not have historic data generated
  const chartData = [
    { mes: 'Ene', ingresos: 4000 },
    { mes: 'Feb', ingresos: 3000 },
    { mes: 'Mar', ingresos: 5000 },
    { mes: 'Abr', ingresos: 4500 },
    { mes: 'May', ingresos: 6000 },
    { mes: 'Jun', ingresos: data?.kpis?.ingresos?.mes || 7500 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1 text-sm">Resumen de la actividad de tu empresa</p>
        </div>
        <Link href="/reservas" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          + Nueva Reserva
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard 
          title="Ingresos del mes" 
          value={`$${(data?.kpis?.ingresos?.mes || 0).toLocaleString()}`} 
          change={data?.kpis?.ingresos?.cambio || 0} 
          icon="💰" 
        />
        <StatsCard 
          title="Reservas activas" 
          value={data?.kpis?.reservas?.mes || 0} 
          change={data?.kpis?.reservas?.cambio || 0} 
          icon="📋" 
        />
        <StatsCard 
          title="Nuevos Clientes" 
          value={data?.kpis?.clientes?.mes || 0} 
          change={data?.kpis?.clientes?.cambio || 0} 
          icon="👥" 
        />
        <StatsCard 
          title="Tasa de Ocupación" 
          value={`${data?.ocupacion?.ocupadas ? Math.round((data.ocupacion.ocupadas / (data.ocupacion.ocupadas + data.ocupacion.disponibles)) * 100) : 0}%`} 
          change={5} 
          icon="🏨" 
        />
      </div>

      <div className="grid gap-6 md:grid-cols-7">
        {/* Gráfico de Ingresos */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm md:col-span-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Evolución de Ingresos</h2>
          </div>
          <SalesChart data={chartData} />
        </div>

        {/* Últimas Reservas (Lista) */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm md:col-span-3 hover:shadow-md transition-shadow">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Últimas Reservas</h2>
            <Link href="/reservas" className="text-sm font-medium text-blue-600 hover:text-blue-700">Ver todas</Link>
          </div>
          
          <div className="space-y-4">
            {data?.ultimasReservas?.length ? (
              data.ultimasReservas.map((reserva: any) => (
                <div key={reserva.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors border border-transparent hover:border-gray-100">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-bold">
                      {reserva.cliente.nombre[0]}{reserva.cliente.apellido[0]}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{reserva.cliente.nombre} {reserva.cliente.apellido}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{reserva.tipo === 'hotel' ? `Hab. ${reserva.habitacion?.numero}` : reserva.paquete?.nombre}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-gray-900">${reserva.precioTotal}</p>
                    <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full mt-1 inline-block badge-${reserva.estado}`}>
                      {reserva.estado}
                    </span>
                  </div>
                </div>
              ))
            ) : (
                <p className="text-center text-sm text-gray-500 py-8">No hay reservas recientes</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
