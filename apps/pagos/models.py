from django.db import models
from apps.clientes.models import Empresa
from apps.reservas.models import Reserva
import uuid

class Pago(models.Model):
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta_credito', 'Tarjeta de Crédito'),
        ('tarjeta_debito', 'Tarjeta de Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('deposito', 'Depósito Bancario'),
        ('yape', 'Yape'),
        ('plin', 'Plin'),
        ('paypal', 'PayPal'),
        ('otro', 'Otro'),
    ]

    ESTADO_PAGO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('cancelado', 'Cancelado'),
        ('reembolsado', 'Reembolsado'),
    ]

    TIPO_PAGO_CHOICES = [
        ('reserva', 'Pago de Reserva'),
        ('adelanto', 'Adelanto'),
        ('saldo', 'Saldo'),
        ('servicio_adicional', 'Servicio Adicional'),
        ('multa', 'Multa/ Penalidad'),
        ('reembolso', 'Reembolso'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, verbose_name="Reserva")
    codigo_pago = models.CharField(max_length=20, unique=True, verbose_name="Código de Pago")
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES, verbose_name="Tipo de Pago")
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, verbose_name="Método de Pago")
    estado = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='pendiente', verbose_name="Estado")
    fecha_pago = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Pago")
    referencia = models.CharField(max_length=100, blank=True, verbose_name="Referencia")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    banco_origen = models.CharField(max_length=100, blank=True, verbose_name="Banco Origen")
    banco_destino = models.CharField(max_length=100, blank=True, verbose_name="Banco Destino")
    numero_operacion = models.CharField(max_length=50, blank=True, verbose_name="Número de Operación")
    comprobante_generado = models.BooleanField(default=False, verbose_name="Comprobante Generado")
    tipo_comprobante = models.CharField(
        max_length=20,
        choices=[
            ('boleta', 'Boleta'),
            ('factura', 'Factura'),
            ('recibo', 'Recibo'),
        ],
        blank=True,
        verbose_name="Tipo de Comprobante"
    )
    numero_comprobante = models.CharField(max_length=50, blank=True, verbose_name="Número de Comprobante")
    registrado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name="Registrado por")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-creado_en']

    def __str__(self):
        return f"Pago {self.codigo_pago} - {self.reserva.codigo_reserva}"

    def save(self, *args, **kwargs):
        if not self.codigo_pago:
            from django.utils import timezone
            year = timezone.now().year
            last_pago = Pago.objects.filter(
                empresa=self.empresa,
                codigo_pago__startswith=f'PAG-{year}'
            ).order_by('-codigo_pago').first()
            
            if last_pago:
                last_number = int(last_pago.codigo_pago.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.codigo_pago = f'PAG-{year}-{new_number:06d}'
        
        super().save(*args, **kwargs)

class MetodoPagoConfiguracion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    metodo_pago = models.CharField(max_length=20, choices=Pago.METODO_PAGO_CHOICES, verbose_name="Método de Pago")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    requiere_comprobante = models.BooleanField(default=False, verbose_name="Requiere Comprobante")
    comision_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Comisión (%)")
    comision_fija = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Comisión Fija")
    configuracion_adicional = models.JSONField(default=dict, blank=True, verbose_name="Configuración Adicional")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Configuración de Método de Pago"
        verbose_name_plural = "Configuraciones de Métodos de Pago"
        unique_together = ['empresa', 'metodo_pago']

    def __str__(self):
        return f"{self.empresa.nombre} - {self.get_metodo_pago_display()}"

class Reembolso(models.Model):
    ESTADO_REEMBOLSO_CHOICES = [
        ('solicitado', 'Solicitado'),
        ('aprobado', 'Aprobado'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('rechazado', 'Rechazado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pago_original = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='reembolsos', verbose_name="Pago Original")
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, verbose_name="Reserva")
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto a Reembolsar")
    motivo = models.TextField(verbose_name="Motivo del Reembolso")
    estado = models.CharField(max_length=20, choices=ESTADO_REEMBOLSO_CHOICES, default='solicitado', verbose_name="Estado")
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Solicitud")
    fecha_procesamiento = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Procesamiento")
    metodo_reembolso = models.CharField(max_length=20, choices=Pago.METODO_PAGO_CHOICES, verbose_name="Método de Reembolso")
    referencia_reembolso = models.CharField(max_length=100, blank=True, verbose_name="Referencia de Reembolso")
    aprobado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='reembolsos_aprobados', verbose_name="Aprobado por")
    procesado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='reembolsos_procesados', verbose_name="Procesado por")
    notas = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Reembolso"
        verbose_name_plural = "Reembolsos"
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Reembolso {self.id} - {self.reserva.codigo_reserva}"
