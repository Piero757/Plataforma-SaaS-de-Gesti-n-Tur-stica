from rest_framework import serializers
from .models import Reporte, ReporteProgramado, MetricaReporte, DashboardConfiguracion

class MetricaReporteSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    
    class Meta:
        model = MetricaReporte
        fields = '__all__'
        read_only_fields = ['id', 'fecha_actualizacion']

class DashboardConfiguracionSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    nombre_creador = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    
    class Meta:
        model = DashboardConfiguracion
        fields = '__all__'
        read_only_fields = ['id', 'creado_en', 'actualizado_en']

class ReporteProgramadoSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    tipo_reporte_display = serializers.CharField(source='get_tipo_reporte_display', read_only=True)
    frecuencia_display = serializers.CharField(source='get_frecuencia_display', read_only=True)
    nombre_creador = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    email_destinatarios_list = serializers.SerializerMethodField()
    
    class Meta:
        model = ReporteProgramado
        fields = '__all__'
        read_only_fields = ['id', 'ultima_ejecucion', 'proxima_ejecucion', 
                           'creado_en', 'actualizado_en']

    def get_email_destinatarios_list(self, obj):
        return obj.get_email_destinatarios_list()

class ReporteSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    tipo_reporte_display = serializers.CharField(source='get_tipo_reporte_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    nombre_solicitado_por = serializers.CharField(source='solicitado_por.get_full_name', read_only=True)
    
    class Meta:
        model = Reporte
        fields = '__all__'
        read_only_fields = ['id', 'fecha_solicitud', 'fecha_generacion']

class ReporteListSerializer(serializers.ModelSerializer):
    tipo_reporte_display = serializers.CharField(source='get_tipo_reporte_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    nombre_solicitado_por = serializers.CharField(source='solicitado_por.get_full_name', read_only=True)
    
    class Meta:
        model = Reporte
        fields = ['id', 'nombre', 'tipo_reporte', 'tipo_reporte_display', 
                 'fecha_inicio', 'fecha_fin', 'estado', 'estado_display', 
                 'registros_totales', 'tiempo_generacion', 'nombre_solicitado_por', 
                 'fecha_solicitud', 'fecha_generacion']

class ReporteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = ['empresa', 'tipo_reporte', 'nombre', 'descripcion', 
                 'fecha_inicio', 'fecha_fin', 'parametros']

class ReporteProgramadoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteProgramado
        fields = ['empresa', 'tipo_reporte', 'nombre', 'descripcion', 
                 'frecuencia', 'dia_ejecucion', 'hora_ejecucion', 'parametros', 
                 'email_destinatarios', 'publico']
