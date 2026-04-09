from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'clientes', views.ClienteViewSet)
router.register(r'proveedores', views.ProveedorViewSet)
router.register(r'productos', views.ProductoViewSet)
router.register(r'inventario', views.InventarioViewSet)
router.register(r'ventas', views.VentaViewSet)
router.register(r'compras', views.CompraViewSet)
router.register(r'servicios', views.RegistroServicioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
