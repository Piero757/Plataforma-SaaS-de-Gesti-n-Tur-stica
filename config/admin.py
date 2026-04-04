from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

# Personalizar el título del admin
admin.site.site_header = 'Plataforma SaaS de Gestión Turística'
admin.site.site_title = 'Panel de Administración'
admin.site.index_title = 'Bienvenido al Sistema de Gestión Turística'

# Configuración personalizada del admin
class CustomAdminSite(admin.AdminSite):
    site_header = 'Plataforma SaaS de Gestión Turística'
    site_title = 'Panel de Administración'
    index_title = 'Bienvenido al Sistema de Gestión Turística'

# Usar el admin personalizado
# admin.site = CustomAdminSite()

# Registrar modelos personalizados si es necesario
from apps.clientes.models import Usuario
from apps.clientes.admin import UsuarioAdmin

# Reemplazar el UserAdmin estándar
admin.site.unregister(Usuario)
admin.site.register(Usuario, UsuarioAdmin)
