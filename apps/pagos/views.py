from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Q
from django.utils import timezone

from .models import Pago, MetodoPagoConfiguracion, Reembolso
from .serializers import (
    PagoSerializer, PagoListSerializer, PagoCreateSerializer,
    MetodoPagoConfiguracionSerializer, ReembolsoSerializer, ReembolsoCreateSerializer
)

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'reserva', 'tipo_pago', 'metodo_pago', 'estado']
    search_fields = ['codigo_pago', 'referencia', 'numero_operacion']
    ordering_fields = ['creado_en', 'fecha_pago', 'monto']

    def get_serializer_class(self):
        if self.action == 'list':
            return PagoListSerializer
        elif self.action == 'create':
            return PagoCreateSerializer
        return PagoSerializer

    def perform_create(self, serializer):
        serializer.save(registrado_por=self.request.user)

    @action(detail=True, methods=['post'])
    def procesar_pago(self, request, pk=None):
        pago = self.get_object()
        
        if pago.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden procesar pagos pendientes'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pago.estado = 'completado'
        pago.fecha_pago = timezone.now()
        pago.save()
        
        # Actualizar monto pagado de la reserva
        reserva = pago.reserva
        reserva.monto_pagado += pago.monto
        reserva.save()
        
        return Response({
            'message': 'Pago procesado correctamente',
            'estado': pago.estado,
            'fecha_pago': pago.fecha_pago
        })

    @action(detail=True, methods=['post'])
    def cancelar_pago(self, request, pk=None):
        pago = self.get_object()
        
        if pago.estado == 'completado':
            return Response(
                {'error': 'No se pueden cancelar pagos completados'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pago.estado = 'cancelado'
        pago.save()
        
        return Response({
            'message': 'Pago cancelado correctamente',
            'estado': pago.estado
        })

    @action(detail=True, methods=['post'])
    def generar_comprobante(self, request, pk=None):
        pago = self.get_object()
        tipo_comprobante = request.data.get('tipo_comprobante')
        
        if not tipo_comprobante:
            return Response(
                {'error': 'Debe proporcionar el tipo de comprobante'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Aquí iría la lógica para generar el comprobante (PDF, etc.)
        # Por ahora solo marcamos como generado
        pago.tipo_comprobante = tipo_comprobante
        pago.comprobante_generado = True
        pago.numero_comprobante = f"{tipo_comprobante.upper()}-{pago.codigo_pago}"
        pago.save()
        
        return Response({
            'message': 'Comprobante generado correctamente',
            'tipo_comprobante': pago.tipo_comprobante,
            'numero_comprobante': pago.numero_comprobante
        })

    @action(detail=True, methods=['post'])
    def solicitar_reembolso(self, request, pk=None):
        pago = self.get_object()
        monto = request.data.get('monto')
        motivo = request.data.get('motivo')
        metodo_reembolso = request.data.get('metodo_reembolso')
        
        if pago.estado != 'completado':
            return Response(
                {'error': 'Solo se pueden solicitar reembolsos de pagos completados'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not monto or not motivo or not metodo_reembolso:
            return Response(
                {'error': 'Debe proporcionar monto, motivo y método de reembolso'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if monto > pago.monto:
            return Response(
                {'error': 'El monto del reembolso no puede ser mayor al monto del pago'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reembolso = Reembolso.objects.create(
            pago_original=pago,
            reserva=pago.reserva,
            monto=monto,
            motivo=motivo,
            metodo_reembolso=metodo_reembolso
        )
        
        serializer = ReembolsoSerializer(reembolso)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def por_reserva(self, request):
        reserva_id = request.query_params.get('reserva')
        
        if not reserva_id:
            return Response(
                {'error': 'Debe proporcionar el ID de la reserva'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(reserva_id=reserva_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PagoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PagoListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_fecha(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        empresa_id = request.query_params.get('empresa')
        
        if not fecha_inicio or not fecha_fin:
            return Response(
                {'error': 'Debe proporcionar fecha_inicio y fecha_fin'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(
            fecha_pago__gte=fecha_inicio,
            fecha_pago__lte=fecha_fin,
            estado='completado'
        )
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PagoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PagoListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        empresa_id = request.query_params.get('empresa')
        queryset = self.queryset
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        total_pagos = queryset.count()
        pagos_completados = queryset.filter(estado='completado').count()
        pagos_pendientes = queryset.filter(estado='pendiente').count()
        pagos_cancelados = queryset.filter(estado='cancelado').count()
        
        # Ingresos totales
        ingresos_totales = queryset.filter(estado='completado').aggregate(
            total=Sum('monto')
        )['total'] or 0
        
        # Estadísticas por método de pago
        stats_metodo_pago = {}
        for choice in Pago.METODO_PAGO_CHOICES:
            metodo_id = choice[0]
            metodo_nombre = choice[1]
            count = queryset.filter(metodo_pago=metodo_id).count()
            total = queryset.filter(metodo_pago=metodo_id, estado='completado').aggregate(
                total=Sum('monto')
            )['total'] or 0
            stats_metodo_pago[metodo_nombre] = {
                'cantidad': count,
                'total': total
            }
        
        return Response({
            'total_pagos': total_pagos,
            'pagos_completados': pagos_completados,
            'pagos_pendientes': pagos_pendientes,
            'pagos_cancelados': pagos_cancelados,
            'ingresos_totales': ingresos_totales,
            'tasa_completacion': round((pagos_completados / total_pagos * 100) if total_pagos > 0 else 0, 2),
            'estadisticas_metodo_pago': stats_metodo_pago,
        })

class MetodoPagoConfiguracionViewSet(viewsets.ModelViewSet):
    queryset = MetodoPagoConfiguracion.objects.all()
    serializer_class = MetodoPagoConfiguracionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['empresa', 'metodo_pago', 'activo']
    ordering_fields = ['metodo_pago', 'creado_en']

class ReembolsoViewSet(viewsets.ModelViewSet):
    queryset = Reembolso.objects.all()
    serializer_class = ReembolsoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['pago_original', 'reserva', 'estado', 'metodo_reembolso']
    search_fields = ['motivo', 'referencia_reembolso']
    ordering_fields = ['fecha_solicitud', 'fecha_procesamiento']

    def get_serializer_class(self):
        if self.action == 'create':
            return ReembolsoCreateSerializer
        return ReembolsoSerializer

    @action(detail=True, methods=['post'])
    def aprobar_reembolso(self, request, pk=None):
        reembolso = self.get_object()
        
        if reembolso.estado != 'solicitado':
            return Response(
                {'error': 'Solo se pueden aprobar reembolsos solicitados'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reembolso.estado = 'aprobado'
        reembolso.aprobado_por = request.user
        reembolso.fecha_aprobacion = timezone.now()
        reembolso.save()
        
        return Response({
            'message': 'Reembolso aprobado correctamente',
            'estado': reembolso.estado,
            'fecha_aprobacion': reembolso.fecha_aprobacion
        })

    @action(detail=True, methods=['post'])
    def procesar_reembolso(self, request, pk=None):
        reembolso = self.get_object()
        referencia = request.data.get('referencia_reembolso')
        
        if reembolso.estado != 'aprobado':
            return Response(
                {'error': 'Solo se pueden procesar reembolsos aprobados'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reembolso.estado = 'completado'
        reembolso.procesado_por = request.user
        reembolso.fecha_procesamiento = timezone.now()
        if referencia:
            reembolso.referencia_reembolso = referencia
        reembolso.save()
        
        return Response({
            'message': 'Reembolso procesado correctamente',
            'estado': reembolso.estado,
            'fecha_procesamiento': reembolso.fecha_procesamiento
        })

    @action(detail=True, methods=['post'])
    def rechazar_reembolso(self, request, pk=None):
        reembolso = self.get_object()
        motivo = request.data.get('motivo')
        
        if reembolso.estado != 'solicitado':
            return Response(
                {'error': 'Solo se pueden rechazar reembolsos solicitados'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reembolso.estado = 'rechazado'
        reembolso.aprobado_por = request.user
        reembolso.fecha_aprobacion = timezone.now()
        if motivo:
            reembolso.notas += f"\n\nRECHAZO: {motivo}"
        reembolso.save()
        
        return Response({
            'message': 'Reembolso rechazado correctamente',
            'estado': reembolso.estado
        })
