# Diagrama Entidad-Relación (ERD) - Sistema de Gestión Turística

## 📊 Vista General del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PLATAFORMA SaaS TURÍSTICA                              │
│                               (Multi-Tenancy)                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                      EMPRESA                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   EMPRESA       │  │    USUARIO      │  │    CLIENTE      │  │   EMPLEADO      │ │
│  │  - id (PK)      │  │  - id (PK)      │  │  - id (PK)      │  │  - id (PK)      │ │
│  │  - nombre        │◄─┤  - empresa (FK) │◄─┤  - empresa (FK) │◄─┤  - empresa (FK) │ │
│  │  - ruc          │  │  - username     │  │  - nombres       │  │  - nombres       │ │
│  │  - dirección    │  │  - email        │  │  - apellidos     │  │  - apellidos     │ │
│  │  - teléfono     │  │  - rol          │  │  - tipo_doc      │  │  - cargo         │ │
│  │  - email        │  │  - is_active    │  │  - num_doc       │  │  - departamento  │ │
│  │  - activo       │  │  - creado_en    │  │  - telefono      │  │  - estado        │ │
│  │  - creado_en    │  │  - actualizado  │  │  - email         │  │  - fecha_contrato│ │
│  │  - actualizado  │  │                 │  │  - vip           │  │  - salario       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                GESTIÓN DE HOTELES                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │     HOTEL       │  │  HOTEL_IMAGEN   │  │   TIPO_HAB      │  │   HABITACION    │ │
│  │  - id (PK)      │  │  - id (PK)      │  │  - id (PK)      │  │  - id (PK)      │ │
│  │  - empresa (FK) │◄─┤  - hotel (FK)   │  │  - nombre       │◄─┤  - hotel (FK)   │ │
│  │  - nombre        │  │  - imagen       │  │  - descripcion  │  │  - tipo (FK)    │ │
│  │  - categoría    │  │  - descripcion  │  │  - cap_max      │  │  - numero       │ │
│  │  - descripción  │  │  - orden        │  │  - cap_adultos  │  │  - piso         │ │
│  │  - dirección    │  │  - creado_en    │  │  - cap_ninos    │  │  - estado       │ │
│  │  - ciudad       │  └─────────────────┘  │  - creado_en    │  │  - precio_base  │ │
│  │  - país         │                      └─────────────────┘  │  - precio_temp  │ │
│  │  - teléfono     │                                                │  - servicios    │ │
│  │  - email        │                                                │  - activa       │ │
│  │  - check_in     │                                                │  - creado_en    │ │
│  │  - check_out    │                                                └─────────────────┘ │
│  │  - servicios    │                                                                     │
│  │  - activo       │                                                ┌─────────────────┐ │
│  │  - creado_en    │                                                │ HABITACION_IMG  │ │
│  └─────────────────┘                                                │  - id (PK)      │ │
                                                                      │  - habitacion(FK)│ │
                                                                      │  - imagen       │ │
                                                                      │  - descripcion  │ │
                                                                      │  - orden        │ │
                                                                      │  - creado_en    │ │
                                                                      └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              PAQUETES TURÍSTICOS                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ PAQUETE_TURIST  │  │  PAQUETE_HOTEL  │  │ PAQUETE_SERVICIO │  │   RESERVA       │ │
│  │  - id (PK)      │  │  - id (PK)      │  │  - id (PK)      │  │  - id (PK)      │ │
│  │  - empresa (FK) │◄─┤  - paquete (FK) │◄─┤  - paquete (FK) │◄─┤  - empresa (FK) │ │
│  │  - nombre        │  │  - hotel (FK)   │  │  - tipo         │  │  - codigo_res   │ │
│  │  - tipo          │  │  - noches       │  │  - nombre       │  │  - cliente (FK) │ │
│  │  - descripción  │  │  - tipo_hab     │  │  - descripcion  │  │  - tipo_res     │ │
│  │  - incluye      │  │  - regimen      │  │  - incluido     │  │  - paquete (FK) │ │
│  │  - no_incluye   │  │  - creado_en    │  │  - costo_adic   │  │  - fecha_check  │ │
│  │  - duracion_dias │  └─────────────────┘  │  - creado_en    │  │  - fecha_checkout│ │
│  │  - duracion_noch│                      └─────────────────┘  │  - adultos      │ │
│  │  - precio_base  │                                                │  - ninos        │ │
│  │  - precio_temp  │                                                │  - estado       │ │
│  │  - cap_min      │                                                │  - subtotal_hab │ │
│  │  - cap_max      │                                                │  - subtotal_paqt│ │
│  │  - destinos     │                                                │  - subtotal_serv│ │
│  │  - actividades  │                                                │  - descuento    │ │
│  │  - requisitos   │                                                │  - impuestos    │ │
│  │  - condiciones  │                                                │  - total        │ │
│  │  - es_promocion │                                                │  - monto_pagado │ │
│  │  - descuento    │                                                │  - saldo_pend   │ │
│  │  - activo       │                                                │  - notas        │ │
│  │  - creado_en    │                                                │  - creado_por   │ │
│  └─────────────────┘                                                │  - creado_en    │ │
                                                                      └─────────────────┘ │
                                                                                  │
                                                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            DETALLES DE RESERVA                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ RESERVA_HABIT   │  │ RESERVA_SERV_AD │  │     CHECKIN     │  │    CHECKOUT    │ │
│  │  - id (PK)      │  │  - id (PK)      │  │  - id (PK)      │  │  - id (PK)      │ │
│  │  - reserva (FK) │◄─┤  - reserva (FK) │◄─┤  - reserva (FK) │◄─┤  - reserva (FK) │ │
│  │  - habitacion(FK)│  │  - nombre_serv  │  │  - fecha_hora   │  │  - fecha_hora   │ │
│  │  - fecha_check  │  │  - descripcion  │  │  - responsable  │  │  - responsable  │ │
│  │  - fecha_checkout│  │  - cantidad    │  │  - observaciones│  │  - observaciones│ │
│  │  - adultos      │  │  - precio_unit  │  │  - doc_entregado│  │  - cargo_adic   │ │
│  │  - ninos        │  │  - subtotal     │  │  - deposito     │  │  - deposito_dev │ │
│  │  - precio_noche │  │  - fecha_serv   │  │  - creado_en    │  │  - metodo_pago  │ │
│  │  - subtotal     │  │  - creado_en    │  └─────────────────┘  │  - creado_en    │ │
│  │  - creado_en    │  └─────────────────┘                      └─────────────────┘ │
│  └─────────────────┘                                                                     │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SISTEMA DE PAGOS                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │      PAGO       │  │ METODO_PAGO_CONF │  │    REEMBOLSO    │  │   EMPLEADO      │ │
│  │  - id (PK)      │  │  - id (PK)      │  │  - id (PK)      │  │  - id (PK)      │ │
│  │  - empresa (FK) │◄─┤  - empresa (FK) │  │  - pago_orig(FK) │◄─┤  - empresa (FK) │ │
│  │  - reserva (FK) │  │  - metodo_pago  │  │  - reserva (FK) │  │  - codigo_emp   │ │
│  │  - codigo_pago  │  │  - activo       │  │  - monto        │  │  - nombres      │ │
│  │  - tipo_pago    │  │  - req_comprob  │  │  - motivo       │  │  - apellidos    │ │
│  │  - monto        │  │  - comision_%   │  │  - estado       │  │  - cargo        │ │
│  │  - metodo_pago  │  │  - comision_fija│  │  - fecha_sol    │  │  - departamento │ │
│  │  - estado       │  │  - conf_adic    │  │  - fecha_proc   │  │  - turno        │ │
│  │  - fecha_pago   │  │  - creado_en    │  │  - metodo_ref   │  │  - estado       │ │
│  │  - referencia   │  │  - actualizado  │  │  - referencia   │  │  - fecha_contrat│ │
│  │  - banco_orig   │  └─────────────────┘  │  - aprobado_por │  │  - usuario_sist │ │
│  │  - banco_dest   │                      │  - procesado_por│  │  - creado_en    │ │
│  │  - num_operacion│                      │  - notas        │  └─────────────────┘ │
│  │  - comp_gen     │                      │  - creado_en    │                         │
│  │  - tipo_comp    │                      └─────────────────┘                         │
│  │  - num_comp    │                                                                     │
│  │  - reg_por      │                                                ┌─────────────────┐ │
│  │  - creado_en    │                                                │ HORARIO_EMPLEADO│ │
│  └─────────────────┘                                                │  - id (PK)      │ │
                                                                      │  - empleado (FK)│ │
                                                                      │  - dia_semana   │ │
                                                                      │  - hora_entrada │ │
                                                                      │  - hora_salida  │ │
                                                                      │  - activo       │ │
                                                                      │  - creado_en    │ │
                                                                      └─────────────────┘ │
                                                                                  │
                                                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           RECURSOS HUMANOS                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ ASISTENCIA_EMP  │  │  PERMISO_EMPLE  │  │     REPORTE     │  │ METRICA_REPORTE│ │
│  │  - id (PK)      │  │  - id (PK)      │  │  - id (PK)      │  │  - id (PK)      │ │
│  │  - empleado (FK)│◄─┤  - empleado (FK)│◄─┤  - empresa (FK) │◄─┤  - empresa (FK) │ │
│  │  - fecha        │  │  - tipo_permiso │  │  - tipo_reporte │  │  - nombre       │ │
│  │  - hora_entrada │  │  - fecha_inicio │  │  - nombre       │  │  - descripcion  │ │
│  │  - hora_salida  │  │  - fecha_fin    │  │  - descripcion  │  │  - formula      │ │
│  │  - estado       │  │  - dias_solic   │  │  - fecha_inicio │  │  - unidad_med   │ │
│  │  - horas_trab   │  │  - motivo       │  │  - fecha_fin    │  │  - valor_actual │ │
│  │  - observaciones│  │  - estado       │  │  - parametros   │  │  - valor_anterior│ │
│  │  - reg_por      │  │  - aprobado_por │  │  - estado       │  │  - variacion_%  │ │
│  │  - creado_en    │  │  - fecha_aprob  │  │  - archivo_gen  │  │  - fecha_act   │ │
│  └─────────────────┘  │  - procesado_por│  │  - tam_archivo  │  │  - activo       │ │
                       │  - notas        │  │  - reg_total    │  └─────────────────┘ │
                       │  - creado_en    │  │  - tiempo_gen   │                         │
                       │  - actualizado  │  │  - error_msg    │                         │
                       └─────────────────┘  │  - solicitado   │                         │
                                              │  - fecha_sol    │                         │
                                              │  - fecha_gen    │                         │
                                              └─────────────────┘                         │
                                                                                  │
                                                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DASHBOARD Y ALERTAS                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ ESTADISTICA_GEN │  │ METRICA_TIEMPO │  │ ALERTA_DASHBOARD│  │ WIDGET_DASHBOARD│ │
│  │  - id (PK)      │  │  - id (PK)      │  │  - id (PK)      │  │  - id (PK)      │ │
│  │  - empresa (FK) │◄─┤  - empresa (FK) │◄─┤  - empresa (FK) │◄─┤  - empresa (FK) │ │
│  │  - fecha        │  │  - tipo_metrica │  │  - titulo       │  │  - nombre       │ │
│  │  - total_res    │  │  - valor        │  │  - mensaje      │  │  - tipo_widget  │ │
│  │  - res_conf     │  │  - unidad       │  │  - tipo_alerta  │  │  - posicion_x   │ │
│  │  - res_cancel   │  │  - ult_actual   │  │  - prioridad    │  │  - posicion_y   │ │
│  │  - cli_nuevos   │  └─────────────────┘  │  - leida        │  │  - ancho        │ │
│  │  - total_ing    │                      │  - acc_req      │  │  - alto         │ │
│  │  - ocup_prom    │                      │  - url_accion   │  │  - configuracion│ │
│  │  - ticket_prom  │                      │  - fecha_exp    │  │  - datos        │ │
│  │  - creado_en    │                      │  - creado_en    │  │  - refresco_auto│ │
│  └─────────────────┘                      └─────────────────┘  │  - intervalo_ref│ │
                                                                      │  - activo       │ │
                                                                      │  - creado_por   │ │
                                                                      │  - creado_en    │ │
                                                                      └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔗 Relaciones Principales

### Relaciones Uno a Muchos (1:N)
```
EMPRESA ──► USUARIO
EMPRESA ──► CLIENTE
EMPRESA ──► EMPLEADO
EMPRESA ──► HOTEL
EMPRESA ──► PAQUETE_TURIST
EMPRESA ──► RESERVA
EMPRESA ──► PAGO
EMPRESA ──► REPORTES

HOTEL ──► HABITACION
HOTEL ──► HOTEL_IMAGEN
TIPO_HABITACION ──► HABITACION
HABITACION ──► HABITACION_IMAGEN

PAQUETE_TURIST ──► PAQUETE_HOTEL
PAQUETE_TURIST ──► PAQUETE_SERVICIO

RESERVA ──► RESERVA_HABITACION
RESERVA ──► RESERVA_SERVICIO_ADICIONAL
RESERVA ──► CHECKIN
RESERVA ──► CHECKOUT

PAGO ──► REEMBOLSO

EMPLEADO ──► HORARIO_EMPLEADO
EMPLEADO ──► ASISTENCIA_EMPLEADO
EMPLEADO ──► PERMISO_EMPLEADO
```

### Relaciones Muchos a Uno (N:1)
```
USUARIO ──► EMPRESA
CLIENTE ──► EMPRESA
EMPLEADO ──► EMPRESA
HOTEL ──► EMPRESA
HABITACION ──► HOTEL
HABITACION ──► TIPO_HABITACION
PAQUETE_HOTEL ──► PAQUETE_TURIST
PAQUETE_HOTEL ──► HOTEL
PAQUETE_SERVICIO ──► PAQUETE_TURIST
RESERVA ──► EMPRESA
RESERVA ──► CLIENTE
RESERVA ──► PAQUETE_TURIST
RESERVA_HABITACION ──► RESERVA
RESERVA_HABITACION ──► HABITACION
PAGO ──► EMPRESA
PAGO ──► RESERVA
REEMBOLSO ──► PAGO
REEMBOLSO ──► RESERVA
```

## 📊 Estadísticas del Modelo

### Número de Tablas: 25
- **Gestión de Usuarios**: 3 (Empresa, Usuario, Cliente, Empleado)
- **Gestión de Hoteles**: 4 (Hotel, HotelImagen, TipoHabitacion, Habitacion, HabitacionImagen)
- **Gestión de Paquetes**: 3 (PaqueteTuristico, PaqueteHotel, PaqueteServicio)
- **Gestión de Reservas**: 5 (Reserva, ReservaHabitacion, ReservaServicioAdicional, CheckIn, CheckOut)
- **Gestión de Pagos**: 3 (Pago, MetodoPagoConfiguracion, Reembolso)
- **Recursos Humanos**: 3 (HorarioEmpleado, AsistenciaEmpleado, PermisoEmpleado)
- **Reportes**: 4 (Reporte, ReporteProgramado, MetricaReporte, DashboardConfiguracion)
- **Dashboard**: 4 (EstadisticaGeneral, MetricaTiempoReal, AlertaDashboard, WidgetDashboard)

### Número de Relaciones: ~45
- **Relaciones FK**: 35
- **Relaciones OneToOne**: 2
- **Relaciones ManyToMany**: 0 (optimizado con FK)

### Campos Totales: ~250
- **Campos de texto**: ~80
- **Campos numéricos**: ~60
- **Campos de fecha**: ~40
- **Campos booleanos**: ~30
- **Campos JSON**: ~10
- **Campos de imagen**: ~15
- **Campos UUID**: ~25

## 🔍 Características Técnicas del Diseño

### Primary Keys
- **UUIDs** para todas las tablas principales
- **Ventajas**: Seguridad, escalabilidad, no colisiones
- **Formato**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### Foreign Keys
- **Relaciones explícitas** con `on_delete` apropiado
- **PROTECT**: Para datos críticos
- **SET_NULL**: Para datos opcionales
- **CASCADE**: Para datos dependientes

### Auditoría
- **creado_en**: Timestamp de creación
- **actualizado_en**: Timestamp de última modificación
- **creado_por**: Usuario que creó el registro (donde aplica)

### Validaciones
- **Choices**: Para campos con valores predefinidos
- **Validators**: Para formatos específicos
- **Constraints**: Para integridad de datos

### Índices Estratégicos
- **empresa_id**: Para multi-tenancy
- **fechas**: Para consultas temporales
- **estados**: Para filtrado rápido
- **búsqueda**: Para campos de texto

## 🚀 Optimizaciones de Rendimiento

### Select Related y Prefetch Related
```python
# Optimización de consultas
Reserva.objects.select_related(
    'cliente', 'empresa', 'paquete'
).prefetch_related(
    'habitaciones__habitacion',
    'servicios_adicionales'
)
```

### Índices Compuestos
```python
# Índices para búsquedas comunes
class Meta:
    indexes = [
        models.Index(fields=['empresa', 'estado']),
        models.Index(fields=['fecha_checkin', 'fecha_checkout']),
        models.Index(fields=['cliente', 'creado_en']),
    ]
```

### Cache Estratégico
- **Redis** para métricas en tiempo real
- **Cache de consultas** frecuentes
- **Cache de sesiones** de usuario

## 🔐 Seguridad del Modelo

### Multi-Tenancy
- **Aislamiento** de datos por empresa
- **Filtros automáticos** en todos los querysets
- **Validación** de pertenencia a empresa

### Validaciones de Negocio
- **No sobrebooking** en habitaciones
- **Estados consistentes** en reservas
- **Saldos correctos** en pagos

### Integridad Referencial
- **PROTECT** para evitar borrados accidentales
- **SET_NULL** para datos opcionales
- **CASCADE** para datos dependientes

---

**Este ERD representa un sistema empresarial completo, escalable y optimizado para la gestión turística moderna.**
