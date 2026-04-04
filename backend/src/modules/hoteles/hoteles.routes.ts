import { Router } from 'express';
import * as ctrl from './hoteles.controller';
import { authMiddleware } from '../../middleware/auth.middleware';
import { rbac } from '../../middleware/rbac.middleware';

const router = Router();
router.use(authMiddleware);

// Disponibilidad (sin RBAC — solo auth)
router.get('/disponibilidad', ctrl.disponibilidad);

// Hoteles CRUD
router.get('/',     rbac('hoteles', 'leer'),       ctrl.listar);
router.post('/',    rbac('hoteles', 'crear'),       ctrl.crear);
router.get('/:id',  rbac('hoteles', 'leer'),        ctrl.obtener);
router.put('/:id',  rbac('hoteles', 'actualizar'),  ctrl.actualizar);
router.delete('/:id', rbac('hoteles', 'eliminar'),  ctrl.eliminar);

// Habitaciones por hotel
router.get('/:hotelId/habitaciones',  rbac('habitaciones', 'leer'),   ctrl.listarHabitaciones);
router.post('/:hotelId/habitaciones', rbac('habitaciones', 'crear'),  ctrl.crearHabitacion);

export default router;
