from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, F
from django.utils import timezone
from django.http import HttpResponse
from django import forms
from django.contrib.auth.decorators import login_required
from .models import Venta, Producto, Inventario, RegistroServicio, Cliente, Proveedor, Compra, FacturaElectronica
from .forms import ClienteForm, UsuarioCreateForm
import openpyxl
from django.contrib.auth.models import User

@login_required
def dashboard_view(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Metrics
    total_usuarios = User.objects.count()
    ventas_hoy = Venta.objects.filter(fecha__date=today).aggregate(Sum('total'))['total__sum'] or 0
    productos_inventario = Producto.objects.filter(categoria='SOUVENIR').count()
    servicios_realizados = RegistroServicio.objects.count()
    ingresos_mes = Venta.objects.filter(fecha__date__gte=month_start).aggregate(Sum('total'))['total__sum'] or 0

    # Stock alertas
    alertas_stock = Inventario.objects.filter(stock_actual__lte=F('producto__stock_minimo'))[:5] # Example

    context = {
        'total_usuarios': total_usuarios,
        'ventas_hoy': ventas_hoy,
        'productos_inventario': productos_inventario,
        'servicios_realizados': servicios_realizados,
        'ingresos_mes': ingresos_mes,
        'ventas_recientes': Venta.objects.order_by('-fecha')[:5],
    }
    return render(request, 'gestion/dashboard.html', context)

@login_required
def usuarios_list(request):
    usuarios = User.objects.all()
    return render(request, 'gestion/usuarios_list.html', {'usuarios': usuarios})

@login_required
def clientes_list(request):
    clientes = Cliente.objects.all()
    return render(request, 'gestion/clientes_list.html', {'clientes': clientes})

@login_required
def ventas_list(request):
    ventas = Venta.objects.all().order_by('-fecha')
    return render(request, 'gestion/ventas_list.html', {'ventas': ventas})

@login_required
def inventario_list(request):
    inventario = Inventario.objects.all()
    return render(request, 'gestion/inventario_list.html', {'inventario': inventario})

@login_required
def proveedores_list(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'gestion/proveedores_list.html', {'proveedores': proveedores})

@login_required
def compras_list(request):
    compras = Compra.objects.all().order_by('-fecha')
    return render(request, 'gestion/compras_list.html', {'compras': compras})

@login_required
def facturacion_list(request):
    # Mostramos ventas que tienen factura electrónica generada o pendiente
    facturas = FacturaElectronica.objects.all().order_by('-fecha_emision')
    return render(request, 'gestion/facturacion_list.html', {'facturas': facturas})

@login_required
def servicios_list(request):
    servicios = RegistroServicio.objects.all().order_by('-fecha')
    return render(request, 'gestion/servicios_list.html', {'servicios': servicios})

@login_required
def reportes_view(request):
    # Datos básicos para gráficos (simulados o reales)
    ventas_por_mes = Venta.objects.extra(select={'month': "EXTRACT(month FROM fecha)"}).values('month').annotate(total=Sum('total')).order_by('month')
    servicios_populares = RegistroServicio.objects.values('nombre_servicio').annotate(count=Count('id')).order_by('-count')[:5]
    
    context = {
        'ventas_por_mes': ventas_por_mes,
        'servicios_populares': servicios_populares,
        'clientes_top': Cliente.objects.annotate(num_ventas=Count('venta')).order_by('-num_ventas')[:5],
    }
    return render(request, 'gestion/reportes.html', context)

# --- ACCIONES FUNCIONALES ---

@login_required
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clientes_list')
    else:
        form = ClienteForm()
    return render(request, 'gestion/cliente_form.html', {'form': form})

@login_required
def exportar_ventas_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ventas"

    # Encabezados
    columns = ['ID', 'Fecha', 'Cliente', 'Tipo', 'Serie-Numero', 'Total', 'Forma Pago', 'Estado SUNAT']
    ws.append(columns)

    # Datos
    ventas = Venta.objects.all().order_by('-fecha')
    for v in ventas:
        ws.append([
            v.id,
            v.fecha.strftime('%d/%m/%Y %H:%M'),
            v.cliente.nombre_razon_social,
            v.tipo_comprobante,
            f"{v.serie}-{v.numero}",
            float(v.total),
            v.forma_pago,
            v.estado_sunat
        ])

    wb.save(response)
    return response

@login_required
def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuarios_list')
    else:
        form = UsuarioCreateForm()
    return render(request, 'gestion/usuario_form.html', {'form': form})
