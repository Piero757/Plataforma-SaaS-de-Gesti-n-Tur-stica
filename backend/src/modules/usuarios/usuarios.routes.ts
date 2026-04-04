import { Router } from 'express';
import * as ctrl from './usuarios.controller';
import { authMiddleware } from '../../middleware/auth.middleware';
import { rbac } from '../../middleware/rbac.middleware';

const router = Router();
router.use(authMiddleware);

// Usuarios
router.get('/',              rbac('usuarios', 'leer'),       ctrl.listar);
router.post('/',             rbac('usuarios', 'crear'),      ctrl.crear);
router.put('/:id',           rbac('usuarios', 'actualizar'), ctrl.actualizar);
router.delete('/:id',        rbac('usuarios', 'eliminar'),   ctrl.desactivar);

// Roles
router.get('/roles',                      rbac('roles', 'leer'),       ctrl.listarRoles);
router.post('/roles',                     rbac('roles', 'crear'),      ctrl.crearRol);
router.put('/roles/:rolId/permisos',      rbac('roles', 'actualizar'), ctrl.actualizarPermisos);

export default router;
