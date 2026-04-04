import { Request, Response } from 'express';
import * as svc from './reservas.service';
import { successResponse, paginatedResponse } from '../../shared/utils/response';

export async function listar(req: Request, res: Response) {
  const { reservas, total, page, limit } = await svc.listarReservas(req.tenantId!, req.query as any);
  res.json(paginatedResponse(reservas, total, page, limit));
}

export async function obtener(req: Request, res: Response) {
  const reserva = await svc.obtenerReserva(req.tenantId!, req.params.id);
  res.json(successResponse(reserva));
}

export async function crear(req: Request, res: Response) {
  const reserva = await svc.crearReserva(req.tenantId!, req.user!.sub, req.body);
  res.status(201).json(successResponse(reserva, 'Reserva creada exitosamente'));
}

export async function actualizar(req: Request, res: Response) {
  const reserva = await svc.actualizarReserva(req.tenantId!, req.params.id, req.body);
  res.json(successResponse(reserva, 'Reserva actualizada'));
}

export async function confirmar(req: Request, res: Response) {
  const r = await svc.actualizarEstadoReserva(req.tenantId!, req.params.id, 'confirmada', req.user!.sub);
  res.json(successResponse(r, 'Reserva confirmada'));
}

export async function cancelar(req: Request, res: Response) {
  const r = await svc.actualizarEstadoReserva(req.tenantId!, req.params.id, 'cancelada', req.user!.sub);
  res.json(successResponse(r, 'Reserva cancelada'));
}

export async function completar(req: Request, res: Response) {
  const r = await svc.actualizarEstadoReserva(req.tenantId!, req.params.id, 'completada', req.user!.sub);
  res.json(successResponse(r, 'Reserva completada'));
}
