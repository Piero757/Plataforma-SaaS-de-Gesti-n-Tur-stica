import { Request, Response } from 'express';
import * as svc from './reportes.service';
import { successResponse } from '../../shared/utils/response';
import { AppError } from '../../shared/utils/AppError';

export async function dashboard(req: Request, res: Response) {
  const stats = await svc.getDashboardStats(req.tenantId!);
  res.json(successResponse(stats));
}

export async function reporteReservas(req: Request, res: Response) {
  const { fechaDesde, fechaHasta } = req.query as Record<string, string>;
  if (!fechaDesde || !fechaHasta) throw new AppError('fechaDesde y fechaHasta son requeridas', 400);
  const reservas = await svc.getReporteReservas(req.tenantId!, new Date(fechaDesde), new Date(fechaHasta));
  res.json(successResponse(reservas));
}

export async function reporteIngresos(req: Request, res: Response) {
  const anio = parseInt(String(req.query.anio ?? new Date().getFullYear()));
  const data = await svc.getReporteIngresos(req.tenantId!, anio);
  res.json(successResponse(data));
}

export async function reporteOcupacion(req: Request, res: Response) {
  const data = await svc.getReporteOcupacion(req.tenantId!);
  res.json(successResponse(data));
}
