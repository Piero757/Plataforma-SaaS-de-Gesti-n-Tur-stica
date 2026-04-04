from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import TipoHabitacion, Habitacion, HabitacionImagen
from .serializers import (
    TipoHabitacionSerializer, HabitacionSerializer, HabitacionListSerializer,
    HabitacionCreateSerializer, HabitacionImagenSerializer
)

class TipoHabitacionViewSet(viewsets.ModelViewSet):
    queryset = TipoHabitacion.objects.all()
    serializer_class = TipoHabitacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'creado_en']

class HabitacionViewSet(viewsets.ModelViewSet):
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hotel', 'tipo', 'estado', 'activa', 'tiene_vista', 'tiene_balcon']
    search_fields = ['numero', 'descripcion', 'servicios']
    ordering_fields = ['hotel', 'piso', 'numero', 'precio_base']

    def get_serializer_class(self):
        if self.action == 'list':
            return HabitacionListSerializer
        elif self.action == 'create':
            return HabitacionCreateSerializer
        return HabitacionSerializer

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        habitacion = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado not in dict(Habitacion.ESTADO_CHOICES):
            return Response(
                {'error': 'Estado no válido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        habitacion.estado = nuevo_estado
        habitacion.save()
        
        return Response({
            'message': f'Estado cambiado a {habitacion.get_estado_display()} correctamente',
            'estado': habitacion.estado,
            'estado_display': habitacion.get_estado_display()
        })

    @action(detail=True, methods=['post'])
    def activar_desactivar(self, request, pk=None):
        habitacion = self.get_object()
        habitacion.activa = not habitacion.activa
        habitacion.save()
        
        estado = 'activada' if habitacion.activa else 'desactivada'
        return Response({'message': f'Habitación {estado} correctamente'})

    @action(detail=True, methods=['get'])
    def disponibilidad(self, request, pk=None):
        habitacion = self.get_object()
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return Response(
                {'error': 'Debe proporcionar fecha_inicio y fecha_fin'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.reservas.models import ReservaHabitacion
        
        # Verificar si la habitación está ocupada en el rango de fechas
        reservas_solapadas = ReservaHabitacion.objects.filter(
            habitacion=habitacion,
            fecha_checkin__lt=fecha_fin,
            fecha_checkout__gt=fecha_inicio
        ).exists()
        
        disponible = not reservas_solapadas and habitacion.estado == 'disponible'
        
        return Response({
            'disponible': disponible,
            'estado_actual': habitacion.estado,
            'estado_display': habitacion.get_estado_display(),
            'precio_actual': habitacion.get_precio_actual(),
        })

    @action(detail=True, methods=['post'])
    def agregar_imagen(self, request, pk=None):
        habitacion = self.get_object()
        imagen = request.FILES.get('imagen')
        descripcion = request.data.get('descripcion', '')
        orden = request.data.get('orden', 0)
        
        if not imagen:
            return Response(
                {'error': 'Debe proporcionar una imagen'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        habitacion_imagen = HabitacionImagen.objects.create(
            habitacion=habitacion,
            imagen=imagen,
            descripcion=descripcion,
            orden=orden
        )
        
        serializer = HabitacionImagenSerializer(habitacion_imagen)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def eliminar_imagen(self, request, pk=None):
        habitacion = self.get_object()
        imagen_id = request.data.get('imagen_id')
        
        if not imagen_id:
            return Response(
                {'error': 'Debe proporcionar el ID de la imagen'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            imagen = HabitacionImagen.objects.get(id=imagen_id, habitacion=habitacion)
            imagen.imagen.delete()
            imagen.delete()
            return Response({'message': 'Imagen eliminada correctamente'})
        except HabitacionImagen.DoesNotExist:
            return Response(
                {'error': 'Imagen no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        hotel_id = request.query_params.get('hotel')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        if not hotel_id or not fecha_inicio or not fecha_fin:
            return Response(
                {'error': 'Debe proporcionar hotel, fecha_inicio y fecha_fin'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.reservas.models import ReservaHabitacion
        
        # Obtener habitaciones disponibles del hotel
        queryset = self.queryset.filter(hotel_id=hotel_id, activa=True, estado='disponible')
        
        # Excluir habitaciones ocupadas en el rango de fechas
        habitaciones_ocupadas = ReservaHabitacion.objects.filter(
            habitacion__hotel_id=hotel_id,
            fecha_checkin__lt=fecha_fin,
            fecha_checkout__gt=fecha_inicio
        ).values_list('habitacion_id', flat=True)
        
        habitaciones_disponibles = queryset.exclude(id__in=habitaciones_ocupadas)
        
        page = self.paginate_queryset(habitaciones_disponibles)
        if page is not None:
            serializer = HabitacionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = HabitacionListSerializer(habitaciones_disponibles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        tipo_id = request.query_params.get('tipo')
        hotel_id = request.query_params.get('hotel')
        
        queryset = self.queryset.filter(tipo_id=tipo_id)
        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = HabitacionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = HabitacionListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        hotel_id = request.query_params.get('hotel')
        queryset = self.queryset
        
        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)
        
        total_habitaciones = queryset.count()
        habitaciones_activas = queryset.filter(activa=True).count()
        habitaciones_disponibles = queryset.filter(estado='disponible').count()
        habitaciones_ocupadas = queryset.filter(estado='ocupada').count()
        habitaciones_mantenimiento = queryset.filter(estado='mantenimiento').count()
        
        # Estadísticas por tipo
        stats_tipo = {}
        for tipo in TipoHabitacion.objects.all():
            count = queryset.filter(tipo=tipo).count()
            stats_tipo[tipo.nombre] = count
        
        return Response({
            'total_habitaciones': total_habitaciones,
            'habitaciones_activas': habitaciones_activas,
            'habitaciones_disponibles': habitaciones_disponibles,
            'habitaciones_ocupadas': habitaciones_ocupadas,
            'habitaciones_mantenimiento': habitaciones_mantenimiento,
            'tasa_ocupacion': round((habitaciones_ocupadas / total_habitaciones * 100) if total_habitaciones > 0 else 0, 2),
            'estadisticas_tipo': stats_tipo,
        })

class HabitacionImagenViewSet(viewsets.ModelViewSet):
    queryset = HabitacionImagen.objects.all()
    serializer_class = HabitacionImagenSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['habitacion']
    ordering_fields = ['orden', 'creado_en']
