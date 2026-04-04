import { Router } from 'express';
import * as ctrl from './paquetes.controller';
import { authMiddleware } from '../../middleware/auth.middleware';
import { rbac } from '../../middleware/rbac.middleware';

const router = Router();
router.use(authMiddleware);

router.get('/',        rbac('paquetes', 'leer'),       ctrl.listar);
router.post('/',       rbac('paquetes', 'crear'),      ctrl.crear);
router.get('/:id',     rbac('paquetes', 'leer'),       ctrl.obtener);
router.put('/:id',     rbac('paquetes', 'actualizar'), ctrl.actualizar);
router.delete('/:id',  rbac('paquetes', 'eliminar'),   ctrl.eliminar);

export default router;
