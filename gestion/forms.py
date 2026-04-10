from django import forms
from django.contrib.auth.models import User
from .models import Cliente, Proveedor, Producto, Compra, Venta, RegistroServicio, Inventario

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo_documento', 'numero_documento', 'nombre_razon_social', 'direccion', 'email', 'telefono']
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12345678 o 20123456789'}),
            'nombre_razon_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez o Empresa S.A.C.'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Av. Principal 123'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 987654321'}),
        }

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['ruc', 'razon_social', 'direccion', 'email', 'telefono']
        widgets = {
            'ruc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 20123456789'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Distribuidora Turística S.A.'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Jr. Independencia 456'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'proveedor@empresa.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 01 4445566'}),
        }

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'descripcion', 'categoria', 'precio_compra', 'precio_venta', 'stock_minimo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: PROD-001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Tour Montaña de Colores'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción breve del producto o servicio...'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 5'}),
        }

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor', 'fecha', 'tipo_comprobante', 'numero_comprobante', 'total']
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_comprobante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Factura'}),
            'numero_comprobante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: F001-000123'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
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
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}))
    is_staff = forms.BooleanField(required=False, initial=True, label="¿Es Administrador?", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: jperez'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'jperez@turismo.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pérez'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
