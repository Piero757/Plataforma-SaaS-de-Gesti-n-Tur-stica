from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import Empresa, Usuario, Cliente

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ruc', 'email', 'telefono', 'activo', 'creado_en']
    list_filter = ['activo', 'creado_en']
    search_fields = ['nombre', 'ruc', 'email']
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'ruc', 'logo')
        }),
        ('Contacto', {
            'fields': ('direccion', 'telefono', 'email', 'sitio_web')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'nombre_completo', 'empresa', 'rol', 'is_active', 'creado_en']
    list_filter = ['empresa', 'rol', 'is_active', 'is_staff', 'creado_en']
    search_fields = ['username', 'email', 'nombres', 'apellidos']
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    ordering = ['username']
    
    fieldsets = (
        ('Información de Usuario', {
            'fields': ('username', 'password', 'empresa')
        }),
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'email', 'telefono')
        }),
        ('Información Laboral', {
            'fields': ('cargo', 'rol')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'empresa', 'rol'),
        }),
    )
    
    def nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellidos}" if obj.nombres and obj.apellidos else obj.username
    nombre_completo.short_description = 'Nombre Completo'

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'tipo_documento', 'numero_documento', 'email', 'telefono', 'vip', 'activo', 'empresa']
    list_filter = ['empresa', 'tipo_documento', 'vip', 'activo', 'creado_en']
    search_fields = ['nombres', 'apellidos', 'numero_documento', 'email', 'telefono']
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    ordering = ['apellidos', 'nombres']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('empresa', 'nombres', 'apellidos', 'tipo_documento', 'numero_documento')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'direccion')
        }),
        ('Información Adicional', {
            'fields': ('fecha_nacimiento', 'nacionalidad', 'preferencias')
        }),
        ('Estado', {
            'fields': ('vip', 'activo')
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def nombre_completo(self, obj):
        return f"{obj.apellidos}, {obj.nombres}"
    nombre_completo.short_description = 'Nombre Completo'
    
    def vip(self, obj):
        if obj.vip:
            return format_html('<span style="color: gold;">⭐ VIP</span>')
        return 'No'
    vip.boolean = True
    vip.short_description = 'VIP'
