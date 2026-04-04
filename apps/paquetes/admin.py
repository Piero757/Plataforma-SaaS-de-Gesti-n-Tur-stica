from django.contrib import admin
from django.utils.html import format_html
from .models import PaqueteTuristico, PaqueteHotel, PaqueteServicio

class PaqueteHotelInline(admin.TabularInline):
    model = PaqueteHotel
    extra = 1
    readonly_fields = ['id', 'creado_en']
    fields = ['hotel', 'noches', 'tipo_habitacion_incluida', 'regimen_alimenticio']

class PaqueteServicioInline(admin.TabularInline):
    model = PaqueteServicio
    extra = 1
    readonly_fields = ['id', 'creado_en']
    fields = ['tipo', 'nombre', 'descripcion', 'incluido_en_precio', 'costo_adicional']

@admin.register(PaqueteTuristico)
class PaqueteTuristicoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'empresa', 'tipo', 'duracion', 'precio_base', 'precio_actual', 'promocion_badge', 'activo']
    list_filter = ['empresa', 'tipo', 'activo', 'es_promocion', 'creado_en']
    search_fields = ['nombre', 'descripcion', 'incluye', 'destinos']
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    inlines = [PaqueteHotelInline, PaqueteServicioInline]
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'nombre', 'tipo', 'imagen')
        }),
        ('Descripción', {
            'fields': ('descripcion', 'incluye', 'no_incluye')
        }),
        ('Duración', {
            'fields': ('duracion_dias', 'duracion_noches')
        }),
        ('Precios', {
            'fields': ('precio_base', 'precio_temporada_alta', 'capacidad_minima', 'capacidad_maxima')
        }),
        ('Destinos y Actividades', {
            'fields': ('destinos', 'actividades')
        }),
        ('Información Adicional', {
            'fields': ('requisitos', 'condiciones')
        }),
        ('Promoción', {
            'fields': ('es_promocion', 'descuento_porcentaje')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def duracion(self, obj):
        return f"{obj.duracion_dias}d / {obj.duracion_noches}n"
    duracion.short_description = 'Duración'
    
    def precio_actual(self, obj):
        precio = obj.get_precio_actual()
        return f"S/. {precio:.2f}"
    precio_actual.short_description = 'Precio Actual'
    
    def promocion_badge(self, obj):
        if obj.es_promocion:
            descuento = obj.descuento_porcentaje or 0
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px 8px; border-radius: 3px;">PROMO {}%</span>',
                descuento
            )
        return 'No'
    promocion_badge.short_description = 'Promoción'

@admin.register(PaqueteHotel)
class PaqueteHotelAdmin(admin.ModelAdmin):
    list_display = ['paquete', 'hotel', 'noches', 'tipo_habitacion_incluida', 'regimen_alimenticio', 'creado_en']
    list_filter = ['paquete', 'hotel', 'regimen_alimenticio', 'creado_en']
    search_fields = ['paquete__nombre', 'hotel__nombre']
    readonly_fields = ['id', 'creado_en']
    ordering = ['paquete', 'hotel']

@admin.register(PaqueteServicio)
class PaqueteServicioAdmin(admin.ModelAdmin):
    list_display = ['paquete', 'tipo', 'nombre', 'incluido_en_precio', 'costo_adicional', 'creado_en']
    list_filter = ['paquete', 'tipo', 'incluido_en_precio', 'creado_en']
    search_fields = ['paquete__nombre', 'nombre', 'descripcion']
    readonly_fields = ['id', 'creado_en']
    ordering = ['paquete', 'tipo', 'nombre']
