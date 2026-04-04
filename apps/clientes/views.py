from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Empresa, Usuario, Cliente
from .serializers import (
    EmpresaSerializer, UsuarioSerializer, ClienteSerializer,
    ClienteListSerializer, ClienteCreateSerializer
)

class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'ruc', 'email']
    ordering_fields = ['nombre', 'creado_en']

    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        empresa = self.get_object()
        total_clientes = Cliente.objects.filter(empresa=empresa).count()
        total_usuarios = Usuario.objects.filter(empresa=empresa).count()
        
        return Response({
            'total_clientes': total_clientes,
            'total_usuarios': total_usuarios,
        })

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'rol', 'is_active']
    search_fields = ['username', 'nombres', 'apellidos', 'email']
    ordering_fields = ['username', 'creado_en']

    @action(detail=True, methods=['post'])
    def cambiar_password(self, request, pk=None):
        usuario = self.get_object()
        nueva_password = request.data.get('password')
        
        if not nueva_password:
            return Response(
                {'error': 'Debe proporcionar una nueva contraseña'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuario.set_password(nueva_password)
        usuario.save()
        
        return Response({'message': 'Contraseña actualizada correctamente'})

    @action(detail=True, methods=['post'])
    def activar_desactivar(self, request, pk=None):
        usuario = self.get_object()
        usuario.is_active = not usuario.is_active
        usuario.save()
        
        estado = 'activado' if usuario.is_active else 'desactivado'
        return Response({'message': f'Usuario {estado} correctamente'})

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'tipo_documento', 'vip', 'activo']
    search_fields = ['nombres', 'apellidos', 'numero_documento', 'email', 'telefono']
    ordering_fields = ['apellidos', 'nombres', 'creado_en']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClienteListSerializer
        elif self.action == 'create':
            return ClienteCreateSerializer
        return ClienteSerializer

    @action(detail=True, methods=['get'])
    def historial_reservas(self, request, pk=None):
        cliente = self.get_object()
        from apps.reservas.models import Reserva
        
        reservas = Reserva.objects.filter(cliente=cliente).order_by('-creado_en')
        from apps.reservas.serializers import ReservaListSerializer
        serializer = ReservaListSerializer(reservas, many=True)
        
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def marcar_vip(self, request, pk=None):
        cliente = self.get_object()
        cliente.vip = not cliente.vip
        cliente.save()
        
        estado = 'marcado como VIP' if cliente.vip else 'desmarcado como VIP'
        return Response({
            'message': f'Cliente {estado} correctamente',
            'vip': cliente.vip
        })

    @action(detail=True, methods=['post'])
    def activar_desactivar(self, request, pk=None):
        cliente = self.get_object()
        cliente.activo = not cliente.activo
        cliente.save()
        
        estado = 'activado' if cliente.activo else 'desactivado'
        return Response({'message': f'Cliente {estado} correctamente'})

    @action(detail=False, methods=['get'])
    def buscar_por_documento(self, request):
        numero_documento = request.query_params.get('documento')
        empresa_id = request.query_params.get('empresa')
        
        if not numero_documento:
            return Response(
                {'error': 'Debe proporcionar el número de documento'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        try:
            cliente = queryset.get(numero_documento=numero_documento)
            serializer = self.get_serializer(cliente)
            return Response(serializer.data)
        except Cliente.DoesNotExist:
            return Response(
                {'error': 'Cliente no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def vip_list(self, request):
        empresa_id = request.query_params.get('empresa')
        queryset = self.queryset.filter(vip=True)
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ClienteListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ClienteListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        empresa_id = request.query_params.get('empresa')
        queryset = self.queryset
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        total_clientes = queryset.count()
        clientes_vip = queryset.filter(vip=True).count()
        clientes_activos = queryset.filter(activo=True).count()
        
        return Response({
            'total_clientes': total_clientes,
            'clientes_vip': clientes_vip,
            'clientes_activos': clientes_activos,
            'porcentaje_vip': round((clientes_vip / total_clientes * 100) if total_clientes > 0 else 0, 2),
            'porcentaje_activos': round((clientes_activos / total_clientes * 100) if total_clientes > 0 else 0, 2),
        })
