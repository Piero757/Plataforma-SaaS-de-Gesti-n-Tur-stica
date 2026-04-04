from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'message': 'Turismo API is running',
        'version': '1.0.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),  # Dashboard principal
    path('api/health/', api_health_check, name='api_health_check'),
    path('api/auth/', include('rest_framework_simplejwt.urls')),
    path('api/clientes/', include('apps.clientes.urls')),
    path('api/reservas/', include('apps.reservas.urls')),
    path('api/hoteles/', include('apps.hoteles.urls')),
    path('api/habitaciones/', include('apps.habitaciones.urls')),
    path('api/paquetes/', include('apps.paquetes.urls')),
    path('api/pagos/', include('apps.pagos.urls')),
    path('api/empleados/', include('apps.empleados.urls')),
    path('api/reportes/', include('apps.reportes.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
