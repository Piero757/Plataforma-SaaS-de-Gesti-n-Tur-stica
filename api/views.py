from rest_framework import viewsets, permissions
from gestion.models import Cliente, Proveedor, Producto, Inventario, Venta, Compra, RegistroServicio
from .serializers import (
    UserSerializer, ClienteSerializer, ProveedorSerializer, 
    ProductoSerializer, InventarioSerializer, VentaSerializer, 
    CompraSerializer, RegistroServicioSerializer
)
from django.contrib.auth.models import User

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.all()
    serializer_class = InventarioSerializer

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

class RegistroServicioViewSet(viewsets.ModelViewSet):
    queryset = RegistroServicio.objects.all()
    serializer_class = RegistroServicioSerializer
