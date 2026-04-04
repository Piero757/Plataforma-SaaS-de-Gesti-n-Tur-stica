import { Router } from 'express';
import * as authController from './auth.controller';
import { authMiddleware } from '../../middleware/auth.middleware';
import { validate } from '../../middleware/validate.middleware';
import {
  loginSchema,
  registerSchema,
  refreshSchema,
} from './auth.schema';

const router = Router();

/**
 * @swagger
 * /api/auth/login:
 *   post:
 *     summary: Iniciar sesión
 *     tags: [Auth]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [email, password]
 *             properties:
 *               email:
 *                 type: string
 *               password:
 *                 type: string
 */
router.post('/login', validate(loginSchema), authController.login);

/**
 * @swagger
 * /api/auth/register:
 *   post:
 *     summary: Registrar nueva empresa y usuario admin
 *     tags: [Auth]
 */
router.post('/register', validate(registerSchema), authController.register);

/**
 * @swagger
 * /api/auth/refresh:
 *   post:
 *     summary: Renovar access token usando refresh token
 *     tags: [Auth]
 */
router.post('/refresh', validate(refreshSchema), authController.refresh);

/**
 * @swagger
 * /api/auth/logout:
 *   post:
 *     summary: Cerrar sesión
 *     tags: [Auth]
 *     security:
 *       - bearerAuth: []
 */
router.post('/logout', validate(refreshSchema), authController.logout);

/**
 * @swagger
 * /api/auth/me:
 *   get:
 *     summary: Obtener perfil del usuario autenticado
 *     tags: [Auth]
 *     security:
 *       - bearerAuth: []
 */
router.get('/me', authMiddleware, authController.me);

export default router;
