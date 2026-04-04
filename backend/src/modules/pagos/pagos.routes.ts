import { Router } from 'express';
import * as ctrl from './pagos.controller';
import { authMiddleware } from '../../middleware/auth.middleware';
import { rbac } from '../../middleware/rbac.middleware';

const router = Router();
router.use(authMiddleware);

router.get('/',      rbac('pagos', 'leer'),   ctrl.listar);
router.get('/:id',   rbac('pagos', 'leer'),   ctrl.obtener);
router.post('/',     rbac('pagos', 'crear'),  ctrl.registrar);

export default router;
