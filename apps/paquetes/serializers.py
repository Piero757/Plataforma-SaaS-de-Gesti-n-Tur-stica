from rest_framework import serializers
from .models import PaqueteTuristico, PaqueteHotel, PaqueteServicio

class PaqueteHotelSerializer(serializers.ModelSerializer):
    nombre_hotel = serializers.CharField(source='hotel.nombre', read_only=True)
    regimen_display = serializers.CharField(source='get_regimen_alimenticio_display', read_only=True)
    
    class Meta:
        model = PaqueteHotel
        fields = '__all__'
        read_only_fields = ['id', 'creado_en']

class PaqueteServicioSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = PaqueteServicio
        fields = '__all__'
        read_only_fields = ['id', 'creado_en']

class PaqueteTuristicoSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    destinos_list = serializers.SerializerMethodField()
    actividades_list = serializers.SerializerMethodField()
    precio_actual = serializers.SerializerMethodField()
    hoteles = PaqueteHotelSerializer(many=True, read_only=True)
    servicios = PaqueteServicioSerializer(many=True, read_only=True)
    
    class Meta:
        model = PaqueteTuristico
        fields = '__all__'
        read_only_fields = ['id', 'creado_en', 'actualizado_en']

    def get_destinos_list(self, obj):
        return obj.get_destinos_list()

    def get_actividades_list(self, obj):
        return obj.get_actividades_list()

    def get_precio_actual(self, obj):
        return obj.get_precio_actual()

class PaqueteListSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    precio_actual = serializers.SerializerMethodField()
    
    class Meta:
        model = PaqueteTuristico
        fields = ['id', 'nombre', 'tipo', 'tipo_display', 'duracion_dias', 
                 'duracion_noches', 'precio_base', 'precio_actual', 
                 'capacidad_minima', 'capacidad_maxima', 'es_promocion', 
                 'descuento_porcentaje', 'activo']

    def get_precio_actual(self, obj):
        return obj.get_precio_actual()

class PaqueteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaqueteTuristico
        fields = ['empresa', 'nombre', 'tipo', 'descripcion', 'incluye', 
                 'no_incluye', 'duracion_dias', 'duracion_noches', 
                 'precio_base', 'precio_temporada_alta', 'capacidad_minima', 
                 'capacidad_maxima', 'destinos', 'actividades', 'requisitos', 
                 'condiciones', 'es_promocion', 'descuento_porcentaje']
