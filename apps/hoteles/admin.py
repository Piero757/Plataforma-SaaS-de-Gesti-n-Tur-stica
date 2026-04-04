from django.contrib import admin
from django.utils.html import format_html
from .models import Hotel, HotelImagen

class HotelImagenInline(admin.TabularInline):
    model = HotelImagen
    extra = 1
    readonly_fields = ['id', 'creado_en']
    fields = ['imagen', 'descripcion', 'orden']

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria_estrellas', 'ciudad', 'pais', 'telefono', 'activo', 'creado_en']
    list_filter = ['empresa', 'categoria', 'ciudad', 'pais', 'activo', 'creado_en']
    search_fields = ['nombre', 'descripcion', 'direccion', 'ciudad']
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    inlines = [HotelImagenInline]
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'nombre', 'categoria', 'imagen_principal')
        }),
        ('Descripción', {
            'fields': ('descripcion',)
        }),
        ('Ubicación', {
            'fields': ('direccion', 'ciudad', 'pais', 'coordenadas_lat', 'coordenadas_lng')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'sitio_web')
        }),
        ('Operaciones', {
            'fields': ('check_in_time', 'check_out_time')
        }),
        ('Servicios y Políticas', {
            'fields': ('servicios', 'politicas')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def categoria_estrellas(self, obj):
        estrellas = '⭐' * obj.categoria
        return format_html(f'<span>{estrellas}</span>')
    categoria_estrellas.short_description = 'Categoría'

@admin.register(HotelImagen)
class HotelImagenAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'descripcion', 'orden', 'thumbnail', 'creado_en']
    list_filter = ['hotel', 'creado_en']
    search_fields = ['hotel__nombre', 'descripcion']
    readonly_fields = ['id', 'creado_en']
    ordering = ['hotel', 'orden', 'creado_en']
    
    def thumbnail(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" />', obj.imagen.url)
        return 'Sin imagen'
    thumbnail.short_description = 'Vista Previa'
