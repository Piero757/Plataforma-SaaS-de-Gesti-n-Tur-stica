import { Request, Response } from 'express';
import * as svc from './paquetes.service';
import { successResponse, paginatedResponse } from '../../shared/utils/response';

export async function listar(req: Request, res: Response) {
  const { paquetes, total, page, limit } = await svc.listarPaquetes(req.tenantId!, req.query as any);
  res.json(paginatedResponse(paquetes, total, page, limit));
}
export async function obtener(req: Request, res: Response) {
  res.json(successResponse(await svc.obtenerPaquete(req.tenantId!, req.params.id)));
}
export async function crear(req: Request, res: Response) {
  res.status(201).json(successResponse(await svc.crearPaquete(req.tenantId!, req.body), 'Paquete creado'));
}
export async function actualizar(req: Request, res: Response) {
  res.json(successResponse(await svc.actualizarPaquete(req.tenantId!, req.params.id, req.body), 'Paquete actualizado'));
}
export async function eliminar(req: Request, res: Response) {
  await svc.eliminarPaquete(req.tenantId!, req.params.id);
  res.json(successResponse(null, 'Paquete desactivado'));
}
