import { prisma } from '../../config/database';
import { AppError } from '../../shared/utils/AppError';
import { parsePagination } from '../../shared/utils/response';

export async function listarEmpleados(tenantId: string, query: Record<string, unknown>) {
  const { page, limit, skip } = parsePagination(query);
  const busqueda = String(query.busqueda ?? '');

  const where = {
    empresaId: tenantId,
    activo: true,
    ...(busqueda && {
      OR: [
        { nombre: { contains: busqueda, mode: 'insensitive' as const } },
        { apellido: { contains: busqueda, mode: 'insensitive' as const } },
        { cargo: { contains: busqueda, mode: 'insensitive' as const } },
      ],
    }),
  };

  const [empleados, total] = await Promise.all([
    prisma.empleado.findMany({
      where, skip, take: limit,
      orderBy: { creadoEn: 'desc' },
      include: { usuario: { select: { email: true, rol: { select: { nombre: true } } } } },
    }),
    prisma.empleado.count({ where }),
  ]);

  return { empleados, total, page, limit };
}

export async function crearEmpleado(tenantId: string, data: Record<string, unknown>) {
  return prisma.empleado.create({
    data: { empresaId: tenantId, ...(data as any) },
  });
}

export async function actualizarEmpleado(tenantId: string, id: string, data: Record<string, unknown>) {
  const empleado = await prisma.empleado.findFirst({ where: { id, empresaId: tenantId } });
  if (!empleado) throw new AppError('Empleado no encontrado', 404);
  return prisma.empleado.update({ where: { id }, data: data as any });
}

export async function eliminarEmpleado(tenantId: string, id: string) {
  const empleado = await prisma.empleado.findFirst({ where: { id, empresaId: tenantId } });
  if (!empleado) throw new AppError('Empleado no encontrado', 404);
  return prisma.empleado.update({ where: { id }, data: { activo: false } });
}
