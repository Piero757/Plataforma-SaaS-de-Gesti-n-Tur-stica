from .models import ConfiguracionEmpresa

def empresa_config(request):
    try:
        config = ConfiguracionEmpresa.objects.get(id=1)
    except ConfiguracionEmpresa.DoesNotExist:
        config = None
    return {
        'empresa_config': config
    }
