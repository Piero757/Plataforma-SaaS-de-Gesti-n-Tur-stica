from django.db import models
from django.core.validators import MinValueValidator
from apps.clientes.models import Empresa, Cliente
from apps.hoteles.models import Hotel
from apps.habitaciones.models import Habitacion
from apps.paquetes.models import PaqueteTuristico
import uuid

class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('checkin', 'Check-in Realizado'),
        ('checkout', 'Check-out Realizado'),
        ('cancelada', 'Cancelada'),
        ('no_show', 'No Show'),
    ]

    TIPO_RESERVA_CHOICES = [
        ('habitacion', 'Solo Habitación'),
        ('paquete', 'Paquete Turístico'),
        ('grupal', 'Reserva Grupal'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    codigo_reserva = models.CharField(max_length=20, unique=True, verbose_name="Código de Reserva")
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, verbose_name="Cliente")
    tipo_reserva = models.CharField(max_length=20, choices=TIPO_RESERVA_CHOICES, verbose_name="Tipo de Reserva")
    paquete = models.ForeignKey(PaqueteTuristico, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Paquete Turístico")
    fecha_checkin = models.DateField(verbose_name="Fecha de Check-in")
    fecha_checkout = models.DateField(verbose_name="Fecha de Check-out")
    adultos = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Adultos")
    ninos = models.PositiveIntegerField(default=0, verbose_name="Niños")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name="Estado")
    subtotal_habitaciones = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Subtotal Habitaciones")
    subtotal_paquete = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Subtotal Paquete")
    subtotal_servicios_adicionales = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Subtotal Servicios Adicionales")
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Descuento")
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Impuestos")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total")
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Monto Pagado")
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Saldo Pendiente")
    notas = models.TextField(blank=True, verbose_name="Notas")
    solicitudes_especiales = models.TextField(blank=True, verbose_name="Solicitudes Especiales")
    creado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name="Creado por")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-creado_en']

    def __str__(self):
        return f"Reserva {self.codigo_reserva} - {self.cliente.nombre_completo}"

    def save(self, *args, **kwargs):
        if not self.codigo_reserva:
            from django.utils import timezone
            year = timezone.now().year
            last_reserva = Reserva.objects.filter(
                empresa=self.empresa,
                codigo_reserva__startswith=f'RES-{year}'
            ).order_by('-codigo_reserva').first()
            
            if last_reserva:
                last_number = int(last_reserva.codigo_reserva.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.codigo_reserva = f'RES-{year}-{new_number:06d}'
        
        self.saldo_pendiente = self.total - self.monto_pagado
        super().save(*args, **kwargs)

    @property
    def noches(self):
        return (self.fecha_checkout - self.fecha_checkin).days

class ReservaHabitacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='habitaciones', verbose_name="Reserva")
    habitacion = models.ForeignKey(Habitacion, on_delete=models.PROTECT, verbose_name="Habitación")
    fecha_checkin = models.DateField(verbose_name="Fecha de Check-in")
    fecha_checkout = models.DateField(verbose_name="Fecha de Check-out")
    adultos = models.PositiveIntegerField(default=1, verbose_name="Adultos")
    ninos = models.PositiveIntegerField(default=0, verbose_name="Niños")
    precio_por_noche = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por Noche")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Habitación Reservada"
        verbose_name_plural = "Habitaciones Reservadas"

    def __str__(self):
        return f"{self.reserva.codigo_reserva} - {self.habitacion.numero}"

    def save(self, *args, **kwargs):
        noches = (self.fecha_checkout - self.fecha_checkin).days
        self.subtotal = self.precio_por_noche * noches
        super().save(*args, **kwargs)

class ReservaServicioAdicional(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='servicios_adicionales', verbose_name="Reserva")
    nombre_servicio = models.CharField(max_length=200, verbose_name="Nombre del Servicio")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")
    fecha_servicio = models.DateField(null=True, blank=True, verbose_name="Fecha del Servicio")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Servicio Adicional"
        verbose_name_plural = "Servicios Adicionales"

    def __str__(self):
        return f"{self.reserva.codigo_reserva} - {self.nombre_servicio}"

    def save(self, *args, **kwargs):
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)

class CheckIn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, verbose_name="Reserva")
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    responsable = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name="Responsable")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    documento_entregado = models.BooleanField(default=False, verbose_name="Documento Entregado")
    deposito_recibido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Depósito Recibido")

    class Meta:
        verbose_name = "Check-in"
        verbose_name_plural = "Check-ins"

    def __str__(self):
        return f"Check-in {self.reserva.codigo_reserva}"

class CheckOut(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, verbose_name="Reserva")
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    responsable = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name="Responsable")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    cargo_adicional = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Cargo Adicional")
    deposito_devuelto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Depósito Devuelto")
    metodo_pago_adicional = models.CharField(max_length=50, blank=True, verbose_name="Método de Pago Adicional")

    class Meta:
        verbose_name = "Check-out"
        verbose_name_plural = "Check-outs"

    def __str__(self):
        return f"Check-out {self.reserva.codigo_reserva}"
