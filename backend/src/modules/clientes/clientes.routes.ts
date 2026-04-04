import { Router } from 'express';
import * as ctrl from './clientes.controller';
import { authMiddleware } from '../../middleware/auth.middleware';
import { rbac } from '../../middleware/rbac.middleware';

const router = Router();
router.use(authMiddleware);

router.get('/',          rbac('clientes', 'leer'),       ctrl.listar);
router.post('/',         rbac('clientes', 'crear'),      ctrl.crear);
router.get('/:id',       rbac('clientes', 'leer'),       ctrl.obtener);
router.put('/:id',       rbac('clientes', 'actualizar'), ctrl.actualizar);
router.delete('/:id',    rbac('clientes', 'eliminar'),   ctrl.eliminar);

export default router;
