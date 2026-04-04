from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, HotelImagenViewSet

router = DefaultRouter()
router.register(r'hoteles', HotelViewSet)
router.register(r'imagenes', HotelImagenViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
