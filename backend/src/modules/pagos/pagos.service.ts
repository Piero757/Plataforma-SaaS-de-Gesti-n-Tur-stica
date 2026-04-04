import { prisma } from '../../config/database';
import { AppError } from '../../shared/utils/AppError';
import { parsePagination } from '../../shared/utils/response';

export async function listarPagos(tenantId: string, query: Record<string, unknown>) {
  const { page, limit, skip } = parsePagination(query);
  const { estado, reservaId } = query as Record<string, string>;

  const where = {
    empresaId: tenantId,
    ...(estado && { estado }),
    ...(reservaId && { reservaId }),
  };

  const [pagos, total] = await Promise.all([
    prisma.pago.findMany({
      where, skip, take: limit,
      orderBy: { creadoEn: 'desc' },
      include: {
        cliente: { select: { nombre: true, apellido: true } },
        reserva: { select: { codigoRef: true, tipo: true } },
      },
    }),
    prisma.pago.count({ where }),
  ]);

  return { pagos, total, page, limit };
}

export async function registrarPago(tenantId: string, data: Record<string, unknown>) {
  const { reservaId, monto, metodoPago, referencia, moneda, notas } = data as any;

  // Verificar reserva pertenece al tenant
  const reserva = await prisma.reserva.findFirst({
    where: { id: reservaId, empresaId: tenantId },
    include: { cliente: true },
  });
  if (!reserva) throw new AppError('Reserva no encontrada', 404);

  const pago = await prisma.pago.create({
    data: {
      empresaId: tenantId,
      reservaId,
      clienteId: reserva.clienteId,
      monto: Number(monto),
      metodoPago,
      referencia,
      moneda: moneda || 'USD',
      notas,
      estado: 'completado',
      fechaPago: new Date(),
    },
  });

  // Verificar si el pago cubre el total de la reserva → cambiar estado a confirmada
  const totalPagado = await prisma.pago.aggregate({
    where: { reservaId, estado: 'completado' },
    _sum: { monto: true },
  });

  if (Number(totalPagado._sum.monto) >= Number(reserva.precioTotal)) {
    await prisma.reserva.update({
      where: { id: reservaId },
      data: { estado: 'confirmada' },
    });
  }

  return pago;
}

export async function obtenerPago(tenantId: string, id: string) {
  const pago = await prisma.pago.findFirst({
    where: { id, empresaId: tenantId },
    include: {
      cliente: true,
      reserva: { include: { habitacion: true, paquete: true } },
    },
  });
  if (!pago) throw new AppError('Pago no encontrado', 404);
  return pago;
}
