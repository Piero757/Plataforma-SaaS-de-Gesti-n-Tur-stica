from rest_framework import serializers
from .models import EstadisticaGeneral, MetricaTiempoReal, AlertaDashboard, WidgetDashboard

class WidgetDashboardSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    tipo_widget_display = serializers.CharField(source='get_tipo_widget_display', read_only=True)
    nombre_creador = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    
    class Meta:
        model = WidgetDashboard
        fields = '__all__'
        read_only_fields = ['id', 'creado_en', 'actualizado_en']

class AlertaDashboardSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    tipo_alerta_display = serializers.CharField(source='get_tipo_alerta_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    
    class Meta:
        model = AlertaDashboard
        fields = '__all__'
        read_only_fields = ['id', 'creado_en']

class MetricaTiempoRealSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    tipo_metrica_display = serializers.CharField(source='get_tipo_metrica_display', read_only=True)
    
    class Meta:
        model = MetricaTiempoReal
        fields = '__all__'
        read_only_fields = ['id', 'ultima_actualizacion']

class EstadisticaGeneralSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.CharField(source='empresa.nombre', read_only=True)
    
    class Meta:
        model = EstadisticaGeneral
        fields = '__all__'
        read_only_fields = ['id', 'creado_en']

class DashboardDataSerializer(serializers.Serializer):
    estadisticas_generales = EstadisticaGeneralSerializer(many=True, read_only=True)
    metricas_tiempo_real = MetricaTiempoRealSerializer(many=True, read_only=True)
    alertas = AlertaDashboardSerializer(many=True, read_only=True)
    widgets = WidgetDashboardSerializer(many=True, read_only=True)
    
    class Meta:
        fields = ['estadisticas_generales', 'metricas_tiempo_real', 'alertas', 'widgets']

class MetricaActualizacionSerializer(serializers.Serializer):
    empresa_id = serializers.UUIDField()
    
    class Meta:
        fields = ['empresa_id']

class AlertaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertaDashboard
        fields = ['empresa', 'titulo', 'mensaje', 'tipo_alerta', 'prioridad', 
                 'accion_requerida', 'url_accion', 'fecha_expiracion']

class WidgetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WidgetDashboard
        fields = ['empresa', 'nombre', 'tipo_widget', 'posicion_x', 'posicion_y', 
                 'ancho', 'alto', 'configuracion', 'datos', 'refresco_automatico', 
                 'intervalo_refresco']
