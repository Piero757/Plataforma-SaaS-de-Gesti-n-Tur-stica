from django.db import models
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from apps.clientes.models import Empresa
from apps.reservas.models import Reserva
from apps.pagos.models import Pago
from apps.clientes.models import Cliente
from apps.empleados.models import Empleado
import uuid

class EstadisticaGeneral(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    fecha = models.DateField(verbose_name="Fecha")
    total_reservas = models.PositiveIntegerField(default=0, verbose_name="Total Reservas")
    reservas_confirmadas = models.PositiveIntegerField(default=0, verbose_name="Reservas Confirmadas")
    reservas_canceladas = models.PositiveIntegerField(default=0, verbose_name="Reservas Canceladas")
    total_clientes_nuevos = models.PositiveIntegerField(default=0, verbose_name="Total Clientes Nuevos")
    total_ingresos = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total Ingresos")
    ocupacion_promedio = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Ocupación Promedio (%)")
    ticket_promedio = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Ticket Promedio")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Estadística General"
        verbose_name_plural = "Estadísticas Generales"
        unique_together = ['empresa', 'fecha']
        ordering = ['-fecha']

    def __str__(self):
        return f"Estadísticas {self.empresa.nombre} - {self.fecha}"

    @classmethod
    def generar_estadisticas_diarias(cls, empresa, fecha=None):
        if fecha is None:
            fecha = timezone.now().date()
        
        from apps.reservas.models import Reserva
        from apps.pagos.models import Pago
        from apps.clientes.models import Cliente
        
        reservas_dia = Reserva.objects.filter(
            empresa=empresa,
            creado_en__date=fecha
        )
        
        pagos_dia = Pago.objects.filter(
            empresa=empresa,
            estado='completado',
            fecha_pago__date=fecha
        )
        
        clientes_nuevos = Cliente.objects.filter(
            empresa=empresa,
            creado_en__date=fecha
        )
        
        total_reservas = reservas_dia.count()
        reservas_confirmadas = reservas_dia.filter(estado='confirmada').count()
        reservas_canceladas = reservas_dia.filter(estado='cancelada').count()
        total_clientes_nuevos = clientes_nuevos.count()
        total_ingresos = pagos_dia.aggregate(total=Sum('monto'))['total'] or 0
        
        ticket_promedio = total_ingresos / reservas_confirmadas if reservas_confirmadas > 0 else 0
        
        estadistica, created = cls.objects.update_or_create(
            empresa=empresa,
            fecha=fecha,
            defaults={
                'total_reservas': total_reservas,
                'reservas_confirmadas': reservas_confirmadas,
                'reservas_canceladas': reservas_canceladas,
                'total_clientes_nuevos': total_clientes_nuevos,
                'total_ingresos': total_ingresos,
                'ticket_promedio': ticket_promedio,
            }
        )
        
        return estadistica

class MetricaTiempoReal(models.Model):
    TIPO_METRICA_CHOICES = [
        ('reservas_hoy', 'Reservas de Hoy'),
        ('ingresos_hoy', 'Ingresos de Hoy'),
        ('ocupacion_actual', 'Ocupación Actual'),
        ('checkins_pendientes', 'Check-ins Pendientes'),
        ('checkouts_pendientes', 'Check-outs Pendientes'),
        ('habitaciones_disponibles', 'Habitaciones Disponibles'),
        ('clientes_activos_mes', 'Clientes Activos del Mes'),
        ('tasa_cancelacion', 'Tasa de Cancelación'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    tipo_metrica = models.CharField(max_length=30, choices=TIPO_METRICA_CHOICES, verbose_name="Tipo de Métrica")
    valor = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor")
    unidad = models.CharField(max_length=20, default='unidad', verbose_name="Unidad")
    ultima_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Métrica en Tiempo Real"
        verbose_name_plural = "Métricas en Tiempo Real"
        unique_together = ['empresa', 'tipo_metrica']

    def __str__(self):
        return f"{self.get_tipo_metrica_display()} - {self.empresa.nombre}"

    @classmethod
    def actualizar_metricas(cls, empresa):
        from apps.reservas.models import Reserva, CheckIn, CheckOut
        from apps.pagos.models import Pago
        from apps.clientes.models import Cliente
        from apps.habitaciones.models import Habitacion
        from django.utils import timezone
        
        hoy = timezone.now().date()
        inicio_mes = hoy.replace(day=1)
        
        # Reservas de hoy
        reservas_hoy = Reserva.objects.filter(
            empresa=empresa,
            creado_en__date=hoy
        ).count()
        
        # Ingresos de hoy
        ingresos_hoy = Pago.objects.filter(
            empresa=empresa,
            estado='completado',
            fecha_pago__date=hoy
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        # Ocupación actual
        total_habitaciones = Habitacion.objects.filter(empresa=empresa, activa=True).count()
        habitaciones_ocupadas = Reserva.objects.filter(
            empresa=empresa,
            estado='checkin',
            fecha_checkin__lte=hoy,
            fecha_checkout__gt=hoy
        ).count()
        
        ocupacion_actual = (habitaciones_ocupadas / total_habitaciones * 100) if total_habitaciones > 0 else 0
        
        # Check-ins pendientes
        checkins_pendientes = Reserva.objects.filter(
            empresa=empresa,
            estado='confirmada',
            fecha_checkin=hoy
        ).exclude(checkin__isnull=False).count()
        
        # Check-outs pendientes
        checkouts_pendientes = Reserva.objects.filter(
            empresa=empresa,
            estado='checkin',
            fecha_checkout=hoy
        ).exclude(checkout__isnull=False).count()
        
        # Habitaciones disponibles
        habitaciones_disponibles = Habitacion.objects.filter(
            empresa=empresa,
            estado='disponible',
            activa=True
        ).count()
        
        # Clientes activos del mes
        clientes_activos_mes = Cliente.objects.filter(
            empresa=empresa,
            reserva__fecha_checkin__gte=inicio_mes,
            reserva__fecha_checkin__lte=hoy
        ).distinct().count()
        
        # Tasa de cancelación
        total_reservas_mes = Reserva.objects.filter(
            empresa=empresa,
            creado_en__gte=inicio_mes,
            creado_en__lte=hoy
        ).count()
        
        reservas_canceladas_mes = Reserva.objects.filter(
            empresa=empresa,
            estado='cancelada',
            creado_en__gte=inicio_mes,
            creado_en__lte=hoy
        ).count()
        
        tasa_cancelacion = (reservas_canceladas_mes / total_reservas_mes * 100) if total_reservas_mes > 0 else 0
        
        # Actualizar métricas
        metricas_data = [
            ('reservas_hoy', reservas_hoy, 'reservas'),
            ('ingresos_hoy', ingresos_hoy, 'soles'),
            ('ocupacion_actual', ocupacion_actual, '%'),
            ('checkins_pendientes', checkins_pendientes, 'check-ins'),
            ('checkouts_pendientes', checkouts_pendientes, 'check-outs'),
            ('habitaciones_disponibles', habitaciones_disponibles, 'habitaciones'),
            ('clientes_activos_mes', clientes_activos_mes, 'clientes'),
            ('tasa_cancelacion', tasa_cancelacion, '%'),
        ]
        
        for tipo_metrica, valor, unidad in metricas_data:
            cls.objects.update_or_create(
                empresa=empresa,
                tipo_metrica=tipo_metrica,
                defaults={
                    'valor': valor,
                    'unidad': unidad
                }
            )

class AlertaDashboard(models.Model):
    TIPO_ALERTA_CHOICES = [
        ('info', 'Información'),
        ('success', 'Éxito'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('critical', 'Crítico'),
    ]

    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensaje = models.TextField(verbose_name="Mensaje")
    tipo_alerta = models.CharField(max_length=20, choices=TIPO_ALERTA_CHOICES, default='info', verbose_name="Tipo de Alerta")
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media', verbose_name="Prioridad")
    leida = models.BooleanField(default=False, verbose_name="Leída")
    accion_requerida = models.BooleanField(default=False, verbose_name="Acción Requerida")
    url_accion = models.CharField(max_length=200, blank=True, verbose_name="URL de Acción")
    fecha_expiracion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Expiración")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Alerta de Dashboard"
        verbose_name_plural = "Alertas de Dashboard"
        ordering = ['-prioridad', '-creado_en']

    def __str__(self):
        return f"{self.titulo} - {self.empresa.nombre}"

    @classmethod
    def crear_alerta_automatica(cls, empresa, tipo_alerta, titulo, mensaje, prioridad='media', accion_requerida=False, url_accion=''):
        alerta = cls.objects.create(
            empresa=empresa,
            titulo=titulo,
            mensaje=mensaje,
            tipo_alerta=tipo_alerta,
            prioridad=prioridad,
            accion_requerida=accion_requerida,
            url_accion=url_accion
        )
        return alerta

    def marcar_como_leida(self):
        self.leida = True
        self.save(update_fields=['leida'])

class WidgetDashboard(models.Model):
    TIPO_WIDGET_CHOICES = [
        ('numero', 'Número'),
        ('grafico_barras', 'Gráfico de Barras'),
        ('grafico_lineas', 'Gráfico de Líneas'),
        ('grafico_pastel', 'Gráfico Circular'),
        ('tabla', 'Tabla'),
        ('lista', 'Lista'),
        ('calendario', 'Calendario'),
        ('mapa', 'Mapa'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Widget")
    tipo_widget = models.CharField(max_length=20, choices=TIPO_WIDGET_CHOICES, verbose_name="Tipo de Widget")
    posicion_x = models.PositiveIntegerField(default=0, verbose_name="Posición X")
    posicion_y = models.PositiveIntegerField(default=0, verbose_name="Posición Y")
    ancho = models.PositiveIntegerField(default=4, verbose_name="Ancho")
    alto = models.PositiveIntegerField(default=3, verbose_name="Alto")
    configuracion = models.JSONField(default=dict, verbose_name="Configuración")
    datos = models.JSONField(default=dict, verbose_name="Datos")
    refresco_automatico = models.BooleanField(default=True, verbose_name="Refresco Automático")
    intervalo_refresco = models.PositiveIntegerField(default=5, verbose_name="Intervalo de Refresco (minutos)")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name="Creado por")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Widget de Dashboard"
        verbose_name_plural = "Widgets de Dashboard"
        ordering = ['posicion_y', 'posicion_x']

    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre}"
