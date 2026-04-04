import { Router } from 'express';
import * as ctrl from './notificaciones.controller';
import { authMiddleware } from '../../middleware/auth.middleware';

const router = Router();
router.use(authMiddleware);

router.get('/',                    ctrl.listar);
router.put('/:id/leer',            ctrl.marcarLeida);
router.put('/leer-todas',          ctrl.marcarTodasLeidas);

export default router;
