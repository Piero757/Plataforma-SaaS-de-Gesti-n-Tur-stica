from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    TIPO_DOCUMENTO = [
        ('DNI', 'DNI'),
        ('RUC', 'RUC'),
        ('CE', 'Carnet de Extranjería'),
    ]
    tipo_documento = models.CharField(max_length=5, choices=TIPO_DOCUMENTO, default='DNI')
    numero_documento = models.CharField(max_length=20, unique=True)
    nombre_razon_social = models.CharField(max_length=200)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.numero_documento} - {self.nombre_razon_social}"

class Proveedor(models.Model):
    ruc = models.CharField(max_length=11, unique=True)
    razon_social = models.CharField(max_length=200)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.razon_social

class Producto(models.Model):
    CATEGORIAS = [
        ('TURISMO', 'Servicio Turístico'),
        ('HOSPEDAJE', 'Hospedaje'),
        ('SOUVENIR', 'Souvenir / Producto'),
        ('OTROS', 'Otros'),
    ]
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='SOUVENIR')
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock_minimo = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.nombre

class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE)
    stock_actual = models.IntegerField(default=0)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.producto.nombre} - Stock: {self.stock_actual}"

class Venta(models.Model):
    TIPO_COMPROBANTE = [
        ('BOLETA', 'Boleta de Venta'),
        ('FACTURA', 'Factura Electrónica'),
        ('TICKET', 'Ticket'),
        ('NOTA_CREDITO', 'Nota de Crédito'),
    ]
    FORMA_PAGO = [
        ('CONTADO', 'Contado'),
        ('CREDITO', 'Crédito'),
    ]
    ESTADO_SUNAT = [
        ('PENDIENTE', 'Pendiente de Envío'),
        ('ACEPTADO', 'Aceptado por SUNAT'),
        ('RECHAZADO', 'Rechazado por SUNAT'),
        ('ERROR', 'Error de Comunicación'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    tipo_comprobante = models.CharField(max_length=20, choices=TIPO_COMPROBANTE)
    serie = models.CharField(max_length=10)
    numero = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pago = models.CharField(max_length=10, choices=FORMA_PAGO, default='CONTADO')
    estado_sunat = models.CharField(max_length=20, choices=ESTADO_SUNAT, default='PENDIENTE')
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo_comprobante} {self.serie}-{self.numero}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle {self.venta.id} - {self.producto.nombre}"

class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    fecha = models.DateField()
    tipo_comprobante = models.CharField(max_length=50) # Factura de proveedor
    numero_comprobante = models.CharField(max_length=50)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Compra {self.numero_comprobante} - {self.proveedor.razon_social}"

class RegistroServicio(models.Model):
    nombre_servicio = models.CharField(max_length=200)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    comentarios = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_servicio} - {self.cliente.nombre_razon_social}"

class FacturaElectronica(models.Model):
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE)
    xml_file = models.FileField(upload_to='comprobantes/xml/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='comprobantes/pdf/', blank=True, null=True)
    qr_image = models.ImageField(upload_to='comprobantes/qr/', blank=True, null=True)
    hash_cpe = models.CharField(max_length=100, blank=True, null=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CPE {self.venta.serie}-{self.venta.numero}"
