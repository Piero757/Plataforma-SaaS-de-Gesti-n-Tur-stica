import { Request, Response, NextFunction } from 'express';
import { prisma } from '../config/database';
import { AppError } from '../shared/utils/AppError';

/**
 * Middleware RBAC — verifica que el usuario tiene el permiso requerido
 * Uso: router.get('/clientes', auth, rbac('clientes', 'leer'), controller)
 */
export function rbac(modulo: string, accion: string) {
  return async (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      throw new AppError('No autenticado', 401);
    }

    const { rolNombre, tenantId } = req.user;

    // El admin siempre tiene acceso completo
    if (rolNombre === 'admin') {
      return next();
    }

    // Buscar el rol del usuario
    const rol = await prisma.rol.findFirst({
      where: { nombre: rolNombre, empresaId: tenantId },
      include: {
        permisos: {
          include: { permiso: true },
        },
      },
    });

    if (!rol) {
      throw new AppError('Rol no encontrado', 403);
    }

    // Verificar si tiene el permiso requerido
    const tienePermiso = rol.permisos.some(
      (rp) => rp.permiso.modulo === modulo && rp.permiso.accion === accion
    );

    if (!tienePermiso) {
      throw new AppError(
        `No tienes permiso para ${accion} ${modulo}`,
        403
      );
    }

    next();
  };
}
