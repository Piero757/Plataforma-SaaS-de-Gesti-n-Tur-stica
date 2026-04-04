from rest_framework import serializers
from .models import TipoHabitacion, Habitacion, HabitacionImagen

class TipoHabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoHabitacion
        fields = '__all__'
        read_only_fields = ['id', 'creado_en']

class HabitacionImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitacionImagen
        fields = '__all__'
        read_only_fields = ['id', 'creado_en']

class HabitacionSerializer(serializers.ModelSerializer):
    nombre_hotel = serializers.CharField(source='hotel.nombre', read_only=True)
    nombre_tipo = serializers.CharField(source='tipo.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    servicios_list = serializers.SerializerMethodField()
    precio_actual = serializers.SerializerMethodField()
    imagenes = HabitacionImagenSerializer(many=True, read_only=True)
    
    class Meta:
        model = Habitacion
        fields = '__all__'
        read_only_fields = ['id', 'creado_en', 'actualizado_en']

    def get_servicios_list(self, obj):
        return obj.get_servicios_list()

    def get_precio_actual(self, obj):
        return obj.get_precio_actual()

class HabitacionListSerializer(serializers.ModelSerializer):
    nombre_hotel = serializers.CharField(source='hotel.nombre', read_only=True)
    nombre_tipo = serializers.CharField(source='tipo.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    precio_actual = serializers.SerializerMethodField()
    
    class Meta:
        model = Habitacion
        fields = ['id', 'numero', 'nombre_hotel', 'nombre_tipo', 'estado', 
                 'estado_display', 'precio_base', 'precio_actual', 'activa']

    def get_precio_actual(self, obj):
        return obj.get_precio_actual()

class HabitacionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habitacion
        fields = ['hotel', 'tipo', 'numero', 'piso', 'precio_base', 
                 'precio_temporada_alta', 'descripcion', 'servicios', 
                 'metros_cuadrados', 'tiene_vista', 'tiene_balcon', 
                 'tiene_jacuzzi', 'permite_mascotas', 'es_fumador']
