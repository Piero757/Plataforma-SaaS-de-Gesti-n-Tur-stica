import { prisma } from '../../config/database';
import { parsePagination } from '../../shared/utils/response';

export async function listarNotificaciones(tenantId: string, usuarioId: string, query: Record<string, unknown>) {
  const { page, limit, skip } = parsePagination(query);
  const soloPendientes = query.pendientes === 'true';

  const where = {
    empresaId: tenantId,
    usuarioId,
    ...(soloPendientes && { leida: false }),
  };

  const [notificaciones, total, noLeidas] = await Promise.all([
    prisma.notificacion.findMany({ where, skip, take: limit, orderBy: { creadoEn: 'desc' } }),
    prisma.notificacion.count({ where }),
    prisma.notificacion.count({ where: { empresaId: tenantId, usuarioId, leida: false } }),
  ]);

  return { notificaciones, total, page, limit, noLeidas };
}

export async function marcarComoLeida(tenantId: string, usuarioId: string, id: string) {
  return prisma.notificacion.updateMany({
    where: { id, empresaId: tenantId, usuarioId },
    data: { leida: true },
  });
}

export async function marcarTodasLeidas(tenantId: string, usuarioId: string) {
  return prisma.notificacion.updateMany({
    where: { empresaId: tenantId, usuarioId, leida: false },
    data: { leida: true },
  });
}
