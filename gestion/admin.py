from django.contrib import admin
from .models import Cliente, Proveedor, Producto, Inventario, Venta, DetalleVenta, Compra, RegistroServicio, FacturaElectronica

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'nombre_razon_social', 'tipo_documento', 'telefono')
    search_fields = ('numero_documento', 'nombre_razon_social')

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('ruc', 'razon_social', 'telefono')
    search_fields = ('ruc', 'razon_social')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio_venta', 'precio_compra')
    list_filter = ('categoria',)
    search_fields = ('codigo', 'nombre')

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'stock_actual', 'ultima_actualizacion')

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('tipo_comprobante', 'serie', 'numero', 'cliente', 'fecha', 'total', 'estado_sunat')
    list_filter = ('tipo_comprobante', 'estado_sunat', 'forma_pago')
    inlines = [DetalleVentaInline]

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('numero_comprobante', 'proveedor', 'fecha', 'total')

@admin.register(RegistroServicio)
class RegistroServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre_servicio', 'cliente', 'fecha', 'precio')

@admin.register(FacturaElectronica)
class FacturaElectronicaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'fecha_emision', 'hash_cpe')
