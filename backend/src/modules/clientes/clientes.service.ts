import { prisma } from '../../config/database';
import { AppError } from '../../shared/utils/AppError';
import { parsePagination } from '../../shared/utils/response';

export async function listarClientes(tenantId: string, query: Record<string, unknown>) {
  const { page, limit, skip } = parsePagination(query);
  const busqueda = String(query.busqueda ?? '');
  const activo = query.activo !== undefined ? query.activo === 'true' : undefined;

  const where = {
    empresaId: tenantId,
    ...(activo !== undefined && { activo }),
    ...(busqueda && {
      OR: [
        { nombre: { contains: busqueda, mode: 'insensitive' as const } },
        { apellido: { contains: busqueda, mode: 'insensitive' as const } },
        { email: { contains: busqueda, mode: 'insensitive' as const } },
        { documentoNum: { contains: busqueda, mode: 'insensitive' as const } },
      ],
    }),
  };

  const [clientes, total] = await Promise.all([
    prisma.cliente.findMany({
      where,
      orderBy: { creadoEn: 'desc' },
      skip,
      take: limit,
      select: {
        id: true, nombre: true, apellido: true, email: true,
        telefono: true, documentoTipo: true, documentoNum: true,
        pais: true, ciudad: true, activo: true, creadoEn: true,
        _count: { select: { reservas: true } },
      },
    }),
    prisma.cliente.count({ where }),
  ]);

  return { clientes, total, page, limit };
}

export async function obtenerCliente(tenantId: string, id: string) {
  const cliente = await prisma.cliente.findFirst({
    where: { id, empresaId: tenantId },
    include: {
      reservas: {
        orderBy: { creadoEn: 'desc' },
        take: 5,
        select: {
          id: true, tipo: true, fechaInicio: true, fechaFin: true,
          precioTotal: true, estado: true, codigoRef: true,
        },
      },
    },
  });

  if (!cliente) throw new AppError('Cliente no encontrado', 404);
  return cliente;
}

export async function crearCliente(tenantId: string, data: Record<string, unknown>) {
  // Verificar duplicado si se provee documento
  if (data.documentoTipo && data.documentoNum) {
    const existente = await prisma.cliente.findFirst({
      where: {
        empresaId: tenantId,
        documentoTipo: String(data.documentoTipo),
        documentoNum: String(data.documentoNum),
      },
    });
    if (existente) throw new AppError('Ya existe un cliente con ese documento', 409);
  }

  return prisma.cliente.create({
    data: { empresaId: tenantId, ...(data as any) },
  });
}

export async function actualizarCliente(
  tenantId: string,
  id: string,
  data: Record<string, unknown>
) {
  const cliente = await prisma.cliente.findFirst({ where: { id, empresaId: tenantId } });
  if (!cliente) throw new AppError('Cliente no encontrado', 404);

  return prisma.cliente.update({
    where: { id },
    data: data as any,
  });
}

export async function eliminarCliente(tenantId: string, id: string) {
  const cliente = await prisma.cliente.findFirst({ where: { id, empresaId: tenantId } });
  if (!cliente) throw new AppError('Cliente no encontrado', 404);

  // Verificar si tiene reservas activas
  const reservasActivas = await prisma.reserva.count({
    where: { clienteId: id, estado: { in: ['pendiente', 'confirmada'] } },
  });
  if (reservasActivas > 0) {
    throw new AppError('No se puede eliminar un cliente con reservas activas', 400);
  }

  return prisma.cliente.update({
    where: { id },
    data: { activo: false },
  });
}
