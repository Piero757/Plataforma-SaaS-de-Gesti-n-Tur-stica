from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PagoViewSet, MetodoPagoConfiguracionViewSet, ReembolsoViewSet
)

router = DefaultRouter()
router.register(r'pagos', PagoViewSet)
router.register(r'metodos-pago', MetodoPagoConfiguracionViewSet)
router.register(r'reembolsos', ReembolsoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
