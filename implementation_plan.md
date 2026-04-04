# Plataforma SaaS de Gestión Turística — Plan de Implementación Completo

> **Rol asumido:** Arquitecto de Software Senior + Ingeniero SaaS + Especialista DevOps + Diseñador de Productos Digitales

---

## Resumen Ejecutivo

Se diseñará y construirá una **plataforma SaaS multi-tenant profesional** para la industria turística y hotelera. El sistema permitirá que múltiples empresas (agencias, hoteles, operadores) operen sobre la misma infraestructura con **aislamiento total de datos**.

---

## Decisiones Arquitectónicas Clave

### Estrategia Multi-Tenant Elegida: **Shared Database + tenant_id**

| Estrategia | Costo | Escalabilidad | Aislamiento | Elección |
|---|---|---|---|---|
| DB por empresa | Alto | Baja | Total | ❌ |
| Schema por empresa | Medio | Media | Alta | ❌ |
| **Shared DB + tenant_id** | **Bajo** | **Alta** | **Lógica** | **✅** |

**Justificación:** La estrategia de base de datos compartida con `tenant_id` es ideal para una plataforma SaaS en etapa de crecimiento porque:
- **Costo operacional mínimo** — un solo servidor PostgreSQL atiende a todos los tenants
- **Escalabilidad horizontal** — fácil de escalar con conexión pooling (pgBouncer)
- **Mantenimiento simplificado** — una sola migración aplica a todos los tenants
- **Tiempo de onboarding instantáneo** — agregar una empresa no requiere provisionar infraestructura

---

## Stack Tecnológico

### Backend
- **Runtime:** Node.js 20 LTS con Express.js
- **ORM:** Prisma (type-safe, migraciones automáticas)
- **Auth:** JWT (access token 15min) + Refresh Token (7 días, rotación automática)
- **Cache:** Redis 7 (sesiones, rate limiting, notificaciones)
- **Validación:** Zod
- **Documentación API:** Swagger/OpenAPI 3.0
- **Testing:** Jest + Supertest

### Frontend
- **Framework:** Next.js 14 (App Router)
- **UI Library:** shadcn/ui + Tailwind CSS
- **Estado global:** Zustand
- **Fetching:** TanStack Query (React Query)
- **Gráficas:** Recharts
- **Formularios:** React Hook Form + Zod
- **Tablas:** TanStack Table

### Base de Datos
- **Principal:** PostgreSQL 16
- **Cache/Queue:** Redis 7
- **Migraciones:** Prisma Migrate

### DevOps
- **Contenedores:** Docker + Docker Compose
- **CI/CD:** GitHub Actions
- **Proxy:** Nginx
- **Certificados SSL:** Let's Encrypt (Certbot)
- **Monitoreo:** Prometheus + Grafana (stack básico)

---

## Arquitectura del Sistema

```
                          ┌─────────────────────────┐
                          │     INTERNET/CLIENTES    │
                          └────────────┬────────────┘
                                       │
                          ┌────────────▼────────────┐
                          │    NGINX (Reverse Proxy) │
                          │    SSL Termination       │
                          └──────┬──────────┬────────┘
                                 │          │
              ┌──────────────────▼─┐    ┌───▼──────────────────┐
              │  Frontend          │    │  Backend API          │
              │  Next.js 14        │    │  Node.js + Express    │
              │  Port: 3000        │    │  Port: 4000           │
              └────────────────────┘    └───────────┬───────────┘
                                                    │
                              ┌─────────────────────┼──────────────────┐
                              │                     │                  │
                   ┌──────────▼────────┐  ┌─────────▼──────┐  ┌───────▼────────┐
                   │  PostgreSQL 16    │  │   Redis 7       │  │  File Storage  │
                   │  (Multi-tenant)   │  │  Cache/Sessions │  │  (S3/Spaces)   │
                   └───────────────────┘  └────────────────┘  └────────────────┘
```

---

## Diseño de Base de Datos

### Tablas Principales y Relaciones

```sql
-- ============================
-- TABLA: empresas (tenants)
-- ============================
CREATE TABLE empresas (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre      VARCHAR(200) NOT NULL,
    slug        VARCHAR(100) UNIQUE NOT NULL,  -- subdomain identifier
    email       VARCHAR(255) UNIQUE NOT NULL,
    telefono    VARCHAR(20),
    direccion   TEXT,
    logo_url    TEXT,
    activo      BOOLEAN DEFAULT TRUE,
    plan_id     UUID REFERENCES suscripciones(id),
    creado_en   TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NOW()
);

-- ============================
-- TABLA: roles
-- ============================
CREATE TABLE roles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id  UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    nombre      VARCHAR(100) NOT NULL,  -- admin, gerente, recepcionista, agente
    descripcion TEXT,
    es_sistema  BOOLEAN DEFAULT FALSE,  -- roles predeterminados del sistema
    creado_en   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, nombre)
);

-- ============================
-- TABLA: permisos
-- ============================
CREATE TABLE permisos (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    modulo      VARCHAR(100) NOT NULL,  -- clientes, reservas, hoteles...
    accion      VARCHAR(50) NOT NULL,   -- crear, leer, actualizar, eliminar
    descripcion TEXT,
    UNIQUE(modulo, accion)
);

CREATE TABLE roles_permisos (
    rol_id      UUID REFERENCES roles(id) ON DELETE CASCADE,
    permiso_id  UUID REFERENCES permisos(id) ON DELETE CASCADE,
    PRIMARY KEY (rol_id, permiso_id)
);

-- ============================
-- TABLA: usuarios
-- ============================
CREATE TABLE usuarios (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id      UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    rol_id          UUID NOT NULL REFERENCES roles(id),
    nombre          VARCHAR(200) NOT NULL,
    email           VARCHAR(255) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    avatar_url      TEXT,
    activo          BOOLEAN DEFAULT TRUE,
    ultimo_login    TIMESTAMPTZ,
    creado_en       TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, email)
);

-- ============================
-- TABLA: refresh_tokens
-- ============================
CREATE TABLE refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id  UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL UNIQUE,
    expira_en   TIMESTAMPTZ NOT NULL,
    revocado    BOOLEAN DEFAULT FALSE,
    creado_en   TIMESTAMPTZ DEFAULT NOW()
);

-- ============================
-- TABLA: clientes
-- ============================
CREATE TABLE clientes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id      UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    nombre          VARCHAR(200) NOT NULL,
    apellido        VARCHAR(200) NOT NULL,
    email           VARCHAR(255),
    telefono        VARCHAR(20),
    documento_tipo  VARCHAR(20),  -- DNI, Pasaporte, RUC
    documento_num   VARCHAR(50),
    fecha_nacimiento DATE,
    pais            VARCHAR(100),
    ciudad          VARCHAR(100),
    direccion       TEXT,
    notas           TEXT,
    activo          BOOLEAN DEFAULT TRUE,
    creado_en       TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, documento_tipo, documento_num)
);

-- ============================
-- TABLA: hoteles
-- ============================
CREATE TABLE hoteles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id      UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    nombre          VARCHAR(200) NOT NULL,
    descripcion     TEXT,
    stars           SMALLINT CHECK (stars BETWEEN 1 AND 5),
    email           VARCHAR(255),
    telefono        VARCHAR(20),
    pais            VARCHAR(100),
    ciudad          VARCHAR(100),
    direccion       TEXT,
    imagen_url      TEXT,
    activo          BOOLEAN DEFAULT TRUE,
    creado_en       TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ DEFAULT NOW()
);

-- ============================
-- TABLA: habitaciones
-- ============================
CREATE TABLE habitaciones (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotel_id        UUID NOT NULL REFERENCES hoteles(id) ON DELETE CASCADE,
    empresa_id      UUID NOT NULL REFERENCES empresas(id),
    numero          VARCHAR(20) NOT NULL,
    tipo            VARCHAR(50) NOT NULL,  -- simple, doble, suite, familiar
    capacidad       SMALLINT NOT NULL,
    precio_noche    DECIMAL(10,2) NOT NULL,
    descripcion     TEXT,
    amenidades      JSONB,  -- ["WiFi", "TV", "AC", "Jacuzzi"]
    estado          VARCHAR(20) DEFAULT 'disponible',  -- disponible, ocupada, mantenimiento
    imagen_url      TEXT,
    activo          BOOLEAN DEFAULT TRUE,
    creado_en       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(hotel_id, numero)
);

-- ============================
-- TABLA: paquetes_turisticos
-- ============================
CREATE TABLE paquetes_turisticos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id      UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    nombre          VARCHAR(200) NOT NULL,
    descripcion     TEXT,
    duracion_dias   SMALLINT NOT NULL,
    precio          DECIMAL(10,2) NOT NULL,
    precio_incluye  TEXT,
    itinerario      JSONB,
    max_personas    SMALLINT,
    imagen_url      TEXT,
    activo          BOOLEAN DEFAULT TRUE,
    creado_en       TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ DEFAULT NOW()
);

-- ============================
-- TABLA: reservas
-- ============================
CREATE TABLE reservas (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id      UUID NOT NULL REFERENCES empresas(id),
    cliente_id      UUID NOT NULL REFERENCES clientes(id),
    habitacion_id   UUID REFERENCES habitaciones(id),
    paquete_id      UUID REFERENCES paquetes_turisticos(id),
    usuario_id      UUID REFERENCES usuarios(id),  -- agente que registró
    tipo            VARCHAR(20) NOT NULL,  -- hotel, paquete
    fecha_inicio    DATE NOT NULL,
    fecha_fin       DATE NOT NULL,
    num_personas    SMALLINT NOT NULL DEFAULT 1,
    precio_total    DECIMAL(10,2) NOT NULL,
    estado          VARCHAR(20) DEFAULT 'pendiente',  -- pendiente, confirmada, cancelada, completada
    notas           TEXT,
    creado_en       TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ DEFAULT NOW()
);

-- ============================
-- TABLA: pagos
-- ============================
CREATE TABLE pagos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id      UUID NOT NULL REFERENCES empresas(id),
    reserva_id      UUID NOT NULL REFERENCES reservas(id),
    cliente_id      UUID NOT NULL REFERENCES clientes(id),
    monto           DECIMAL(10,2) NOT NULL,
    metodo_pago     VARCHAR(50),  -- efectivo, tarjeta, transferencia, stripe
    referencia      VARCHAR(200),  -- transaction ID externo
    estado          VARCHAR(20) DEFAULT 'pendiente',  -- pendiente, completado, fallido, reembolsado
    moneda          VARCHAR(3) DEFAULT 'USD',
    fecha_pago      TIMESTAMPTZ,
    creado_en       TIMESTAMPTZ DEFAULT NOW()
);

-- ============================
-- TABLA: empleados
-- ============================
CREATE TABLE empleados (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id      UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    usuario_id      UUID REFERENCES usuarios(id),
    nombre          VARCHAR(200) NOT NULL,
    apellido        VARCHAR(200) NOT NULL,
    cargo           VARCHAR(100),
    departamento    VARCHAR(100),
    email           VARCHAR(255),
    telefono        VARCHAR(20),
    fecha_ingreso   DATE,
    salario         DECIMAL(10,2),
    activo          BOOLEAN DEFAULT TRUE,
    creado_en       TIMESTAMPTZ DEFAULT NOW()
);

-- ============================
-- TABLA: planes_suscripcion
-- ============================
CREATE TABLE planes_suscripcion (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre          VARCHAR(100) NOT NULL,  -- Básico, Profesional, Empresarial
    descripcion     TEXT,
    precio_mensual  DECIMAL(10,2) NOT NULL,
    max_usuarios    INTEGER NOT NULL,
    max_reservas_mes INTEGER,  -- NULL = ilimitado
    max_hoteles     INTEGER,
    caracteristicas JSONB,
    activo          BOOLEAN DEFAULT TRUE
);

-- ============================
-- TABLA: suscripciones
-- ============================
CREATE TABLE suscripciones (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id      UUID NOT NULL REFERENCES empresas(id),
    plan_id         UUID NOT NULL REFERENCES planes_suscripcion(id),
    estado          VARCHAR(20) DEFAULT 'activa',  -- activa, suspendida, cancelada
    fecha_inicio    DATE NOT NULL,
    fecha_fin       DATE,
    precio_pagado   DECIMAL(10,2),
    renovacion_auto BOOLEAN DEFAULT TRUE,
    creado_en       TIMESTAMPTZ DEFAULT NOW()
);

-- ============================
-- TABLA: facturas
-- ============================
CREATE TABLE facturas (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id      UUID NOT NULL REFERENCES empresas(id),
    suscripcion_id  UUID REFERENCES suscripciones(id),
    reserva_id      UUID REFERENCES reservas(id),
    numero_factura  VARCHAR(50) UNIQUE NOT NULL,
    tipo            VARCHAR(20),  -- suscripcion, servicio
    subtotal        DECIMAL(10,2) NOT NULL,
    impuesto        DECIMAL(10,2) DEFAULT 0,
    total           DECIMAL(10,2) NOT NULL,
    estado          VARCHAR(20) DEFAULT 'pendiente',
    fecha_emision   DATE NOT NULL,
    fecha_vencimiento DATE,
    pdf_url         TEXT,
    creado_en       TIMESTAMPTZ DEFAULT NOW()
);

-- ============================
-- TABLA: notificaciones
-- ============================
CREATE TABLE notificaciones (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id      UUID NOT NULL REFERENCES empresas(id),
    usuario_id      UUID REFERENCES usuarios(id),
    titulo          VARCHAR(200) NOT NULL,
    mensaje         TEXT NOT NULL,
    tipo            VARCHAR(50),  -- reserva, pago, sistema, alerta
    leida           BOOLEAN DEFAULT FALSE,
    creado_en       TIMESTAMPTZ DEFAULT NOW()
);

-- ============================
-- ÍNDICES DE RENDIMIENTO
-- ============================
CREATE INDEX idx_usuarios_empresa ON usuarios(empresa_id);
CREATE INDEX idx_clientes_empresa ON clientes(empresa_id);
CREATE INDEX idx_reservas_empresa ON reservas(empresa_id);
CREATE INDEX idx_reservas_cliente ON reservas(cliente_id);
CREATE INDEX idx_reservas_estado ON reservas(estado);
CREATE INDEX idx_reservas_fecha ON reservas(fecha_inicio, fecha_fin);
CREATE INDEX idx_habitaciones_hotel ON habitaciones(hotel_id);
CREATE INDEX idx_pagos_reserva ON pagos(reserva_id);
CREATE INDEX idx_notificaciones_usuario ON notificaciones(usuario_id, leida);
```

---

## Diagrama ER (Entidad-Relación)

```
EMPRESAS ────────────────────────────────────────────────────┐
    │ 1                                                        │
    │ ├── N USUARIOS ── 1 ROL ── N ROLES_PERMISOS ── N PERMISOS
    │ ├── N CLIENTES                                           │
    │ ├── N HOTELES ── N HABITACIONES                          │
    │ ├── N PAQUETES_TURISTICOS                                │
    │ ├── N EMPLEADOS                                          │
    │ ├── N RESERVAS ──── 1 CLIENTES                          │
    │ │         │    └─── 1 HABITACIONES                      │
    │ │         │    └─── 1 PAQUETES_TURISTICOS                │
    │ │         └──── N PAGOS                                  │
    │ ├── N SUSCRIPCIONES ── 1 PLANES_SUSCRIPCION             │
    │ ├── N FACTURAS                                           │
    └── N NOTIFICACIONES                                       │
                                                               │
REFRESH_TOKENS ──── 1 USUARIOS ──────────────────────────────┘
```

---

## Diseño de API REST

### Autenticación

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/auth/login` | Login con email/password, retorna access + refresh token |
| POST | `/api/auth/logout` | Invalida el refresh token actual |
| POST | `/api/auth/refresh` | Genera nuevo access token desde refresh token |
| POST | `/api/auth/register` | Registro completo de nueva empresa + admin |
| POST | `/api/auth/reset-password` | Solicitud de reset de contraseña |

### Empresas

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/empresas/me` | Datos de la empresa actual (tenant) |
| PUT | `/api/empresas/me` | Actualizar datos de la empresa |
| PUT | `/api/empresas/me/logo` | Subir logo de la empresa |

### Usuarios y Roles

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/usuarios` | Listar usuarios de la empresa |
| POST | `/api/usuarios` | Crear nuevo usuario |
| GET | `/api/usuarios/:id` | Detalle de un usuario |
| PUT | `/api/usuarios/:id` | Actualizar usuario |
| DELETE | `/api/usuarios/:id` | Desactivar usuario |
| GET | `/api/roles` | Listar roles de la empresa |
| POST | `/api/roles` | Crear nuevo rol |
| PUT | `/api/roles/:id/permisos` | Asignar permisos a un rol |

### Clientes

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/clientes` | Listar clientes (paginado, filtrable) |
| POST | `/api/clientes` | Crear cliente |
| GET | `/api/clientes/:id` | Detalle de cliente |
| PUT | `/api/clientes/:id` | Actualizar cliente |
| DELETE | `/api/clientes/:id` | Eliminar cliente |
| GET | `/api/clientes/:id/reservas` | Historial de reservas del cliente |

### Hoteles y Habitaciones

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/hoteles` | Listar hoteles |
| POST | `/api/hoteles` | Crear hotel |
| PUT | `/api/hoteles/:id` | Actualizar hotel |
| DELETE | `/api/hoteles/:id` | Eliminar hotel |
| GET | `/api/hoteles/:id/habitaciones` | Habitaciones por hotel |
| POST | `/api/hoteles/:id/habitaciones` | Agregar habitación |
| PUT | `/api/habitaciones/:id` | Actualizar habitación |

### Reservas

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/reservas` | Listar reservas (filtros: fecha, estado, cliente) |
| POST | `/api/reservas` | Crear nueva reserva |
| GET | `/api/reservas/:id` | Detalle de reserva |
| PUT | `/api/reservas/:id` | Actualizar reserva |
| PUT | `/api/reservas/:id/confirmar` | Confirmar reserva |
| PUT | `/api/reservas/:id/cancelar` | Cancelar reserva |
| GET | `/api/reservas/disponibilidad` | Verificar disponibilidad de habitación |

### Paquetes Turísticos

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/paquetes` | Listar paquetes |
| POST | `/api/paquetes` | Crear paquete |
| GET | `/api/paquetes/:id` | Detalle de paquete |
| PUT | `/api/paquetes/:id` | Actualizar paquete |
| DELETE | `/api/paquetes/:id` | Eliminar paquete |

### Pagos

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/pagos` | Listar pagos |
| POST | `/api/pagos` | Registrar pago |
| GET | `/api/pagos/:id` | Detalle de pago |
| POST | `/api/pagos/stripe/checkout` | Crear sesión Stripe |
| POST | `/api/pagos/stripe/webhook` | Webhook de Stripe |

### Dashboard y Reportes

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/dashboard/stats` | KPIs principales del dashboard |
| GET | `/api/reportes/reservas` | Reporte de reservas por período |
| GET | `/api/reportes/ingresos` | Reporte de ingresos |
| GET | `/api/reportes/clientes` | Reporte de clientes |
| GET | `/api/reportes/ocupacion` | Tasa de ocupación hotelera |

---

## Estructura del Proyecto

```
plataforma-saas-turismo/
│
├── backend/                          # API Node.js + Express
│   ├── src/
│   │   ├── config/
│   │   │   ├── database.ts           # Prisma client
│   │   │   ├── redis.ts              # Redis client
│   │   │   └── env.ts                # Variables de entorno con Zod
│   │   ├── middleware/
│   │   │   ├── auth.middleware.ts    # JWT verification
│   │   │   ├── tenant.middleware.ts  # Extrae empresa del token
│   │   │   ├── rbac.middleware.ts    # Control de acceso por rol
│   │   │   ├── rateLimit.middleware.ts
│   │   │   └── error.middleware.ts   # Error handler global
│   │   ├── modules/
│   │   │   ├── auth/
│   │   │   │   ├── auth.controller.ts
│   │   │   │   ├── auth.service.ts
│   │   │   │   ├── auth.routes.ts
│   │   │   │   └── auth.schema.ts    # Validación Zod
│   │   │   ├── empresas/
│   │   │   ├── usuarios/
│   │   │   ├── clientes/
│   │   │   ├── hoteles/
│   │   │   ├── habitaciones/
│   │   │   ├── reservas/
│   │   │   ├── paquetes/
│   │   │   ├── pagos/
│   │   │   ├── empleados/
│   │   │   ├── notificaciones/
│   │   │   ├── reportes/
│   │   │   └── suscripciones/
│   │   ├── shared/
│   │   │   ├── utils/
│   │   │   ├── types/
│   │   │   └── constants/
│   │   └── app.ts                    # Express app setup
│   ├── prisma/
│   │   ├── schema.prisma
│   │   ├── migrations/
│   │   └── seeds/
│   ├── tests/
│   ├── Dockerfile
│   ├── package.json
│   └── .env.example
│
├── frontend/                         # Next.js 14 App Router
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   ├── (dashboard)/
│   │   │   │   ├── layout.tsx        # Sidebar + Navbar
│   │   │   │   ├── page.tsx          # Dashboard principal
│   │   │   │   ├── clientes/
│   │   │   │   ├── reservas/
│   │   │   │   ├── hoteles/
│   │   │   │   ├── paquetes/
│   │   │   │   ├── empleados/
│   │   │   │   ├── pagos/
│   │   │   │   ├── reportes/
│   │   │   │   ├── usuarios/
│   │   │   │   └── configuracion/
│   │   │   └── portal/               # Portal público de reservas
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn/ui components
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Navbar.tsx
│   │   │   │   └── MobileMenu.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── StatsCard.tsx
│   │   │   │   ├── ReservationChart.tsx
│   │   │   │   └── OccupancyGauge.tsx
│   │   │   ├── tables/
│   │   │   │   └── DataTable.tsx     # TanStack Table genérico
│   │   │   └── forms/
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useTenant.ts
│   │   │   └── usePermissions.ts
│   │   ├── services/
│   │   │   ├── api.ts                # Axios config con interceptors
│   │   │   ├── auth.service.ts
│   │   │   ├── clientes.service.ts
│   │   │   └── reservas.service.ts
│   │   └── store/
│   │       ├── authStore.ts          # Zustand auth state
│   │       └── uiStore.ts
│   ├── Dockerfile
│   └── package.json
│
├── database/
│   ├── schema.sql                    # Schema completo exportado
│   └── seeds/
│       ├── 01_planes.sql
│       ├── 02_permisos.sql
│       └── 03_demo_data.sql
│
├── nginx/
│   └── nginx.conf
│
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

---

## Módulos a Implementar (Código)

### 1. Sistema de Autenticación (Backend)
- JWT Access Token (15 min) + Refresh Token (7 días)
- Middleware `tenant.middleware.ts` que extrae `empresa_id` del JWT
- Middleware `rbac.middleware.ts` para control de permisos granular
- Hash bcrypt para contraseñas

### 2. Middleware Multi-Tenant
- Todo request autenticado incluye `req.tenantId`
- Todos los queries de Prisma incluyen `where: { empresa_id: tenantId }`

### 3. Frontend: Dashboard Administrativo
- KPIs: reservas del mes, ingresos, clientes activos, ocupación
- Gráfica de reservas por mes (Recharts)
- Tabla de últimas reservas
- Notificaciones en tiempo real (polling)

### 4. Portal Público de Reservas
- Página pública accesible por slug de empresa (`/portal/[slug]`)
- Búsqueda de disponibilidad
- Formulario de reserva online

---

## Plan de Implementación por Fases

### Fase 1 — Análisis de Requerimientos (1 semana)
- Levantamiento detallado con cada cliente
- Definición de flujos de trabajo específicos
- Validación de requerimientos con stakeholders
- Wireframes de baja fidelidad

### Fase 2 — Arquitectura del Sistema (1 semana)
- Diseño final del schema de BD
- Diseño de la API REST (contratos OpenAPI)
- Setup del repositorio y CI/CD
- Configuración de entornos (dev, staging, prod)

### Fase 3 — Desarrollo (8–12 semanas)
- **Sprint 1:** Auth + Empresas + Usuarios/Roles
- **Sprint 2:** Clientes + Hoteles + Habitaciones
- **Sprint 3:** Reservas + Sistema de disponibilidad
- **Sprint 4:** Paquetes turísticos + Pagos (Stripe)
- **Sprint 5:** Dashboard + Reportes + Notificaciones
- **Sprint 6:** Portal público + Responsive + Facturación
- **Sprint 7:** DevOps + Docker + Despliegue
- **Sprint 8:** QA + Correcciones + Optimización

### Fase 4 — Pruebas (2 semanas)
- Pruebas unitarias (Jest)
- Pruebas de integración API (Supertest)
- Pruebas de aislamiento multi-tenant
- Pruebas de carga (k6)
- UAT con usuarios finales

### Fase 5 — Implementación (1 semana)
- Despliegue en producción (AWS/DigitalOcean)
- Configuración SSL
- Monitoreo con Prometheus + Grafana
- Smoke tests en producción

### Fase 6 — Capacitación (1–2 semanas)
- **Capacitación Básica (3 días):** Navegación del sistema, gestión de clientes, registro de reservas simples
- **Capacitación Operativa (5 días):** Gestión avanzada de reservas, reportes, gestión de hoteles/paquetes, roles y usuarios
- Creación de manual de usuario en PDF
- Videos tutoriales por módulo

---

## Plan de Capacitación Detallado

### Día 1–3: Capacitación Básica
| Tema | Duración |
|---|---|
| Introducción al sistema y navegación | 2h |
| Gestión de clientes (crear, buscar, editar) | 2h |
| Registro de reservas de hotel | 3h |
| Consulta de reservas y estados | 1h |

### Día 4–8: Capacitación Operativa
| Tema | Duración |
|---|---|
| Gestión de hoteles y habitaciones | 3h |
| Paquetes turísticos y reservas avanzadas | 3h |
| Gestión de pagos y facturas | 3h |
| Dashboard y métricas clave | 2h |
| Generación de reportes | 3h |
| Gestión de usuarios y roles | 2h |

---

## Soporte Post-Implementación

| Tipo | Descripción |
|---|---|
| **Soporte Técnico** | Canal de soporte por email/chat (L–V 9am–6pm), respuesta < 4h |
| **Soporte Crítico** | 24/7 para issues de producción (caídas, pérdida de datos) |
| **Actualizaciones** | Releases mensuales con nuevas funcionalidades |
| **Corrección de Errores** | Hotfixes dentro de 24–48h tras reporte |
| **Monitoreo** | Uptime monitoring 24/7, alertas automáticas |
| **Backups** | Backups automáticos diarios de BD con retención 30 días |

---

## Estimación de Costos

### Desarrollo

| Ítem | Horas | Costo (USD) |
|---|---|---|
| Arquitectura y diseño | 40h | $2,000 |
| Backend API completo | 200h | $10,000 |
| Frontend completo | 160h | $8,000 |
| DevOps + Infraestructura | 40h | $2,000 |
| QA y pruebas | 60h | $3,000 |
| **Total Desarrollo** | **500h** | **$25,000** |

### Infraestructura (mensual)

| Ítem | Costo/mes |
|---|---|
| Servidor VPS (DigitalOcean/AWS) | $40–$120 |
| Base de datos gestionada | $15–$50 |
| Almacenamiento de archivos | $5–$20 |
| Certificado SSL | $0 (Let's Encrypt) |
| **Total Infraestructura** | **$60–$190/mes** |

### Mantenimiento (mensual)

| Ítem | Costo/mes |
|---|---|
| Soporte técnico (10h/mes) | $500 |
| Actualizaciones del sistema | $300 |
| Monitoreo y backups | $100 |
| **Total Mantenimiento** | **$900/mes** |

---

## Modelo de Negocio SaaS

### Planes de Suscripción

| Característica | Plan Básico | Plan Profesional | Plan Empresarial |
|---|---|---|---|
| **Precio** | $49/mes | $149/mes | $399/mes |
| Usuarios | 5 | 20 | Ilimitados |
| Hoteles gestionados | 2 | 10 | Ilimitados |
| Reservas/mes | 100 | 500 | Ilimitadas |
| Clientes | 500 | 5,000 | Ilimitados |
| Reportes | Básicos | Avanzados | Personalizados |
| API de integración | ❌ | ✅ | ✅ |
| Soporte | Email | Chat + Email | Dedicado |
| Portal de reservas online | ❌ | ✅ | ✅ |
| White-label | ❌ | ❌ | ✅ |

### Proyección de Ingresos

| Clientes | Mix de planes | Ingreso Mensual |
|---|---|---|
| 10 empresas | 60% Básico / 30% Pro / 10% Emp | $1,584/mes |
| 50 empresas | mismo mix | $7,920/mes |
| 100 empresas | mismo mix | $15,840/mes |

---

## Guía de Despliegue con Docker

### docker-compose.yml (Desarrollo)
```yaml
version: '3.9'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: saas_turismo
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@postgres:5432/saas_turismo
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "4000:4000"
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:4000
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Despliegue en Producción (DigitalOcean)
1. **Crear Droplet** (Ubuntu 22.04, 4GB RAM mínimo)
2. **Instalar Docker + Docker Compose**
3. **Configurar dominio** + registros DNS
4. **Clonar repositorio** en el servidor
5. **Configurar `.env` de producción** con credenciales reales
6. **Ejecutar:** `docker-compose -f docker-compose.prod.yml up -d`
7. **SSL:** `certbot --nginx -d midominio.com`
8. **Configurar GitHub Actions** para CI/CD automático

### Despliegue en AWS
- **EC2** para el servidor de aplicación
- **RDS PostgreSQL** gestionado (Multi-AZ para alta disponibilidad)
- **ElastiCache Redis** gestionado
- **S3** para almacenamiento de archivos
- **CloudFront** CDN para el frontend
- **Route 53** para DNS y SSL

---

## Preguntas Abiertas

> [!IMPORTANT]
> Antes de comenzar la construcción, necesito confirmar los siguientes puntos:

1. **¿Qué deseas construir ahora?** La solicitud es muy amplia. Puedo:
   - **Opción A:** Construir el **código fuente completo funcional** (backend + frontend) en el workspace
   - **Opción B:** Generar toda la **documentación técnica** (arquitectura, BD, API, guías) en archivos `.md`
   - **Opción C:** Construir una **demo visual del frontend** (Next.js con UI completa y datos de ejemplo)
   - **Opción D:** Todo lo anterior (estimado: sesión muy larga)

2. **¿Tienes Node.js y npm instalados** en tu máquina para correr el proyecto localmente?

3. **¿Necesitas autenticación real con PostgreSQL** o es suficiente con **datos en memoria/mock** para una demo?

4. **¿Tienes credenciales de Stripe** para las pasarelas de pago o usamos un simulador?

5. **Idioma del sistema:** ¿Todo en español (nombres de campos, mensajes de UI) o inglés para el código y español para la UI?

