import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clientes.models import Empresa, Usuario

def crear_superusuario():
    """Crear superusuario Piero con contraseña piero12345"""
    
    # Crear empresa por defecto si no existe
    empresa, created = Empresa.objects.get_or_create(
        ruc='20123456789',
        defaults={
            'nombre': 'Empresa Demo',
            'direccion': 'Av. Principal 123, Lima, Perú',
            'telefono': '+51 1 2345678',
            'email': 'info@empresademo.com',
            'activo': True
        }
    )
    
    if created:
        print(f"Empresa '{empresa.nombre}' creada exitosamente")
    else:
        print(f"Empresa '{empresa.nombre}' ya existe")
    
    # Crear superusuario Piero
    try:
        usuario = Usuario.objects.create_superuser(
            username='piero',
            email='piero@turismo.com',
            password='piero12345',
            empresa=empresa,
            nombres='Piero',
            apellidos='Administrador',
            rol='admin'
        )
        print(f"Superusuario '{usuario.username}' creado exitosamente")
        print(f"Email: {usuario.email}")
        print(f"Contraseña: piero12345")
        print(f"Empresa: {empresa.nombre}")
    except Exception as e:
        if "already exists" in str(e):
            print(f"El usuario 'piero' ya existe")
        else:
            print(f"Error al crear superusuario: {e}")

if __name__ == '__main__':
    crear_superusuario()
