from rest_framework import serializers
from .models import Empleado, HorarioEmpleado, AsistenciaEmpleado, PermisoEmpleado

class HorarioEmpleadoSerializer(serializers.ModelSerializer):
    dia_semana_display = serializers.CharField(source='get_dia_semana_display', read_only=True)
    
    class Meta:
        model = HorarioEmpleado
        fields = '__all__'
        read_only_fields = ['id', 'creado_en']

class AsistenciaEmpleadoSerializer(serializers.ModelSerializer):
    nombre_empleado = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    nombre_registrado_por = serializers.CharField(source='registrado_por.get_full_name', read_only=True)
    
    class Meta:
        model = AsistenciaEmpleado
        fields = '__all__'
        read_only_fields = ['id', 'creado_en']

class PermisoEmpleadoSerializer(serializers.ModelSerializer):
    nombre_empleado = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    tipo_permiso_display = serializers.CharField(source='get_tipo_permiso_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    nombre_aprobado_por = serializers.CharField(source='aprobado_por.get_full_name', read_only=True)
    
    class Meta:
        model = PermisoEmpleado
        fields = '__all__'
        read_only_fields = ['id', 'fecha_solicitud', 'fecha_aprobacion', 'actualizado_en']

class EmpleadoSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    cargo_display = serializers.CharField(source='get_cargo_display', read_only=True)
    turno_display = serializers.CharField(source='get_turno_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_contrato_display = serializers.CharField(source='get_tipo_contrato_display', read_only=True)
    nombre_completo = serializers.ReadOnlyField()
    edad = serializers.ReadOnlyField()
    habilidades_list = serializers.SerializerMethodField()
    idiomas_list = serializers.SerializerMethodField()
    horarios = HorarioEmpleadoSerializer(many=True, read_only=True)
    asistencias = AsistenciaEmpleadoSerializer(many=True, read_only=True)
    permisos = PermisoEmpleadoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Empleado
        fields = '__all__'
        read_only_fields = ['id', 'codigo_empleado', 'creado_en', 'actualizado_en']

    def get_habilidades_list(self, obj):
        return obj.get_habilidades_list()

    def get_idiomas_list(self, obj):
        return obj.get_idiomas_list()

class EmpleadoListSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()
    cargo_display = serializers.CharField(source='get_cargo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Empleado
        fields = ['id', 'codigo_empleado', 'nombre_completo', 'cargo', 
                 'cargo_display', 'departamento', 'telefono', 'email', 
                 'estado', 'estado_display', 'fecha_contratacion']

class EmpleadoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = ['empresa', 'nombres', 'apellidos', 'tipo_documento', 
                 'numero_documento', 'fecha_nacimiento', 'telefono', 'email', 
                 'email_corporativo', 'direccion', 'cargo', 'departamento', 
                 'fecha_contratacion', 'tipo_contrato', 'salario', 'turno', 
                 'habilidades', 'certificaciones', 'idiomas', 'experiencia_previa', 
                 'contacto_emergencia_nombre', 'contacto_emergencia_telefono', 
                 'contacto_emergencia_parentesco']
