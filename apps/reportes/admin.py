from django.contrib import admin
from django.utils.html import format_html
from .models import Reporte, ReporteProgramado, MetricaReporte, DashboardConfiguracion

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'empresa', 'tipo_reporte', 'estado_badge', 'fecha_inicio', 'fecha_fin', 'registros_totales', 'tiempo_generacion', 'solicitado_por']
    list_filter = ['empresa', 'tipo_reporte', 'estado', 'fecha_solicitud', 'fecha_generacion']
    search_fields = ['nombre', 'descripcion', 'empresa__nombre']
    readonly_fields = ['id', 'codigo_archivo', 'tamaño_archivo', 'tiempo_generacion', 'fecha_solicitud', 'fecha_generacion']
    ordering = ['-fecha_solicitud']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'nombre', 'tipo_reporte', 'descripcion')
        }),
        ('Rango de Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Configuración', {
            'fields': ('parametros',)
        }),
        ('Estado', {
            'fields': ('estado', 'error_message')
        }),
        ('Archivo Generado', {
            'fields': ('archivo_generado', 'tamaño_archivo', 'registros_totales', 'tiempo_generacion'),
            'classes': ('collapse',)
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'solicitado_por', 'fecha_solicitud', 'fecha_generacion'),
            'classes': ('collapse',)
        }),
    )
    
    def estado_badge(self, obj):
        colores = {
            'generando': 'blue',
            'completado': 'green',
            'error': 'red',
            'cancelado': 'gray'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def codigo_archivo(self, obj):
        if obj.archivo_generado:
            return format_html('<a href="{}" target="_blank">Descargar</a>', obj.archivo_generado.url)
        return 'No disponible'
    codigo_archivo.short_description = 'Archivo'

@admin.register(ReporteProgramado)
class ReporteProgramadoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'empresa', 'tipo_reporte', 'frecuencia', 'activo', 'proxima_ejecucion', 'ultima_ejecucion', 'creado_por']
    list_filter = ['empresa', 'tipo_reporte', 'frecuencia', 'activo', 'creado_en']
    search_fields = ['nombre', 'descripcion', 'empresa__nombre']
    readonly_fields = ['id', 'ultima_ejecucion', 'proxima_ejecucion', 'creado_en', 'actualizado_en']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'nombre', 'tipo_reporte', 'descripcion')
        }),
        ('Programación', {
            'fields': ('frecuencia', 'dia_ejecucion', 'hora_ejecucion')
        }),
        ('Configuración', {
            'fields': ('parametros', 'email_destinatarios')
        }),
        ('Estado', {
            'fields': ('activo', 'publico', 'url_compartida')
        }),
        ('Ejecución', {
            'fields': ('ultima_ejecucion', 'proxima_ejecucion'),
            'classes': ('collapse',)
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'creado_por', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MetricaReporte)
class MetricaReporteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'empresa', 'valor_actual', 'valor_anterior', 'variacion_badge', 'unidad_medida', 'activo', 'fecha_actualizacion']
    list_filter = ['empresa', 'activo', 'fecha_actualizacion']
    search_fields = ['nombre', 'descripcion', 'empresa__nombre']
    readonly_fields = ['id', 'fecha_actualizacion']
    ordering = ['empresa', 'nombre']
    
    def variacion_badge(self, obj):
        if obj.variacion_porcentual is None:
            return 'N/A'
        
        if obj.variacion_porcentual > 0:
            color = 'green'
            icono = '↑'
        elif obj.variacion_porcentual < 0:
            color = 'red'
            icono = '↓'
        else:
            color = 'gray'
            icono = '→'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {:.2f}%</span>',
            color,
            icono,
            abs(obj.variacion_porcentual)
        )
    variacion_badge.short_description = 'Variación'

@admin.register(DashboardConfiguracion)
class DashboardConfiguracionAdmin(admin.ModelAdmin):
    list_display = ['nombre_dashboard', 'empresa', 'publico', 'periodo_actualizacion', 'creado_por', 'creado_en']
    list_filter = ['empresa', 'publico', 'creado_en']
    search_fields = ['nombre_dashboard', 'empresa__nombre']
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    ordering = ['nombre_dashboard']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'nombre_dashboard', 'periodo_actualizacion')
        }),
        ('Configuración', {
            'fields': ('layout_configuracion', 'widgets_configuracion', 'filtros_configuracion')
        }),
        ('Compartir', {
            'fields': ('publico', 'url_compartida')
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'creado_por', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
