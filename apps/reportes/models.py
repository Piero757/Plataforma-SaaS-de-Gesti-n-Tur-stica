from django.db import models
from apps.clientes.models import Empresa
import uuid

class Reporte(models.Model):
    TIPO_REPORTE_CHOICES = [
        ('ocupacion', 'Reporte de Ocupación'),
        ('ingresos', 'Reporte de Ingresos'),
        ('reservas', 'Reporte de Reservas'),
        ('clientes', 'Reporte de Clientes'),
        ('empleados', 'Reporte de Empleados'),
        ('pagos', 'Reporte de Pagos'),
        ('paquetes', 'Reporte de Paquetes Turísticos'),
        ('servicios', 'Reporte de Servicios Adicionales'),
        ('cancelaciones', 'Reporte de Cancelaciones'),
        ('mensual', 'Reporte Mensual'),
        ('anual', 'Reporte Anual'),
    ]

    ESTADO_CHOICES = [
        ('generando', 'Generando'),
        ('completado', 'Completado'),
        ('error', 'Error'),
        ('cancelado', 'Cancelado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    tipo_reporte = models.CharField(max_length=30, choices=TIPO_REPORTE_CHOICES, verbose_name="Tipo de Reporte")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Reporte")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")
    parametros = models.JSONField(default=dict, blank=True, verbose_name="Parámetros")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='generando', verbose_name="Estado")
    archivo_generado = models.FileField(upload_to='reportes/', null=True, blank=True, verbose_name="Archivo Generado")
    tamaño_archivo = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tamaño del Archivo (bytes)")
    registros_totales = models.PositiveIntegerField(null=True, blank=True, verbose_name="Registros Totales")
    tiempo_generacion = models.DurationField(null=True, blank=True, verbose_name="Tiempo de Generación")
    error_message = models.TextField(blank=True, verbose_name="Mensaje de Error")
    solicitado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name="Solicitado por")
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Solicitud")
    fecha_generacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Generación")

    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre}"

class ReporteProgramado(models.Model):
    FRECUENCIA_CHOICES = [
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    tipo_reporte = models.CharField(max_length=30, choices=Reporte.TIPO_REPORTE_CHOICES, verbose_name="Tipo de Reporte")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Reporte Programado")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    frecuencia = models.CharField(max_length=20, choices=FRECUENCIA_CHOICES, verbose_name="Frecuencia")
    dia_ejecucion = models.PositiveIntegerField(null=True, blank=True, verbose_name="Día de Ejecución (1-31)")
    hora_ejecucion = models.TimeField(default='09:00', verbose_name="Hora de Ejecución")
    parametros = models.JSONField(default=dict, blank=True, verbose_name="Parámetros")
    email_destinatarios = models.TextField(help_text="Emails separados por coma", verbose_name="Email Destinatarios")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    ultima_ejecucion = models.DateTimeField(null=True, blank=True, verbose_name="Última Ejecución")
    proxima_ejecucion = models.DateTimeField(null=True, blank=True, verbose_name="Próxima Ejecución")
    creado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name="Creado por")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Reporte Programado"
        verbose_name_plural = "Reportes Programados"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre}"

    def get_email_destinatarios_list(self):
        if self.email_destinatarios:
            return [email.strip() for email in self.email_destinatarios.split(',')]
        return []

class MetricaReporte(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Métrica")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    formula = models.TextField(verbose_name="Fórmula de Cálculo")
    unidad_medida = models.CharField(max_length=50, verbose_name="Unidad de Medida")
    valor_actual = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Valor Actual")
    valor_anterior = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Valor Anterior")
    variacion_porcentual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Variación Porcentual")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Métrica de Reporte"
        verbose_name_plural = "Métricas de Reportes"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre}"

    def save(self, *args, **kwargs):
        if self.valor_anterior and self.valor_actual:
            if self.valor_anterior != 0:
                self.variacion_porcentual = ((self.valor_actual - self.valor_anterior) / abs(self.valor_anterior)) * 100
            else:
                self.variacion_porcentual = None
        super().save(*args, **kwargs)

class DashboardConfiguracion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    nombre_dashboard = models.CharField(max_length=200, verbose_name="Nombre del Dashboard")
    layout_configuracion = models.JSONField(default=dict, verbose_name="Configuración del Layout")
    widgets_configuracion = models.JSONField(default=dict, verbose_name="Configuración de Widgets")
    filtros_configuracion = models.JSONField(default=dict, verbose_name="Configuración de Filtros")
    periodo_actualizacion = models.PositiveIntegerField(default=5, verbose_name="Período de Actualización (minutos)")
    publico = models.BooleanField(default=False, verbose_name="Público")
    url_compartida = models.CharField(max_length=100, blank=True, verbose_name="URL Compartida")
    creado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name="Creado por")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Configuración de Dashboard"
        verbose_name_plural = "Configuraciones de Dashboards"
        ordering = ['nombre_dashboard']

    def __str__(self):
        return f"{self.nombre_dashboard} - {self.empresa.nombre}"
