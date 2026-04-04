import { Request, Response, NextFunction } from 'express';
import { ZodSchema, ZodError } from 'zod';
import { AppError } from '../shared/utils/AppError';

export function validate(schema: ZodSchema) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      const data = schema.parse({
        body: req.body,
        query: req.query,
        params: req.params,
      });
      req.body = data.body ?? req.body;
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const messages = error.errors.map((e) => `${e.path.join('.')}: ${e.message}`);
        throw new AppError(`Error de validación: ${messages.join(', ')}`, 422);
      }
      next(error);
    }
  };
}
