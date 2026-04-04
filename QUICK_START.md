# 🚀 Quick Start - Guía Rápida de Inicio

## 📋 Requisitos Mínimos

### Software Necesario
- **Python 3.8+**
- **PostgreSQL 12+**
- **Git** (ya lo tienes)

### Opcionales (para desarrollo completo)
- **Redis** (para tareas asíncronas)
- **Postman** (para probar APIs)

---

## ⚡ Inicio Rápido (5 minutos)

### Paso 1: Configurar Base de Datos

```bash
# Abrir PostgreSQL y crear base de datos
psql -U postgres
CREATE DATABASE turismo_db;
\q
```

### Paso 2: Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Linux/Mac)
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Variables

Edita el archivo `.env`:
```env
DB_NAME=turismo_db
DB_USER=postgres
DB_PASSWORD=tu_password_postgres
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=django-insecure-key-de-desarrollo
DEBUG=True
```

### Paso 5: Configuración Automática

```bash
python setup_local.py
```

### Paso 6: Iniciar Servidor

```bash
# Opción 1: Script automático
start_dev.bat

# Opción 2: Manual
python manage.py runserver
```

---

## 🌐 Acceder al Sistema

Una vez iniciado el servidor, accede a:

| Componente | URL | Descripción |
|------------|-----|-------------|
| **Dashboard** | http://localhost:8000/ | Interfaz principal |
| **Panel Admin** | http://localhost:8000/admin/ | Administración Django |
| **API Health** | http://localhost:8000/api/health/ | Estado de la API |

### Credenciales de Acceso
- **Usuario**: `piero`
- **Contraseña**: `piero12345`

---

## 🧪 Pruebas Rápidas

### 1. Probar Panel Administrativo

1. Ve a http://localhost:8000/admin/
2. Inicia sesión con `piero` / `piero12345`
3. Explora las secciones:
   - Clientes → Agregar nuevo cliente
   - Hoteles → Ver hotel demo
   - Habitaciones → Ver habitación 101
   - Empleados → Agregar empleado

### 2. Probar Dashboard

1. Ve a http://localhost:8000/
2. Verás:
   - Métricas en tiempo real
   - Gráficos interactivos
   - Alertas automáticas

### 3. Probar API

```bash
# Health check
curl http://localhost:8000/api/health/

# Login JWT
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "piero", "password": "piero12345"}'
```

---

## 🔧 Solución de Problemas Comunes

### Error: "Base de datos no existe"
```bash
# Crear base de datos
createdb turismo_db

# O en PostgreSQL
psql -U postgres
CREATE DATABASE turismo_db;
```

### Error: "Python no encontrado"
```bash
# Instalar Python 3.8+
# Windows: Descargar desde python.org
# Linux: sudo apt install python3.8
```

### Error: "PostgreSQL no conecta"
```bash
# Verificar que PostgreSQL esté corriendo
pg_ctl status

# O iniciar servicio
# Windows: net start postgresql-x64-13
# Linux: sudo systemctl start postgresql
```

### Error: "Módulo no encontrado"
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

---

## 📊 Datos de Ejemplo Creados

El script `setup_local.py` crea automáticamente:

### Empresa Demo
- **Nombre**: Empresa Demo
- **RUC**: 20123456789

### Hotel Demo
- **Nombre**: Hotel Paradise Lima
- **Categoría**: 5 estrellas
- **Dirección**: Av. Larco 123, Miraflores

### Habitación Demo
- **Número**: 101
- **Tipo**: Suite Deluxe
- **Precio**: S/. 350.00

### Cliente Demo
- **Nombre**: Juan Pérez
- **DNI**: 12345678

---

## 🎯 Flujo de Prueba Completo

### 1. Crear Reserva
1. En el panel admin → Clientes → Agregar cliente
2. Hoteles → Seleccionar hotel
3. Habitaciones → Ver disponibilidad
4. Reservas → Crear nueva reserva

### 2. Procesar Pago
1. Pagos → Agregar pago
2. Seleccionar método de pago
3. Confirmar transacción

### 3. Check-in Digital
1. Reservas → Buscar reserva
2. Acción → Realizar check-in
3. Verificar estado actualizado

### 4. Ver Dashboard
1. Ir a http://localhost:8000/
2. Ver métricas actualizadas
3. Explorar gráficos y alertas

---

## 📚 Documentación Adicional

- **README.md**: Documentación completa
- **GUIA_IMPLEMENTACION.md**: Guía detallada
- **COSTOS_IMPLEMENTACION.md**: Análisis financiero
- **DIAGRAMA_ERD.md**: Diseño de base de datos

---

## 🆘 Ayuda

### Si algo no funciona:

1. **Revisa los logs**:
   ```bash
   python manage.py check
   ```

2. **Verifica configuración**:
   ```bash
   python manage.py diffsettings
   ```

3. **Ejecuta setup completo**:
   ```bash
   python setup_local.py
   ```

4. **Reinicia servidor**:
   ```bash
   python manage.py runserver
   ```

---

## 🎉 ¡Listo!

Una vez que completes estos pasos, tendrás:

✅ Sistema corriendo localmente  
✅ Datos de ejemplo cargados  
✅ Usuario admin configurado  
✅ API funcionando  
✅ Dashboard operativo  

**¡Ahora puedes explorar y probar todas las funcionalidades del sistema!**
