from rest_framework import serializers
from .models import Pago, MetodoPagoConfiguracion, Reembolso

class MetodoPagoConfiguracionSerializer(serializers.ModelSerializer):
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    
    class Meta:
        model = MetodoPagoConfiguracion
        fields = '__all__'
        read_only_fields = ['id', 'creado_en', 'actualizado_en']

class ReembolsoSerializer(serializers.ModelSerializer):
    nombre_pago_original = serializers.CharField(source='pago_original.codigo_pago', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    metodo_reembolso_display = serializers.CharField(source='get_metodo_reembolso_display', read_only=True)
    nombre_aprobado_por = serializers.CharField(source='aprobado_por.get_full_name', read_only=True)
    nombre_procesado_por = serializers.CharField(source='procesado_por.get_full_name', read_only=True)
    
    class Meta:
        model = Reembolso
        fields = '__all__'
        read_only_fields = ['id', 'fecha_solicitud', 'fecha_procesamiento']

class PagoSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    codigo_reserva = serializers.CharField(source='reserva.codigo_reserva', read_only=True)
    tipo_pago_display = serializers.CharField(source='get_tipo_pago_display', read_only=True)
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_comprobante_display = serializers.CharField(source='get_tipo_comprobante_display', read_only=True)
    nombre_registrado_por = serializers.CharField(source='registrado_por.get_full_name', read_only=True)
    reembolsos = ReembolsoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pago
        fields = '__all__'
        read_only_fields = ['id', 'codigo_pago', 'creado_en', 'actualizado_en']

class PagoListSerializer(serializers.ModelSerializer):
    codigo_reserva = serializers.CharField(source='reserva.codigo_reserva', read_only=True)
    tipo_pago_display = serializers.CharField(source='get_tipo_pago_display', read_only=True)
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Pago
        fields = ['id', 'codigo_pago', 'codigo_reserva', 'tipo_pago', 
                 'tipo_pago_display', 'monto', 'metodo_pago', 'metodo_pago_display', 
                 'estado', 'estado_display', 'fecha_pago', 'referencia', 
                 'comprobante_generado', 'creado_en']

class PagoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['empresa', 'reserva', 'tipo_pago', 'monto', 'metodo_pago', 
                 'referencia', 'descripcion', 'banco_origen', 'banco_destino', 
                 'numero_operacion', 'tipo_comprobante']

class ReembolsoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reembolso
        fields = ['pago_original', 'reserva', 'monto', 'motivo', 
                 'metodo_reembolso', 'referencia_reembolso', 'notas']
