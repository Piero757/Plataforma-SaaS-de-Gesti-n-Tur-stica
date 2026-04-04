from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmpresaViewSet, UsuarioViewSet, ClienteViewSet

router = DefaultRouter()
router.register(r'empresas', EmpresaViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'clientes', ClienteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
