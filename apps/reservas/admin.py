from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Reserva, ReservaHabitacion, ReservaServicioAdicional, CheckIn, CheckOut

class ReservaHabitacionInline(admin.TabularInline):
    model = ReservaHabitacion
    extra = 1
    readonly_fields = ['id', 'creado_en', 'subtotal']
    fields = ['habitacion', 'fecha_checkin', 'fecha_checkout', 'adultos', 'ninos', 'precio_por_noche']

class ReservaServicioAdicionalInline(admin.TabularInline):
    model = ReservaServicioAdicional
    extra = 1
    readonly_fields = ['id', 'creado_en', 'subtotal']
    fields = ['nombre_servicio', 'descripcion', 'cantidad', 'precio_unitario', 'fecha_servicio']

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['codigo_reserva', 'cliente', 'tipo_reserva', 'estado_badge', 'fecha_checkin', 'noches', 'total', 'saldo_pendiente', 'creado_en']
    list_filter = ['empresa', 'tipo_reserva', 'estado', 'fecha_checkin', 'creado_en']
    search_fields = ['codigo_reserva', 'cliente__nombres', 'cliente__apellidos', 'notas']
    readonly_fields = ['id', 'codigo_reserva', 'noches', 'subtotal_habitaciones', 'subtotal_paquete', 
                      'subtotal_servicios_adicionales', 'total', 'saldo_pendiente', 'creado_en', 'actualizado_en']
    inlines = [ReservaHabitacionInline, ReservaServicioAdicionalInline]
    ordering = ['-creado_en']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'codigo_reserva', 'cliente', 'tipo_reserva', 'paquete')
        }),
        ('Fechas', {
            'fields': ('fecha_checkin', 'fecha_checkout')
        }),
        ('Ocupación', {
            'fields': ('adultos', 'ninos')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Información Adicional', {
            'fields': ('notas', 'solicitudes_especiales')
        }),
        ('Resumen Financiero', {
            'fields': ('subtotal_habitaciones', 'subtotal_paquete', 'subtotal_servicios_adicionales', 
                       'descuento', 'impuestos', 'total', 'monto_pagado', 'saldo_pendiente'),
            'classes': ('collapse',)
        }),
        ('Información de Auditoría', {
            'fields': ('id', 'creado_por', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def noches(self, obj):
        return (obj.fecha_checkout - obj.fecha_checkin).days
    noches.short_description = 'Noches'
    
    def estado_badge(self, obj):
        colores = {
            'pendiente': 'orange',
            'confirmada': 'blue',
            'checkin': 'green',
            'checkout': 'purple',
            'cancelada': 'red',
            'no_show': 'gray'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'

@admin.register(ReservaHabitacion)
class ReservaHabitacionAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'habitacion', 'fecha_checkin', 'fecha_checkout', 'adultos', 'ninos', 'subtotal']
    list_filter = ['reserva', 'habitacion__hotel', 'fecha_checkin', 'creado_en']
    search_fields = ['reserva__codigo_reserva', 'habitacion__numero']
    readonly_fields = ['id', 'creado_en', 'subtotal']
    ordering = ['-fecha_checkin']

@admin.register(ReservaServicioAdicional)
class ReservaServicioAdicionalAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'nombre_servicio', 'cantidad', 'precio_unitario', 'subtotal', 'fecha_servicio']
    list_filter = ['reserva', 'fecha_servicio', 'creado_en']
    search_fields = ['reserva__codigo_reserva', 'nombre_servicio']
    readonly_fields = ['id', 'creado_en', 'subtotal']
    ordering = ['-fecha_servicio']

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'fecha_hora', 'responsable', 'documento_entregado', 'deposito_recibido']
    list_filter = ['reserva__hotel', 'responsable', 'documento_entregado', 'fecha_hora']
    search_fields = ['reserva__codigo_reserva', 'responsable__username']
    readonly_fields = ['id', 'fecha_hora']
    ordering = ['-fecha_hora']

@admin.register(CheckOut)
class CheckOutAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'fecha_hora', 'responsable', 'cargo_adicional', 'deposito_devuelto']
    list_filter = ['reserva__hotel', 'responsable', 'metodo_pago_adicional', 'fecha_hora']
    search_fields = ['reserva__codigo_reserva', 'responsable__username']
    readonly_fields = ['id', 'fecha_hora']
    ordering = ['-fecha_hora']
