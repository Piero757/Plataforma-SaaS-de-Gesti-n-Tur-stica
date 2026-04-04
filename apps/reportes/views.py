from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
import csv
import io
from datetime import datetime, timedelta

from .models import Reporte, ReporteProgramado, MetricaReporte, DashboardConfiguracion
from .serializers import (
    ReporteSerializer, ReporteListSerializer, ReporteCreateSerializer,
    ReporteProgramadoSerializer, ReporteProgramadoCreateSerializer,
    MetricaReporteSerializer, DashboardConfiguracionSerializer
)

class ReporteViewSet(viewsets.ModelViewSet):
    queryset = Reporte.objects.all()
    serializer_class = ReporteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'tipo_reporte', 'estado']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['fecha_solicitud', 'fecha_generacion']

    def get_serializer_class(self):
        if self.action == 'list':
            return ReporteListSerializer
        elif self.action == 'create':
            return ReporteCreateSerializer
        return ReporteSerializer

    def perform_create(self, serializer):
        serializer.save(solicitado_por=self.request.user)

    @action(detail=True, methods=['post'])
    def generar(self, request, pk=None):
        reporte = self.get_object()
        
        if reporte.estado != 'generando':
            return Response(
                {'error': 'Este reporte ya fue procesado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Iniciar generación del reporte
            inicio_tiempo = timezone.now()
            
            # Generar datos según el tipo de reporte
            datos = self._generar_datos_reporte(reporte)
            
            # Crear archivo CSV
            archivo_csv = self._crear_csv(reporte, datos)
            
            # Actualizar reporte
            reporte.estado = 'completado'
            reporte.archivo_generado = archivo_csv
            reporte.registros_totales = len(datos) if datos else 0
            reporte.tiempo_generacion = timezone.now() - inicio_tiempo
            reporte.fecha_generacion = timezone.now()
            reporte.save()
            
            return Response({
                'message': 'Reporte generado correctamente',
                'estado': reporte.estado,
                'registros_totales': reporte.registros_totales,
                'tiempo_generacion': str(reporte.tiempo_generacion)
            })
            
        except Exception as e:
            reporte.estado = 'error'
            reporte.error_message = str(e)
            reporte.save()
            
            return Response(
                {'error': f'Error al generar reporte: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _generar_datos_reporte(self, reporte):
        """Generar datos según el tipo de reporte"""
        if reporte.tipo_reporte == 'ocupacion':
            return self._generar_reporte_ocupacion(reporte)
        elif reporte.tipo_reporte == 'ingresos':
            return self._generar_reporte_ingresos(reporte)
        elif reporte.tipo_reporte == 'reservas':
            return self._generar_reporte_reservas(reporte)
        elif reporte.tipo_reporte == 'clientes':
            return self._generar_reporte_clientes(reporte)
        elif reporte.tipo_reporte == 'empleados':
            return self._generar_reporte_empleados(reporte)
        elif reporte.tipo_reporte == 'pagos':
            return self._generar_reporte_pagos(reporte)
        else:
            return []

    def _generar_reporte_ocupacion(self, reporte):
        """Generar reporte de ocupación"""
        from apps.habitaciones.models import Habitacion
        from apps.reservas.models import ReservaHabitacion
        
        habitaciones = Habitacion.objects.filter(empresa=reporte.empresa)
        datos = []
        
        for habitacion in habitaciones:
            # Calcular ocupación en el rango de fechas
            noches_ocupadas = ReservaHabitacion.objects.filter(
                habitacion=habitacion,
                fecha_checkin__gte=reporte.fecha_inicio,
                fecha_checkout__lte=reporte.fecha_fin
            ).count()
            
            total_noches = (reporte.fecha_fin - reporte.fecha_inicio).days
            tasa_ocupacion = (noches_ocupadas / total_noches * 100) if total_noches > 0 else 0
            
            datos.append({
                'hotel': habitacion.hotel.nombre,
                'habitacion': habitacion.numero,
                'tipo': habitacion.tipo.nombre,
                'noches_ocupadas': noches_ocupadas,
                'total_noches': total_noches,
                'tasa_ocupacion': round(tasa_ocupacion, 2)
            })
        
        return datos

    def _generar_reporte_ingresos(self, reporte):
        """Generar reporte de ingresos"""
        from apps.pagos.models import Pago
        
        pagos = Pago.objects.filter(
            empresa=reporte.empresa,
            estado='completado',
            fecha_pago__gte=reporte.fecha_inicio,
            fecha_pago__lte=reporte.fecha_fin
        )
        
        datos = []
        for pago in pagos:
            datos.append({
                'codigo_pago': pago.codigo_pago,
                'codigo_reserva': pago.reserva.codigo_reserva,
                'cliente': pago.reserva.cliente.nombre_completo,
                'monto': float(pago.monto),
                'metodo_pago': pago.get_metodo_pago_display(),
                'tipo_pago': pago.get_tipo_pago_display(),
                'fecha_pago': pago.fecha_pago.strftime('%Y-%m-%d') if pago.fecha_pago else '',
                'referencia': pago.referencia
            })
        
        return datos

    def _generar_reporte_reservas(self, reporte):
        """Generar reporte de reservas"""
        from apps.reservas.models import Reserva
        
        reservas = Reserva.objects.filter(
            empresa=reporte.empresa,
            creado_en__gte=reporte.fecha_inicio,
            creado_en__lte=reporte.fecha_fin
        )
        
        datos = []
        for reserva in reservas:
            datos.append({
                'codigo_reserva': reserva.codigo_reserva,
                'cliente': reserva.cliente.nombre_completo,
                'tipo_reserva': reserva.get_tipo_reserva_display(),
                'estado': reserva.get_estado_display(),
                'fecha_checkin': reserva.fecha_checkin.strftime('%Y-%m-%d'),
                'fecha_checkout': reserva.fecha_checkout.strftime('%Y-%m-%d'),
                'noches': reserva.noches,
                'adultos': reserva.adultos,
                'ninos': reserva.ninos,
                'total': float(reserva.total),
                'monto_pagado': float(reserva.monto_pagado),
                'saldo_pendiente': float(reserva.saldo_pendiente),
                'fecha_creacion': reserva.creado_en.strftime('%Y-%m-%d')
            })
        
        return datos

    def _generar_reporte_clientes(self, reporte):
        """Generar reporte de clientes"""
        from apps.clientes.models import Cliente
        
        clientes = Cliente.objects.filter(
            empresa=reporte.empresa,
            creado_en__gte=reporte.fecha_inicio,
            creado_en__lte=reporte.fecha_fin
        )
        
        datos = []
        for cliente in clientes:
            # Contar reservas del cliente
            from apps.reservas.models import Reserva
            total_reservas = Reserva.objects.filter(cliente=cliente).count()
            
            datos.append({
                'nombres': cliente.nombres,
                'apellidos': cliente.apellidos,
                'tipo_documento': cliente.get_tipo_documento_display(),
                'numero_documento': cliente.numero_documento,
                'telefono': cliente.telefono,
                'email': cliente.email,
                'fecha_nacimiento': cliente.fecha_nacimiento.strftime('%Y-%m-%d') if cliente.fecha_nacimiento else '',
                'nacionalidad': cliente.nacionalidad,
                'vip': cliente.vip,
                'total_reservas': total_reservas,
                'fecha_creacion': cliente.creado_en.strftime('%Y-%m-%d')
            })
        
        return datos

    def _generar_reporte_empleados(self, reporte):
        """Generar reporte de empleados"""
        from apps.empleados.models import Empleado
        
        empleados = Empleado.objects.filter(empresa=reporte.empresa)
        
        datos = []
        for empleado in empleados:
            # Calcular asistencia en el período
            from apps.empleados.models import AsistenciaEmpleado
            asistencias = AsistenciaEmpleado.objects.filter(
                empleado=empleado,
                fecha__gte=reporte.fecha_inicio,
                fecha__lte=reporte.fecha_fin
            )
            
            dias_trabajados = asistencias.filter(estado='presente').count()
            total_horas = asistencias.aggregate(total=Sum('horas_trabajadas'))['total'] or 0
            
            datos.append({
                'codigo_empleado': empleado.codigo_empleado,
                'nombres': empleado.nombres,
                'apellidos': empleado.apellidos,
                'cargo': empleado.get_cargo_display(),
                'departamento': empleado.departamento,
                'turno': empleado.get_turno_display(),
                'estado': empleado.get_estado_display(),
                'salario': float(empleado.salario),
                'fecha_contratacion': empleado.fecha_contratacion.strftime('%Y-%m-%d'),
                'dias_trabajados': dias_trabajados,
                'total_horas': float(total_horas),
                'telefono': empleado.telefono,
                'email': empleado.email
            })
        
        return datos

    def _generar_reporte_pagos(self, reporte):
        """Generar reporte de pagos"""
        from apps.pagos.models import Pago
        
        pagos = Pago.objects.filter(
            empresa=reporte.empresa,
            creado_en__gte=reporte.fecha_inicio,
            creado_en__lte=reporte.fecha_fin
        )
        
        datos = []
        for pago in pagos:
            datos.append({
                'codigo_pago': pago.codigo_pago,
                'codigo_reserva': pago.reserva.codigo_reserva,
                'cliente': pago.reserva.cliente.nombre_completo,
                'monto': float(pago.monto),
                'metodo_pago': pago.get_metodo_pago_display(),
                'tipo_pago': pago.get_tipo_pago_display(),
                'estado': pago.get_estado_display(),
                'fecha_pago': pago.fecha_pago.strftime('%Y-%m-%d') if pago.fecha_pago else '',
                'referencia': pago.referencia,
                'comprobante_generado': pago.comprobante_generado,
                'tipo_comprobante': pago.get_tipo_comprobante_display() if pago.tipo_comprobante else '',
                'numero_comprobante': pago.numero_comprobante,
                'fecha_creacion': pago.creado_en.strftime('%Y-%m-%d')
            })
        
        return datos

    def _crear_csv(self, reporte, datos):
        """Crear archivo CSV con los datos"""
        if not datos:
            return None
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Escribir encabezados
        if datos:
            writer.writerow(datos[0].keys())
        
        # Escribir datos
        for fila in datos:
            writer.writerow(fila.values())
        
        # Guardar archivo
        filename = f"reportes/{reporte.tipo_reporte}_{reporte.empresa.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        from django.core.files.base import ContentFile
        reporte.archivo_generado.save(filename, ContentFile(output.getvalue().encode('utf-8')))
        
        return reporte.archivo_generado

    @action(detail=False, methods=['get'])
    def tipos_disponibles(self, request):
        """Obtener lista de tipos de reporte disponibles"""
        tipos = [
            {'value': choice[0], 'label': choice[1]} 
            for choice in Reporte.TIPO_REPORTE_CHOICES
        ]
        return Response(tipos)

class ReporteProgramadoViewSet(viewsets.ModelViewSet):
    queryset = ReporteProgramado.objects.all()
    serializer_class = ReporteProgramadoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'tipo_reporte', 'frecuencia', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'proxima_ejecucion']

    def get_serializer_class(self):
        if self.action == 'create':
            return ReporteProgramadoCreateSerializer
        return ReporteProgramadoSerializer

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

    @action(detail=True, methods=['post'])
    def activar_desactivar(self, request, pk=None):
        reporte = self.get_object()
        reporte.activo = not reporte.activo
        reporte.save()
        
        estado = 'activado' if reporte.activo else 'desactivado'
        return Response({'message': f'Reporte programado {estado} correctamente'})

    @action(detail=True, methods=['post'])
    def ejecutar_ahora(self, request, pk=None):
        """Ejecutar reporte programado inmediatamente"""
        reporte_programado = self.get_object()
        
        # Crear reporte instantáneo
        reporte = Reporte.objects.create(
            empresa=reporte_programado.empresa,
            tipo_reporte=reporte_programado.tipo_reporte,
            nombre=f"Ejecución manual: {reporte_programado.nombre}",
            descripcion=reporte_programado.descripcion,
            fecha_inicio=timezone.now().date() - timedelta(days=30),
            fecha_fin=timezone.now().date(),
            parametros=reporte_programado.parametros,
            solicitado_por=request.user
        )
        
        # Generar reporte
        from apps.reportes.views import ReporteViewSet
        viewset = ReporteViewSet()
        viewset.request = request
        resultado = viewset._generar_datos_reporte(reporte)
        
        if resultado:
            archivo = viewset._crear_csv(reporte, resultado)
            reporte.estado = 'completado'
            reporte.archivo_generado = archivo
            reporte.registros_totales = len(resultado)
            reporte.fecha_generacion = timezone.now()
            reporte.save()
        
        serializer = ReporteSerializer(reporte)
        return Response(serializer.data)

class MetricaReporteViewSet(viewsets.ModelViewSet):
    queryset = MetricaReporte.objects.all()
    serializer_class = MetricaReporteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'fecha_actualizacion']

class DashboardConfiguracionViewSet(viewsets.ModelViewSet):
    queryset = DashboardConfiguracion.objects.all()
    serializer_class = DashboardConfiguracionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'publico']
    search_fields = ['nombre_dashboard']
    ordering_fields = ['nombre_dashboard']

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)
