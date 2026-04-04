from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import PaqueteTuristico, PaqueteHotel, PaqueteServicio
from .serializers import (
    PaqueteTuristicoSerializer, PaqueteListSerializer, PaqueteCreateSerializer,
    PaqueteHotelSerializer, PaqueteServicioSerializer
)

class PaqueteTuristicoViewSet(viewsets.ModelViewSet):
    queryset = PaqueteTuristico.objects.all()
    serializer_class = PaqueteTuristicoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'tipo', 'activo', 'es_promocion']
    search_fields = ['nombre', 'descripcion', 'incluye', 'destinos']
    ordering_fields = ['nombre', 'precio_base', 'duracion_dias', 'creado_en']

    def get_serializer_class(self):
        if self.action == 'list':
            return PaqueteListSerializer
        elif self.action == 'create':
            return PaqueteCreateSerializer
        return PaqueteTuristicoSerializer

    @action(detail=True, methods=['post'])
    def activar_desactivar(self, request, pk=None):
        paquete = self.get_object()
        paquete.activo = not paquete.activo
        paquete.save()
        
        estado = 'activado' if paquete.activo else 'desactivado'
        return Response({'message': f'Paquete {estado} correctamente'})

    @action(detail=True, methods=['post'])
    def marcar_promocion(self, request, pk=None):
        paquete = self.get_object()
        paquete.es_promocion = not paquete.es_promocion
        descuento = request.data.get('descuento_porcentaje')
        
        if descuento is not None:
            paquete.descuento_porcentaje = descuento
        
        paquete.save()
        
        estado = 'marcado como promoción' if paquete.es_promocion else 'desmarcado como promoción'
        return Response({
            'message': f'Paquete {estado} correctamente',
            'es_promocion': paquete.es_promocion,
            'descuento_porcentaje': paquete.descuento_porcentaje
        })

    @action(detail=True, methods=['post'])
    def agregar_hotel(self, request, pk=None):
        paquete = self.get_object()
        hotel_id = request.data.get('hotel_id')
        noches = request.data.get('noches', 1)
        tipo_habitacion_incluida = request.data.get('tipo_habitacion_incluida')
        regimen_alimenticio = request.data.get('regimen_alimenticio', 'desayuno')
        
        if not hotel_id or not tipo_habitacion_incluida:
            return Response(
                {'error': 'Debe proporcionar hotel_id y tipo_habitacion_incluida'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.hoteles.models import Hotel
        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            return Response(
                {'error': 'Hotel no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        paquete_hotel = PaqueteHotel.objects.create(
            paquete=paquete,
            hotel=hotel,
            noches=noches,
            tipo_habitacion_incluida=tipo_habitacion_incluida,
            regimen_alimenticio=regimen_alimenticio
        )
        
        serializer = PaqueteHotelSerializer(paquete_hotel)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def agregar_servicio(self, request, pk=None):
        paquete = self.get_object()
        tipo = request.data.get('tipo')
        nombre = request.data.get('nombre')
        descripcion = request.data.get('descripcion', '')
        incluido_en_precio = request.data.get('incluido_en_precio', True)
        costo_adicional = request.data.get('costo_adicional')
        
        if not tipo or not nombre:
            return Response(
                {'error': 'Debe proporcionar tipo y nombre'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        paquete_servicio = PaqueteServicio.objects.create(
            paquete=paquete,
            tipo=tipo,
            nombre=nombre,
            descripcion=descripcion,
            incluido_en_precio=incluido_en_precio,
            costo_adicional=costo_adicional
        )
        
        serializer = PaqueteServicioSerializer(paquete_servicio)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        tipo = request.query_params.get('tipo')
        empresa_id = request.query_params.get('empresa')
        
        if not tipo:
            return Response(
                {'error': 'Debe proporcionar el tipo'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(tipo=tipo)
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PaqueteListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PaqueteListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def promociones(self, request):
        empresa_id = request.query_params.get('empresa')
        queryset = self.queryset.filter(es_promocion=True, activo=True)
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PaqueteListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PaqueteListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        empresa_id = request.query_params.get('empresa')
        queryset = self.queryset
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        total_paquetes = queryset.count()
        paquetes_activos = queryset.filter(activo=True).count()
        paquetes_promocion = queryset.filter(es_promocion=True).count()
        
        # Estadísticas por tipo
        stats_tipo = {}
        for choice in PaqueteTuristico.TIPO_PAQUETE_CHOICES:
            tipo_id = choice[0]
            tipo_nombre = choice[1]
            count = queryset.filter(tipo=tipo_id).count()
            stats_tipo[tipo_nombre] = count
        
        return Response({
            'total_paquetes': total_paquetes,
            'paquetes_activos': paquetes_activos,
            'paquetes_promocion': paquetes_promocion,
            'porcentaje_activos': round((paquetes_activos / total_paquetes * 100) if total_paquetes > 0 else 0, 2),
            'porcentaje_promocion': round((paquetes_promocion / total_paquetes * 100) if total_paquetes > 0 else 0, 2),
            'estadisticas_tipo': stats_tipo,
        })

class PaqueteHotelViewSet(viewsets.ModelViewSet):
    queryset = PaqueteHotel.objects.all()
    serializer_class = PaqueteHotelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['paquete', 'hotel']
    ordering_fields = ['noches', 'creado_en']

class PaqueteServicioViewSet(viewsets.ModelViewSet):
    queryset = PaqueteServicio.objects.all()
    serializer_class = PaqueteServicioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['paquete', 'tipo', 'incluido_en_precio']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['tipo', 'nombre', 'creado_en']
