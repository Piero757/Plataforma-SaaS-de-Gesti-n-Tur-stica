import bcrypt from 'bcryptjs';
import { prisma } from '../../config/database';
import { AppError } from '../../shared/utils/AppError';
import { parsePagination } from '../../shared/utils/response';
import { env } from '../../config/env';

export async function listarUsuarios(tenantId: string, query: Record<string, unknown>) {
  const { page, limit, skip } = parsePagination(query);
  const [usuarios, total] = await Promise.all([
    prisma.usuario.findMany({
      where: { empresaId: tenantId },
      skip, take: limit,
      orderBy: { creadoEn: 'desc' },
      select: {
        id: true, nombre: true, email: true, activo: true,
        ultimoLogin: true, creadoEn: true, avatarUrl: true,
        rol: { select: { id: true, nombre: true } },
      },
    }),
    prisma.usuario.count({ where: { empresaId: tenantId } }),
  ]);
  return { usuarios, total, page, limit };
}

export async function crearUsuario(tenantId: string, data: Record<string, unknown>) {
  const { nombre, email, password, rolId } = data as any;

  const existente = await prisma.usuario.findFirst({
    where: { empresaId: tenantId, email },
  });
  if (existente) throw new AppError('Ya existe un usuario con ese email', 409);

  const rol = await prisma.rol.findFirst({ where: { id: rolId, empresaId: tenantId } });
  if (!rol) throw new AppError('Rol no encontrado', 404);

  const passwordHash = await bcrypt.hash(password, env.BCRYPT_ROUNDS);

  return prisma.usuario.create({
    data: { empresaId: tenantId, nombre, email, passwordHash, rolId },
    select: { id: true, nombre: true, email: true, creadoEn: true, rol: { select: { nombre: true } } },
  });
}

export async function actualizarUsuario(tenantId: string, id: string, data: Record<string, unknown>) {
  const usuario = await prisma.usuario.findFirst({ where: { id, empresaId: tenantId } });
  if (!usuario) throw new AppError('Usuario no encontrado', 404);

  // Si envían nueva contraseña
  const updateData: Record<string, unknown> = { ...data };
  if (updateData.password) {
    updateData.passwordHash = await bcrypt.hash(String(updateData.password), env.BCRYPT_ROUNDS);
    delete updateData.password;
  }
  delete updateData.email; // email no se puede cambiar via este endpoint

  return prisma.usuario.update({
    where: { id },
    data: updateData as any,
    select: { id: true, nombre: true, email: true, activo: true, rol: { select: { nombre: true } } },
  });
}

export async function desactivarUsuario(tenantId: string, id: string, adminId: string) {
  if (id === adminId) throw new AppError('No puedes desactivarte a ti mismo', 400);
  const usuario = await prisma.usuario.findFirst({ where: { id, empresaId: tenantId } });
  if (!usuario) throw new AppError('Usuario no encontrado', 404);
  return prisma.usuario.update({ where: { id }, data: { activo: false } });
}

// ─── ROLES ────────────────────────────────────────────────
export async function listarRoles(tenantId: string) {
  return prisma.rol.findMany({
    where: { empresaId: tenantId },
    include: { _count: { select: { usuarios: true } }, permisos: { include: { permiso: true } } },
  });
}

export async function crearRol(tenantId: string, data: Record<string, unknown>) {
  const { nombre, descripcion, permisoIds } = data as any;
  const existente = await prisma.rol.findFirst({ where: { empresaId: tenantId, nombre } });
  if (existente) throw new AppError('Ya existe un rol con ese nombre', 409);

  const rol = await prisma.rol.create({
    data: { empresaId: tenantId, nombre, descripcion },
  });

  if (permisoIds?.length) {
    await prisma.rolPermiso.createMany({
      data: permisoIds.map((pid: string) => ({ rolId: rol.id, permisoId: pid })),
      skipDuplicates: true,
    });
  }
  return rol;
}

export async function actualizarPermisos(tenantId: string, rolId: string, permisoIds: string[]) {
  const rol = await prisma.rol.findFirst({ where: { id: rolId, empresaId: tenantId } });
  if (!rol) throw new AppError('Rol no encontrado', 404);
  if (rol.esSistema && rol.nombre === 'admin') throw new AppError('No se pueden modificar los permisos del admin', 400);

  await prisma.rolPermiso.deleteMany({ where: { rolId } });
  if (permisoIds.length) {
    await prisma.rolPermiso.createMany({
      data: permisoIds.map((pid) => ({ rolId, permisoId: pid })),
      skipDuplicates: true,
    });
  }
  return prisma.permiso.findMany({ where: { id: { in: permisoIds } } });
}
