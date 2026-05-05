from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, F
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Venta, Producto, Inventario, RegistroServicio, Cliente, Proveedor, Compra, FacturaElectronica, DetalleVenta, ConfiguracionEmpresa
from .forms import ClienteForm, UsuarioCreateForm, ProveedorForm, ProductoForm, CompraForm, VentaForm, ServicioForm, ConfiguracionEmpresaForm
import openpyxl
import csv
from datetime import datetime
from .utils import render_to_pdf
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth
import json

# --- DASHBOARD ---

@login_required
def dashboard_view(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    modulo = request.session.get('modulo', 'HOTEL')
    
    total_usuarios = User.objects.count()
    ventas_hoy = Venta.objects.filter(fecha__date=today, modulo=modulo).aggregate(Sum('total'))['total__sum'] or 0
    productos_inventario = Producto.objects.filter(modulo=modulo).count()
    servicios_realizados = RegistroServicio.objects.filter(modulo=modulo).count()
    ingresos_mes = Venta.objects.filter(fecha__date__gte=month_start, modulo=modulo).aggregate(Sum('total'))['total__sum'] or 0

    context = {
        'modulo_actual': modulo,
        'total_usuarios': total_usuarios,
        'ventas_hoy': ventas_hoy,
        'productos_inventario': productos_inventario,
        'servicios_realizados': servicios_realizados,
        'ingresos_mes': ingresos_mes,
        'ventas_recientes': Venta.objects.filter(modulo=modulo).order_by('-fecha')[:5],
    }
    return render(request, 'gestion/dashboard.html', context)

@login_required
def restaurante_view(request):
    today = timezone.now().date()
    # Productos de restaurante
    productos = Producto.objects.filter(categoria='RESTAURANTE', activo=True)
    
    # Ventas de restaurante (aquellas que incluyen al menos un producto de restaurante)
    ventas_restaurante = Venta.objects.filter(
        detalles__producto__categoria='RESTAURANTE'
    ).distinct().order_by('-fecha')
    
    # Métricas hoy
    ventas_hoy = Venta.objects.filter(
        fecha__date=today,
        detalles__producto__categoria='RESTAURANTE'
    ).distinct().aggregate(Sum('total'))['total__sum'] or 0
    
    context = {
        'productos': productos,
        'ventas_recientes': ventas_restaurante[:5],
        'ventas_hoy': ventas_hoy,
        'cantidad_productos': productos.count(),
        'titulo': 'Panel de Restaurante'
    }
    return render(request, 'gestion/restaurante_dashboard.html', context)

@login_required
def cambiar_modulo(request):
    modulo = request.GET.get('modulo', 'HOTEL')
    if modulo in ['HOTEL', 'RESTAURANTE']:
        request.session['modulo'] = modulo
        messages.success(request, f"Cambiado al módulo: {modulo.capitalize()}")
    return redirect('dashboard')

# --- USUARIOS ---

@login_required
def usuarios_list(request):
    usuarios = User.objects.all()
    return render(request, 'gestion/usuarios_list.html', {'usuarios': usuarios})

@login_required
def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect('usuarios_list')
    else:
        form = UsuarioCreateForm()
    return render(request, 'gestion/usuario_form.html', {'form': form, 'titulo': 'Crear Usuario'})

@login_required
def usuario_update(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST, instance=usuario)
        # Note: Password handling in update needs care, for simplicity we reuse the form or could filter
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('usuarios_list')
    else:
        form = UsuarioCreateForm(instance=usuario)
    return render(request, 'gestion/usuario_form.html', {'form': form, 'titulo': 'Editar Usuario'})

@login_required
def usuario_toggle_status(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, "No puedes desactivarte a ti mismo.")
    else:
        usuario.is_active = not usuario.is_active
        usuario.save()
        status = "activado" if usuario.is_active else "desactivado"
        messages.info(request, f"Usuario {status} correctamente.")
    return redirect('usuarios_list')

from django.db.models import Q

# --- CLIENTES ---

@login_required
def clientes_list(request):
    modulo = request.session.get('modulo', 'HOTEL')
    query = request.GET.get('q')
    tipo = request.GET.get('tipo')
    
    clientes = Cliente.objects.filter(activo=True, modulo=modulo)
    
    if query:
        clientes = clientes.filter(
            Q(nombre_razon_social__icontains=query) | 
            Q(numero_documento__icontains=query)
        )
    
    if tipo and tipo != 'Todos':
        clientes = clientes.filter(tipo_documento=tipo)
        
    context = {
        'clientes': clientes,
        'query': query,
        'tipo_seleccionado': tipo,
        'tipos_documento': Cliente.TIPO_DOCUMENTO
    }
    return render(request, 'gestion/clientes_list.html', context)

@login_required
def clientes_historial(request):
    query = request.GET.get('q')
    tipo = request.GET.get('tipo')
    
    clientes = Cliente.objects.filter(activo=False)
    
    if query:
        clientes = clientes.filter(
            Q(nombre_razon_social__icontains=query) | 
            Q(numero_documento__icontains=query)
        )
    
    if tipo and tipo != 'Todos':
        clientes = clientes.filter(tipo_documento=tipo)

    return render(request, 'gestion/clientes_list.html', {
        'clientes': clientes, 
        'es_historial': True,
        'titulo': 'Historial de Clientes (Eliminados)',
        'query': query,
        'tipo_seleccionado': tipo,
        'tipos_documento': Cliente.TIPO_DOCUMENTO
    })

@login_required
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.modulo = request.session.get('modulo', 'HOTEL')
            cliente.save()
            messages.success(request, "Cliente registrado correctamente.")
            return redirect('clientes_list')
    else:
        form = ClienteForm()
    return render(request, 'gestion/cliente_form.html', {'form': form, 'titulo': 'Nuevo Cliente'})

@login_required
def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente actualizado.")
            return redirect('clientes_list')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'gestion/cliente_form.html', {'form': form, 'titulo': 'Editar Cliente'})

@login_required
def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.activo = False
    cliente.save()
    messages.success(request, "Cliente movido al historial.")
    return redirect('clientes_list')

@login_required
def cliente_restore(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.activo = True
    cliente.save()
    messages.success(request, "Cliente restaurado correctamente.")
    return redirect('clientes_list')

# --- PROVEEDORES ---

@login_required
def proveedores_list(request):
    modulo = request.session.get('modulo', 'HOTEL')
    proveedores = Proveedor.objects.filter(activo=True, modulo=modulo)
    return render(request, 'gestion/proveedores_list.html', {'proveedores': proveedores})

@login_required
def proveedores_historial(request):
    proveedores = Proveedor.objects.filter(activo=False)
    return render(request, 'gestion/proveedores_list.html', {
        'proveedores': proveedores,
        'es_historial': True,
        'titulo': 'Historial de Proveedores'
    })

@login_required
def proveedor_create(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            prov = form.save(commit=False)
            prov.modulo = request.session.get('modulo', 'HOTEL')
            prov.save()
            messages.success(request, "Proveedor registrado.")
            return redirect('proveedores_list')
    else:
        form = ProveedorForm()
    return render(request, 'gestion/base_form.html', {'form': form, 'titulo': 'Nuevo Proveedor'})

@login_required
def proveedor_update(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor actualizado.")
            return redirect('proveedores_list')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'gestion/base_form.html', {'form': form, 'titulo': 'Editar Proveedor'})

@login_required
def proveedor_delete(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    proveedor.activo = False
    proveedor.save()
    messages.success(request, "Proveedor movido al historial.")
    return redirect('proveedores_list')

@login_required
def proveedor_restore(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    proveedor.activo = True
    proveedor.save()
    messages.success(request, "Proveedor restaurado.")
    return redirect('proveedores_list')

# --- PRODUCTOS / INVENTARIO ---

@login_required
def inventario_list(request):
    modulo = request.session.get('modulo', 'HOTEL')
    inventario = Inventario.objects.filter(producto__activo=True, producto__modulo=modulo)
    return render(request, 'gestion/inventario_list.html', {'inventario': inventario})

@login_required
def inventario_historial(request):
    inventario = Inventario.objects.filter(producto__activo=False)
    return render(request, 'gestion/inventario_list.html', {
        'inventario': inventario,
        'es_historial': True,
        'titulo': 'Historial de Productos'
    })

@login_required
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.modulo = request.session.get('modulo', 'HOTEL')
            producto.save()
            # Crear entrada en inventario si no existe
            Inventario.objects.get_or_create(producto=producto, defaults={'stock_actual': 0})
            messages.success(request, "Producto creado.")
            return redirect('inventario_list')
    else:
        form = ProductoForm()
    return render(request, 'gestion/base_form.html', {'form': form, 'titulo': 'Nuevo Producto'})

@login_required
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado.")
            return redirect('inventario_list')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'gestion/base_form.html', {'form': form, 'titulo': 'Editar Producto'})
@login_required
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.activo = False
    producto.save()
    messages.success(request, "Producto movido al historial.")
    return redirect('inventario_list')

@login_required
def producto_restore(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.activo = True
    producto.save()
    messages.success(request, "Producto restaurado.")
    return redirect('inventario_list')

# --- VENTAS ---

@login_required
def ventas_list(request):
    modulo = request.session.get('modulo', 'HOTEL')
    ventas = Venta.objects.filter(modulo=modulo).order_by('-fecha')
    return render(request, 'gestion/ventas_list.html', {'ventas': ventas})

@login_required
def venta_create(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            venta = form.save(commit=False)
            venta.usuario = request.user
            venta.modulo = request.session.get('modulo', 'HOTEL')
            venta.save()
            messages.success(request, "Venta registrada correctamente.")
            return redirect('ventas_list')
    else:
        form = VentaForm()
    return render(request, 'gestion/base_form.html', {'form': form, 'titulo': 'Nueva Venta'})

@login_required
def venta_pdf(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    detalles = venta.detalles.all()
    
    # Cálculos para el comprobante
    total = float(venta.total)
    op_gravada = total / 1.18
    igv = total - op_gravada
    
    data = {
        'venta': venta,
        'detalles': detalles,
        'op_gravada': op_gravada,
        'igv': igv,
        'total_letras': "MONTO REFERENCIAL"
    }
    
    pdf = render_to_pdf('gestion/comprobante_pdf.html', data)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"{venta.tipo_comprobante}_{venta.serie}-{venta.numero}.pdf"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    
    messages.error(request, "No se pudo generar el PDF del comprobante.")
    return redirect('ventas_list')

@login_required
def importar_ventas(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        if not (archivo.name.endswith('.xlsx') or archivo.name.endswith('.csv')):
            messages.error(request, "Solo se admiten archivos .xlsx o .csv")
            return redirect('ventas_list')

        try:
            ventas_creadas = 0
            if archivo.name.endswith('.xlsx'):
                wb = openpyxl.load_workbook(archivo, data_only=True)
                ws = wb.active
                headers = [str(cell.value).lower().strip() if cell.value else "" for cell in ws[1]]
                rows = ws.iter_rows(min_row=2, values_only=True)
            else:
                decoded_file = archivo.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                headers = [h.lower().strip() for h in next(reader)]
                rows = reader

            # Mapeo de columnas comunes
            idx_fecha = -1
            idx_cliente = -1
            idx_doc = -1
            idx_tipo = -1
            idx_serie = -1
            idx_numero = -1
            idx_total = -1

            for i, h in enumerate(headers):
                if 'fecha' in h or 'emision' in h: idx_fecha = i
                elif 'cliente' in h or 'nombre' in h or 'razon' in h: idx_cliente = i
                elif 'ruc' in h or 'dni' in h or 'documento' in h: idx_doc = i
                elif 'tipo' in h or 'comprobante' in h: idx_tipo = i
                elif 'serie' in h: idx_serie = i
                elif 'numero' in h or 'correlativo' in h: idx_numero = i
                elif 'total' in h or 'monto' in h or 'importe' in h: idx_total = i

            if idx_total == -1 or (idx_cliente == -1 and idx_doc == -1):
                messages.error(request, "No se pudieron identificar las columnas necesarias en el archivo.")
                return redirect('ventas_list')

            for row in rows:
                if not any(row): continue
                
                try:
                    fecha_val = row[idx_fecha] if idx_fecha != -1 else None
                    if isinstance(fecha_val, datetime):
                        fecha = fecha_val
                    elif isinstance(fecha_val, str):
                        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
                            try:
                                fecha = datetime.strptime(fecha_val, fmt)
                                break
                            except: continue
                        else: fecha = timezone.now()
                    else: fecha = timezone.now()

                    monto_total = float(row[idx_total])
                    nombre_cliente = str(row[idx_cliente]) if idx_cliente != -1 else "Cliente Importado"
                    doc_cliente = str(row[idx_doc]) if idx_doc != -1 else "00000000"
                    
                    tipo_raw = str(row[idx_tipo]).upper() if idx_tipo != -1 else "BOLETA"
                    if 'FACTURA' in tipo_raw: tipo_comp = 'FACTURA'
                    elif 'NOTA' in tipo_raw and 'CREDITO' in tipo_raw: tipo_comp = 'NOTA_CREDITO'
                    else: tipo_comp = 'BOLETA'
                    
                    serie = str(row[idx_serie]) if idx_serie != -1 else "E001"
                    numero_val = row[idx_numero] if idx_numero != -1 else 1
                    try: numero = int(numero_val)
                    except: numero = 1

                    cliente, _ = Cliente.objects.get_or_create(
                        numero_documento=doc_cliente,
                        defaults={
                            'nombre_razon_social': nombre_cliente,
                            'tipo_documento': 'RUC' if len(doc_cliente) == 11 else 'DNI'
                        }
                    )

                    Venta.objects.create(
                        cliente=cliente,
                        usuario=request.user,
                        fecha=fecha,
                        tipo_comprobante=tipo_comp,
                        serie=serie,
                        numero=numero,
                        total=monto_total,
                        forma_pago='CONTADO',
                        estado_sunat='ACEPTADO'
                    )
                    ventas_creadas += 1
                except Exception as e:
                    print(f"Error en fila: {e}")
                    continue

            messages.success(request, f"Importación finalizada: {ventas_creadas} ventas registradas.")
        except Exception as e:
            messages.error(request, f"Error crítico al importar: {str(e)}")
            
    return redirect('ventas_list')

# --- COMPRAS ---

@login_required
def compras_list(request):
    modulo = request.session.get('modulo', 'HOTEL')
    compras = Compra.objects.filter(modulo=modulo).order_by('-fecha')
    return render(request, 'gestion/compras_list.html', {'compras': compras})

@login_required
def compra_create(request):
    if request.method == 'POST':
        form = CompraForm(request.POST)
        if form.is_valid():
            compra = form.save(commit=False)
            compra.modulo = request.session.get('modulo', 'HOTEL')
            compra.save()
            messages.success(request, "Compra registrada.")
            return redirect('compras_list')
    else:
        form = CompraForm()
    return render(request, 'gestion/base_form.html', {'form': form, 'titulo': 'Registrar Compra'})

# --- SERVICIOS ---

@login_required
def servicios_list(request):
    modulo = request.session.get('modulo', 'HOTEL')
    servicios = RegistroServicio.objects.filter(modulo=modulo).order_by('-fecha')
    return render(request, 'gestion/servicios_list.html', {'servicios': servicios})

@login_required
def servicio_create(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            servicio = form.save(commit=False)
            servicio.modulo = request.session.get('modulo', 'HOTEL')
            servicio.save()
            messages.success(request, "Servicio registrado.")
            return redirect('servicios_list')
    else:
        form = ServicioForm()
    return render(request, 'gestion/base_form.html', {'form': form, 'titulo': 'Nuevo Registro de Servicio'})

@login_required
def servicio_update(request, pk):
    servicio = get_object_or_404(RegistroServicio, pk=pk)
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio actualizado.")
            return redirect('servicios_list')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'gestion/base_form.html', {'form': form, 'titulo': 'Editar Servicio'})

@login_required
def servicio_delete(request, pk):
    servicio = get_object_or_404(RegistroServicio, pk=pk)
    servicio.delete()
    messages.success(request, "Servicio eliminado.")
    return redirect('servicios_list')

# --- FACTURACION / SUNAT ---

@login_required
def facturacion_list(request):
    facturas = FacturaElectronica.objects.all().order_by('-fecha_emision')
    return render(request, 'gestion/facturacion_list.html', {'facturas': facturas})

@login_required
def enviar_sunat(request, pk):
    # Simulación de envío a SUNAT
    messages.success(request, f"Comprobante #{pk} enviado correctamente a SUNAT.")
    return redirect('facturacion_list')

# --- REPORTES / EXCEL ---

@login_required
def reportes_view(request):
    # --- FILTROS ---
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    usuario_id = request.GET.get('usuario')
    periodo = request.GET.get('periodo', 'mes') # dia, semana, mes
    
    ventas_qs = Venta.objects.all()
    servicios_qs = RegistroServicio.objects.all()
    
    if fecha_inicio:
        ventas_qs = ventas_qs.filter(fecha__date__gte=fecha_inicio)
        servicios_qs = servicios_qs.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        ventas_qs = ventas_qs.filter(fecha__date__lte=fecha_fin)
        servicios_qs = servicios_qs.filter(fecha__date__lte=fecha_fin)
    if usuario_id and usuario_id != 'Todos':
        ventas_qs = ventas_qs.filter(usuario_id=usuario_id)
    
    # --- AGRUPACIÓN DE VENTAS ---
    from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
    
    if periodo == 'dia':
        trunc_func = TruncDay('fecha')
        date_format = '%d/%m'
    elif periodo == 'semana':
        trunc_func = TruncWeek('fecha')
        date_format = 'Sem %W'
    else: # mes
        trunc_func = TruncMonth('fecha')
        date_format = '%b'

    ventas_agrupadas = ventas_qs.annotate(
        time_unit=trunc_func
    ).values('time_unit').annotate(total=Sum('total')).order_by('time_unit')
    
    sales_labels = []
    sales_data = []
    
    for v in ventas_agrupadas:
        if v['time_unit']:
            label = v['time_unit'].strftime(date_format)
            sales_labels.append(label)
            sales_data.append(float(v['total']))
        
    # --- SERVICIOS POPULARES ---
    servicios_query = servicios_qs.values('nombre_servicio').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    services_labels = [s['nombre_servicio'] for s in servicios_query]
    services_data = [s['count'] for s in servicios_query]
    
    # --- TOP CLIENTES ---
    clientes_top = Cliente.objects.filter(venta__in=ventas_qs).distinct().annotate(
        num_ventas=Count('venta'),
        total_invertido=Sum('venta__total')
    ).order_by('-total_invertido')[:10]
    
    context = {
        'sales_labels': json.dumps(sales_labels),
        'sales_data': json.dumps(sales_data),
        'services_labels': json.dumps(services_labels),
        'services_data': json.dumps(services_data),
        'clientes_top': clientes_top,
        'usuarios': User.objects.all(),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'usuario_seleccionado': usuario_id,
        'periodo_seleccionado': periodo,
    }
    return render(request, 'gestion/reportes.html', context)

@login_required
def exportar_ventas_excel(request):
    # ... (keeping existing code)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.xlsx"'
    # ... (omitting for brevity in instruction but I will include full logic in the tool call)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ventas"
    columns = ['ID', 'Fecha', 'Cliente', 'Tipo', 'Serie-Numero', 'Total', 'Forma Pago', 'Estado SUNAT']
    ws.append(columns)
    ventas = Venta.objects.all().order_by('-fecha')
    for v in ventas:
        ws.append([v.id, v.fecha.strftime('%d/%m/%Y %H:%M'), v.cliente.nombre_razon_social,
                   v.tipo_comprobante, f"{v.serie}-{v.numero}", float(v.total), v.forma_pago, v.estado_sunat])
    wb.save(response)
    return response

@login_required
def reporte_general_pdf(request):
    today = timezone.now()
    month_start = today.replace(day=1, hour=0, minute=0, second=0)
    
    # Estadísticas para el reporte
    ingresos_mes = Venta.objects.filter(fecha__gte=month_start).aggregate(Sum('total'))['total__sum'] or 0
    servicios_totales = RegistroServicio.objects.count()
    nuevos_clientes = Cliente.objects.filter(id__gt=0).count() # Placeholder logic
    stock_critico = Inventario.objects.filter(stock_actual__lte=F('producto__stock_minimo')).count()
    
    # Top Clientes (con suma de ventas)
    clientes_top = Cliente.objects.annotate(
        num_ventas=Count('venta'),
        total_invertido=Sum('venta__total')
    ).order_by('-total_invertido')[:5]
    
    data = {
        'fecha': today,
        'ingresos_mes': ingresos_mes,
        'servicios_totales': servicios_totales,
        'nuevos_clientes': nuevos_clientes,
        'stock_critico': stock_critico,
        'clientes_top': clientes_top,
        'ventas_recientes': Venta.objects.all().order_by('-fecha')[:10]
    }
    
    pdf = render_to_pdf('gestion/reporte_pro_pdf.html', data)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="Reporte_Gestion_TurismoERP.pdf"'
        return response
    return HttpResponse("Error generando reporte", status=400)

@login_required
def configuracion_empresa(request):
    config, created = ConfiguracionEmpresa.objects.get_or_create(id=1, defaults={
        'ruc': '20123456789',
        'razon_social': 'Mi Empresa Turística S.A.C.',
        'direccion': 'Calle Principal 123, Arequipa',
    })
    
    if request.method == 'POST':
        form = ConfiguracionEmpresaForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración guardada correctamente.")
            return redirect('configuracion_empresa')
    else:
        form = ConfiguracionEmpresaForm(instance=config)
        
    return render(request, 'gestion/configuracion.html', {'form': form, 'config': config})
