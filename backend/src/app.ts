import 'express-async-errors';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';
import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';

import { env } from './config/env';
import { logger } from './config/logger';
import { errorMiddleware, notFoundMiddleware } from './middleware/error.middleware';

// Rutas
import authRoutes from './modules/auth/auth.routes';
import clientesRoutes from './modules/clientes/clientes.routes';
import hotelesRoutes from './modules/hoteles/hoteles.routes';
import reservasRoutes from './modules/reservas/reservas.routes';
import paquetesRoutes from './modules/paquetes/paquetes.routes';
import pagosRoutes from './modules/pagos/pagos.routes';
import usuariosRoutes from './modules/usuarios/usuarios.routes';
import empleadosRoutes from './modules/empleados/empleados.routes';
import notificacionesRoutes from './modules/notificaciones/notificaciones.routes';
import reportesRoutes from './modules/reportes/reportes.routes';

const app = express();

// ─── SEGURIDAD ────────────────────────────────────────────────────
app.use(helmet());
app.set('trust proxy', 1);

// CORS
app.use(cors({
  origin: [env.FRONTEND_URL, 'http://localhost:3000', 'http://localhost:3001'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

// Rate limiting global
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 200,
  message: { success: false, message: 'Demasiadas solicitudes, intente más tarde' },
  standardHeaders: true,
  legacyHeaders: false,
});
app.use('/api', limiter);

// Rate limiting más estricto para auth
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 20,
  message: { success: false, message: 'Demasiados intentos de autenticación' },
});
app.use('/api/auth/login', authLimiter);

// ─── MIDDLEWARES BASE ─────────────────────────────────────────────
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(morgan(env.NODE_ENV === 'production' ? 'combined' : 'dev', {
  stream: { write: (msg) => logger.info(msg.trim()) },
}));

// ─── SWAGGER ──────────────────────────────────────────────────────
const swaggerOptions: swaggerJsdoc.Options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Plataforma SaaS de Gestión Turística — API',
      version: '1.0.0',
      description: 'API REST completa para la plataforma SaaS multi-tenant de gestión turística y hotelera',
      contact: { name: 'Soporte', email: 'soporte@saasturismo.com' },
    },
    servers: [
      { url: `http://localhost:${env.PORT}`, description: 'Desarrollo' },
    ],
    components: {
      securitySchemes: {
        bearerAuth: { type: 'http', scheme: 'bearer', bearerFormat: 'JWT' },
      },
    },
    security: [{ bearerAuth: [] }],
  },
  apis: ['./src/modules/**/*.routes.ts'],
};

const swaggerSpec = swaggerJsdoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec, {
  customCss: '.swagger-ui .topbar { background-color: #1e40af; }',
  customSiteTitle: 'SaaS Turismo API Docs',
}));

// ─── HEALTH CHECK ─────────────────────────────────────────────────
app.get('/health', (_, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString(), env: env.NODE_ENV });
});

// ─── RUTAS API ────────────────────────────────────────────────────
app.use('/api/auth',            authRoutes);
app.use('/api/clientes',        clientesRoutes);
app.use('/api/hoteles',         hotelesRoutes);
app.use('/api/reservas',        reservasRoutes);
app.use('/api/paquetes',        paquetesRoutes);
app.use('/api/pagos',           pagosRoutes);
app.use('/api/usuarios',        usuariosRoutes);
app.use('/api/empleados',       empleadosRoutes);
app.use('/api/notificaciones',  notificacionesRoutes);
app.use('/api/reportes',        reportesRoutes);

// ─── ERROR HANDLING ───────────────────────────────────────────────
app.use(notFoundMiddleware);
app.use(errorMiddleware);

export default app;
