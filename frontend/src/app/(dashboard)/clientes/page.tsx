'use client';

import { useEffect, useState } from 'react';
import { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/tables/DataTable';
import { clientesService } from '@/services/clientes.service';
import Link from 'next/link';

export default function ClientesPage() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    clientesService.listar()
      .then((res: any) => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const columns: ColumnDef<any>[] = [
    {
      accessorKey: 'nombre',
      header: 'Cliente',
      cell: ({ row }) => (
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-xs uppercase">
            {row.original.nombre[0]}{row.original.apellido[0]}
          </div>
          <div>
            <p className="font-medium text-gray-900">{row.original.nombre} {row.original.apellido}</p>
            <p className="text-xs text-gray-500">{row.original.email}</p>
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'documentoNum',
      header: 'Documento',
      cell: ({ row }) => <span className="text-gray-600">{row.original.documentoTipo}: {row.original.documentoNum}</span>,
    },
    {
      accessorKey: 'telefono',
      header: 'Contacto',
      cell: ({ row }) => (
        <div className="text-sm">
          <p className="text-gray-900">{row.original.telefono || '-'}</p>
          <p className="text-gray-500 text-xs">{row.original.ciudad}, {row.original.pais}</p>
        </div>
      )
    },
    {
      accessorKey: '_count.reservas',
      header: 'Reservas',
      cell: ({ row }) => <span className="font-semibold text-gray-700">{row.original._count.reservas}</span>,
    },
    {
      accessorKey: 'activo',
      header: 'Estado',
      cell: ({ row }) => (
        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${row.original.activo ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {row.original.activo ? 'Activo' : 'Inactivo'}
        </span>
      ),
    },
    {
      id: 'actions',
      cell: () => (
        <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">Ver perfil</button>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Directorio de Clientes</h1>
          <p className="text-gray-500 mt-1 text-sm">Gestiona la información y el historial de tus clientes</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          + Nuevo Cliente
        </button>
      </div>

      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
        <div className="flex gap-4 mb-4">
           {/* Filtros simples */}
           <input 
             type="text" 
             placeholder="Buscar cliente por nombre, documento o email..." 
             className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500" 
           />
        </div>
        <DataTable columns={columns} data={data} isLoading={loading} />
      </div>
    </div>
  );
}
