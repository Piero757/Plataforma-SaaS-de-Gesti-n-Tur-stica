import { Router } from 'express';
import * as ctrl from './reportes.controller';
import { authMiddleware } from '../../middleware/auth.middleware';
import { rbac } from '../../middleware/rbac.middleware';

const router = Router();
router.use(authMiddleware);

router.get('/dashboard',          ctrl.dashboard);
router.get('/reservas',           rbac('reportes', 'leer'), ctrl.reporteReservas);
router.get('/ingresos',           rbac('reportes', 'leer'), ctrl.reporteIngresos);
router.get('/ocupacion',          rbac('reportes', 'leer'), ctrl.reporteOcupacion);

export default router;
