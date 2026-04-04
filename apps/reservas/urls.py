from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReservaViewSet, ReservaHabitacionViewSet, 
    ReservaServicioAdicionalViewSet, CheckInViewSet, CheckOutViewSet
)

router = DefaultRouter()
router.register(r'reservas', ReservaViewSet)
router.register(r'habitaciones', ReservaHabitacionViewSet)
router.register(r'servicios-adicionales', ReservaServicioAdicionalViewSet)
router.register(r'checkins', CheckInViewSet)
router.register(r'checkouts', CheckOutViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
