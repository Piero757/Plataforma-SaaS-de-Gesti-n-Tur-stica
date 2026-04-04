import { Router } from 'express';
import { authMiddleware } from '../../middleware/auth.middleware';
import { rbac } from '../../middleware/rbac.middleware';
import { Request, Response } from 'express';
import * as svc from './empleados.service';
import { successResponse, paginatedResponse } from '../../shared/utils/response';

const router = Router();
router.use(authMiddleware);

router.get('/', rbac('empleados', 'leer'), async (req: Request, res: Response) => {
  const { empleados, total, page, limit } = await svc.listarEmpleados(req.tenantId!, req.query as any);
  res.json(paginatedResponse(empleados, total, page, limit));
});

router.post('/', rbac('empleados', 'crear'), async (req: Request, res: Response) => {
  res.status(201).json(successResponse(await svc.crearEmpleado(req.tenantId!, req.body), 'Empleado creado'));
});

router.put('/:id', rbac('empleados', 'actualizar'), async (req: Request, res: Response) => {
  res.json(successResponse(await svc.actualizarEmpleado(req.tenantId!, req.params.id, req.body)));
});

router.delete('/:id', rbac('empleados', 'eliminar'), async (req: Request, res: Response) => {
  await svc.eliminarEmpleado(req.tenantId!, req.params.id);
  res.json(successResponse(null, 'Empleado desactivado'));
});

export default router;
