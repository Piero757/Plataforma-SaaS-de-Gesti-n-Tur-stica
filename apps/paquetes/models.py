from django.db import models
from apps.clientes.models import Empresa
from apps.hoteles.models import Hotel
from apps.habitaciones.models import Habitacion
import uuid

class PaqueteTuristico(models.Model):
    TIPO_PAQUETE_CHOICES = [
        ('individual', 'Individual'),
        ('pareja', 'Pareja'),
        ('familiar', 'Familiar'),
        ('grupal', 'Grupal'),
        ('corporativo', 'Corporativo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Paquete")
    tipo = models.CharField(max_length=20, choices=TIPO_PAQUETE_CHOICES, verbose_name="Tipo de Paquete")
    descripcion = models.TextField(verbose_name="Descripción")
    incluye = models.TextField(verbose_name="¿Qué incluye?")
    no_incluye = models.TextField(blank=True, verbose_name="¿Qué no incluye?")
    duracion_dias = models.PositiveIntegerField(verbose_name="Duración (días)")
    duracion_noches = models.PositiveIntegerField(verbose_name="Duración (noches)")
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Base")
    precio_temporada_alta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio Temporada Alta")
    capacidad_minima = models.PositiveIntegerField(default=1, verbose_name="Capacidad Mínima")
    capacidad_maxima = models.PositiveIntegerField(verbose_name="Capacidad Máxima")
    imagen = models.ImageField(upload_to='paquetes/', null=True, blank=True, verbose_name="Imagen")
    destinos = models.TextField(verbose_name="Destinos (separados por coma)")
    actividades = models.TextField(blank=True, verbose_name="Actividades (separados por coma)")
    requisitos = models.TextField(blank=True, verbose_name="Requisitos")
    condiciones = models.TextField(blank=True, verbose_name="Condiciones")
    es_promocion = models.BooleanField(default=False, verbose_name="Es Promoción")
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Descuento (%)")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Paquete Turístico"
        verbose_name_plural = "Paquetes Turísticos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre}"

    def get_destinos_list(self):
        if self.destinos:
            return [destino.strip() for destino in self.destinos.split(',')]
        return []

    def get_actividades_list(self):
        if self.actividades:
            return [actividad.strip() for actividad in self.actividades.split(',')]
        return []

    def get_precio_actual(self, fecha=None):
        from datetime import datetime
        if fecha is None:
            fecha = datetime.now().date()
        
        mes = fecha.month
        if mes in [12, 1, 2, 7, 8] and self.precio_temporada_alta:
            precio = self.precio_temporada_alta
        else:
            precio = self.precio_base
        
        if self.es_promocion and self.descuento_porcentaje:
            precio = precio * (1 - self.descuento_porcentaje / 100)
        
        return precio

class PaqueteHotel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paquete = models.ForeignKey(PaqueteTuristico, on_delete=models.CASCADE, related_name='hoteles', verbose_name="Paquete")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name="Hotel")
    noches = models.PositiveIntegerField(default=1, verbose_name="Número de Noches")
    tipo_habitacion_incluida = models.CharField(max_length=100, verbose_name="Tipo de Habitación Incluida")
    regimen_alimenticio = models.CharField(
        max_length=50,
        choices=[
            ('solo_alojamiento', 'Solo Alojamiento'),
            ('desayuno', 'Desayuno'),
            ('media_pension', 'Media Pensión'),
            ('pension_completa', 'Pensión Completa'),
            ('todo_incluido', 'Todo Incluido'),
        ],
        default='desayuno',
        verbose_name="Régimen Alimenticio"
    )
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Hotel del Paquete"
        verbose_name_plural = "Hoteles del Paquete"
        unique_together = ['paquete', 'hotel']

    def __str__(self):
        return f"{self.paquete.nombre} - {self.hotel.nombre}"

class PaqueteServicio(models.Model):
    TIPO_SERVICIO_CHOICES = [
        ('transporte', 'Transporte'),
        ('guia', 'Guía Turístico'),
        ('entrada', 'Entrada a Atracción'),
        ('comida', 'Comida Especial'),
        ('actividad', 'Actividad Especial'),
        ('seguro', 'Seguro de Viaje'),
        ('otro', 'Otro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paquete = models.ForeignKey(PaqueteTuristico, on_delete=models.CASCADE, related_name='servicios', verbose_name="Paquete")
    tipo = models.CharField(max_length=20, choices=TIPO_SERVICIO_CHOICES, verbose_name="Tipo de Servicio")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Servicio")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    incluido_en_precio = models.BooleanField(default=True, verbose_name="Incluido en el Precio")
    costo_adicional = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Costo Adicional")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Servicio del Paquete"
        verbose_name_plural = "Servicios del Paquete"
        ordering = ['tipo', 'nombre']

    def __str__(self):
        return f"{self.paquete.nombre} - {self.nombre}"
