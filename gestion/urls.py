from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    path('restaurante/', views.restaurante_view, name='restaurante'),
    path('modulo/cambiar/', views.cambiar_modulo, name='cambiar_modulo'),
    
    # Usuarios
    path('register/', views.register_view, name='register'),
    path('usuarios/', views.usuarios_list, name='usuarios_list'),
    path('usuarios/nuevo/', views.usuario_create, name='usuario_create'),
    path('usuarios/editar/<int:pk>/', views.usuario_update, name='usuario_update'),
    path('usuarios/estado/<int:pk>/', views.usuario_toggle_status, name='usuario_toggle_status'),
    path('usuarios/admin/<int:pk>/', views.usuario_toggle_admin, name='usuario_toggle_admin'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/password/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    
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
    
    path('categorias/', views.categorias_list, name='categorias_list'),
    path('categorias/eliminar/<int:pk>/', views.categoria_delete, name='categoria_delete'),
    
    # Ventas
    path('ventas/', views.ventas_list, name='ventas_list'),
    path('ventas/nuevo/', views.venta_create, name='venta_create'),
    path('ventas/pdf/<int:pk>/', views.venta_pdf, name='venta_pdf'),
    path('ventas/exportar/', views.exportar_ventas_excel, name='exportar_ventas_excel'),
    path('ventas/importar/', views.importar_ventas, name='importar_ventas'),
    
    # Compras
    path('compras/', views.compras_list, name='compras_list'),
    path('compras/nuevo/', views.compra_create, name='compra_create'),
    path('compras/detalle/<int:pk>/', views.compra_detalle, name='compra_detalle'),
    path('compras/eliminar/<int:pk>/', views.compra_delete, name='compra_delete'),
    path('compras/historial/', views.compras_historial, name='compras_historial'),
    path('compras/restaurar/<int:pk>/', views.compra_restore, name='compra_restore'),
    
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
    path('reportes/ventas-generales/excel/', views.exportar_ventas_generales_excel, name='exportar_ventas_generales_excel'),
    path('reportes/ventas-generales/pdf/', views.exportar_ventas_generales_pdf, name='exportar_ventas_generales_pdf'),
    path('reportes/compras/excel/', views.exportar_compras_excel, name='exportar_compras_excel'),
    path('reportes/usuarios/excel/', views.exportar_usuarios_excel, name='exportar_usuarios_excel'),
    path('reportes/inventario/excel/', views.exportar_inventario_excel, name='exportar_inventario_excel'),
    
    # Hotel Management
    path('habitaciones/', views.habitaciones_list, name='habitaciones_list'),
    path('habitaciones/nuevo/', views.habitacion_create, name='habitacion_create'),
    path('habitaciones/editar/<int:pk>/', views.habitacion_update, name='habitacion_update'),
    path('habitaciones/eliminar/<int:pk>/', views.habitacion_delete, name='habitacion_delete'),
    path('habitaciones/historial/', views.habitaciones_historial, name='habitaciones_historial'),
    path('habitaciones/restaurar/<int:pk>/', views.habitacion_restore, name='habitacion_restore'),
    path('reservas/', views.reserva_list, name='reserva_list'),
    path('reservas/nuevo/', views.reserva_create, name='reserva_create'),
    path('reservas/pedido/<int:reserva_id>/', views.pedido_habitacion_create, name='pedido_habitacion_create'),
    path('reservas/checkout/<int:reserva_id>/', views.reserva_checkout, name='reserva_checkout'),
    path('reservas/detalle/<int:pk>/', views.reserva_detalle, name='reserva_detalle'),
    path('reservas/finalizar/<int:pk>/', views.reserva_finalizar_temprano, name='reserva_finalizar_temprano'),
    path('reservas/eliminar/<int:pk>/', views.reserva_delete, name='reserva_delete'),
    path('reservas/historial/', views.reservas_historial, name='reservas_historial'),
    path('reservas/restaurar/<int:pk>/', views.reserva_restore, name='reserva_restore'),

    # Restaurante Management
    path('restaurante/mesa/<int:mesa_id>/', views.mesa_detalle, name='mesa_detalle'),
    path('restaurante/mesa/abrir/<int:mesa_id>/', views.mesa_abrir, name='mesa_abrir'),
    path('restaurante/mesa/cerrar/<int:venta_id>/', views.mesa_cerrar, name='mesa_cerrar'),
    path('restaurante/mesa/agregar-item/<int:venta_id>/', views.mesa_agregar_item, name='mesa_agregar_item'),
    path('restaurante/mesas/', views.mesas_list, name='mesas_list'),
    path('restaurante/mesas/nuevo/', views.mesa_create, name='mesa_create'),
    path('restaurante/mesas/editar/<int:pk>/', views.mesa_update, name='mesa_update'),
    path('restaurante/mesas/eliminar/<int:pk>/', views.mesa_delete, name='mesa_delete'),
    path('restaurante/carta/', views.carta_lista, name='carta_lista'),
    path('restaurante/ticket/<int:pk>/', views.ticket_print, name='ticket_print'),
]
