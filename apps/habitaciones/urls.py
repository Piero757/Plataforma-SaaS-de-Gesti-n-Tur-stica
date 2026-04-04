from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TipoHabitacionViewSet, HabitacionViewSet, HabitacionImagenViewSet

router = DefaultRouter()
router.register(r'tipos', TipoHabitacionViewSet)
router.register(r'habitaciones', HabitacionViewSet)
router.register(r'imagenes', HabitacionImagenViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
