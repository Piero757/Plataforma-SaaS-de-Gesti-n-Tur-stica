import { Request, Response } from 'express';
import * as svc from './hoteles.service';
import { successResponse, paginatedResponse } from '../../shared/utils/response';

// ─── HOTELES ─────────────────────────────────
export async function listar(req: Request, res: Response) {
  const { hoteles, total, page, limit } = await svc.listarHoteles(req.tenantId!, req.query as any);
  res.json(paginatedResponse(hoteles, total, page, limit));
}

export async function obtener(req: Request, res: Response) {
  const hotel = await svc.obtenerHotel(req.tenantId!, req.params.id);
  res.json(successResponse(hotel));
}

export async function crear(req: Request, res: Response) {
  const hotel = await svc.crearHotel(req.tenantId!, req.body);
  res.status(201).json(successResponse(hotel, 'Hotel creado exitosamente'));
}

export async function actualizar(req: Request, res: Response) {
  const hotel = await svc.actualizarHotel(req.tenantId!, req.params.id, req.body);
  res.json(successResponse(hotel, 'Hotel actualizado'));
}

export async function eliminar(req: Request, res: Response) {
  await svc.eliminarHotel(req.tenantId!, req.params.id);
  res.json(successResponse(null, 'Hotel desactivado'));
}

// ─── HABITACIONES ─────────────────────────────
export async function listarHabitaciones(req: Request, res: Response) {
  const habitaciones = await svc.listarHabitaciones(req.tenantId!, req.params.hotelId, req.query as any);
  res.json(successResponse(habitaciones));
}

export async function crearHabitacion(req: Request, res: Response) {
  const habitacion = await svc.crearHabitacion(req.tenantId!, req.params.hotelId, req.body);
  res.status(201).json(successResponse(habitacion, 'Habitación creada'));
}

export async function actualizarHabitacion(req: Request, res: Response) {
  const habitacion = await svc.actualizarHabitacion(req.tenantId!, req.params.id, req.body);
  res.json(successResponse(habitacion, 'Habitación actualizada'));
}

export async function disponibilidad(req: Request, res: Response) {
  const { habitacionId, fechaInicio, fechaFin } = req.query as Record<string, string>;
  const disponible = await svc.verificarDisponibilidad(
    req.tenantId!, habitacionId,
    new Date(fechaInicio), new Date(fechaFin)
  );
  res.json(successResponse({ disponible }));
}
