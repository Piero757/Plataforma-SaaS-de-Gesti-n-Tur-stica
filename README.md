# 🌍 Plataforma SaaS de Gestión Turística

Plataforma SaaS multi-tenant para la gestión integral de empresas de turismo y hotelería.

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Node.js 20 + Express + TypeScript |
| ORM | Prisma |
| Frontend | Next.js 14 (App Router) |
| UI | shadcn/ui + Tailwind CSS |
| Base de datos | PostgreSQL 16 |
| Cache | Redis 7 |
| Auth | JWT + Refresh Tokens |
| Deploy | Docker + Nginx |

## Estructura del Proyecto

```
plataforma-saas-turismo/
├── backend/          # API REST Node.js
├── frontend/         # Next.js 14 App
├── database/         # Migraciones y seeds SQL
├── nginx/            # Configuración proxy reverso
├── docs/             # Documentación completa
├── docker-compose.yml
└── docker-compose.prod.yml
```

## Inicio Rápido (Desarrollo)

```bash
# 1. Copiar variables de entorno
cp .env.example .env

# 2. Levantar servicios con Docker
docker-compose up -d

# 3. Ejecutar migraciones
cd backend && npx prisma migrate dev

# 4. Sembrar datos de prueba
npx prisma db seed

# 5. Acceder al sistema
# Frontend: http://localhost:3000
# API:      http://localhost:4000
# API Docs: http://localhost:4000/api-docs
```

## Credenciales de Demo

```
Email: admin@demo.com
Password: Admin123!
```

## Planes de Suscripción

| Plan | Precio | Usuarios | Reservas/mes |
|------|--------|----------|--------------|
| Básico | $49/mes | 5 | 100 |
| Profesional | $149/mes | 20 | 500 |
| Empresarial | $399/mes | Ilimitados | Ilimitadas |

## Documentación

- [Arquitectura del Sistema](./docs/ARQUITECTURA.md)
- [Documentación de la API](./docs/API.md)
- [Guía de Despliegue](./docs/DESPLIEGUE.md)
- [Plan de Capacitación](./docs/CAPACITACION.md)
- [Modelo de Negocio](./docs/MODELO_NEGOCIO.md)

## Licencia

Propietario — Todos los derechos reservados.
