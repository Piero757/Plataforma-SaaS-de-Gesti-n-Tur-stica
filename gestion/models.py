from django.db import models
from django.contrib.auth.models import User

MODULO_CHOICES = [
    ('HOTEL', 'Hotel'),
    ('RESTAURANTE', 'Restaurante'),
]

class Cliente(models.Model):
    TIPO_DOCUMENTO = [
        ('DNI', 'DNI'),
        ('RUC', 'RUC'),
        ('CE', 'Carnet de Extranjería'),
    ]
    tipo_documento = models.CharField(max_length=5, choices=TIPO_DOCUMENTO, default='DNI')
    numero_documento = models.CharField(max_length=20, unique=True)
    nombre_razon_social = models.CharField(max_length=200)
    persona_contacto = models.CharField(max_length=200, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    activo = models.BooleanField(default=True)
    modulo = models.CharField(max_length=20, choices=MODULO_CHOICES, default='HOTEL')

    def __str__(self):
        return f"{self.numero_documento} - {self.nombre_razon_social}"

class Proveedor(models.Model):
    ruc = models.CharField(max_length=11, unique=True)
    razon_social = models.CharField(max_length=200)
    persona_contacto = models.CharField(max_length=200, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    activo = models.BooleanField(default=True)
    modulo = models.CharField(max_length=20, choices=MODULO_CHOICES, default='HOTEL')

    def __str__(self):
        return self.razon_social

class CategoriaPersonalizada(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    modulo = models.CharField(max_length=20, default='RESTAURANTE')
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    CATEGORIAS = [
        ('TURISMO', 'Servicio Turístico'),
        ('HOSPEDAJE', 'Hospedaje'),
        ('SOUVENIR', 'Souvenir / Producto'),
        ('RESTAURANTE', 'Restaurante'),
        ('OTROS', 'Otros'),
    ]
    IMPUESTOS = [
        ('IGV', 'IGV (18%)'),
        ('EXONERADO', 'Exonerado'),
        ('INAFECTO', 'Inafecto'),
    ]
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='SOUVENIR')
    
    SUBCATEGORIAS_RESTAURANTE = [
        ('ENTRADA', 'Entrada'),
        ('PLATO_FONDO', 'Plato de Fondo'),
        ('POSTRE', 'Postre'),
        ('BEBIDA', 'Bebida'),
        ('LICOR', 'Licor / Trago'),
        ('OTRO', 'Otro'),
    ]
    subcategoria = models.CharField(max_length=100, default='OTRO', blank=True, null=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    impuesto = models.CharField(max_length=20, choices=IMPUESTOS, default='IGV')
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    precio_corporativo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Precio Corporativo")
    stock_minimo = models.PositiveIntegerField(default=5)
    stock_ideal = models.PositiveIntegerField(default=0)
    stock_alerta = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    modulo = models.CharField(max_length=20, choices=MODULO_CHOICES, default='HOTEL')

    def __str__(self):
        return self.nombre

class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE)
    stock_actual = models.IntegerField(default=0)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    @property
    def valoracion(self):
        return float(self.stock_actual) * float(self.producto.precio_venta)

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
    modulo = models.CharField(max_length=20, choices=MODULO_CHOICES, default='HOTEL')
    mesa = models.ForeignKey('Mesa', on_delete=models.SET_NULL, null=True, blank=True)
    es_comanda = models.BooleanField(default=False, help_text="Si es True, es un pedido abierto en mesa")

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
    TIPO_COMPROBANTE = [
        ('BOLETA', 'Boleta'),
        ('FACTURA', 'Factura'),
        ('TICKET', 'Ticket'),
        ('OTRO', 'Otro'),
    ]
    FORMA_PAGO = [
        ('CONTADO', 'Contado'),
        ('CREDITO', 'Crédito'),
    ]
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    fecha = models.DateField()
    tipo_comprobante = models.CharField(max_length=50, choices=TIPO_COMPROBANTE, default='FACTURA')
    numero_comprobante = models.CharField(max_length=50)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pago = models.CharField(max_length=20, choices=FORMA_PAGO, default='CONTADO')
    num_cuotas = models.PositiveIntegerField(default=1)
    activo = models.BooleanField(default=True)
    modulo = models.CharField(max_length=20, choices=MODULO_CHOICES, default='HOTEL')

    def __str__(self):
        return f"Compra {self.numero_comprobante} - {self.proveedor.razon_social}"

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

class CuotaCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='cuotas')
    numero_cuota = models.PositiveIntegerField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_vencimiento = models.DateField()
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return f"Cuota {self.numero_cuota} - {self.compra.numero_comprobante}"

class RegistroServicio(models.Model):
    nombre_servicio = models.CharField(max_length=200)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    comentarios = models.TextField(blank=True, null=True)
    modulo = models.CharField(max_length=20, choices=MODULO_CHOICES, default='HOTEL')

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

class ConfiguracionEmpresa(models.Model):
    # Datos Legales
    nombre_sistema = models.CharField(max_length=100, default='TurismoERP')
    logo = models.ImageField(upload_to='empresa/logos/', blank=True, null=True)
    ruc = models.CharField(max_length=11)
    razon_social = models.CharField(max_length=255)
    nombre_comercial = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255)
    departamento = models.CharField(max_length=50, default='AREQUIPA')
    provincia = models.CharField(max_length=50, default='AREQUIPA')
    distrito = models.CharField(max_length=50, default='AREQUIPA')
    
    # Preferencias de Sistema
    TIPO_IMPRESION = [
        ('A4', 'Impresora Estándar (A4)'),
        ('TICKET_80', 'Ticketera Térmica (80mm)'),
        ('TICKET_58', 'Ticketera Térmica (58mm)'),
    ]
    tipo_impresion = models.CharField(max_length=20, choices=TIPO_IMPRESION, default='A4')
    formato_hotel = models.CharField(max_length=20, choices=TIPO_IMPRESION, default='A4')
    formato_restaurante = models.CharField(max_length=20, choices=TIPO_IMPRESION, default='TICKET_80')
    mensaje_pie_pagina = models.TextField(blank=True, null=True, help_text="Mensaje al final de los tickets")
    imprimir_logo_ticket = models.BooleanField(default=True)
    nombre_impresora_hotel = models.CharField(max_length=100, blank=True, null=True, help_text="Nombre de la impresora en Windows para el Hotel")
    nombre_impresora_restaurante = models.CharField(max_length=100, blank=True, null=True, help_text="Nombre de la impresora en Windows para el Restaurante")
    
    FORMA_LOGO = [
        ('RECTANGULAR', 'Rectangular / Original'),
        ('CIRCULAR', 'Circular (Avatar)'),
    ]
    forma_logo = models.CharField(max_length=20, choices=FORMA_LOGO, default='RECTANGULAR')
    
    ruta_referencia = models.CharField(max_length=255, blank=True, null=True, help_text="Ruta local de instalación o backups")
    
    # Credenciales SUNAT
    usuario_sol = models.CharField(max_length=50, default='MODDATOS')
    clave_sol = models.CharField(max_length=50, default='MODDATOS')
    certificado_digital = models.FileField(upload_to='certificados/', blank=True, null=True)
    password_certificado = models.CharField(max_length=100, blank=True, null=True)
    
    # Entorno
    AMBIENTE_CHOICES = [
        ('BETA', 'Pruebas (BETA)'),
        ('PRODUCCION', 'Producción'),
    ]
    ambiente = models.CharField(max_length=20, choices=AMBIENTE_CHOICES, default='BETA')
    
    class Meta:
        verbose_name = "Configuración de Empresa"
        verbose_name_plural = "Configuración de Empresa"

    def __str__(self):
        return f"{self.ruc} - {self.razon_social}"

class Habitacion(models.Model):
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('OCUPADA', 'Ocupada'),
        ('LIMPIEZA', 'En Limpieza'),
        ('MANTENIMIENTO', 'Mantenimiento'),
    ]
    TIPO_CHOICES = [
        ('SIMPLE', 'Simple'),
        ('DOBLE', 'Doble'),
        ('MATRIMONIAL', 'Matrimonial'),
        ('TRIPLE', 'Triple'),
        ('SUITE', 'Suite'),
    ]
    numero = models.CharField(max_length=10, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='SIMPLE')
    precio_noche = models.DecimalField(max_digits=10, decimal_places=2)
    precio_noche_corporativo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='DISPONIBLE')
    imagen = models.ImageField(upload_to='habitaciones/', blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Hab. {self.numero} ({self.get_tipo_display()})"

class Mesa(models.Model):
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('OCUPADA', 'Ocupada'),
        ('RESERVADA', 'Reservada'),
        ('LIMPIEZA', 'En Limpieza'),
    ]
    numero = models.CharField(max_length=10, unique=True)
    capacidad = models.PositiveIntegerField(default=4)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='DISPONIBLE')
    posicion_x = models.IntegerField(default=0, help_text="Para el mapa visual")
    posicion_y = models.IntegerField(default=0, help_text="Para el mapa visual")

    def __str__(self):
        return f"Mesa {self.numero} ({self.capacidad} pers.)"

class Reserva(models.Model):
    ESTADO_RESERVA = [
        ('PENDIENTE', 'Pendiente'),
        ('CHECKIN', 'En Hospedaje'),
        ('CHECKOUT', 'Finalizada (Pagada)'),
        ('CANCELADA', 'Cancelada'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)
    fecha_ingreso = models.DateTimeField()
    fecha_salida = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_RESERVA, default='PENDIENTE')
    total_hospedaje = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    adelanto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    observaciones = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserva {self.id} - {self.cliente.nombre_razon_social}"

class PedidoHabitacion(models.Model):
    reserva = models.ForeignKey(Reserva, related_name='pedidos', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    pagado = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pedido {self.id} - Hab. {self.reserva.habitacion.numero}"
