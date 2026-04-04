from rest_framework import serializers
from .models import Reserva, ReservaHabitacion, ReservaServicioAdicional, CheckIn, CheckOut

class ReservaHabitacionSerializer(serializers.ModelSerializer):
    numero_habitacion = serializers.CharField(source='habitacion.numero', read_only=True)
    nombre_tipo_habitacion = serializers.CharField(source='habitacion.tipo.nombre', read_only=True)
    
    class Meta:
        model = ReservaHabitacion
        fields = '__all__'
        read_only_fields = ['id', 'creado_en']

class ReservaServicioAdicionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaServicioAdicional
        fields = '__all__'
        read_only_fields = ['id', 'creado_en']

class CheckInSerializer(serializers.ModelSerializer):
    nombre_responsable = serializers.CharField(source='responsable.get_full_name', read_only=True)
    
    class Meta:
        model = CheckIn
        fields = '__all__'
        read_only_fields = ['id', 'fecha_hora']

class CheckOutSerializer(serializers.ModelSerializer):
    nombre_responsable = serializers.CharField(source='responsable.get_full_name', read_only=True)
    
    class Meta:
        model = CheckOut
        fields = '__all__'
        read_only_fields = ['id', 'fecha_hora']

class ReservaSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    nombre_cliente = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    tipo_reserva_display = serializers.CharField(source='get_tipo_reserva_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    nombre_paquete = serializers.CharField(source='paquete.nombre', read_only=True)
    noches = serializers.ReadOnlyField()
    habitaciones = ReservaHabitacionSerializer(many=True, read_only=True)
    servicios_adicionales = ReservaServicioAdicionalSerializer(many=True, read_only=True)
    checkin = CheckInSerializer(read_only=True)
    checkout = CheckOutSerializer(read_only=True)
    nombre_creador = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    
    class Meta:
        model = Reserva
        fields = '__all__'
        read_only_fields = ['id', 'codigo_reserva', 'creado_en', 'actualizado_en']

class ReservaListSerializer(serializers.ModelSerializer):
    nombre_cliente = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    tipo_reserva_display = serializers.CharField(source='get_tipo_reserva_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    noches = serializers.ReadOnlyField()
    
    class Meta:
        model = Reserva
        fields = ['id', 'codigo_reserva', 'nombre_cliente', 'tipo_reserva', 
                 'tipo_reserva_display', 'fecha_checkin', 'fecha_checkout', 
                 'noches', 'adultos', 'ninos', 'estado', 'estado_display', 
                 'total', 'monto_pagado', 'saldo_pendiente', 'creado_en']

class ReservaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = ['empresa', 'cliente', 'tipo_reserva', 'paquete', 
                 'fecha_checkin', 'fecha_checkout', 'adultos', 'ninos', 
                 'notas', 'solicitudes_especiales']

class ReservaHabitacionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaHabitacion
        fields = ['reserva', 'habitacion', 'fecha_checkin', 'fecha_checkout', 
                 'adultos', 'ninos', 'precio_por_noche']

class ReservaServicioAdicionalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaServicioAdicional
        fields = ['reserva', 'nombre_servicio', 'descripcion', 'cantidad', 
                 'precio_unitario', 'fecha_servicio']
