from rest_framework import serializers
from gestion.models import Cliente, Proveedor, Producto, Inventario, Venta, DetalleVenta, Compra, RegistroServicio, FacturaElectronica
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class InventarioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    class Meta:
        model = Inventario
        fields = '__all__'

class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    class Meta:
        model = DetalleVenta
        fields = '__all__'

class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    cliente_nombre = serializers.ReadOnlyField(source='cliente.nombre_razon_social')
    class Meta:
        model = Venta
        fields = '__all__'

class CompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compra
        fields = '__all__'

class RegistroServicioSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.ReadOnlyField(source='cliente.nombre_razon_social')
    class Meta:
        model = RegistroServicio
        fields = '__all__'
