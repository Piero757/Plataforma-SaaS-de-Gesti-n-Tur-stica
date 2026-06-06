from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from .models import PerfilUsuario, Habitacion, Mesa, Cliente, Venta, DetalleVenta, EstadoComanda, Producto, ConfiguracionEmpresa, Reserva

class SaaSPlataformaTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Crear usuario administrador para testing
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpassword123',
            first_name='Admin',
            last_name='User'
        )
        # PerfilUsuario se crea automáticamente a través de la señal.
        # Nos aseguramos de que el rol es ADMIN
        self.admin_user.perfil.rol = 'ADMIN'
        self.admin_user.perfil.save()
        
        # Loguear cliente
        self.client.login(username='admin_test', password='testpassword123')
        
        # Configuración de empresa para evitar None en reportes
        self.empresa_config = ConfiguracionEmpresa.objects.create(
            ruc='10123456789',
            razon_social='Empresa de Test S.A.C.',
            direccion='Calle Falsa 123'
        )

        # Datos de prueba
        self.habitacion = Habitacion.objects.create(
            numero='101',
            tipo='SIMPLE',
            precio_noche=Decimal('100.00'),
            estado='DISPONIBLE',
            activo=True
        )
        
        self.mesa = Mesa.objects.create(
            numero='5',
            capacidad=6,
            estado='DISPONIBLE'
        )

    def test_habitaciones_list_view(self):
        """Verifica que la vista de habitaciones carga correctamente sin el error reservas_activas."""
        response = self.client.get(reverse('habitaciones_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('habitaciones', response.context)
        # Verificar que el contexto contiene los tipos de habitación
        self.assertIn('tipos_habitacion', response.context)
        # Verificar que no hay error de variable reservas_activas faltante en el renderizado
        self.assertContains(response, "#101")

    def test_mesa_detalle_sillas_range(self):
        """Verifica que la vista de detalle de mesa calcula correctamente el rango de sillas dinámicas."""
        # Necesitamos un producto y una comanda abierta para que se renderice el formulario con las sillas
        producto = Producto.objects.create(
            codigo='PROD-TEST',
            nombre='Lomo Saltado',
            categoria='RESTAURANTE',
            precio_venta=Decimal('35.00'),
            activo=True,
            modulo='RESTAURANTE'
        )
        
        cliente = Cliente.objects.create(
            tipo_documento='DNI',
            numero_documento='00000000',
            nombre_razon_social='Público General',
            modulo='RESTAURANTE'
        )
        
        comanda = Venta.objects.create(
            cliente=cliente,
            usuario=self.admin_user,
            tipo_comprobante='TICKET',
            serie='COM',
            numero=1,
            total=Decimal('0.00'),
            es_comanda=True,
            mesa=self.mesa,
            modulo='RESTAURANTE'
        )

        response = self.client.get(reverse('mesa_detalle', kwargs={'mesa_id': self.mesa.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('sillas_range', response.context)
        # El rango debe ser del 1 al 6 (capacidad de la mesa es 6)
        self.assertEqual(list(response.context['sillas_range']), [1, 2, 3, 4, 5, 6])
        # Verificar que se renderizan opciones de sillas dinámicas en el HTML
        self.assertContains(response, '<option value="6">Silla 6</option>')
        self.assertNotContains(response, '<option value="7">Silla 7</option>')

    def test_exportar_ventas_generales_pdf(self):
        """Verifica que la vista de exportar PDF ventas generales se ejecuta sin errores."""
        cliente = Cliente.objects.create(
            tipo_documento='DNI',
            numero_documento='12345678',
            nombre_razon_social='Cliente de Prueba',
            modulo='HOTEL'
        )
        
        # Creamos una venta de prueba
        venta = Venta.objects.create(
            cliente=cliente,
            usuario=self.admin_user,
            tipo_comprobante='BOLETA',
            serie='B001',
            numero=1,
            total=Decimal('150.00'),
            forma_pago='CONTADO',
            modulo='HOTEL',
            estado_sunat='ACEPTADO'
        )
        
        # Ejecutar la vista de exportación
        response = self.client.get(reverse('exportar_ventas_generales_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_quick_check_in_and_filtering(self):
        """Verifica que el Check-in rápido crea el cliente temporal y asocia los campos del cuaderno, y que la búsqueda por filtros funciona."""
        checkin_url = reverse('reserva_create')
        data = {
            'nombre_cliente_rapido': 'Huésped Anónimo de Prueba',
            'habitacion': self.habitacion.id,
            'fecha_ingreso': (timezone.now()).strftime('%Y-%m-%dT%H:%M'),
            'fecha_salida': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'total_hospedaje': '100.00',
            'adelanto': '50.00',
            'n_pax': 2,
            'hora_desayuno': '09:00 AM',
            'placa_vehiculo': 'PLATE-TEST',
            'condicion_pago': 'EFECTIVO',
            'observaciones': 'Ninguna'
        }
        
        response = self.client.post(checkin_url, data)
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó el cliente temporal y la reserva
        reserva = Reserva.objects.get(placa_vehiculo='PLATE-TEST')
        self.assertEqual(reserva.n_pax, 2)
        self.assertEqual(reserva.hora_desayuno, '09:00 AM')
        self.assertEqual(reserva.condicion_pago, 'EFECTIVO')
        self.assertTrue(reserva.cliente.numero_documento.startswith('TEMP-'))
        self.assertEqual(reserva.cliente.nombre_razon_social, 'Huésped Anónimo de Prueba')
        self.assertEqual(reserva.habitacion.estado, 'OCUPADA')
        
        # Verificar filtros de búsqueda en la lista de reservas
        list_url = reverse('reserva_list')
        
        # Buscar por placa
        response = self.client.get(list_url, {'q': 'PLATE-TEST'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PLATE-TEST')
        
        # Buscar por cliente instantáneo
        response = self.client.get(list_url, {'q': 'Anónimo'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Huésped Anónimo de Prueba')
