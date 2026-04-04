'use client';

import { useEffect, useState } from 'react';
import { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/tables/DataTable';
import { reservasService } from '@/services/reservas.service';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export default function ReservasPage() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reservasService.listar()
      .then((res: any) => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const columns: ColumnDef<any>[] = [
    {
      accessorKey: 'codigoRef',
      header: 'Código',
      cell: ({ row }) => <span className="font-mono text-xs font-bold bg-gray-100 px-2 py-1 rounded text-gray-600">{row.original.codigoRef}</span>,
    },
    {
      accessorKey: 'cliente.nombre',
      header: 'Cliente',
      cell: ({ row }) => (
          <div>
              <p className="font-medium text-gray-900">{row.original.cliente.nombre} {row.original.cliente.apellido}</p>
              <p className="text-xs text-gray-500">{row.original.cliente.email}</p>
          </div>
      )
    },
    {
        accessorKey: 'servicio',
        header: 'Servicio',
        cell: ({ row }) => {
            const esHotel = row.original.tipo === 'hotel';
            return (
                <div>
                   <div className="flex items-center gap-1.5 text-sm font-medium text-gray-900">
                     <span>{esHotel ? '🏨' : '✈️'}</span>
                     <span>{esHotel ? row.original.habitacion?.hotel?.nombre : row.original.paquete?.nombre}</span>
                   </div>
                   {esHotel && <span className="text-xs text-gray-500 block ml-6">Hab. {row.original.habitacion?.numero} ({row.original.habitacion?.tipo})</span>}
                </div>
            )
        }
    },
    {
      accessorKey: 'fechas',
      header: 'Fechas',
      cell: ({ row }) => (
        <div className="text-sm">
             <p className="text-gray-900 font-medium">{format(new Date(row.original.fechaInicio), "d MMM yyyy", { locale: es })}</p>
             <p className="text-gray-500 text-xs">al {format(new Date(row.original.fechaFin), "d MMM yyyy", { locale: es })}</p>
        </div>
      )
    },
    {
      accessorKey: 'precioTotal',
      header: 'Total',
      cell: ({ row }) => <span className="font-bold text-gray-900">${row.original.precioTotal}</span>,
    },
    {
      accessorKey: 'estado',
      header: 'Estado',
      cell: ({ row }) => (
        <span className={`badge-${row.original.estado} px-2.5 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider`}>
          {row.original.estado}
        </span>
      ),
    },
    {
      id: 'actions',
      cell: () => (
        <button className="text-blue-600 hover:text-blue-800 text-sm font-medium underline">Gestionar</button>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gestor de Reservas</h1>
          <p className="text-gray-500 mt-1 text-sm">Administración centralizada de todas las reservas</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          + Nueva Reserva
        </button>
      </div>

      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
         <div className="flex gap-4 mb-4">
             <select className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-blue-500 bg-white">
                 <option value="">Todos los estados</option>
                 <option value="pendiente">Pendientes</option>
                 <option value="confirmada">Confirmadas</option>
                 <option value="cancelada">Canceladas</option>
             </select>
             <input 
               type="text" 
               placeholder="Buscar por código RES-..." 
               className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-blue-500" 
             />
         </div>
         <DataTable columns={columns} data={data} isLoading={loading} />
      </div>
    </div>
  );
}
