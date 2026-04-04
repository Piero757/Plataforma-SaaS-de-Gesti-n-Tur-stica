from rest_framework import serializers
from .models import Hotel, HotelImagen

class HotelImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImagen
        fields = '__all__'
        read_only_fields = ['id', 'creado_en']

class HotelSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    imagenes = HotelImagenSerializer(many=True, read_only=True)
    servicios_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Hotel
        fields = '__all__'
        read_only_fields = ['id', 'creado_en', 'actualizado_en']

    def get_servicios_list(self, obj):
        return obj.get_servicios_list()

class HotelListSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    
    class Meta:
        model = Hotel
        fields = ['id', 'nombre', 'categoria', 'categoria_display', 'ciudad', 
                 'pais', 'telefono', 'email', 'activo']

class HotelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['empresa', 'nombre', 'categoria', 'descripcion', 'direccion', 
                 'ciudad', 'pais', 'telefono', 'email', 'sitio_web', 
                 'coordenadas_lat', 'coordenadas_lng', 'check_in_time', 
                 'check_out_time', 'servicios', 'politicas']
