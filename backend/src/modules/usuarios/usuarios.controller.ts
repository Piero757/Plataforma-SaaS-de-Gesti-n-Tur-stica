import { Request, Response } from 'express';
import * as svc from './usuarios.service';
import { successResponse, paginatedResponse } from '../../shared/utils/response';

export async function listar(req: Request, res: Response) {
  const { usuarios, total, page, limit } = await svc.listarUsuarios(req.tenantId!, req.query as any);
  res.json(paginatedResponse(usuarios, total, page, limit));
}
export async function crear(req: Request, res: Response) {
  res.status(201).json(successResponse(await svc.crearUsuario(req.tenantId!, req.body), 'Usuario creado'));
}
export async function actualizar(req: Request, res: Response) {
  res.json(successResponse(await svc.actualizarUsuario(req.tenantId!, req.params.id, req.body)));
}
export async function desactivar(req: Request, res: Response) {
  await svc.desactivarUsuario(req.tenantId!, req.params.id, req.user!.sub);
  res.json(successResponse(null, 'Usuario desactivado'));
}
export async function listarRoles(req: Request, res: Response) {
  res.json(successResponse(await svc.listarRoles(req.tenantId!)));
}
export async function crearRol(req: Request, res: Response) {
  res.status(201).json(successResponse(await svc.crearRol(req.tenantId!, req.body), 'Rol creado'));
}
export async function actualizarPermisos(req: Request, res: Response) {
  const permisos = await svc.actualizarPermisos(req.tenantId!, req.params.rolId, req.body.permisoIds);
  res.json(successResponse(permisos, 'Permisos actualizados'));
}
