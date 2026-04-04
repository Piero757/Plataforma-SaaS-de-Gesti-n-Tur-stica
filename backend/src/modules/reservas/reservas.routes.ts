import { Router } from 'express';
import * as ctrl from './reservas.controller';
import { authMiddleware } from '../../middleware/auth.middleware';
import { rbac } from '../../middleware/rbac.middleware';

const router = Router();
router.use(authMiddleware);

router.get('/',                  rbac('reservas', 'leer'),       ctrl.listar);
router.post('/',                 rbac('reservas', 'crear'),      ctrl.crear);
router.get('/:id',               rbac('reservas', 'leer'),       ctrl.obtener);
router.put('/:id',               rbac('reservas', 'actualizar'), ctrl.actualizar);
router.put('/:id/confirmar',     rbac('reservas', 'actualizar'), ctrl.confirmar);
router.put('/:id/cancelar',      rbac('reservas', 'actualizar'), ctrl.cancelar);
router.put('/:id/completar',     rbac('reservas', 'actualizar'), ctrl.completar);

export default router;
