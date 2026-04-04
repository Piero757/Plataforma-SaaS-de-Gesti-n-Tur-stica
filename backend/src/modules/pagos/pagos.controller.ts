import { Request, Response } from 'express';
import * as svc from './pagos.service';
import { successResponse, paginatedResponse } from '../../shared/utils/response';

export async function listar(req: Request, res: Response) {
  const { pagos, total, page, limit } = await svc.listarPagos(req.tenantId!, req.query as any);
  res.json(paginatedResponse(pagos, total, page, limit));
}
export async function obtener(req: Request, res: Response) {
  res.json(successResponse(await svc.obtenerPago(req.tenantId!, req.params.id)));
}
export async function registrar(req: Request, res: Response) {
  res.status(201).json(successResponse(await svc.registrarPago(req.tenantId!, req.body), 'Pago registrado'));
}
