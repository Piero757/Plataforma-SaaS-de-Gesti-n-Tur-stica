from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    dashboard_view, EstadisticaGeneralViewSet, MetricaTiempoRealViewSet,
    AlertaDashboardViewSet, WidgetDashboardViewSet, DashboardViewSet
)

router = DefaultRouter()
router.register(r'estadisticas', EstadisticaGeneralViewSet)
router.register(r'metricas', MetricaTiempoRealViewSet)
router.register(r'alertas', AlertaDashboardViewSet)
router.register(r'widgets', WidgetDashboardViewSet)
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('api/', include(router.urls)),
]
