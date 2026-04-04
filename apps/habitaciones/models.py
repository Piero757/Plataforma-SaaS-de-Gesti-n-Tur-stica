from django.db import models
from apps.hoteles.models import Hotel
import uuid

class TipoHabitacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Tipo")
    descripcion = models.TextField(verbose_name="Descripción")
    capacidad_maxima = models.PositiveIntegerField(verbose_name="Capacidad Máxima")
    capacidad_adultos = models.PositiveIntegerField(default=2, verbose_name="Capacidad Adultos")
    capacidad_ninos = models.PositiveIntegerField(default=0, verbose_name="Capacidad Niños")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Tipo de Habitación"
        verbose_name_plural = "Tipos de Habitación"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Habitacion(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('mantenimiento', 'En Mantenimiento'),
        ('limpieza', 'En Limpieza'),
        ('reservada', 'Reservada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name="Hotel")
    tipo = models.ForeignKey(TipoHabitacion, on_delete=models.PROTECT, verbose_name="Tipo de Habitación")
    numero = models.CharField(max_length=20, verbose_name="Número de Habitación")
    piso = models.CharField(max_length=10, blank=True, verbose_name="Piso")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible', verbose_name="Estado")
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Base")
    precio_temporada_alta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio Temporada Alta")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    servicios = models.TextField(blank=True, verbose_name="Servicios (separados por coma)")
    imagen = models.ImageField(upload_to='habitaciones/', null=True, blank=True, verbose_name="Imagen")
    metros_cuadrados = models.PositiveIntegerField(null=True, blank=True, verbose_name="Metros Cuadrados")
    tiene_vista = models.BooleanField(default=False, verbose_name="Tiene Vista")
    tiene_balcon = models.BooleanField(default=False, verbose_name="Tiene Balcón")
    tiene_jacuzzi = models.BooleanField(default=False, verbose_name="Tiene Jacuzzi")
    permite_mascotas = models.BooleanField(default=False, verbose_name="Permite Mascotas")
    es_fumador = models.BooleanField(default=False, verbose_name="Para Fumadores")
    activa = models.BooleanField(default=True, verbose_name="Activa")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"
        ordering = ['hotel', 'piso', 'numero']
        unique_together = ['hotel', 'numero']

    def __str__(self):
        return f"Habitación {self.numero} - {self.hotel.nombre}"

    def get_servicios_list(self):
        if self.servicios:
            return [servicio.strip() for servicio in self.servicios.split(',')]
        return []

    def get_precio_actual(self, fecha=None):
        from datetime import datetime
        if fecha is None:
            fecha = datetime.now().date()
        
        mes = fecha.month
        if mes in [12, 1, 2, 7, 8] and self.precio_temporada_alta:
            return self.precio_temporada_alta
        return self.precio_base

class HabitacionImagen(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE, related_name='imagenes', verbose_name="Habitación")
    imagen = models.ImageField(upload_to='habitaciones/galeria/', verbose_name="Imagen")
    descripcion = models.CharField(max_length=200, blank=True, verbose_name="Descripción")
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Imagen de Habitación"
        verbose_name_plural = "Imágenes de Habitaciones"
        ordering = ['orden', 'creado_en']

    def __str__(self):
        return f"{self.habitacion.numero} - Imagen {self.orden}"
