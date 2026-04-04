import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import crypto from 'crypto';
import { prisma } from '../../config/database';
import { getRedisClient } from '../../config/redis';
import { env } from '../../config/env';
import { AppError } from '../../shared/utils/AppError';
import type { LoginInput, RegisterInput } from './auth.schema';

// =============================================
// GENERAR TOKENS
// =============================================
function generateAccessToken(userId: string, tenantId: string, rolNombre: string): string {
  return jwt.sign(
    { sub: userId, tenantId, rolNombre },
    env.JWT_SECRET,
    { expiresIn: env.JWT_EXPIRES_IN as jwt.SignOptions['expiresIn'] }
  );
}

function generateRefreshToken(): string {
  return crypto.randomBytes(64).toString('hex');
}

// =============================================
// LOGIN
// =============================================
export async function loginService(
  data: LoginInput,
  userAgent?: string,
  ip?: string
) {
  const { email, password } = data;

  // Buscar usuario por email (cualquier tenant — el email del tenant es único por empresa)
  const usuario = await prisma.usuario.findFirst({
    where: { email, activo: true },
    include: { rol: true, empresa: true },
  });

  if (!usuario) {
    throw new AppError('Credenciales inválidas', 401);
  }

  if (!usuario.empresa.activo) {
    throw new AppError('La empresa no se encuentra activa', 403);
  }

  const passwordValido = await bcrypt.compare(password, usuario.passwordHash);
  if (!passwordValido) {
    throw new AppError('Credenciales inválidas', 401);
  }

  // Generar tokens
  const accessToken = generateAccessToken(usuario.id, usuario.empresaId, usuario.rol.nombre);
  const refreshTokenRaw = generateRefreshToken();
  const tokenHash = crypto.createHash('sha256').update(refreshTokenRaw).digest('hex');

  // Guardar refresh token en DB
  const expiresAt = new Date();
  expiresAt.setDate(expiresAt.getDate() + 7);

  await prisma.refreshToken.create({
    data: {
      usuarioId: usuario.id,
      tokenHash,
      expiraEn: expiresAt,
      userAgent,
      ip,
    },
  });

  // Actualizar último login
  await prisma.usuario.update({
    where: { id: usuario.id },
    data: { ultimoLogin: new Date() },
  });

  return {
    accessToken,
    refreshToken: refreshTokenRaw,
    usuario: {
      id: usuario.id,
      nombre: usuario.nombre,
      email: usuario.email,
      rol: usuario.rol.nombre,
      avatarUrl: usuario.avatarUrl,
    },
    empresa: {
      id: usuario.empresa.id,
      nombre: usuario.empresa.nombre,
      slug: usuario.empresa.slug,
      logoUrl: usuario.empresa.logoUrl,
    },
  };
}

// =============================================
// REGISTRO DE NUEVA EMPRESA
// =============================================
export async function registerService(data: RegisterInput) {
  const {
    empresaNombre, empresaEmail, empresaTelefono,
    empresaPais, empresaCiudad, planId,
    nombre, email, password,
  } = data;

  // Verificar si el email de empresa ya existe
  const empresaExistente = await prisma.empresa.findUnique({ where: { email: empresaEmail } });
  if (empresaExistente) {
    throw new AppError('Ya existe una empresa registrada con ese email', 409);
  }

  // Generar slug único
  let slug = empresaNombre
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');

  const slugExistente = await prisma.empresa.findUnique({ where: { slug } });
  if (slugExistente) {
    slug = `${slug}-${Date.now()}`;
  }

  // Obtener plan (Básico por defecto)
  let planSeleccionado;
  if (planId) {
    planSeleccionado = await prisma.planSuscripcion.findUnique({ where: { id: planId } });
    if (!planSeleccionado) throw new AppError('Plan no encontrado', 404);
  } else {
    planSeleccionado = await prisma.planSuscripcion.findFirst({
      where: { nombre: 'Básico', activo: true },
    });
  }

  const passwordHash = await bcrypt.hash(password, env.BCRYPT_ROUNDS);

  // Crear empresa + rol admin + usuario admin en una transacción
  const resultado = await prisma.$transaction(async (tx) => {
    // 1. Crear empresa
    const empresa = await tx.empresa.create({
      data: {
        nombre: empresaNombre,
        slug,
        email: empresaEmail,
        telefono: empresaTelefono,
        pais: empresaPais,
        ciudad: empresaCiudad,
      },
    });

    // 2. Crear roles del sistema
    const rolAdmin = await tx.rol.create({
      data: {
        empresaId: empresa.id,
        nombre: 'admin',
        descripcion: 'Administrador con acceso completo',
        esSistema: true,
      },
    });

    await tx.rol.createMany({
      data: [
        { empresaId: empresa.id, nombre: 'gerente', descripcion: 'Gerente', esSistema: true },
        { empresaId: empresa.id, nombre: 'recepcionista', descripcion: 'Recepcionista', esSistema: true },
        { empresaId: empresa.id, nombre: 'agente', descripcion: 'Agente de viajes', esSistema: true },
      ],
    });

    // 3. Asignar todos los permisos al admin
    const todosLosPermisos = await tx.permiso.findMany();
    await tx.rolPermiso.createMany({
      data: todosLosPermisos.map((p) => ({ rolId: rolAdmin.id, permisoId: p.id })),
      skipDuplicates: true,
    });

    // 4. Crear usuario admin
    const usuario = await tx.usuario.create({
      data: {
        empresaId: empresa.id,
        rolId: rolAdmin.id,
        nombre,
        email,
        passwordHash,
      },
    });

    // 5. Crear suscripción
    if (planSeleccionado) {
      const fechaInicio = new Date();
      const fechaFin = new Date();
      fechaFin.setMonth(fechaFin.getMonth() + 1);

      await tx.suscripcion.create({
        data: {
          empresaId: empresa.id,
          planId: planSeleccionado.id,
          estado: 'activa',
          fechaInicio,
          fechaFin,
          precioPagado: planSeleccionado.precioMensual,
        },
      });
    }

    return { empresa, usuario, rolAdmin };
  });

  // Generar tokens para login automático
  const accessToken = generateAccessToken(resultado.usuario.id, resultado.empresa.id, 'admin');
  const refreshTokenRaw = generateRefreshToken();
  const tokenHash = crypto.createHash('sha256').update(refreshTokenRaw).digest('hex');
  const expiresAt = new Date();
  expiresAt.setDate(expiresAt.getDate() + 7);

  await prisma.refreshToken.create({
    data: {
      usuarioId: resultado.usuario.id,
      tokenHash,
      expiraEn: expiresAt,
    },
  });

  return {
    accessToken,
    refreshToken: refreshTokenRaw,
    usuario: {
      id: resultado.usuario.id,
      nombre: resultado.usuario.nombre,
      email: resultado.usuario.email,
      rol: 'admin',
    },
    empresa: {
      id: resultado.empresa.id,
      nombre: resultado.empresa.nombre,
      slug: resultado.empresa.slug,
    },
  };
}

// =============================================
// REFRESH TOKEN
// =============================================
export async function refreshTokenService(rawToken: string) {
  const tokenHash = crypto.createHash('sha256').update(rawToken).digest('hex');

  const storedToken = await prisma.refreshToken.findUnique({
    where: { tokenHash },
    include: { usuario: { include: { rol: true } } },
  });

  if (!storedToken || storedToken.revocado || storedToken.expiraEn < new Date()) {
    throw new AppError('Refresh token inválido o expirado', 401);
  }

  if (!storedToken.usuario.activo) {
    throw new AppError('Usuario inactivo', 401);
  }

  const { usuario } = storedToken;

  // Revocar token anterior (rotación)
  await prisma.refreshToken.update({
    where: { id: storedToken.id },
    data: { revocado: true },
  });

  // Generar nuevo par de tokens
  const newAccessToken = generateAccessToken(usuario.id, usuario.empresaId, usuario.rol.nombre);
  const newRefreshTokenRaw = generateRefreshToken();
  const newTokenHash = crypto.createHash('sha256').update(newRefreshTokenRaw).digest('hex');
  const expiresAt = new Date();
  expiresAt.setDate(expiresAt.getDate() + 7);

  await prisma.refreshToken.create({
    data: {
      usuarioId: usuario.id,
      tokenHash: newTokenHash,
      expiraEn: expiresAt,
    },
  });

  return { accessToken: newAccessToken, refreshToken: newRefreshTokenRaw };
}

// =============================================
// LOGOUT
// =============================================
export async function logoutService(rawToken: string) {
  const tokenHash = crypto.createHash('sha256').update(rawToken).digest('hex');
  await prisma.refreshToken.updateMany({
    where: { tokenHash },
    data: { revocado: true },
  });
}

// =============================================
// ME (perfil del usuario logueado)
// =============================================
export async function getMeService(userId: string) {
  return prisma.usuario.findUnique({
    where: { id: userId },
    select: {
      id: true,
      nombre: true,
      email: true,
      avatarUrl: true,
      ultimoLogin: true,
      creadoEn: true,
      rol: { select: { id: true, nombre: true } },
      empresa: {
        select: {
          id: true,
          nombre: true,
          slug: true,
          logoUrl: true,
          plan: false,
        },
      },
    },
  });
}
