from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum
from django.utils import timezone

from .models import Reserva, ReservaHabitacion, ReservaServicioAdicional, CheckIn, CheckOut
from .serializers import (
    ReservaSerializer, ReservaListSerializer, ReservaCreateSerializer,
    ReservaHabitacionSerializer, ReservaHabitacionCreateSerializer,
    ReservaServicioAdicionalSerializer, ReservaServicioAdicionalCreateSerializer,
    CheckInSerializer, CheckOutSerializer
)

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'cliente', 'tipo_reserva', 'estado', 'fecha_checkin', 'fecha_checkout']
    search_fields = ['codigo_reserva', 'cliente__nombres', 'cliente__apellidos', 'notas']
    ordering_fields = ['creado_en', 'fecha_checkin', 'codigo_reserva']

    def get_serializer_class(self):
        if self.action == 'list':
            return ReservaListSerializer
        elif self.action == 'create':
            return ReservaCreateSerializer
        return ReservaSerializer

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        reserva = self.get_object()
        
        if reserva.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden confirmar reservas pendientes'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reserva.estado = 'confirmada'
        reserva.save()
        
        return Response({
            'message': 'Reserva confirmada correctamente',
            'estado': reserva.estado,
            'estado_display': reserva.get_estado_display()
        })

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        reserva = self.get_object()
        motivo = request.data.get('motivo', '')
        
        if reserva.estado in ['checkin', 'checkout']:
            return Response(
                {'error': 'No se pueden cancelar reservas en curso o finalizadas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reserva.estado = 'cancelada'
        reserva.notas += f"\n\nCANCELACIÓN: {motivo}"
        reserva.save()
        
        return Response({
            'message': 'Reserva cancelada correctamente',
            'estado': reserva.estado,
            'estado_display': reserva.get_estado_display()
        })

    @action(detail=True, methods=['post'])
    def realizar_checkin(self, request, pk=None):
        reserva = self.get_object()
        
        if reserva.estado != 'confirmada':
            return Response(
                {'error': 'Solo se puede hacer check-in de reservas confirmadas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        observaciones = request.data.get('observaciones', '')
        documento_entregado = request.data.get('documento_entregado', False)
        deposito_recibido = request.data.get('deposito_recibido')
        
        checkin = CheckIn.objects.create(
            reserva=reserva,
            responsable=request.user,
            observaciones=observaciones,
            documento_entregado=documento_entregado,
            deposito_recibido=deposito_recibido
        )
        
        reserva.estado = 'checkin'
        reserva.save()
        
        # Actualizar estado de las habitaciones
        for reserva_habitacion in reserva.habitaciones.all():
            reserva_habitacion.habitacion.estado = 'ocupada'
            reserva_habitacion.habitacion.save()
        
        serializer = CheckInSerializer(checkin)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def realizar_checkout(self, request, pk=None):
        reserva = self.get_object()
        
        if reserva.estado != 'checkin':
            return Response(
                {'error': 'Solo se puede hacer checkout de reservas con check-in realizado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        observaciones = request.data.get('observaciones', '')
        cargo_adicional = request.data.get('cargo_adicional', 0)
        deposito_devuelto = request.data.get('deposito_devuelto')
        metodo_pago_adicional = request.data.get('metodo_pago_adicional', '')
        
        checkout = CheckOut.objects.create(
            reserva=reserva,
            responsable=request.user,
            observaciones=observaciones,
            cargo_adicional=cargo_adicional,
            deposito_devuelto=deposito_devuelto,
            metodo_pago_adicional=metodo_pago_adicional
        )
        
        reserva.estado = 'checkout'
        reserva.save()
        
        # Actualizar estado de las habitaciones
        for reserva_habitacion in reserva.habitaciones.all():
            reserva_habitacion.habitacion.estado = 'disponible'
            reserva_habitacion.habitacion.save()
        
        serializer = CheckOutSerializer(checkout)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def agregar_habitacion(self, request, pk=None):
        reserva = self.get_object()
        
        if reserva.estado not in ['pendiente', 'confirmada']:
            return Response(
                {'error': 'Solo se pueden agregar habitaciones a reservas pendientes o confirmadas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = request.data.copy()
        data['reserva'] = reserva.id
        
        serializer = ReservaHabitacionCreateSerializer(data=data)
        if serializer.is_valid():
            reserva_habitacion = serializer.save()
            
            # Actualizar subtotal de habitaciones
            subtotal_habitaciones = reserva.habitaciones.aggregate(
                total=Sum('subtotal')
            )['total'] or 0
            reserva.subtotal_habitaciones = subtotal_habitaciones
            reserva.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def agregar_servicio_adicional(self, request, pk=None):
        reserva = self.get_object()
        
        if reserva.estado not in ['pendiente', 'confirmada', 'checkin']:
            return Response(
                {'error': 'No se pueden agregar servicios adicionales a esta reserva'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = request.data.copy()
        data['reserva'] = reserva.id
        
        serializer = ReservaServicioAdicionalCreateSerializer(data=data)
        if serializer.is_valid():
            servicio = serializer.save()
            
            # Actualizar subtotal de servicios adicionales
            subtotal_servicios = reserva.servicios_adicionales.aggregate(
                total=Sum('subtotal')
            )['total'] or 0
            reserva.subtotal_servicios_adicionales = subtotal_servicios
            reserva.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            fecha_checkin__gte=fecha_inicio,
            fecha_checkin__lte=fecha_fin
        )
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReservaListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ReservaListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def checkins_pendientes(self, request):
        fecha = request.query_params.get('fecha', timezone.now().date())
        empresa_id = request.query_params.get('empresa')
        
        queryset = self.queryset.filter(
            fecha_checkin=fecha,
            estado='confirmada'
        )
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReservaListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ReservaListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def checkouts_pendientes(self, request):
        fecha = request.query_params.get('fecha', timezone.now().date())
        empresa_id = request.query_params.get('empresa')
        
        queryset = self.queryset.filter(
            fecha_checkout=fecha,
            estado='checkin'
        )
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReservaListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ReservaListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        empresa_id = request.query_params.get('empresa')
        queryset = self.queryset
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        total_reservas = queryset.count()
        reservas_pendientes = queryset.filter(estado='pendiente').count()
        reservas_confirmadas = queryset.filter(estado='confirmada').count()
        reservas_checkin = queryset.filter(estado='checkin').count()
        reservas_checkout = queryset.filter(estado='checkout').count()
        reservas_canceladas = queryset.filter(estado='cancelada').count()
        
        # Ingresos totales
        ingresos_totales = queryset.aggregate(
            total=Sum('total')
        )['total'] or 0
        
        return Response({
            'total_reservas': total_reservas,
            'reservas_pendientes': reservas_pendientes,
            'reservas_confirmadas': reservas_confirmadas,
            'reservas_checkin': reservas_checkin,
            'reservas_checkout': reservas_checkout,
            'reservas_canceladas': reservas_canceladas,
            'ingresos_totales': ingresos_totales,
            'tasa_cancelacion': round((reservas_canceladas / total_reservas * 100) if total_reservas > 0 else 0, 2),
        })

class ReservaHabitacionViewSet(viewsets.ModelViewSet):
    queryset = ReservaHabitacion.objects.all()
    serializer_class = ReservaHabitacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['reserva', 'habitacion', 'fecha_checkin', 'fecha_checkout']
    ordering_fields = ['fecha_checkin', 'fecha_checkout', 'creado_en']

class ReservaServicioAdicionalViewSet(viewsets.ModelViewSet):
    queryset = ReservaServicioAdicional.objects.all()
    serializer_class = ReservaServicioAdicionalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['reserva', 'fecha_servicio']
    search_fields = ['nombre_servicio', 'descripcion']
    ordering_fields = ['fecha_servicio', 'creado_en']

class CheckInViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CheckIn.objects.all()
    serializer_class = CheckInSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['reserva', 'responsable']
    ordering_fields = ['fecha_hora']

class CheckOutViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CheckOut.objects.all()
    serializer_class = CheckOutSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['reserva', 'responsable']
    ordering_fields = ['fecha_hora']
