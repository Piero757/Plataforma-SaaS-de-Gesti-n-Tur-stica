from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Hotel, HotelImagen
from .serializers import (
    HotelSerializer, HotelListSerializer, HotelCreateSerializer,
    HotelImagenSerializer
)

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'categoria', 'ciudad', 'pais', 'activo']
    search_fields = ['nombre', 'descripcion', 'direccion', 'ciudad']
    ordering_fields = ['nombre', 'categoria', 'creado_en']

    def get_serializer_class(self):
        if self.action == 'list':
            return HotelListSerializer
        elif self.action == 'create':
            return HotelCreateSerializer
        return HotelSerializer

    @action(detail=True, methods=['get'])
    def habitaciones(self, request, pk=None):
        hotel = self.get_object()
        from apps.habitaciones.models import Habitacion
        from apps.habitaciones.serializers import HabitacionListSerializer
        
        habitaciones = Habitacion.objects.filter(hotel=hotel)
        serializer = HabitacionListSerializer(habitaciones, many=True)
        
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def disponibilidad(self, request, pk=None):
        hotel = self.get_object()
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return Response(
                {'error': 'Debe proporcionar fecha_inicio y fecha_fin'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.habitaciones.models import Habitacion
        from apps.reservas.models import ReservaHabitacion
        
        # Obtener todas las habitaciones del hotel
        todas_habitaciones = Habitacion.objects.filter(hotel=hotel, activa=True)
        
        # Obtener habitaciones ocupadas en el rango de fechas
        habitaciones_ocupadas = ReservaHabitacion.objects.filter(
            habitacion__hotel=hotel,
            fecha_checkin__lt=fecha_fin,
            fecha_checkout__gt=fecha_inicio
        ).values_list('habitacion_id', flat=True)
        
        # Habitaciones disponibles
        habitaciones_disponibles = todas_habitaciones.exclude(
            id__in=habitaciones_ocupadas
        )
        
        from apps.habitaciones.serializers import HabitacionListSerializer
        serializer = HabitacionListSerializer(habitaciones_disponibles, many=True)
        
        return Response({
            'total_habitaciones': todas_habitaciones.count(),
            'habitaciones_ocupadas': len(habitaciones_ocupadas),
            'habitaciones_disponibles': habitaciones_disponibles.count(),
            'disponibles': serializer.data
        })

    @action(detail=True, methods=['post'])
    def activar_desactivar(self, request, pk=None):
        hotel = self.get_object()
        hotel.activo = not hotel.activo
        hotel.save()
        
        estado = 'activado' if hotel.activo else 'desactivado'
        return Response({'message': f'Hotel {estado} correctamente'})

    @action(detail=True, methods=['post'])
    def agregar_imagen(self, request, pk=None):
        hotel = self.get_object()
        imagen = request.FILES.get('imagen')
        descripcion = request.data.get('descripcion', '')
        orden = request.data.get('orden', 0)
        
        if not imagen:
            return Response(
                {'error': 'Debe proporcionar una imagen'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        hotel_imagen = HotelImagen.objects.create(
            hotel=hotel,
            imagen=imagen,
            descripcion=descripcion,
            orden=orden
        )
        
        serializer = HotelImagenSerializer(hotel_imagen)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def eliminar_imagen(self, request, pk=None):
        hotel = self.get_object()
        imagen_id = request.data.get('imagen_id')
        
        if not imagen_id:
            return Response(
                {'error': 'Debe proporcionar el ID de la imagen'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            imagen = HotelImagen.objects.get(id=imagen_id, hotel=hotel)
            imagen.imagen.delete()
            imagen.delete()
            return Response({'message': 'Imagen eliminada correctamente'})
        except HotelImagen.DoesNotExist:
            return Response(
                {'error': 'Imagen no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def por_ciudad(self, request):
        ciudad = request.query_params.get('ciudad')
        empresa_id = request.query_params.get('empresa')
        
        if not ciudad:
            return Response(
                {'error': 'Debe proporcionar la ciudad'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(ciudad__icontains=ciudad)
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = HotelListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = HotelListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        empresa_id = request.query_params.get('empresa')
        queryset = self.queryset
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        total_hoteles = queryset.count()
        hoteles_activos = queryset.filter(activo=True).count()
        
        # Estadísticas por categoría
        stats_categoria = {}
        for choice in Hotel.CATEGORIA_CHOICES:
            categoria_id = choice[0]
            categoria_nombre = choice[1]
            count = queryset.filter(categoria=categoria_id).count()
            stats_categoria[categoria_nombre] = count
        
        return Response({
            'total_hoteles': total_hoteles,
            'hoteles_activos': hoteles_activos,
            'porcentaje_activos': round((hoteles_activos / total_hoteles * 100) if total_hoteles > 0 else 0, 2),
            'estadisticas_categoria': stats_categoria,
        })

class HotelImagenViewSet(viewsets.ModelViewSet):
    queryset = HotelImagen.objects.all()
    serializer_class = HotelImagenSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['hotel']
    ordering_fields = ['orden', 'creado_en']
