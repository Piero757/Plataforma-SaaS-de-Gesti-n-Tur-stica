// Respuesta exitosa estándar
export function successResponse<T>(
  data: T,
  message = 'Operación exitosa',
  meta?: Record<string, unknown>
) {
  return {
    success: true,
    message,
    data,
    ...(meta && { meta }),
  };
}

// Respuesta paginada
export function paginatedResponse<T>(
  data: T[],
  total: number,
  page: number,
  limit: number,
  message = 'Lista obtenida exitosamente'
) {
  return {
    success: true,
    message,
    data,
    meta: {
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit),
      hasNextPage: page * limit < total,
      hasPrevPage: page > 1,
    },
  };
}

// Helper para parsear paginación de query params
export function parsePagination(query: Record<string, unknown>) {
  const page = Math.max(1, parseInt(String(query.page ?? 1)));
  const limit = Math.min(100, Math.max(1, parseInt(String(query.limit ?? 20))));
  const skip = (page - 1) * limit;
  return { page, limit, skip };
}
