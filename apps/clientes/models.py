from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid

class Empresa(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Empresa")
    ruc = models.CharField(max_length=11, unique=True, verbose_name="RUC")
    direccion = models.TextField(verbose_name="Dirección")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Email corporativo")
    logo = models.ImageField(upload_to='empresas/logos/', null=True, blank=True, verbose_name="Logo")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    cargo = models.CharField(max_length=100, blank=True, verbose_name="Cargo")
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('gerente', 'Gerente'),
        ('recepcion', 'Recepción'),
        ('ventas', 'Ventas'),
        ('operativo', 'Operativo'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='operativo', verbose_name="Rol")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['username']

    def __str__(self):
        return f"{self.username} - {self.empresa.nombre}"

class Cliente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    tipo_documento = models.CharField(
        max_length=20,
        choices=[
            ('dni', 'DNI'),
            ('pasaporte', 'Pasaporte'),
            ('cedula', 'Cédula'),
        ],
        default='dni',
        verbose_name="Tipo de documento"
    )
    numero_documento = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de documento",
        validators=[RegexValidator(r'^[0-9]+$', 'Solo se permiten números')]
    )
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Email")
    direccion = models.TextField(blank=True, verbose_name="Dirección")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")
    nacionalidad = models.CharField(max_length=50, default='Peruana', verbose_name="Nacionalidad")
    preferencias = models.TextField(blank=True, verbose_name="Preferencias")
    vip = models.BooleanField(default=False, verbose_name="Cliente VIP")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['apellidos', 'nombres']
        unique_together = ['empresa', 'numero_documento']

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"
