from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Cliente, Proveedor, Producto, Compra, Venta, RegistroServicio, 
    Inventario, ConfiguracionEmpresa, Habitacion, Mesa, Reserva, PedidoHabitacion,
    DetalleCompra, CuotaCompra, PerfilUsuario
)

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo_documento', 'numero_documento', 'nombre_razon_social', 'persona_contacto', 'direccion', 'email', 'telefono']
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12345678 o 20123456789'}),
            'nombre_razon_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez o Empresa S.A.C.'}),
            'persona_contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Contacto de compras'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Av. Principal 123'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 987654321'}),
        }

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['ruc', 'razon_social', 'persona_contacto', 'direccion', 'email', 'telefono']
        widgets = {
            'ruc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 20123456789'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Distribuidora Turística S.A.'}),
            'persona_contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Jr. Independencia 456'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'proveedor@empresa.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 01 4445566'}),
        }

SUBCATEGORIAS_REST = [
    ('', '--- Seleccione ---'),
    ('ENTRADA', 'Entrada'),
    ('PLATO_FONDO', 'Plato de Fondo'),
    ('POSTRE', 'Postre'),
    ('BEBIDA', 'Bebida'),
    ('LICOR', 'Licor / Trago'),
    ('OTRO', 'Otro'),
]

class ProductoForm(forms.ModelForm):
    stock = forms.IntegerField(
        label="Stock Actual",
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 10'})
    )

    stock_minimo = forms.IntegerField(required=False, initial=5, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 5'}))
    stock_ideal = forms.IntegerField(required=False, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 20'}))
    stock_alerta = forms.IntegerField(required=False, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2'}))

    class Meta:
        model = Producto
        fields = [
            'codigo', 'nombre', 'descripcion', 'categoria', 'subcategoria', 
            'impuesto', 'precio_compra', 'precio_venta', 'precio_corporativo', 
            'comision', 'imagen'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: PROD-001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Tour Montaña de Colores'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción breve del producto o servicio...'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'subcategoria': forms.Select(choices=SUBCATEGORIAS_REST, attrs={'class': 'form-select'}),
            'impuesto': forms.Select(attrs={'class': 'form-select'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'precio_corporativo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'comision': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar el stock actual si el producto ya existe
        if self.instance and self.instance.pk:
            try:
                self.fields['stock'].initial = self.instance.inventario.stock_actual
            except:
                self.fields['stock'].initial = 0
                
        # Cargar subcategorias dinámicas
        from .models import CategoriaPersonalizada
        try:
            categorias_extra = list(CategoriaPersonalizada.objects.values_list('nombre', 'nombre'))
        except:
            categorias_extra = []
            
        base_choices = [
            ('', '--- Seleccione ---'),
            ('ENTRADA', 'Entrada'),
            ('PLATO_FONDO', 'Plato de Fondo'),
            ('POSTRE', 'Postre'),
            ('BEBIDA', 'Bebida'),
            ('LICOR', 'Licor / Trago'),
            ('OTRO', 'Otro'),
        ]
        
        # Eliminar duplicados
        base_keys = [k for k, v in base_choices]
        for key, val in categorias_extra:
            if key not in base_keys:
                base_choices.append((key, val))
                
        self.fields['subcategoria'].widget = forms.Select(choices=base_choices, attrs={'class': 'form-select'})

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor', 'fecha', 'tipo_comprobante', 'numero_comprobante', 'total', 'forma_pago']
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_comprobante': forms.Select(attrs={'class': 'form-select'}),
            'numero_comprobante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: F001-000123'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'readonly': 'readonly'}),
            'forma_pago': forms.Select(attrs={'class': 'form-select'}),
        }

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente', 'tipo_comprobante', 'serie', 'numero', 'total', 'forma_pago', 'observaciones']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'tipo_comprobante': forms.Select(attrs={'class': 'form-select'}),
            'serie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: B001 o F001'}),
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'forma_pago': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notas adicionales...'}),
        }

class ServicioForm(forms.ModelForm):
    class Meta:
        model = RegistroServicio
        fields = ['nombre_servicio', 'cliente', 'fecha', 'precio', 'comentarios']
        widgets = {
            'nombre_servicio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Servicio de Guiado Privado'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'comentarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles del servicio brindado...'}),
        }

class UsuarioCreateForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Dejar en blanco para no cambiar'}),
        label="Contraseña"
    )
    rol = forms.ChoiceField(
        choices=PerfilUsuario.ROL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Rol del Usuario",
        initial='ADMIN'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: jperez'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'jperez@turismo.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pérez'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando un usuario existente, cargamos su rol actual
        if self.instance and self.instance.pk:
            try:
                self.fields['rol'].initial = self.instance.perfil.rol
            except PerfilUsuario.DoesNotExist:
                self.fields['rol'].initial = 'ADMIN'

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        # Actualizar flags de staff/superuser según el rol
        rol = self.cleaned_data.get('rol', 'ADMIN')
        if rol == 'ADMIN':
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False
        if commit:
            user.save()
            # Guardar o actualizar el perfil con el rol
            perfil, _ = PerfilUsuario.objects.get_or_create(usuario=user)
            perfil.rol = rol
            perfil.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@ejemplo.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
        }

class ConfiguracionEmpresaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionEmpresa
        fields = '__all__'
        widgets = {
            'nombre_sistema': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'ruc': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '11'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_comercial': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
            'distrito': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_impresion': forms.Select(attrs={'class': 'form-select'}),
            'formato_hotel': forms.Select(attrs={'class': 'form-select'}),
            'formato_restaurante': forms.Select(attrs={'class': 'form-select'}),
            'mensaje_pie_pagina': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: Gracias por su visita...'}),
            'imprimir_logo_ticket': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'nombre_impresora_hotel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: EPSON L3110'}),
            'nombre_impresora_restaurante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: POS-80-Series'}),
            'forma_logo': forms.Select(attrs={'class': 'form-select'}),
            'ruta_referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: C:/Program Files/TurismoERP'}),
            'usuario_sol': forms.TextInput(attrs={'class': 'form-control'}),
            'clave_sol': forms.PasswordInput(attrs={'class': 'form-control'}, render_value=True),
            'certificado_digital': forms.FileInput(attrs={'class': 'form-control'}),
            'password_certificado': forms.PasswordInput(attrs={'class': 'form-control'}, render_value=True),
            'ambiente': forms.Select(attrs={'class': 'form-select'}),
        }

class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['numero', 'capacidad', 'estado']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1, 2, VIP-1'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitacion
        fields = ['numero', 'tipo', 'precio_noche', 'precio_noche_corporativo', 'estado', 'imagen', 'descripcion']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'precio_noche': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_noche_corporativo': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ReservaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(activo=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Cliente Registrado"
    )

    class Meta:
        model = Reserva
        fields = [
            'cliente', 'habitacion', 'fecha_ingreso', 'fecha_salida',
            'total_hospedaje', 'adelanto', 'n_pax', 'hora_desayuno',
            'placa_vehiculo', 'condicion_pago', 'observaciones'
        ]
        widgets = {
            'habitacion': forms.Select(attrs={'class': 'form-select'}),
            'fecha_ingreso': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'fecha_salida': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'total_hospedaje': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'adelanto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'n_pax': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'hora_desayuno': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 8:00 AM'}),
            'placa_vehiculo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ABC-123 (opcional)'}),
            'condicion_pago': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Efectivo, Yape, Tarjeta'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notas adicionales...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.db.models import Q
        
        habitacion_qs = Habitacion.objects.filter(activo=True)
        if self.instance and self.instance.pk:
            habitacion_qs = habitacion_qs.filter(
                Q(estado='DISPONIBLE') | 
                Q(estado='LIMPIEZA') |
                Q(estado='RESERVADA') |
                Q(id=self.instance.habitacion_id)
            )
        else:
            habitacion_qs = habitacion_qs.filter(
                Q(estado='DISPONIBLE') | 
                Q(estado='LIMPIEZA')
            )
        
        self.fields['habitacion'].queryset = habitacion_qs
        def label_hab(obj):
            sufijo = ''
            if obj.estado == 'LIMPIEZA':  sufijo = ' ⚠ En Limpieza'
            if obj.estado == 'RESERVADA': sufijo = ' 📅 Reservada'
            return f"Hab. {obj.numero} ({obj.get_tipo_display()}){sufijo}"
        self.fields['habitacion'].label_from_instance = label_hab

class PedidoHabitacionForm(forms.ModelForm):
    class Meta:
        model = PedidoHabitacion
        fields = ['producto', 'cantidad', 'precio_unitario', 'observaciones']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: De 4pm a 6pm, o detalles especiales...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(activo=True)
        self.fields['producto'].label_from_instance = lambda obj: f"{obj.nombre} - S/ {obj.precio_venta}"

class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select select2'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class CuotaCompraForm(forms.ModelForm):
    class Meta:
        model = CuotaCompra
        fields = ['numero_cuota', 'monto', 'fecha_vencimiento']
        widgets = {
            'numero_cuota': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@ejemplo.com'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
