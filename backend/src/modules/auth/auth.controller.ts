import { Request, Response } from 'express';
import * as authService from './auth.service';
import { successResponse } from '../../shared/utils/response';

export async function login(req: Request, res: Response) {
  const result = await authService.loginService(
    req.body,
    req.headers['user-agent'],
    req.ip
  );
  res.status(200).json(successResponse(result, 'Login exitoso'));
}

export async function register(req: Request, res: Response) {
  const result = await authService.registerService(req.body);
  res.status(201).json(successResponse(result, 'Empresa registrada exitosamente'));
}

export async function refresh(req: Request, res: Response) {
  const result = await authService.refreshTokenService(req.body.refreshToken);
  res.status(200).json(successResponse(result, 'Token renovado'));
}

export async function logout(req: Request, res: Response) {
  await authService.logoutService(req.body.refreshToken);
  res.status(200).json(successResponse(null, 'Sesión cerrada exitosamente'));
}

export async function me(req: Request, res: Response) {
  const usuario = await authService.getMeService(req.user!.sub);
  res.status(200).json(successResponse(usuario));
}
