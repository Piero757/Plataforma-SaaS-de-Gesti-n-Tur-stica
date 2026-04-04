from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmpleadoViewSet, HorarioEmpleadoViewSet, 
    AsistenciaEmpleadoViewSet, PermisoEmpleadoViewSet
)

router = DefaultRouter()
router.register(r'empleados', EmpleadoViewSet)
router.register(r'horarios', HorarioEmpleadoViewSet)
router.register(r'asistencias', AsistenciaEmpleadoViewSet)
router.register(r'permisos', PermisoEmpleadoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
