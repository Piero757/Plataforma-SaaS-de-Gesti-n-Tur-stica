from django.contrib import admin
from django.utils.html import format_html
from .models import Pago, MetodoPagoConfiguracion, Reembolso

class ReembolsoInline(admin.TabularInline):
    model = Reembolso
    extra = 0
    readonly_fields = ['id', 'fecha_solicitud', 'fecha_procesamiento']
    fields = ['monto', 'motivo', 'metodo_reembolso', 'estado', 'referencia_reembolso']

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['codigo_pago', 'reserva', 'tipo_pago', 'metodo_pago', 'monto', 'estado_badge', 'fecha_pago', 'comprobante_badge']
    list_filter = ['empresa', 'tipo_pago', 'metodo_pago', 'estado', 'comprobante_generado', 'fecha_pago', 'creado_en']
    search_fields = ['codigo_pago', 'reserva__codigo_reserva', 'referencia', 'numero_operacion']
    readonly_fields = ['id', 'codigo_pago', 'creado_en', 'actualizado_en']
    inlines = [ReembolsoInline]
    ordering = ['-creado_en']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'codigo_pago', 'reserva', 'tipo_pago')
        }),
        ('Monto y Método', {
            'fields': ('monto', 'metodo_pago')
        }),
        ('Estado', {
            'fields': ('estado', 'fecha_pago')
        }),
        ('Información Bancaria', {
            'fields': ('referencia', 'banco_origen', 'banco_destino', 'numero_operacion')
        }),
        ('Comprobante', {
            'fields': ('comprobante_generado', 'tipo_comprobante', 'numero_comprobante')
        }),
        ('Descripción', {
            'fields': ('descripcion',)
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'registrado_por', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def estado_badge(self, obj):
        colores = {
            'pendiente': 'orange',
            'procesando': 'blue',
            'completado': 'green',
            'fallido': 'red',
            'cancelado': 'gray',
            'reembolsado': 'purple'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def comprobante_badge(self, obj):
        if obj.comprobante_generado:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 8px; border-radius: 3px;">✓</span>'
            )
        return 'No'
    comprobante_badge.short_description = 'Comprobante'

@admin.register(MetodoPagoConfiguracion)
class MetodoPagoConfiguracionAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'metodo_pago', 'activo', 'comision_porcentaje', 'comision_fija']
    list_filter = ['empresa', 'metodo_pago', 'activo', 'creado_en']
    search_fields = ['empresa__nombre', 'metodo_pago']
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    ordering = ['empresa', 'metodo_pago']

@admin.register(Reembolso)
class ReembolsoAdmin(admin.ModelAdmin):
    list_display = ['pago_original', 'reserva', 'monto', 'metodo_reembolso', 'estado_badge', 'fecha_solicitud', 'fecha_procesamiento']
    list_filter = ['pago_original__empresa', 'estado', 'metodo_reembolso', 'fecha_solicitud', 'fecha_procesamiento']
    search_fields = ['pago_original__codigo_pago', 'reserva__codigo_reserva', 'motivo']
    readonly_fields = ['id', 'fecha_solicitud']
    ordering = ['-fecha_solicitud']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('pago_original', 'reserva', 'monto', 'motivo')
        }),
        ('Procesamiento', {
            'fields': ('metodo_reembolso', 'estado', 'referencia_reembolso')
        }),
        ('Aprobación', {
            'fields': ('aprobado_por', 'fecha_aprobacion')
        }),
        ('Procesamiento Final', {
            'fields': ('procesado_por', 'fecha_procesamiento')
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'fecha_solicitud'),
            'classes': ('collapse',)
        }),
    )
    
    def estado_badge(self, obj):
        colores = {
            'solicitado': 'orange',
            'aprobado': 'blue',
            'procesando': 'purple',
            'completado': 'green',
            'rechazado': 'red'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
