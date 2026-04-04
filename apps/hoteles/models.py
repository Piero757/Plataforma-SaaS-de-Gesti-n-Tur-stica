from django.db import models
from apps.clientes.models import Empresa
import uuid

class Hotel(models.Model):
    CATEGORIA_CHOICES = [
        (1, '1 Estrella'),
        (2, '2 Estrellas'),
        (3, '3 Estrellas'),
        (4, '4 Estrellas'),
        (5, '5 Estrellas'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Hotel")
    categoria = models.IntegerField(choices=CATEGORIA_CHOICES, verbose_name="Categoría")
    descripcion = models.TextField(verbose_name="Descripción")
    direccion = models.TextField(verbose_name="Dirección")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad")
    pais = models.CharField(max_length=100, default='Perú', verbose_name="País")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Email")
    sitio_web = models.URLField(blank=True, verbose_name="Sitio Web")
    imagen_principal = models.ImageField(upload_to='hoteles/imagenes/', null=True, blank=True, verbose_name="Imagen Principal")
    coordenadas_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name="Latitud")
    coordenadas_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name="Longitud")
    check_in_time = models.TimeField(default='14:00', verbose_name="Hora de Check-in")
    check_out_time = models.TimeField(default='12:00', verbose_name="Hora de Check-out")
    servicios = models.TextField(blank=True, verbose_name="Servicios (separados por coma)")
    politicas = models.TextField(blank=True, verbose_name="Políticas del hotel")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Hotel"
        verbose_name_plural = "Hoteles"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre}"

    def get_servicios_list(self):
        if self.servicios:
            return [servicio.strip() for servicio in self.servicios.split(',')]
        return []

class HotelImagen(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='imagenes', verbose_name="Hotel")
    imagen = models.ImageField(upload_to='hoteles/galeria/', verbose_name="Imagen")
    descripcion = models.CharField(max_length=200, blank=True, verbose_name="Descripción")
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Imagen de Hotel"
        verbose_name_plural = "Imágenes de Hoteles"
        ordering = ['orden', 'creado_en']

    def __str__(self):
        return f"{self.hotel.nombre} - Imagen {self.orden}"
