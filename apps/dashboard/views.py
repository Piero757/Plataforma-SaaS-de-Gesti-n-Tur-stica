from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import EstadisticaGeneral, MetricaTiempoReal, AlertaDashboard, WidgetDashboard
from .serializers import (
    EstadisticaGeneralSerializer, MetricaTiempoRealSerializer, AlertaDashboardSerializer,
    WidgetDashboardSerializer, DashboardDataSerializer, AlertaCreateSerializer,
    WidgetCreateSerializer, MetricaActualizacionSerializer
)

def dashboard_view(request):
    """Vista principal del dashboard"""
    return render(request, 'dashboard/index.html')

class EstadisticaGeneralViewSet(viewsets.ModelViewSet):
    queryset = EstadisticaGeneral.objects.all()
    serializer_class = EstadisticaGeneralSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['empresa', 'fecha']
    ordering_fields = ['fecha', 'creado_en']

    @action(detail=False, methods=['post'])
    def generar_diarias(self, request):
        """Generar estadísticas diarias para una empresa y fecha específicas"""
        empresa_id = request.data.get('empresa_id')
        fecha = request.data.get('fecha')
        
        if not empresa_id:
            return Response(
                {'error': 'Debe proporcionar el ID de la empresa'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if fecha:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        else:
            fecha = timezone.now().date()
        
        from apps.clientes.models import Empresa
        try:
            empresa = Empresa.objects.get(id=empresa_id)
            estadistica = EstadisticaGeneral.generar_estadisticas_diarias(empresa, fecha)
            serializer = EstadisticaGeneralSerializer(estadistica)
            return Response(serializer.data)
        except Empresa.DoesNotExist:
            return Response(
                {'error': 'Empresa no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class MetricaTiempoRealViewSet(viewsets.ModelViewSet):
    queryset = MetricaTiempoReal.objects.all()
    serializer_class = MetricaTiempoRealSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['empresa', 'tipo_metrica']
    ordering_fields = ['ultima_actualizacion']

    @action(detail=False, methods=['post'])
    def actualizar_todas(self, request):
        """Actualizar todas las métricas de tiempo real para una empresa"""
        empresa_id = request.data.get('empresa_id')
        
        if not empresa_id:
            return Response(
                {'error': 'Debe proporcionar el ID de la empresa'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.clientes.models import Empresa
        try:
            empresa = Empresa.objects.get(id=empresa_id)
            MetricaTiempoReal.actualizar_metricas(empresa)
            
            # Obtener métricas actualizadas
            metricas = MetricaTiempoReal.objects.filter(empresa=empresa)
            serializer = MetricaTiempoRealSerializer(metricas, many=True)
            
            return Response({
                'message': 'Métricas actualizadas correctamente',
                'metricas': serializer.data
            })
        except Empresa.DoesNotExist:
            return Response(
                {'error': 'Empresa no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class AlertaDashboardViewSet(viewsets.ModelViewSet):
    queryset = AlertaDashboard.objects.all()
    serializer_class = AlertaDashboardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'tipo_alerta', 'prioridad', 'leida', 'accion_requerida']
    search_fields = ['titulo', 'mensaje']
    ordering_fields = ['prioridad', 'creado_en']

    def get_serializer_class(self):
        if self.action == 'create':
            return AlertaCreateSerializer
        return AlertaDashboardSerializer

    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        alerta = self.get_object()
        alerta.marcar_como_leida()
        
        return Response({
            'message': 'Alerta marcada como leída',
            'leida': alerta.leida
        })

    @action(detail=True, methods=['post'])
    def marcar_no_leida(self, request, pk=None):
        alerta = self.get_object()
        alerta.leida = False
        alerta.save(update_fields=['leida'])
        
        return Response({
            'message': 'Alerta marcada como no leída',
            'leida': alerta.leida
        })

    @action(detail=False, methods=['post'])
    def marcar_todas_leidas(self, request):
        """Marcar todas las alertas como leídas para una empresa"""
        empresa_id = request.data.get('empresa_id')
        
        if not empresa_id:
            return Response(
                {'error': 'Debe proporcionar el ID de la empresa'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        actualizadas = AlertaDashboard.objects.filter(
            empresa_id=empresa_id,
            leida=False
        ).update(leida=True)
        
        return Response({
            'message': f'{actualizadas} alertas marcadas como leídas',
            'total_actualizadas': actualizadas
        })

    @action(detail=False, methods=['get'])
    def no_leidas(self, request):
        """Obtener alertas no leídas para una empresa"""
        empresa_id = request.query_params.get('empresa')
        
        if not empresa_id:
            return Response(
                {'error': 'Debe proporcionar el ID de la empresa'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(empresa_id=empresa_id, leida=False)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AlertaDashboardSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = AlertaDashboardSerializer(queryset, many=True)
        return Response(serializer.data)

class WidgetDashboardViewSet(viewsets.ModelViewSet):
    queryset = WidgetDashboard.objects.all()
    serializer_class = WidgetDashboardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'tipo_widget', 'activo']
    search_fields = ['nombre']
    ordering_fields = ['posicion_y', 'posicion_x', 'nombre']

    def get_serializer_class(self):
        if self.action == 'create':
            return WidgetCreateSerializer
        return WidgetDashboardSerializer

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

    @action(detail=True, methods=['post'])
    def actualizar_datos(self, request, pk=None):
        """Actualizar datos de un widget específico"""
        widget = self.get_object()
        
        # Aquí iría la lógica para actualizar los datos del widget
        # según su tipo y configuración
        
        datos_actualizados = self._generar_datos_widget(widget)
        
        widget.datos = datos_actualizados
        widget.save(update_fields=['datos'])
        
        return Response({
            'message': 'Datos del widget actualizados correctamente',
            'datos': widget.datos
        })

    def _generar_datos_widget(self, widget):
        """Generar datos para un widget según su tipo"""
        if widget.tipo_widget == 'numero':
            return self._generar_datos_numero(widget)
        elif widget.tipo_widget == 'grafico_barras':
            return self._generar_datos_grafico_barras(widget)
        elif widget.tipo_widget == 'grafico_lineas':
            return self._generar_datos_grafico_lineas(widget)
        elif widget.tipo_widget == 'tabla':
            return self._generar_datos_tabla(widget)
        else:
            return {}

    def _generar_datos_numero(self, widget):
        """Generar datos para widget de tipo número"""
        config = widget.configuracion
        metrica_tipo = config.get('metrica_tipo')
        
        if metrica_tipo == 'reservas_hoy':
            from apps.reservas.models import Reserva
            hoy = timezone.now().date()
            valor = Reserva.objects.filter(
                empresa=widget.empresa,
                creado_en__date=hoy
            ).count()
        elif metrica_tipo == 'ingresos_hoy':
            from apps.pagos.models import Pago
            hoy = timezone.now().date()
            valor = Pago.objects.filter(
                empresa=widget.empresa,
                estado='completado',
                fecha_pago__date=hoy
            ).aggregate(total=Sum('monto'))['total'] or 0
        else:
            valor = 0
        
        return {
            'valor': valor,
            'titulo': config.get('titulo', ''),
            'unidad': config.get('unidad', ''),
            'color': config.get('color', '#007bff')
        }

    def _generar_datos_grafico_barras(self, widget):
        """Generar datos para widget de gráfico de barras"""
        config = widget.configuracion
        dias = config.get('dias', 7)
        
        # Generar datos para los últimos N días
        fechas = []
        valores = []
        
        for i in range(dias):
            fecha = timezone.now().date() - timedelta(days=i)
            fechas.append(fecha.strftime('%Y-%m-%d'))
            
            # Ejemplo: reservas por día
            from apps.reservas.models import Reserva
            valor = Reserva.objects.filter(
                empresa=widget.empresa,
                creado_en__date=fecha
            ).count()
            valores.append(valor)
        
        return {
            'labels': fechas[::-1],
            'datasets': [{
                'label': config.get('titulo', 'Reservas'),
                'data': valores[::-1],
                'backgroundColor': config.get('color', '#007bff')
            }]
        }

    def _generar_datos_grafico_lineas(self, widget):
        """Generar datos para widget de gráfico de líneas"""
        config = widget.configuracion
        dias = config.get('dias', 30)
        
        # Generar datos para los últimos N días
        fechas = []
        valores = []
        
        for i in range(dias):
            fecha = timezone.now().date() - timedelta(days=i)
            fechas.append(fecha.strftime('%Y-%m-%d'))
            
            # Ejemplo: ingresos por día
            from apps.pagos.models import Pago
            valor = Pago.objects.filter(
                empresa=widget.empresa,
                estado='completado',
                fecha_pago__date=fecha
            ).aggregate(total=Sum('monto'))['total'] or 0
            valores.append(float(valor))
        
        return {
            'labels': fechas[::-1],
            'datasets': [{
                'label': config.get('titulo', 'Ingresos'),
                'data': valores[::-1],
                'borderColor': config.get('color', '#007bff'),
                'fill': False
            }]
        }

    def _generar_datos_tabla(self, widget):
        """Generar datos para widget de tabla"""
        config = widget.configuracion
        limite = config.get('limite', 10)
        
        # Ejemplo: últimas reservas
        from apps.reservas.models import Reserva
        from apps.reservas.serializers import ReservaListSerializer
        
        reservas = Reserva.objects.filter(
            empresa=widget.empresa
        ).order_by('-creado_en')[:limite]
        
        serializer = ReservaListSerializer(reservas, many=True)
        
        return {
            'headers': ['Código', 'Cliente', 'Estado', 'Total'],
            'data': [
                [
                    r['codigo_reserva'],
                    r['nombre_cliente'],
                    r['estado_display'],
                    f"S/. {r['total']}"
                ]
                for r in serializer.data
            ]
        }

class DashboardViewSet(viewsets.GenericViewSet):
    """ViewSet principal para el dashboard"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def datos_completos(self, request):
        """Obtener todos los datos para el dashboard de una empresa"""
        empresa_id = request.query_params.get('empresa')
        
        if not empresa_id:
            return Response(
                {'error': 'Debe proporcionar el ID de la empresa'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener estadísticas generales (últimos 7 días)
        estadisticas = EstadisticaGeneral.objects.filter(
            empresa_id=empresa_id,
            fecha__gte=timezone.now().date() - timedelta(days=7)
        ).order_by('-fecha')
        
        # Obtener métricas en tiempo real
        metricas = MetricaTiempoReal.objects.filter(empresa_id=empresa_id)
        
        # Obtener alertas no leídas
        alertas = AlertaDashboard.objects.filter(
            empresa_id=empresa_id,
            leida=False
        ).order_by('-prioridad', '-creado_en')[:10]
        
        # Obtener widgets activos
        widgets = WidgetDashboard.objects.filter(
            empresa_id=empresa_id,
            activo=True
        ).order_by('posicion_y', 'posicion_x')
        
        # Actualizar métricas si es necesario
        if timezone.now() - metricas.first().ultima_actualizacion > timedelta(minutes=5):
            from apps.clientes.models import Empresa
            empresa = Empresa.objects.get(id=empresa_id)
            MetricaTiempoReal.actualizar_metricas(empresa)
            metricas = MetricaTiempoReal.objects.filter(empresa_id=empresa_id)
        
        data = {
            'estadisticas_generales': EstadisticaGeneralSerializer(estadisticas, many=True).data,
            'metricas_tiempo_real': MetricaTiempoRealSerializer(metricas, many=True).data,
            'alertas': AlertaDashboardSerializer(alertas, many=True).data,
            'widgets': WidgetDashboardSerializer(widgets, many=True).data
        }
        
        return Response(data)

    @action(detail=False, methods=['post'])
    def crear_alerta_automatica(self, request):
        """Crear una alerta automáticamente basada en condiciones"""
        empresa_id = request.data.get('empresa_id')
        tipo_alerta = request.data.get('tipo_alerta')
        titulo = request.data.get('titulo')
        mensaje = request.data.get('mensaje')
        prioridad = request.data.get('prioridad', 'media')
        accion_requerida = request.data.get('accion_requerida', False)
        url_accion = request.data.get('url_accion', '')
        
        if not all([empresa_id, tipo_alerta, titulo, mensaje]):
            return Response(
                {'error': 'Debe proporcionar empresa_id, tipo_alerta, titulo y mensaje'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.clientes.models import Empresa
        try:
            empresa = Empresa.objects.get(id=empresa_id)
            alerta = AlertaDashboard.crear_alerta_automatica(
                empresa=empresa,
                tipo_alerta=tipo_alerta,
                titulo=titulo,
                mensaje=mensaje,
                prioridad=prioridad,
                accion_requerida=accion_requerida,
                url_accion=url_accion
            )
            
            serializer = AlertaDashboardSerializer(alerta)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Empresa.DoesNotExist:
            return Response(
                {'error': 'Empresa no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
