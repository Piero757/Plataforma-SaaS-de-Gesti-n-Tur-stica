from django.contrib import admin
from django.utils.html import format_html
from .models import EstadisticaGeneral, MetricaTiempoReal, AlertaDashboard, WidgetDashboard

@admin.register(EstadisticaGeneral)
class EstadisticaGeneralAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'fecha', 'total_reservas', 'reservas_confirmadas', 'total_clientes_nuevos', 'total_ingresos', 'ocupacion_promedio']
    list_filter = ['empresa', 'fecha', 'creado_en']
    search_fields = ['empresa__nombre']
    readonly_fields = ['id', 'creado_en']
    ordering = ['-fecha']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'fecha')
        }),
        ('Estadísticas de Reservas', {
            'fields': ('total_reservas', 'reservas_confirmadas', 'reservas_canceladas')
        }),
        ('Estadísticas de Clientes', {
            'fields': ('total_clientes_nuevos',)
        }),
        ('Estadísticas Financieras', {
            'fields': ('total_ingresos', 'ticket_promedio')
        }),
        ('Estadísticas de Ocupación', {
            'fields': ('ocupacion_promedio',)
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'creado_en'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MetricaTiempoReal)
class MetricaTiempoRealAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'tipo_metrica', 'valor', 'unidad', 'ultima_actualizacion']
    list_filter = ['empresa', 'tipo_metrica', 'ultima_actualizacion']
    search_fields = ['empresa__nombre']
    readonly_fields = ['id', 'ultima_actualizacion']
    ordering = ['empresa', 'tipo_metrica']

@admin.register(AlertaDashboard)
class AlertaDashboardAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'empresa', 'tipo_alerta_badge', 'prioridad_badge', 'leida', 'accion_requerida', 'creado_en']
    list_filter = ['empresa', 'tipo_alerta', 'prioridad', 'leida', 'accion_requerida', 'creado_en']
    search_fields = ['titulo', 'mensaje', 'empresa__nombre']
    readonly_fields = ['id', 'creado_en']
    ordering = ['-prioridad', '-creado_en']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'titulo', 'mensaje')
        }),
        ('Clasificación', {
            'fields': ('tipo_alerta', 'prioridad')
        }),
        ('Estado', {
            'fields': ('leida', 'accion_requerida', 'url_accion')
        }),
        ('Vigencia', {
            'fields': ('fecha_expiracion',)
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'creado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def tipo_alerta_badge(self, obj):
        colores = {
            'info': 'blue',
            'success': 'green',
            'warning': 'orange',
            'error': 'red',
            'critical': 'purple'
        }
        color = colores.get(obj.tipo_alerta, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_tipo_alerta_display()
        )
    tipo_alerta_badge.short_description = 'Tipo'
    
    def prioridad_badge(self, obj):
        colores = {
            'baja': 'green',
            'media': 'blue',
            'alta': 'orange',
            'urgente': 'red'
        }
        color = colores.get(obj.prioridad, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_prioridad_display()
        )
    prioridad_badge.short_description = 'Prioridad'

@admin.register(WidgetDashboard)
class WidgetDashboardAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'empresa', 'tipo_widget', 'posicion', 'activo', 'refresco_automatico', 'creado_en']
    list_filter = ['empresa', 'tipo_widget', 'activo', 'refresco_automatico', 'creado_en']
    search_fields = ['nombre', 'empresa__nombre']
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    ordering = ['empresa', 'posicion_y', 'posicion_x']
    
    def posicion(self, obj):
        return f"({obj.posicion_x}, {obj.posicion_y})"
    posicion.short_description = 'Posición'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'nombre', 'tipo_widget')
        }),
        ('Posición y Tamaño', {
            'fields': ('posicion_x', 'posicion_y', 'ancho', 'alto')
        }),
        ('Configuración', {
            'fields': ('configuracion', 'datos')
        }),
        ('Actualización', {
            'fields': ('refresco_automatico', 'intervalo_refresco')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'creado_por', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
