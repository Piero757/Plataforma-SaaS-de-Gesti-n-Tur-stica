import './config/env'; // Validar env primero
import app from './app';
import { env } from './config/env';
import { connectDatabase, disconnectDatabase } from './config/database';
import { connectRedis, disconnectRedis } from './config/redis';
import { logger } from './config/logger';

async function bootstrap() {
  try {
    // Conectar servicios
    await connectDatabase();
    await connectRedis();

    // Iniciar servidor HTTP
    const server = app.listen(env.PORT, () => {
      logger.info(`🚀 Servidor corriendo en http://localhost:${env.PORT}`);
      logger.info(`📚 API Docs disponibles en http://localhost:${env.PORT}/api-docs`);
      logger.info(`🌍 Entorno: ${env.NODE_ENV}`);
    });

    // Graceful shutdown
    const shutdown = async (signal: string) => {
      logger.info(`\n📴 Recibido ${signal}. Cerrando servidor...`);
      server.close(async () => {
        await disconnectDatabase();
        await disconnectRedis();
        logger.info('✅ Servidor cerrado correctamente');
        process.exit(0);
      });

      // Forzar cierre después de 10 segundos
      setTimeout(() => {
        logger.error('❌ Forzando cierre por timeout');
        process.exit(1);
      }, 10000);
    };

    process.on('SIGTERM', () => shutdown('SIGTERM'));
    process.on('SIGINT', () => shutdown('SIGINT'));

    process.on('unhandledRejection', (reason, promise) => {
      logger.error('Unhandled Rejection:', { reason, promise });
    });

    process.on('uncaughtException', (error) => {
      logger.error('Uncaught Exception:', error);
      process.exit(1);
    });

  } catch (error) {
    logger.error('❌ Error al iniciar el servidor:', error);
    process.exit(1);
  }
}

bootstrap();
