import { prisma } from '../../config/database';
import { AppError } from '../../shared/utils/AppError';
import { parsePagination } from '../../shared/utils/response';

// ─── HOTELES ─────────────────────────────────────────
export async function listarHoteles(tenantId: string, query: Record<string, unknown>) {
  const { page, limit, skip } = parsePagination(query);
  const busqueda = String(query.busqueda ?? '');

  const where = {
    empresaId: tenantId,
    activo: true,
    ...(busqueda && {
      OR: [
        { nombre: { contains: busqueda, mode: 'insensitive' as const } },
        { ciudad: { contains: busqueda, mode: 'insensitive' as const } },
      ],
    }),
  };

  const [hoteles, total] = await Promise.all([
    prisma.hotel.findMany({
      where, skip, take: limit,
      orderBy: { creadoEn: 'desc' },
      include: { _count: { select: { habitaciones: true } } },
    }),
    prisma.hotel.count({ where }),
  ]);

  return { hoteles, total, page, limit };
}

export async function obtenerHotel(tenantId: string, id: string) {
  const hotel = await prisma.hotel.findFirst({
    where: { id, empresaId: tenantId },
    include: {
      habitaciones: { where: { activo: true }, orderBy: { numero: 'asc' } },
    },
  });
  if (!hotel) throw new AppError('Hotel no encontrado', 404);
  return hotel;
}

export async function crearHotel(tenantId: string, data: Record<string, unknown>) {
  return prisma.hotel.create({ data: { empresaId: tenantId, ...(data as any) } });
}

export async function actualizarHotel(tenantId: string, id: string, data: Record<string, unknown>) {
  const hotel = await prisma.hotel.findFirst({ where: { id, empresaId: tenantId } });
  if (!hotel) throw new AppError('Hotel no encontrado', 404);
  return prisma.hotel.update({ where: { id }, data: data as any });
}

export async function eliminarHotel(tenantId: string, id: string) {
  const hotel = await prisma.hotel.findFirst({ where: { id, empresaId: tenantId } });
  if (!hotel) throw new AppError('Hotel no encontrado', 404);
  return prisma.hotel.update({ where: { id }, data: { activo: false } });
}

// ─── HABITACIONES ─────────────────────────────────────
export async function listarHabitaciones(tenantId: string, hotelId: string, query: Record<string, unknown>) {
  const estado = String(query.estado ?? '');
  const hotel = await prisma.hotel.findFirst({ where: { id: hotelId, empresaId: tenantId } });
  if (!hotel) throw new AppError('Hotel no encontrado', 404);

  return prisma.habitacion.findMany({
    where: {
      hotelId,
      empresaId: tenantId,
      activo: true,
      ...(estado && { estado }),
    },
    orderBy: { numero: 'asc' },
  });
}

export async function crearHabitacion(tenantId: string, hotelId: string, data: Record<string, unknown>) {
  const hotel = await prisma.hotel.findFirst({ where: { id: hotelId, empresaId: tenantId } });
  if (!hotel) throw new AppError('Hotel no encontrado', 404);

  const duplicado = await prisma.habitacion.findFirst({
    where: { hotelId, numero: String(data.numero) },
  });
  if (duplicado) throw new AppError('Ya existe una habitación con ese número', 409);

  return prisma.habitacion.create({
    data: { hotelId, empresaId: tenantId, ...(data as any) },
  });
}

export async function actualizarHabitacion(
  tenantId: string, id: string, data: Record<string, unknown>
) {
  const habitacion = await prisma.habitacion.findFirst({ where: { id, empresaId: tenantId } });
  if (!habitacion) throw new AppError('Habitación no encontrada', 404);
  return prisma.habitacion.update({ where: { id }, data: data as any });
}

export async function verificarDisponibilidad(
  tenantId: string,
  habitacionId: string,
  fechaInicio: Date,
  fechaFin: Date,
  excluirReservaId?: string
) {
  const reservaConflicto = await prisma.reserva.findFirst({
    where: {
      empresaId: tenantId,
      habitacionId,
      estado: { in: ['pendiente', 'confirmada'] },
      ...(excluirReservaId && { id: { not: excluirReservaId } }),
      OR: [
        { fechaInicio: { lte: fechaFin }, fechaFin: { gte: fechaInicio } },
      ],
    },
  });
  return !reservaConflicto;
}
