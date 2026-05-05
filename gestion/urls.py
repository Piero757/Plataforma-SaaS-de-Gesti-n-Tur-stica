from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    path('restaurante/', views.restaurante_view, name='restaurante'),
    path('modulo/cambiar/', views.cambiar_modulo, name='cambiar_modulo'),
    
    # Usuarios
    path('usuarios/', views.usuarios_list, name='usuarios_list'),
    path('usuarios/nuevo/', views.usuario_create, name='usuario_create'),
    path('usuarios/editar/<int:pk>/', views.usuario_update, name='usuario_update'),
    path('usuarios/estado/<int:pk>/', views.usuario_toggle_status, name='usuario_toggle_status'),
    
    # Clientes
    path('clientes/', views.clientes_list, name='clientes_list'),
    path('clientes/nuevo/', views.cliente_create, name='cliente_create'),
    path('clientes/editar/<int:pk>/', views.cliente_update, name='cliente_update'),
    path('clientes/eliminar/<int:pk>/', views.cliente_delete, name='cliente_delete'),
    path('clientes/historial/', views.clientes_historial, name='clientes_historial'),
    path('clientes/restaurar/<int:pk>/', views.cliente_restore, name='cliente_restore'),
    
    # Proveedores
    path('proveedores/', views.proveedores_list, name='proveedores_list'),
    path('proveedores/nuevo/', views.proveedor_create, name='proveedor_create'),
    path('proveedores/editar/<int:pk>/', views.proveedor_update, name='proveedor_update'),
    path('proveedores/eliminar/<int:pk>/', views.proveedor_delete, name='proveedor_delete'),
    path('proveedores/historial/', views.proveedores_historial, name='proveedores_historial'),
    path('proveedores/restaurar/<int:pk>/', views.proveedor_restore, name='proveedor_restore'),
    
    # Inventario / Productos
    path('inventario/', views.inventario_list, name='inventario_list'),
    path('productos/nuevo/', views.producto_create, name='producto_create'),
    path('productos/editar/<int:pk>/', views.producto_update, name='producto_update'),
    path('productos/eliminar/<int:pk>/', views.producto_delete, name='producto_delete'),
    path('inventario/historial/', views.inventario_historial, name='inventario_historial'),
    path('productos/restaurar/<int:pk>/', views.producto_restore, name='producto_restore'),
    
    # Ventas
    path('ventas/', views.ventas_list, name='ventas_list'),
    path('ventas/nuevo/', views.venta_create, name='venta_create'),
    path('ventas/pdf/<int:pk>/', views.venta_pdf, name='venta_pdf'),
    path('ventas/exportar/', views.exportar_ventas_excel, name='exportar_ventas_excel'),
    path('ventas/importar/', views.importar_ventas, name='importar_ventas'),
    
    # Compras
    path('compras/', views.compras_list, name='compras_list'),
    path('compras/nuevo/', views.compra_create, name='compra_create'),
    
    # Servicios
    path('servicios/', views.servicios_list, name='servicios_list'),
    path('servicios/nuevo/', views.servicio_create, name='servicio_create'),
    path('servicios/editar/<int:pk>/', views.servicio_update, name='servicio_update'),
    path('servicios/eliminar/<int:pk>/', views.servicio_delete, name='servicio_delete'),
    
    # Facturación / SUNAT
    path('facturacion/', views.facturacion_list, name='facturacion_list'),
    path('facturacion/enviar/<int:pk>/', views.enviar_sunat, name='enviar_sunat'),
    
    # Reportes y Exportación
    path('reportes/', views.reportes_view, name='reportes'),
    path('configuracion/', views.configuracion_empresa, name='configuracion_empresa'),
    path('reportes/pdf/', views.reporte_general_pdf, name='reporte_general_pdf'),
]
