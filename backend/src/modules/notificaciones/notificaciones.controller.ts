import { Request, Response } from 'express';
import * as svc from './notificaciones.service';
import { successResponse, paginatedResponse } from '../../shared/utils/response';

export async function listar(req: Request, res: Response) {
  const { notificaciones, total, page, limit, noLeidas } = await svc.listarNotificaciones(
    req.tenantId!, req.user!.sub, req.query as any
  );
  res.json({ ...paginatedResponse(notificaciones, total, page, limit), noLeidas });
}

export async function marcarLeida(req: Request, res: Response) {
  await svc.marcarComoLeida(req.tenantId!, req.user!.sub, req.params.id);
  res.json(successResponse(null, 'Notificación marcada como leída'));
}

export async function marcarTodasLeidas(req: Request, res: Response) {
  await svc.marcarTodasLeidas(req.tenantId!, req.user!.sub);
  res.json(successResponse(null, 'Todas las notificaciones marcadas como leídas'));
}
