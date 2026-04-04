import { prisma } from '../../config/database';

export async function getDashboardStats(tenantId: string) {
  const ahora = new Date();
  const inicioMes = new Date(ahora.getFullYear(), ahora.getMonth(), 1);
  const inicioMesAnterior = new Date(ahora.getFullYear(), ahora.getMonth() - 1, 1);
  const finMesAnterior = new Date(ahora.getFullYear(), ahora.getMonth(), 0);

  const [
    totalClientes,
    clientesMes,
    clientesMesAnterior,
    totalReservasMes,
    reservasMesAnterior,
    reservasPendientes,
    ingresosMes,
    ingresosMesAnterior,
    reservasPorEstado,
    ultimasReservas,
    ocupacionHoteles,
  ] = await Promise.all([
    // Clientes totales activos
    prisma.cliente.count({ where: { empresaId: tenantId, activo: true } }),

    // Clientes nuevos este mes
    prisma.cliente.count({
      where: { empresaId: tenantId, creadoEn: { gte: inicioMes } },
    }),

    // Clientes mes anterior (para % cambio)
    prisma.cliente.count({
      where: { empresaId: tenantId, creadoEn: { gte: inicioMesAnterior, lte: finMesAnterior } },
    }),

    // Reservas este mes
    prisma.reserva.count({
      where: { empresaId: tenantId, creadoEn: { gte: inicioMes } },
    }),

    // Reservas mes anterior
    prisma.reserva.count({
      where: { empresaId: tenantId, creadoEn: { gte: inicioMesAnterior, lte: finMesAnterior } },
    }),

    // Reservas pendientes
    prisma.reserva.count({ where: { empresaId: tenantId, estado: 'pendiente' } }),

    // Ingresos este mes
    prisma.pago.aggregate({
      where: { empresaId: tenantId, estado: 'completado', creadoEn: { gte: inicioMes } },
      _sum: { monto: true },
    }),

    // Ingresos mes anterior
    prisma.pago.aggregate({
      where: { empresaId: tenantId, estado: 'completado', creadoEn: { gte: inicioMesAnterior, lte: finMesAnterior } },
      _sum: { monto: true },
    }),

    // Reservas por estado
    prisma.reserva.groupBy({
      by: ['estado'],
      where: { empresaId: tenantId },
      _count: { estado: true },
    }),

    // Últimas 5 reservas
    prisma.reserva.findMany({
      where: { empresaId: tenantId },
      orderBy: { creadoEn: 'desc' },
      take: 5,
      include: {
        cliente: { select: { nombre: true, apellido: true } },
        habitacion: { select: { numero: true, tipo: true, hotel: { select: { nombre: true } } } },
        paquete: { select: { nombre: true } },
      },
    }),

    // Habitaciones disponibles vs total
    prisma.habitacion.groupBy({
      by: ['estado'],
      where: { empresaId: tenantId, activo: true },
      _count: { estado: true },
    }),
  ]);

  // Calcular % cambio
  function calcCambio(actual: number, anterior: number) {
    if (anterior === 0) return actual > 0 ? 100 : 0;
    return Math.round(((actual - anterior) / anterior) * 100);
  }

  const ingresosActual = Number(ingresosMes._sum.monto ?? 0);
  const ingresosAnterior = Number(ingresosMesAnterior._sum.monto ?? 0);

  return {
    kpis: {
      clientes: {
        total: totalClientes,
        mes: clientesMes,
        cambio: calcCambio(clientesMes, clientesMesAnterior),
      },
      reservas: {
        mes: totalReservasMes,
        pendientes: reservasPendientes,
        cambio: calcCambio(totalReservasMes, reservasMesAnterior),
      },
      ingresos: {
        mes: ingresosActual,
        cambio: calcCambio(ingresosActual, ingresosAnterior),
      },
    },
    reservasPorEstado: reservasPorEstado.map((r) => ({
      estado: r.estado,
      cantidad: r._count.estado,
    })),
    ultimasReservas,
    ocupacion: {
      disponibles: ocupacionHoteles.find((o) => o.estado === 'disponible')?._count.estado ?? 0,
      ocupadas: ocupacionHoteles.find((o) => o.estado === 'ocupada')?._count.estado ?? 0,
      mantenimiento: ocupacionHoteles.find((o) => o.estado === 'mantenimiento')?._count.estado ?? 0,
    },
  };
}

export async function getReporteReservas(tenantId: string, fechaDesde: Date, fechaHasta: Date) {
  return prisma.reserva.findMany({
    where: {
      empresaId: tenantId,
      creadoEn: { gte: fechaDesde, lte: fechaHasta },
    },
    include: {
      cliente: { select: { nombre: true, apellido: true, email: true } },
      habitacion: { select: { numero: true, tipo: true, hotel: { select: { nombre: true } } } },
      paquete: { select: { nombre: true } },
      pagos: { select: { monto: true, metodoPago: true, estado: true } },
    },
    orderBy: { creadoEn: 'asc' },
  });
}

export async function getReporteIngresos(tenantId: string, anio: number) {
  // Ingresos por mes del año solicitado
  const pagos = await prisma.pago.findMany({
    where: {
      empresaId: tenantId,
      estado: 'completado',
      creadoEn: {
        gte: new Date(`${anio}-01-01`),
        lte: new Date(`${anio}-12-31T23:59:59`),
      },
    },
    select: { monto: true, creadoEn: true, metodoPago: true },
  });

  // Agrupar por mes
  const porMes: Record<number, number> = {};
  pagos.forEach((p) => {
    const mes = new Date(p.creadoEn).getMonth() + 1;
    porMes[mes] = (porMes[mes] ?? 0) + Number(p.monto);
  });

  const meses = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
  return meses.map((nombre, i) => ({
    mes: nombre,
    ingresos: porMes[i + 1] ?? 0,
  }));
}

export async function getReporteOcupacion(tenantId: string) {
  const hoteles = await prisma.hotel.findMany({
    where: { empresaId: tenantId, activo: true },
    include: {
      habitaciones: {
        where: { activo: true },
        select: { estado: true },
      },
    },
  });

  return hoteles.map((hotel) => {
    const total = hotel.habitaciones.length;
    const ocupadas = hotel.habitaciones.filter((h) => h.estado === 'ocupada').length;
    const disponibles = hotel.habitaciones.filter((h) => h.estado === 'disponible').length;
    return {
      hotel: hotel.nombre,
      total,
      ocupadas,
      disponibles,
      tasaOcupacion: total > 0 ? Math.round((ocupadas / total) * 100) : 0,
    };
  });
}
