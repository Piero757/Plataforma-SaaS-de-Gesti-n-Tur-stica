import { prisma } from '../../config/database';
import { AppError } from '../../shared/utils/AppError';
import { parsePagination } from '../../shared/utils/response';

export async function listarPaquetes(tenantId: string, query: Record<string, unknown>) {
  const { page, limit, skip } = parsePagination(query);
  const busqueda = String(query.busqueda ?? '');

  const where = {
    empresaId: tenantId,
    activo: true,
    ...(busqueda && {
      OR: [
        { nombre: { contains: busqueda, mode: 'insensitive' as const } },
        { descripcion: { contains: busqueda, mode: 'insensitive' as const } },
      ],
    }),
  };

  const [paquetes, total] = await Promise.all([
    prisma.paqueteTuristico.findMany({
      where, skip, take: limit,
      orderBy: { creadoEn: 'desc' },
      include: { _count: { select: { reservas: true } } },
    }),
    prisma.paqueteTuristico.count({ where }),
  ]);

  return { paquetes, total, page, limit };
}

export async function obtenerPaquete(tenantId: string, id: string) {
  const paquete = await prisma.paqueteTuristico.findFirst({
    where: { id, empresaId: tenantId },
    include: { _count: { select: { reservas: true } } },
  });
  if (!paquete) throw new AppError('Paquete no encontrado', 404);
  return paquete;
}

export async function crearPaquete(tenantId: string, data: Record<string, unknown>) {
  return prisma.paqueteTuristico.create({
    data: { empresaId: tenantId, ...(data as any) },
  });
}

export async function actualizarPaquete(tenantId: string, id: string, data: Record<string, unknown>) {
  const paquete = await prisma.paqueteTuristico.findFirst({ where: { id, empresaId: tenantId } });
  if (!paquete) throw new AppError('Paquete no encontrado', 404);
  return prisma.paqueteTuristico.update({ where: { id }, data: data as any });
}

export async function eliminarPaquete(tenantId: string, id: string) {
  const paquete = await prisma.paqueteTuristico.findFirst({ where: { id, empresaId: tenantId } });
  if (!paquete) throw new AppError('Paquete no encontrado', 404);
  return prisma.paqueteTuristico.update({ where: { id }, data: { activo: false } });
}
