from django.db import models
from django.core.validators import RegexValidator
from apps.clientes.models import Empresa
import uuid

class Empleado(models.Model):
    CARGO_CHOICES = [
        ('gerente_general', 'Gerente General'),
        ('gerente_operaciones', 'Gerente de Operaciones'),
        ('gerente_ventas', 'Gerente de Ventas'),
        ('recepcionista', 'Recepcionista'),
        ('agente_viajes', 'Agente de Viajes'),
        ('guia_turistico', 'Guía Turístico'),
        ('conserje', 'Conserje'),
        ('personal_limpieza', 'Personal de Limpieza'),
        ('mantenimiento', 'Mantenimiento'),
        ('cocinero', 'Cocinero'),
        ('mesero', 'Mesero'),
        ('administrativo', 'Administrativo'),
        ('contador', 'Contador'),
        ('marketing', 'Marketing'),
        ('otro', 'Otro'),
    ]

    TURNO_CHOICES = [
        ('mañana', 'Mañana (6:00 - 14:00)'),
        ('tarde', 'Tarde (14:00 - 22:00)'),
        ('noche', 'Noche (22:00 - 6:00)'),
        ('mixto', 'Turno Mixto'),
        ('administrativo', 'Administrativo (8:00 - 17:00)'),
    ]

    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('vacaciones', 'Vacaciones'),
        ('licencia', 'Licencia Médica'),
        ('suspendido', 'Suspendido'),
        ('inactivo', 'Inactivo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    codigo_empleado = models.CharField(max_length=20, unique=True, verbose_name="Código de Empleado")
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    tipo_documento = models.CharField(
        max_length=20,
        choices=[
            ('dni', 'DNI'),
            ('pasaporte', 'Pasaporte'),
            ('cedula', 'Cédula'),
            ('carnet_extranjeria', 'Carnet de Extranjería'),
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
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Email Personal")
    email_corporativo = models.EmailField(blank=True, verbose_name="Email Corporativo")
    direccion = models.TextField(verbose_name="Dirección")
    cargo = models.CharField(max_length=50, choices=CARGO_CHOICES, verbose_name="Cargo")
    departamento = models.CharField(max_length=100, verbose_name="Departamento")
    fecha_contratacion = models.DateField(verbose_name="Fecha de Contratación")
    tipo_contrato = models.CharField(
        max_length=20,
        choices=[
            ('tiempo_completo', 'Tiempo Completo'),
            ('medio_tiempo', 'Medio Tiempo'),
            ('temporal', 'Temporal'),
            ('practicas', 'Prácticas'),
            ('consultor', 'Consultor'),
        ],
        default='tiempo_completo',
        verbose_name="Tipo de Contrato"
    )
    salario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salario")
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES, verbose_name="Turno")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo', verbose_name="Estado")
    foto = models.ImageField(upload_to='empleados/fotos/', null=True, blank=True, verbose_name="Foto")
    habilidades = models.TextField(blank=True, verbose_name="Habilidades (separadas por coma)")
    certificaciones = models.TextField(blank=True, verbose_name="Certificaciones")
    idiomas = models.TextField(blank=True, verbose_name="Idiomas (separados por coma)")
    experiencia_previa = models.TextField(blank=True, verbose_name="Experiencia Previa")
    contacto_emergencia_nombre = models.CharField(max_length=200, verbose_name="Contacto de Emergencia - Nombre")
    contacto_emergencia_telefono = models.CharField(max_length=20, verbose_name="Contacto de Emergencia - Teléfono")
    contacto_emergencia_parentesco = models.CharField(max_length=50, verbose_name="Contacto de Emergencia - Parentesco")
    usuario_sistema = models.OneToOneField('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario del Sistema")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ['apellidos', 'nombres']
        unique_together = ['empresa', 'numero_documento']

    def __str__(self):
        return f"{self.apellidos}, {self.nombres} - {self.empresa.nombre}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def edad(self):
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))

    def get_habilidades_list(self):
        if self.habilidades:
            return [habilidad.strip() for habilidad in self.habilidades.split(',')]
        return []

    def get_idiomas_list(self):
        if self.idiomas:
            return [idioma.strip() for idioma in self.idiomas.split(',')]
        return []

class HorarioEmpleado(models.Model):
    DIA_CHOICES = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miércoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sábado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='horarios', verbose_name="Empleado")
    dia_semana = models.CharField(max_length=10, choices=DIA_CHOICES, verbose_name="Día de la Semana")
    hora_entrada = models.TimeField(verbose_name="Hora de Entrada")
    hora_salida = models.TimeField(verbose_name="Hora de Salida")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Horario de Empleado"
        verbose_name_plural = "Horarios de Empleados"
        unique_together = ['empleado', 'dia_semana']

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.get_dia_semana_display()}"

class AsistenciaEmpleado(models.Model):
    ESTADO_CHOICES = [
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
        ('tarde', 'Llegó Tarde'),
        ('permiso', 'Permiso'),
        ('vacaciones', 'Vacaciones'),
        ('licencia', 'Licencia Médica'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='asistencias', verbose_name="Empleado")
    fecha = models.DateField(verbose_name="Fecha")
    hora_entrada = models.TimeField(null=True, blank=True, verbose_name="Hora de Entrada")
    hora_salida = models.TimeField(null=True, blank=True, verbose_name="Hora de Salida")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, verbose_name="Estado")
    horas_trabajadas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Horas Trabajadas")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    registrado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name="Registrado por")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Asistencia de Empleado"
        verbose_name_plural = "Asistencias de Empleados"
        unique_together = ['empleado', 'fecha']
        ordering = ['-fecha', 'empleado']

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.fecha}"

    def save(self, *args, **kwargs):
        if self.hora_entrada and self.hora_salida:
            from datetime import datetime, time
            entrada = datetime.combine(self.fecha, self.hora_entrada)
            salida = datetime.combine(self.fecha, self.hora_salida)
            if salida < entrada:
                from datetime import timedelta
                salida += timedelta(days=1)
            diff = salida - entrada
            self.horas_trabajadas = diff.total_seconds() / 3600
        super().save(*args, **kwargs)

class PermisoEmpleado(models.Model):
    TIPO_PERMISO_CHOICES = [
        ('vacaciones', 'Vacaciones'),
        ('licencia_medica', 'Licencia Médica'),
        ('permiso_personal', 'Permiso Personal'),
        ('duelo', 'Duelo'),
        ('maternidad', 'Maternidad'),
        ('paternidad', 'Paternidad'),
        ('estudio', 'Estudio'),
        ('otro', 'Otro'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('cancelado', 'Cancelado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='permisos', verbose_name="Empleado")
    tipo_permiso = models.CharField(max_length=20, choices=TIPO_PERMISO_CHOICES, verbose_name="Tipo de Permiso")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")
    dias_solicitados = models.PositiveIntegerField(verbose_name="Días Solicitados")
    motivo = models.TextField(verbose_name="Motivo")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name="Estado")
    aprobado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='permisos_aprobados', verbose_name="Aprobado por")
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Aprobación")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Permiso de Empleado"
        verbose_name_plural = "Permisos de Empleados"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.get_tipo_permiso_display()}"
