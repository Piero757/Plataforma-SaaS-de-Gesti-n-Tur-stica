import { z } from 'zod';

export const loginSchema = z.object({
  body: z.object({
    email: z.string().email('Email inválido'),
    password: z.string().min(6, 'Contraseña mínimo 6 caracteres'),
  }),
});

export const registerSchema = z.object({
  body: z.object({
    // Datos de la empresa
    empresaNombre: z.string().min(2, 'Nombre de empresa mínimo 2 caracteres').max(200),
    empresaEmail: z.string().email('Email de empresa inválido'),
    empresaTelefono: z.string().optional(),
    empresaPais: z.string().optional(),
    empresaCiudad: z.string().optional(),
    planId: z.string().uuid('Plan ID inválido').optional(),

    // Datos del usuario admin
    nombre: z.string().min(2, 'Nombre mínimo 2 caracteres').max(200),
    email: z.string().email('Email de usuario inválido'),
    password: z
      .string()
      .min(8, 'Contraseña mínimo 8 caracteres')
      .regex(/[A-Z]/, 'Debe tener al menos una mayúscula')
      .regex(/[0-9]/, 'Debe tener al menos un número'),
  }),
});

export const refreshSchema = z.object({
  body: z.object({
    refreshToken: z.string().min(1, 'Refresh token requerido'),
  }),
});

export const changePasswordSchema = z.object({
  body: z.object({
    currentPassword: z.string().min(6),
    newPassword: z
      .string()
      .min(8, 'Nueva contraseña mínimo 8 caracteres')
      .regex(/[A-Z]/, 'Debe tener al menos una mayúscula')
      .regex(/[0-9]/, 'Debe tener al menos un número'),
  }),
});

export const forgotPasswordSchema = z.object({
  body: z.object({
    email: z.string().email('Email inválido'),
  }),
});

export type LoginInput = z.infer<typeof loginSchema>['body'];
export type RegisterInput = z.infer<typeof registerSchema>['body'];
export type RefreshInput = z.infer<typeof refreshSchema>['body'];
