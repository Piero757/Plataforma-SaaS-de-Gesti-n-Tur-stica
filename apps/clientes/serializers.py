from rest_framework import serializers
from .models import Empresa, Usuario, Cliente

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'
        read_only_fields = ['id', 'creado_en', 'actualizado_en']

class UsuarioSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    
    class Meta:
        model = Usuario
        fields = '__all__'
        read_only_fields = ['id', 'creado_en', 'actualizado_en']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class ClienteSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    tipo_documento_display = serializers.CharField(source='get_tipo_documento_display', read_only=True)
    nombre_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ['id', 'creado_en', 'actualizado_en']

class ClienteListSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()
    tipo_documento_display = serializers.CharField(source='get_tipo_documento_display', read_only=True)
    
    class Meta:
        model = Cliente
        fields = ['id', 'nombre_completo', 'tipo_documento', 'numero_documento', 
                 'telefono', 'email', 'vip', 'activo']

class ClienteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['empresa', 'nombres', 'apellidos', 'tipo_documento', 
                 'numero_documento', 'telefono', 'email', 'direccion', 
                 'fecha_nacimiento', 'nacionalidad', 'preferencias', 'vip']
