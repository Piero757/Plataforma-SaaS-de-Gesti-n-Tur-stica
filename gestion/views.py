from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, F
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Venta, Producto, Inventario, RegistroServicio, Cliente, Proveedor, Compra, FacturaElectronica, DetalleVenta
from .forms import ClienteForm, UsuarioCreateForm, ProveedorForm, ProductoForm, CompraForm, VentaForm, ServicioForm
import openpyxl
from .utils import render_to_pdf
from django.contrib.auth.models import User

# --- DASHBOARD ---

@login_required
def dashboard_view(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    total_usuarios = User.objects.count()
    ventas_hoy = Venta.objects.filter(fecha__date=today).aggregate(Sum('total'))['total__sum'] or 0
    productos_inventario = Producto.objects.filter(categoria='SOUVENIR').count()
    servicios_realizados = RegistroServicio.objects.count()
    ingresos_mes = Venta.objects.filter(fecha__date__gte=month_start).aggregate(Sum('total'))['total__sum'] or 0

    context = {
        'total_usuarios': total_usuarios,
        'ventas_hoy': ventas_hoy,
        'productos_inventario': productos_inventario,
        'servicios_realizados': servicios_realizados,
        'ingresos_mes': ingresos_mes,
        'ventas_recientes': Venta.objects.order_by('-fecha')[:5],
    }
    return render(request, 'gestion/dashboard.html', context)

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

# --- CLIENTES ---

@login_required
def clientes_list(request):
    clientes = Cliente.objects.all()
    return render(request, 'gestion/clientes_list.html', {'clientes': clientes})

@login_required
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
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
    try:
        cliente.delete()
        messages.success(request, "Cliente eliminado.")
    except Exception:
        messages.error(request, "No se puede eliminar el cliente porque tiene registros asociados.")
    return redirect('clientes_list')

# --- PROVEEDORES ---

@login_required
def proveedores_list(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'gestion/proveedores_list.html', {'proveedores': proveedores})

@login_required
def proveedor_create(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
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
    proveedor.delete()
    messages.success(request, "Proveedor eliminado.")
    return redirect('proveedores_list')

# --- PRODUCTOS / INVENTARIO ---

@login_required
def inventario_list(request):
    inventario = Inventario.objects.all()
    return render(request, 'gestion/inventario_list.html', {'inventario': inventario})

@login_required
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
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

# --- VENTAS ---

@login_required
def ventas_list(request):
    ventas = Venta.objects.all().order_by('-fecha')
    return render(request, 'gestion/ventas_list.html', {'ventas': ventas})

@login_required
def venta_create(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            venta = form.save(commit=False)
            venta.usuario = request.user
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

# --- COMPRAS ---

@login_required
def compras_list(request):
    compras = Compra.objects.all().order_by('-fecha')
    return render(request, 'gestion/compras_list.html', {'compras': compras})

@login_required
def compra_create(request):
    if request.method == 'POST':
        form = CompraForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Compra registrada.")
            return redirect('compras_list')
    else:
        form = CompraForm()
    return render(request, 'gestion/base_form.html', {'form': form, 'titulo': 'Registrar Compra'})

# --- SERVICIOS ---

@login_required
def servicios_list(request):
    servicios = RegistroServicio.objects.all().order_by('-fecha')
    return render(request, 'gestion/servicios_list.html', {'servicios': servicios})

@login_required
def servicio_create(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            form.save()
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
    ventas_por_mes = Venta.objects.extra(select={'month': "EXTRACT(month FROM fecha)"}).values('month').annotate(total=Sum('total')).order_by('month')
    servicios_populares = RegistroServicio.objects.values('nombre_servicio').annotate(count=Count('id')).order_by('-count')[:5]
    
    context = {
        'ventas_por_mes': ventas_por_mes,
        'servicios_populares': servicios_populares,
        'clientes_top': Cliente.objects.annotate(num_ventas=Count('venta')).order_by('-num_ventas')[:5],
    }
    return render(request, 'gestion/reportes.html', context)

@login_required
def exportar_ventas_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ventas"

    columns = ['ID', 'Fecha', 'Cliente', 'Tipo', 'Serie-Numero', 'Total', 'Forma Pago', 'Estado SUNAT']
    ws.append(columns)

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
