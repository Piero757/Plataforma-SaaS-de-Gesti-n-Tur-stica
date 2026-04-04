import { Request, Response, NextFunction } from 'express';
import { AppError } from '../shared/utils/AppError';
import { logger } from '../config/logger';
import { env } from '../config/env';

export function errorMiddleware(
  err: Error,
  req: Request,
  res: Response,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  next: NextFunction
) {
  if (err instanceof AppError) {
    logger.warn(`[${req.method}] ${req.path} → ${err.statusCode}: ${err.message}`);
    return res.status(err.statusCode).json({
      success: false,
      message: err.message,
      ...(err.details && { details: err.details }),
    });
  }

  // Errores inesperados
  logger.error('Error interno no controlado:', {
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
  });

  return res.status(500).json({
    success: false,
    message: 'Error interno del servidor',
    ...(env.NODE_ENV === 'development' && { stack: err.stack }),
  });
}

export function notFoundMiddleware(req: Request, res: Response) {
  res.status(404).json({
    success: false,
    message: `Ruta no encontrada: ${req.method} ${req.path}`,
  });
}
