# Plataforma SaaS de Gestión Turística

Un sistema completo de gestión para turismo y hotelería desarrollado en Django, diseñado para pequeñas y medianas empresas del sector turístico.

## 🌟 Características Principales

- **Gestión de Clientes**: Registro completo con historial de reservas
- **Gestión de Reservas**: Sistema integral de reservas con check-in/check-out
- **Gestión de Hoteles**: Administración de múltiples hoteles y propiedades
- **Gestión de Habitaciones**: Control de disponibilidad y estados
- **Paquetes Turísticos**: Creación y gestión de paquetes personalizados
- **Sistema de Pagos**: Procesamiento completo de pagos y reembolsos
- **Gestión de Empleados**: Control de personal, horarios y asistencia
- **Reportes y Estadísticas**: Dashboard en tiempo real y reportes detallados
- **Panel Administrativo**: Interfaz completa de administración Django

## 🏗️ Arquitectura del Sistema

### Backend
- **Framework**: Django 4.2.7
- **API REST**: Django REST Framework
- **Base de Datos**: PostgreSQL
- **Autenticación**: JWT + Sesión Django
- **Tareas Asíncronas**: Celery + Redis

### Frontend
- **Dashboard**: HTML5 + Bootstrap 5 + Chart.js
- **Panel Admin**: Django Admin personalizado
- **Responsive**: Mobile-first design

## 📋 Requisitos del Sistema

### Software Requerido
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Node.js 14+ (opcional para desarrollo frontend)

### Hardware Recomendado
- **Mínimo**: 2GB RAM, 1 CPU, 20GB Storage
- **Recomendado**: 4GB RAM, 2 CPU, 50GB Storage
- **Producción**: 8GB RAM, 4 CPU, 100GB Storage

## 🚀 Guía de Instalación

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd plataforma-saas-gestion-turistica
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Copiar el archivo `.env` y configurar las variables:
```bash
cp .env.example .env
```

Editar `.env`:
```env
DB_NAME=turismo_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=tu_secret_key
DEBUG=True
REDIS_URL=redis://localhost:6379/0
```

### 5. Configurar Base de Datos
```bash
# Crear base de datos en PostgreSQL
createdb turismo_db

# Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear Superusuario
```bash
python crear_superusuario.py
```
Esto creará el usuario admin:
- **Usuario**: piero
- **Contraseña**: piero12345

### 7. Recolectar Archivos Estáticos
```bash
python manage.py collectstatic
```

### 8. Iniciar el Servidor
```bash
python manage.py runserver
```

### 9. Acceder al Sistema
- **Dashboard**: http://localhost:8000/
- **Panel Admin**: http://localhost:8000/admin/
- **API Health**: http://localhost:8000/api/health/

## 📊 Diagrama de Base de Datos

### Entidades Principales

```
Empresa
├── Usuario (extends AbstractUser)
├── Cliente
├── Empleado
├── Hotel
│   └── HotelImagen
├── Habitacion
│   └── HabitacionImagen
├── PaqueteTuristico
│   ├── PaqueteHotel
│   └── PaqueteServicio
├── Reserva
│   ├── ReservaHabitacion
│   ├── ReservaServicioAdicional
│   ├── CheckIn
│   └── CheckOut
├── Pago
│   └── Reembolso
├── Reporte
└── Dashboard
```

### Relaciones Clave
- **Empresa** → Centraliza todas las entidades (multi-tenancy)
- **Cliente** → **Reserva** (1:N)
- **Hotel** → **Habitacion** (1:N)
- **Reserva** → **ReservaHabitacion** (1:N)
- **Reserva** → **Pago** (1:N)

## 🔌 API REST

### Endpoints Principales

#### Autenticación
```
POST /api/auth/login/
POST /api/auth/refresh/
POST /api/auth/logout/
```

#### Clientes
```
GET    /api/clientes/clientes/
POST   /api/clientes/clientes/
GET    /api/clientes/clientes/{id}/
PUT    /api/clientes/clientes/{id}/
DELETE /api/clientes/clientes/{id}/
GET    /api/clientes/clientes/{id}/historial_reservas/
```

#### Reservas
```
GET    /api/reservas/reservas/
POST   /api/reservas/reservas/
GET    /api/reservas/reservas/{id}/
PUT    /api/reservas/reservas/{id}/
POST   /api/reservas/reservas/{id}/confirmar/
POST   /api/reservas/reservas/{id}/realizar_checkin/
POST   /api/reservas/reservas/{id}/realizar_checkout/
```

#### Hoteles
```
GET    /api/hoteles/hoteles/
POST   /api/hoteles/hoteles/
GET    /api/hoteles/hoteles/{id}/
GET    /api/hoteles/hoteles/{id}/disponibilidad/
POST   /api/hoteles/hoteles/{id}/agregar_imagen/
```

#### Dashboard
```
GET    /api/dashboard/datos_completos/
POST   /api/dashboard/metricas/actualizar_todas/
GET    /api/dashboard/alertas/no_leidas/
```

### Autenticación
La API utiliza JWT tokens. Incluir en las cabeceras:
```
Authorization: Bearer <access_token>
```

## 📈 Dashboard y Estadísticas

### Métricas en Tiempo Real
- Reservas del día
- Ingresos acumulados
- Tasa de ocupación
- Check-ins pendientes

### Gráficos Disponibles
- Evolución de reservas (últimos 7 días)
- Estado de habitaciones (disponibles/ocupadas)
- Ingresos mensuales
- Tasa de cancelación

### Alertas Automáticas
- Check-ins pendientes
- Pagos vencidos
- Ocupación crítica
- Mantenimiento programado

## 🛠️ Panel Administrativo

### Características
- Interfaz Django Admin personalizada
- Filtros avanzados
- Búsqueda全文
- Exportación de datos
- Acciones masivas

### Accesos por Defecto
- **URL**: /admin/
- **Usuario**: piero
- **Contraseña**: piero12345

## 📋 Módulos del Sistema

### 1. Gestión de Clientes
- Registro completo de clientes
- Historial de reservas
- Segmentación VIP
- Preferencias personalizadas

### 2. Gestión de Reservas
- Creación y modificación de reservas
- Check-in/Check-out digital
- Gestión de servicios adicionales
- Control de disponibilidad

### 3. Gestión de Hoteles
- Administración multi-hotel
- Información completa del hotel
- Galería de imágenes
- Políticas y servicios

### 4. Gestión de Habitaciones
- Control de estados
- Precios dinámicos
- Características detalladas
- Gestión de imágenes

### 5. Paquetes Turísticos
- Creación de paquetes
- Gestión de servicios incluidos
- Promociones y descuentos
- Control de capacidad

### 6. Sistema de Pagos
- Múltiples métodos de pago
- Procesamiento de reembolsos
- Generación de comprobantes
- Control de saldos

### 7. Gestión de Empleados
- Registro de personal
- Control de horarios
- Sistema de asistencia
- Gestión de permisos

### 8. Reportes
- Reportes personalizables
- Exportación CSV
- Programación automática
- Métricas KPI

## 🔧 Configuración Adicional

### Celery (Tareas Asíncronas)
```bash
# Iniciar worker
celery -A config worker -l info

# Iniciar scheduler
celery -A config beat -l info
```

### Redis (Cache y Message Broker)
```bash
# Iniciar Redis
redis-server
```

### PostgreSQL (Producción)
```bash
# Crear usuario y base de datos
sudo -u postgres psql
CREATE USER turismo_user WITH PASSWORD 'secure_password';
CREATE DATABASE turismo_db OWNER turismo_user;
GRANT ALL PRIVILEGES ON DATABASE turismo_db TO turismo_user;
```

## 🚀 Despliegue en Producción

### Usando Gunicorn
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Configuración Nginx
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }

    location /media/ {
        alias /path/to/your/project/media/;
    }
}
```

### Variables de Entorno Producción
```env
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
SECRET_KEY=clave-super-segura-produccion
DB_NAME=produccion_db
DB_USER=produccion_user
DB_PASSWORD=clave-segura-produccion
```

## 📚 Documentación de la API

### Formato de Respuesta
```json
{
    "count": 150,
    "next": "http://api.example.com/reservas/?page=2",
    "previous": null,
    "results": [...]
}
```

### Códigos de Error
- `200` - OK
- `201` - Creado
- `400` - Bad Request
- `401` - No autorizado
- `403` - Prohibido
- `404` - No encontrado
- `500` - Error del servidor

## 🧪 Testing

### Ejecutar Tests
```bash
python manage.py test
```

### Cobertura de Tests
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 🔄 Mantenimiento

### Tareas Programadas
- Limpieza de sesiones expiradas
- Generación de reportes automáticos
- Backup de base de datos
- Optimización de consultas

### Monitoreo
- Logs de aplicación
- Métricas de rendimiento
- Alertas de sistema
- Uso de recursos

## 🤝 Contribución

### Flujo de Trabajo
1. Fork del proyecto
2. Crear feature branch
3. Hacer cambios
4. Ejecutar tests
5. Enviar Pull Request

### Estándares de Código
- PEP 8 compliance
- Type hints
- Documentación de funciones
- Tests unitarios

## 📞 Soporte

### Canales de Soporte
- **Email**: soporte@turismo-saas.com
- **Teléfono**: +51 1 2345678
- **Chat**: Disponible 24/7
- **Documentation**: https://docs.turismo-saas.com

### Niveles de Soporte
- **Básico**: Email y documentación
- **Estándar**: Email + teléfono 8x5
- **Premium**: Email + teléfono 24x7 + soporte dedicado

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

## 🎯 Roadmap

### Versión 2.0 (Próximo Trimestre)
- [ ] Aplicación móvil iOS/Android
- [ ] Integración con pasarelas de pago adicionales
- [ ] Sistema de reviews y calificaciones
- [ ] Chat integrado con clientes

### Versión 3.0 (Próximo Semestre)
- [ ] Inteligencia artificial para recomendaciones
- [ ] Integración con sistemas de canalización
- [ ] Multi-idioma completo
- [ ] Advanced analytics

---

**Desarrollado con ❤️ para la industria turística peruana**
