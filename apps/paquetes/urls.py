from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaqueteTuristicoViewSet, PaqueteHotelViewSet, PaqueteServicioViewSet

router = DefaultRouter()
router.register(r'paquetes', PaqueteTuristicoViewSet)
router.register(r'hoteles', PaqueteHotelViewSet)
router.register(r'servicios', PaqueteServicioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
