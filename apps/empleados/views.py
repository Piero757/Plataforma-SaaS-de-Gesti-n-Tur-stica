from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Q
from django.utils import timezone

from .models import Empleado, HorarioEmpleado, AsistenciaEmpleado, PermisoEmpleado
from .serializers import (
    EmpleadoSerializer, EmpleadoListSerializer, EmpleadoCreateSerializer,
    HorarioEmpleadoSerializer, AsistenciaEmpleadoSerializer, PermisoEmpleadoSerializer
)

class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'cargo', 'departamento', 'turno', 'estado']
    search_fields = ['nombres', 'apellidos', 'numero_documento', 'email', 'codigo_empleado']
    ordering_fields = ['apellidos', 'nombres', 'fecha_contratacion', 'creado_en']

    def get_serializer_class(self):
        if self.action == 'list':
            return EmpleadoListSerializer
        elif self.action == 'create':
            return EmpleadoCreateSerializer
        return EmpleadoSerializer

    @action(detail=True, methods=['post'])
    def activar_desactivar(self, request, pk=None):
        empleado = self.get_object()
        empleado.estado = 'activo' if empleado.estado != 'activo' else 'inactivo'
        empleado.save()
        
        estado = 'activado' if empleado.estado == 'activo' else 'desactivado'
        return Response({'message': f'Empleado {estado} correctamente'})

    @action(detail=True, methods=['post'])
    def asignar_usuario_sistema(self, request, pk=None):
        empleado = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'Debe proporcionar el ID del usuario'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(id=user_id)
            empleado.usuario_sistema = user
            empleado.save()
            
            return Response({
                'message': 'Usuario asignado correctamente',
                'usuario': user.username
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def registrar_asistencia(self, request, pk=None):
        empleado = self.get_object()
        fecha = request.data.get('fecha', timezone.now().date())
        hora_entrada = request.data.get('hora_entrada')
        hora_salida = request.data.get('hora_salida')
        estado = request.data.get('estado', 'presente')
        observaciones = request.data.get('observaciones', '')
        
        # Verificar si ya existe registro para esta fecha
        asistencia_existente = AsistenciaEmpleado.objects.filter(
            empleado=empleado,
            fecha=fecha
        ).first()
        
        if asistencia_existente:
            return Response(
                {'error': 'Ya existe un registro de asistencia para esta fecha'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        asistencia = AsistenciaEmpleado.objects.create(
            empleado=empleado,
            fecha=fecha,
            hora_entrada=hora_entrada,
            hora_salida=hora_salida,
            estado=estado,
            observaciones=observaciones,
            registrado_por=request.user
        )
        
        serializer = AsistenciaEmpleadoSerializer(asistencia)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def historial_asistencia(self, request, pk=None):
        empleado = self.get_object()
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        queryset = empleado.asistencias.all()
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AsistenciaEmpleadoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = AsistenciaEmpleadoSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def solicitar_permiso(self, request, pk=None):
        empleado = self.get_object()
        tipo_permiso = request.data.get('tipo_permiso')
        fecha_inicio = request.data.get('fecha_inicio')
        fecha_fin = request.data.get('fecha_fin')
        motivo = request.data.get('motivo')
        
        if not all([tipo_permiso, fecha_inicio, fecha_fin, motivo]):
            return Response(
                {'error': 'Debe proporcionar todos los campos requeridos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calcular días solicitados
        from datetime import datetime
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        dias_solicitados = (fecha_fin_dt - fecha_inicio_dt).days + 1
        
        permiso = PermisoEmpleado.objects.create(
            empleado=empleado,
            tipo_permiso=tipo_permiso,
            fecha_inicio=fecha_inicio_dt,
            fecha_fin=fecha_fin_dt,
            dias_solicitados=dias_solicitados,
            motivo=motivo
        )
        
        serializer = PermisoEmpleadoSerializer(permiso)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def permisos(self, request, pk=None):
        empleado = self.get_object()
        queryset = empleado.permisos.all()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PermisoEmpleadoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PermisoEmpleadoSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_cargo(self, request):
        cargo = request.query_params.get('cargo')
        empresa_id = request.query_params.get('empresa')
        
        if not cargo:
            return Response(
                {'error': 'Debe proporcionar el cargo'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(cargo=cargo)
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EmpleadoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EmpleadoListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def activos(self, request):
        empresa_id = request.query_params.get('empresa')
        queryset = self.queryset.filter(estado='activo')
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EmpleadoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EmpleadoListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        empresa_id = request.query_params.get('empresa')
        queryset = self.queryset
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        total_empleados = queryset.count()
        empleados_activos = queryset.filter(estado='activo').count()
        empleados_vacaciones = queryset.filter(estado='vacaciones').count()
        empleados_licencia = queryset.filter(estado='licencia').count()
        
        # Estadísticas por cargo
        stats_cargo = {}
        for choice in Empleado.CARGO_CHOICES:
            cargo_id = choice[0]
            cargo_nombre = choice[1]
            count = queryset.filter(cargo=cargo_id).count()
            stats_cargo[cargo_nombre] = count
        
        # Estadísticas por departamento
        stats_departamento = {}
        departamentos = queryset.values_list('departamento', flat=True).distinct()
        for depto in departamentos:
            if depto:
                count = queryset.filter(departamento=depto).count()
                stats_departamento[depto] = count
        
        return Response({
            'total_empleados': total_empleados,
            'empleados_activos': empleados_activos,
            'empleados_vacaciones': empleados_vacaciones,
            'empleados_licencia': empleados_licencia,
            'tasa_actividad': round((empleados_activos / total_empleados * 100) if total_empleados > 0 else 0, 2),
            'estadisticas_cargo': stats_cargo,
            'estadisticas_departamento': stats_departamento,
        })

class HorarioEmpleadoViewSet(viewsets.ModelViewSet):
    queryset = HorarioEmpleado.objects.all()
    serializer_class = HorarioEmpleadoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['empleado', 'dia_semana', 'activo']
    ordering_fields = ['dia_semana', 'hora_entrada']

class AsistenciaEmpleadoViewSet(viewsets.ModelViewSet):
    queryset = AsistenciaEmpleado.objects.all()
    serializer_class = AsistenciaEmpleadoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empleado', 'estado', 'fecha']
    search_fields = ['empleado__nombres', 'empleado__apellidos', 'observaciones']
    ordering_fields = ['fecha', 'hora_entrada']

class PermisoEmpleadoViewSet(viewsets.ModelViewSet):
    queryset = PermisoEmpleado.objects.all()
    serializer_class = PermisoEmpleadoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empleado', 'tipo_permiso', 'estado', 'fecha_inicio', 'fecha_fin']
    search_fields = ['empleado__nombres', 'empleado__apellidos', 'motivo']
    ordering_fields = ['fecha_inicio', 'fecha_solicitud']

    @action(detail=True, methods=['post'])
    def aprobar_permiso(self, request, pk=None):
        permiso = self.get_object()
        
        if permiso.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden aprobar permisos pendientes'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        permiso.estado = 'aprobado'
        permiso.aprobado_por = request.user
        permiso.fecha_aprobacion = timezone.now()
        permiso.save()
        
        return Response({
            'message': 'Permiso aprobado correctamente',
            'estado': permiso.estado,
            'fecha_aprobacion': permiso.fecha_aprobacion
        })

    @action(detail=True, methods=['post'])
    def rechazar_permiso(self, request, pk=None):
        permiso = self.get_object()
        motivo = request.data.get('motivo')
        
        if permiso.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden rechazar permisos pendientes'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        permiso.estado = 'rechazado'
        permiso.aprobado_por = request.user
        permiso.fecha_aprobacion = timezone.now()
        if motivo:
            permiso.notas += f"\n\nRECHAZO: {motivo}"
        permiso.save()
        
        return Response({
            'message': 'Permiso rechazado correctamente',
            'estado': permiso.estado
        })
