import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { env } from '../config/env';
import { AppError } from '../shared/utils/AppError';

export interface JwtPayload {
  sub: string;       // usuario ID
  tenantId: string;  // empresa ID
  rolNombre: string;
  iat: number;
  exp: number;
}

declare global {
  namespace Express {
    interface Request {
      user?: JwtPayload;
      tenantId?: string;
    }
  }
}

export function authMiddleware(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    throw new AppError('Token de autenticación requerido', 401);
  }

  const token = authHeader.split(' ')[1];

  try {
    const payload = jwt.verify(token, env.JWT_SECRET) as JwtPayload;
    req.user = payload;
    req.tenantId = payload.tenantId;
    next();
  } catch (error) {
    if (error instanceof jwt.TokenExpiredError) {
      throw new AppError('Token expirado', 401);
    }
    throw new AppError('Token inválido', 401);
  }
}

// Middleware opcional — no falla si no hay token
export function optionalAuthMiddleware(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  if (authHeader?.startsWith('Bearer ')) {
    try {
      const token = authHeader.split(' ')[1];
      const payload = jwt.verify(token, env.JWT_SECRET) as JwtPayload;
      req.user = payload;
      req.tenantId = payload.tenantId;
    } catch {
      // Token inválido — continuar sin autenticación
    }
  }
  next();
}
