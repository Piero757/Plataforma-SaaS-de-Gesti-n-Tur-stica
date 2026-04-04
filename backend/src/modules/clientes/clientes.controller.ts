import { Request, Response } from 'express';
import * as svc from './clientes.service';
import { successResponse, paginatedResponse } from '../../shared/utils/response';

export async function listar(req: Request, res: Response) {
  const { clientes, total, page, limit } = await svc.listarClientes(req.tenantId!, req.query as any);
  res.json(paginatedResponse(clientes, total, page, limit));
}

export async function obtener(req: Request, res: Response) {
  const cliente = await svc.obtenerCliente(req.tenantId!, req.params.id);
  res.json(successResponse(cliente));
}

export async function crear(req: Request, res: Response) {
  const cliente = await svc.crearCliente(req.tenantId!, req.body);
  res.status(201).json(successResponse(cliente, 'Cliente creado exitosamente'));
}

export async function actualizar(req: Request, res: Response) {
  const cliente = await svc.actualizarCliente(req.tenantId!, req.params.id, req.body);
  res.json(successResponse(cliente, 'Cliente actualizado'));
}

export async function eliminar(req: Request, res: Response) {
  await svc.eliminarCliente(req.tenantId!, req.params.id);
  res.json(successResponse(null, 'Cliente desactivado'));
}
