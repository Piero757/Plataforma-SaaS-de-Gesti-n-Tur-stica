import { prisma } from '../../config/database';
import { AppError } from '../../shared/utils/AppError';
import { parsePagination } from '../../shared/utils/response';
import { verificarDisponibilidad } from '../hoteles/hoteles.service';
import { v4 as uuidv4 } from 'uuid';

function generarCodigoReserva(): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let codigo = 'RES-';
  for (let i = 0; i < 8; i++) {
    codigo += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return codigo;
}

export async function listarReservas(tenantId: string, query: Record<string, unknown>) {
  const { page, limit, skip } = parsePagination(query);
  const { estado, tipo, clienteId, fechaDesde, fechaHasta } = query as Record<string, string>;

  const where: Record<string, unknown> = {
    empresaId: tenantId,
    ...(estado && { estado }),
    ...(tipo && { tipo }),
    ...(clienteId && { clienteId }),
    ...(fechaDesde && fechaHasta && {
      fechaInicio: { gte: new Date(fechaDesde) },
      fechaFin: { lte: new Date(fechaHasta) },
    }),
  };

  const [reservas, total] = await Promise.all([
    prisma.reserva.findMany({
      where,
      skip,
      take: limit,
      orderBy: { creadoEn: 'desc' },
      include: {
        cliente: { select: { id: true, nombre: true, apellido: true, email: true, telefono: true } },
        habitacion: { select: { id: true, numero: true, tipo: true, hotel: { select: { nombre: true } } } },
        paquete: { select: { id: true, nombre: true } },
        usuario: { select: { id: true, nombre: true } },
        _count: { select: { pagos: true } },
      },
    }),
    prisma.reserva.count({ where }),
  ]);

  return { reservas, total, page, limit };
}

export async function obtenerReserva(tenantId: string, id: string) {
  const reserva = await prisma.reserva.findFirst({
    where: { id, empresaId: tenantId },
    include: {
      cliente: true,
      habitacion: { include: { hotel: true } },
      paquete: true,
      usuario: { select: { id: true, nombre: true, email: true } },
      pagos: { orderBy: { creadoEn: 'desc' } },
      facturas: { orderBy: { creadoEn: 'desc' } },
    },
  });
  if (!reserva) throw new AppError('Reserva no encontrada', 404);
  return reserva;
}

export async function crearReserva(tenantId: string, usuarioId: string, data: Record<string, unknown>) {
  const { clienteId, habitacionId, paqueteId, tipo, fechaInicio, fechaFin, numPersonas, precioTotal, notas } = data as any;

  // Validar cliente pertenece al tenant
  const cliente = await prisma.cliente.findFirst({ where: { id: clienteId, empresaId: tenantId } });
  if (!cliente) throw new AppError('Cliente no encontrado', 404);

  // Validaciones específicas por tipo
  if (tipo === 'hotel') {
    if (!habitacionId) throw new AppError('Se requiere habitación para reserva de hotel', 400);

    const habitacion = await prisma.habitacion.findFirst({
      where: { id: habitacionId, empresaId: tenantId, activo: true },
    });
    if (!habitacion) throw new AppError('Habitación no encontrada', 404);
    if (habitacion.estado === 'mantenimiento') throw new AppError('La habitación está en mantenimiento', 400);

    const disponible = await verificarDisponibilidad(
      tenantId, habitacionId, new Date(fechaInicio), new Date(fechaFin)
    );
    if (!disponible) throw new AppError('La habitación no está disponible en las fechas seleccionadas', 409);
  } else if (tipo === 'paquete') {
    if (!paqueteId) throw new AppError('Se requiere paquete turístico', 400);
    const paquete = await prisma.paqueteTuristico.findFirst({
      where: { id: paqueteId, empresaId: tenantId, activo: true },
    });
    if (!paquete) throw new AppError('Paquete turístico no encontrado', 404);
    if (paquete.maxPersonas && numPersonas > paquete.maxPersonas) {
      throw new AppError(`El paquete tiene un máximo de ${paquete.maxPersonas} personas`, 400);
    }
  }

  // Generar código único
  let codigoRef = generarCodigoReserva();
  while (await prisma.reserva.findUnique({ where: { codigoRef } })) {
    codigoRef = generarCodigoReserva();
  }

  const reserva = await prisma.reserva.create({
    data: {
      empresaId: tenantId,
      clienteId,
      habitacionId: tipo === 'hotel' ? habitacionId : null,
      paqueteId: tipo === 'paquete' ? paqueteId : null,
      usuarioId,
      tipo,
      fechaInicio: new Date(fechaInicio),
      fechaFin: new Date(fechaFin),
      numPersonas: Number(numPersonas) || 1,
      precioTotal: Number(precioTotal),
      notas: notas || null,
      codigoRef,
      estado: 'pendiente',
    },
    include: {
      cliente: { select: { nombre: true, apellido: true, email: true } },
      habitacion: { select: { numero: true, tipo: true } },
      paquete: { select: { nombre: true } },
    },
  });

  // Crear notificación
  await prisma.notificacion.create({
    data: {
      empresaId: tenantId,
      usuarioId,
      titulo: 'Nueva reserva creada',
      mensaje: `Reserva ${codigoRef} para ${cliente.nombre} ${cliente.apellido} registrada exitosamente.`,
      tipo: 'reserva',
      url: `/reservas/${reserva.id}`,
    },
  });

  return reserva;
}

export async function actualizarEstadoReserva(
  tenantId: string,
  id: string,
  nuevoEstado: 'confirmada' | 'cancelada' | 'completada',
  usuarioId: string
) {
  const reserva = await prisma.reserva.findFirst({ where: { id, empresaId: tenantId } });
  if (!reserva) throw new AppError('Reserva no encontrada', 404);

  // Validar transiciones de estado permitidas
  const transicionesPermitidas: Record<string, string[]> = {
    pendiente: ['confirmada', 'cancelada'],
    confirmada: ['completada', 'cancelada'],
    completada: [],
    cancelada: [],
  };

  if (!transicionesPermitidas[reserva.estado]?.includes(nuevoEstado)) {
    throw new AppError(
      `No se puede cambiar de "${reserva.estado}" a "${nuevoEstado}"`,
      400
    );
  }

  const reservaActualizada = await prisma.reserva.update({
    where: { id },
    data: { estado: nuevoEstado },
  });

  // Si se cancela, liberar habitación (solo actualizar estado de la hab si se necesita)
  if (nuevoEstado === 'cancelada' && reserva.habitacionId) {
    await prisma.habitacion.update({
      where: { id: reserva.habitacionId },
      data: { estado: 'disponible' },
    });
  }

  // Notificación de cambio
  await prisma.notificacion.create({
    data: {
      empresaId: tenantId,
      usuarioId,
      titulo: `Reserva ${nuevoEstado}`,
      mensaje: `La reserva ${reserva.codigoRef} ha sido ${nuevoEstado}.`,
      tipo: 'reserva',
      url: `/reservas/${id}`,
    },
  });

  return reservaActualizada;
}

export async function actualizarReserva(tenantId: string, id: string, data: Record<string, unknown>) {
  const reserva = await prisma.reserva.findFirst({ where: { id, empresaId: tenantId } });
  if (!reserva) throw new AppError('Reserva no encontrada', 404);

  if (reserva.estado === 'cancelada' || reserva.estado === 'completada') {
    throw new AppError('No se puede modificar una reserva completada o cancelada', 400);
  }

  return prisma.reserva.update({ where: { id }, data: data as any });
}
