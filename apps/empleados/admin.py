from django.contrib import admin
from django.utils.html import format_html
from .models import Empleado, HorarioEmpleado, AsistenciaEmpleado, PermisoEmpleado

class HorarioEmpleadoInline(admin.TabularInline):
    model = HorarioEmpleado
    extra = 1
    readonly_fields = ['id', 'creado_en']
    fields = ['dia_semana', 'hora_entrada', 'hora_salida', 'activo']

class AsistenciaEmpleadoInline(admin.TabularInline):
    model = AsistenciaEmpleado
    extra = 0
    readonly_fields = ['id', 'creado_en', 'horas_trabajadas']
    fields = ['fecha', 'hora_entrada', 'hora_salida', 'estado', 'observaciones']

class PermisoEmpleadoInline(admin.TabularInline):
    model = PermisoEmpleado
    extra = 0
    readonly_fields = ['id', 'fecha_solicitud', 'fecha_aprobacion', 'actualizado_en']
    fields = ['tipo_permiso', 'fecha_inicio', 'fecha_fin', 'dias_solicitados', 'estado', 'motivo']

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['codigo_empleado', 'nombre_completo', 'cargo', 'departamento', 'turno', 'estado_badge', 'telefono', 'empresa']
    list_filter = ['empresa', 'cargo', 'departamento', 'turno', 'estado', 'activo', 'creado_en']
    search_fields = ['codigo_empleado', 'nombres', 'apellidos', 'numero_documento', 'email']
    readonly_fields = ['id', 'codigo_empleado', 'edad', 'creado_en', 'actualizado_en']
    inlines = [HorarioEmpleadoInline, AsistenciaEmpleadoInline, PermisoEmpleadoInline]
    ordering = ['apellidos', 'nombres']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'codigo_empleado', 'nombres', 'apellidos', 'foto')
        }),
        ('Identificación', {
            'fields': ('tipo_documento', 'numero_documento', 'fecha_nacimiento')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'email_corporativo', 'direccion')
        }),
        ('Información Laboral', {
            'fields': ('cargo', 'departamento', 'fecha_contratacion', 'tipo_contrato', 'salario', 'turno')
        }),
        ('Estado', {
            'fields': ('estado', 'usuario_sistema')
        }),
        ('Habilidades y Experiencia', {
            'fields': ('habilidades', 'certificaciones', 'idiomas', 'experiencia_previa')
        }),
        ('Contacto de Emergencia', {
            'fields': ('contacto_emergencia_nombre', 'contacto_emergencia_telefono', 'contacto_emergencia_parentesco')
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'edad', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def nombre_completo(self, obj):
        return f"{obj.apellidos}, {obj.nombres}"
    nombre_completo.short_description = 'Nombre Completo'
    
    def estado_badge(self, obj):
        colores = {
            'activo': 'green',
            'vacaciones': 'blue',
            'licencia': 'orange',
            'suspendido': 'red',
            'inactivo': 'gray'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'

@admin.register(HorarioEmpleado)
class HorarioEmpleadoAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'dia_semana', 'hora_entrada', 'hora_salida', 'activo']
    list_filter = ['empleado', 'dia_semana', 'activo', 'creado_en']
    search_fields = ['empleado__nombres', 'empleado__apellidos']
    readonly_fields = ['id', 'creado_en']
    ordering = ['empleado', 'dia_semana']

@admin.register(AsistenciaEmpleado)
class AsistenciaEmpleadoAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'fecha', 'hora_entrada', 'hora_salida', 'estado_badge', 'horas_trabajadas', 'registrado_por']
    list_filter = ['empleado', 'estado', 'fecha', 'creado_en']
    search_fields = ['empleado__nombres', 'empleado__apellidos', 'observaciones']
    readonly_fields = ['id', 'creado_en', 'horas_trabajadas']
    ordering = ['-fecha', 'empleado']
    
    def estado_badge(self, obj):
        colores = {
            'presente': 'green',
            'ausente': 'red',
            'tarde': 'orange',
            'permiso': 'blue',
            'vacaciones': 'purple',
            'licencia': 'gray'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'

@admin.register(PermisoEmpleado)
class PermisoEmpleadoAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'tipo_permiso', 'fecha_inicio', 'fecha_fin', 'dias_solicitados', 'estado_badge', 'fecha_solicitud']
    list_filter = ['empleado', 'tipo_permiso', 'estado', 'fecha_solicitud', 'fecha_aprobacion']
    search_fields = ['empleado__nombres', 'empleado__apellidos', 'motivo']
    readonly_fields = ['id', 'fecha_solicitud', 'fecha_aprobacion', 'actualizado_en']
    ordering = ['-fecha_solicitud']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empleado', 'tipo_permiso', 'fecha_inicio', 'fecha_fin', 'dias_solicitados')
        }),
        ('Motivo', {
            'fields': ('motivo',)
        }),
        ('Procesamiento', {
            'fields': ('estado', 'aprobado_por', 'fecha_aprobacion')
        }),
        ('Información Adicional', {
            'fields': ('notas',)
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'fecha_solicitud', 'fecha_aprobacion', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def estado_badge(self, obj):
        colores = {
            'pendiente': 'orange',
            'aprobado': 'green',
            'rechazado': 'red',
            'cancelado': 'gray'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
