from django.contrib import admin
from django.utils.html import format_html
from .models import TipoHabitacion, Habitacion, HabitacionImagen

class HabitacionImagenInline(admin.TabularInline):
    model = HabitacionImagen
    extra = 1
    readonly_fields = ['id', 'creado_en']
    fields = ['imagen', 'descripcion', 'orden']

@admin.register(TipoHabitacion)
class TipoHabitacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'capacidad_maxima', 'capacidad_adultos', 'capacidad_ninos', 'creado_en']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['id', 'creado_en']
    ordering = ['nombre']

@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ['numero', 'hotel', 'tipo', 'piso', 'estado_badge', 'precio_base', 'precio_actual', 'activa']
    list_filter = ['hotel', 'tipo', 'estado', 'activa', 'tiene_vista', 'tiene_balcon', 'tiene_jacuzzi']
    search_fields = ['numero', 'hotel__nombre', 'tipo__nombre', 'descripcion']
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    inlines = [HabitacionImagenInline]
    ordering = ['hotel', 'piso', 'numero']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('hotel', 'tipo', 'numero', 'piso', 'imagen')
        }),
        ('Estado', {
            'fields': ('estado', 'activa')
        }),
        ('Precios', {
            'fields': ('precio_base', 'precio_temporada_alta')
        }),
        ('Características', {
            'fields': ('descripcion', 'servicios', 'metros_cuadrados')
        }),
        ('Comodidades', {
            'fields': ('tiene_vista', 'tiene_balcon', 'tiene_jacuzzi', 'permite_mascotas', 'es_fumador')
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def estado_badge(self, obj):
        colores = {
            'disponible': 'green',
            'ocupada': 'red',
            'mantenimiento': 'orange',
            'limpieza': 'blue',
            'reservada': 'purple'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def precio_actual(self, obj):
        precio = obj.get_precio_actual()
        return f"S/. {precio:.2f}"
    precio_actual.short_description = 'Precio Actual'

@admin.register(HabitacionImagen)
class HabitacionImagenAdmin(admin.ModelAdmin):
    list_display = ['habitacion', 'descripcion', 'orden', 'thumbnail', 'creado_en']
    list_filter = ['habitacion__hotel', 'creado_en']
    search_fields = ['habitacion__numero', 'habitacion__hotel__nombre', 'descripcion']
    readonly_fields = ['id', 'creado_en']
    ordering = ['habitacion', 'orden', 'creado_en']
    
    def thumbnail(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" />', obj.imagen.url)
        return 'Sin imagen'
    thumbnail.short_description = 'Vista Previa'
