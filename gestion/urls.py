from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('usuarios/', views.usuarios_list, name='usuarios_list'),
    path('usuarios/nuevo/', views.usuario_create, name='usuario_create'),
    path('clientes/', views.clientes_list, name='clientes_list'),
    path('clientes/nuevo/', views.cliente_create, name='cliente_create'),
    path('ventas/', views.ventas_list, name='ventas_list'),
    path('ventas/exportar/', views.exportar_ventas_excel, name='exportar_ventas_excel'),
    path('inventario/', views.inventario_list, name='inventario_list'),
    path('proveedores/', views.proveedores_list, name='proveedores_list'),
    path('compras/', views.compras_list, name='compras_list'),
    path('facturacion/', views.facturacion_list, name='facturacion_list'),
    path('servicios/', views.servicios_list, name='servicios_list'),
    path('reportes/', views.reportes_view, name='reportes_view'),
]
