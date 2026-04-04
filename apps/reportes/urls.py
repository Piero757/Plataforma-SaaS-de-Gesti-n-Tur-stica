from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReporteViewSet, ReporteProgramadoViewSet,
    MetricaReporteViewSet, DashboardConfiguracionViewSet
)

router = DefaultRouter()
router.register(r'reportes', ReporteViewSet)
router.register(r'programados', ReporteProgramadoViewSet)
router.register(r'metricas', MetricaReporteViewSet)
router.register(r'dashboards', DashboardConfiguracionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
