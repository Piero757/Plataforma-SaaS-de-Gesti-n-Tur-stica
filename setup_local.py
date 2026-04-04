#!/usr/bin/env python
"""
Script de configuración para desarrollo local
Este script configura todo lo necesario para correr el sistema localmente
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completado exitosamente")
            if result.stdout:
                print(f"   Salida: {result.stdout.strip()}")
        else:
            print(f"❌ Error en {description}")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando {description}: {e}")
        return False
    return True

def check_python_version():
    """Verifica la versión de Python"""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} es compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} no es compatible. Se requiere Python 3.8+")
        return False

def check_requirements():
    """Verifica si requirements.txt existe"""
    if os.path.exists('requirements.txt'):
        print("✅ requirements.txt encontrado")
        return True
    else:
        print("❌ requirements.txt no encontrado")
        return False

def check_env_file():
    """Verifica si .env existe"""
    if os.path.exists('.env'):
        print("✅ Archivo .env encontrado")
        return True
    else:
        print("⚠️  Archivo .env no encontrado, creando uno por defecto...")
        create_default_env()
        return True

def create_default_env():
    """Crea un archivo .env por defecto"""
    env_content = """# Configuración de la Base de Datos
DB_NAME=turismo_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Configuración de Django
SECRET_KEY=django-insecure-tu-secret-key-aqui-cambiar-en-produccion
DEBUG=True

# Configuración de Redis (para Celery)
REDIS_URL=redis://localhost:6379/0
"""
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ Archivo .env creado con configuración por defecto")
    print("⚠️  Por favor, ajusta las variables en el archivo .env según tu configuración")

def setup_django():
    """Configura Django"""
    print("🔧 Configurando Django...")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        print("✅ Django configurado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error configurando Django: {e}")
        return False

def create_superuser():
    """Crea el superusuario Piero"""
    print("👤 Creando superusuario...")
    try:
        from apps.clientes.models import Empresa, Usuario
        
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
            print("✅ Empresa demo creada")
        else:
            print("✅ Empresa demo ya existe")
        
        # Crear superusuario
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
            print("✅ Superusuario 'piero' creado exitosamente")
            print("   Usuario: piero")
            print("   Contraseña: piero12345")
        except Exception as e:
            if "already exists" in str(e):
                print("✅ Superusuario 'piero' ya existe")
            else:
                print(f"❌ Error creando superusuario: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error en setup de superusuario: {e}")
        return False

def create_sample_data():
    """Crea datos de ejemplo"""
    print("📊 Creando datos de ejemplo...")
    try:
        from apps.hoteles.models import Hotel, Habitacion, TipoHabitacion
        from apps.clientes.models import Cliente
        
        # Crear tipo de habitación
        tipo_hab, created = TipoHabitacion.objects.get_or_create(
            nombre="Suite Deluxe",
            defaults={
                'descripcion': 'Habitación de lujo con vista al mar',
                'capacidad_maxima': 4,
                'capacidad_adultos': 2,
                'capacidad_ninos': 2
            }
        )
        
        # Crear hotel
        hotel, created = Hotel.objects.get_or_create(
            nombre="Hotel Paradise Lima",
            defaults={
                'empresa_id': 1,  # Asumimos que la empresa demo tiene ID 1
                'categoria': 5,
                'descripcion': 'Hotel de 5 estrellas en el corazón de Lima',
                'direccion': 'Av. Larco 123, Miraflores',
                'ciudad': 'Lima',
                'país': 'Perú',
                'telefono': '+51 1 2345678',
                'email': 'info@paradise.com',
                'check_in_time': '15:00',
                'check_out_time': '11:00',
                'activo': True
            }
        )
        
        # Crear habitación
        habitacion, created = Habitacion.objects.get_or_create(
            numero="101",
            defaults={
                'hotel': hotel,
                'tipo': tipo_hab,
                'piso': "1",
                'estado': 'disponible',
                'precio_base': 350.00,
                'precio_temporada_alta': 450.00,
                'metros_cuadrados': 45,
                'tiene_vista': True,
                'tiene_balcon': True,
                'activa': True
            }
        )
        
        # Crear cliente de ejemplo
        cliente, created = Cliente.objects.get_or_create(
            numero_documento="12345678",
            defaults={
                'empresa_id': 1,
                'nombres': 'Juan',
                'apellidos': 'Pérez',
                'tipo_documento': 'DNI',
                'telefono': '+51 1 987654321',
                'email': 'juan.perez@email.com',
                'activo': True
            }
        )
        
        print("✅ Datos de ejemplo creados exitosamente")
        print("   - Hotel: Hotel Paradise Lima")
        print("   - Habitación: 101 (Suite Deluxe)")
        print("   - Cliente: Juan Pérez")
        
        return True
    except Exception as e:
        print(f"❌ Error creando datos de ejemplo: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando configuración del Sistema de Gestión Turística")
    print("=" * 60)
    
    # Verificaciones iniciales
    if not check_python_version():
        return False
    
    if not check_requirements():
        return False
    
    if not check_env_file():
        return False
    
    # Configurar Django
    if not setup_django():
        return False
    
    # Ejecutar migraciones
    print("\n🔧 Ejecutando migraciones de la base de datos...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migraciones completadas exitosamente")
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return False
    
    # Crear superusuario
    if not create_superuser():
        return False
    
    # Crear datos de ejemplo
    if not create_sample_data():
        return False
    
    # Recolectar archivos estáticos
    print("\n🔧 Recolectando archivos estáticos...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Archivos estáticos recolectados")
    except Exception as e:
        print(f"❌ Error recolectando archivos estáticos: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ¡Configuración completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Asegúrate de que PostgreSQL esté corriendo")
    print("2. Crea la base de datos 'turismo_db' en PostgreSQL")
    print("3. Ajusta las variables en el archivo .env si es necesario")
    print("4. Inicia el servidor con: python manage.py runserver")
    print("\n🌐 Accesos:")
    print("   - Dashboard: http://localhost:8000/")
    print("   - Panel Admin: http://localhost:8000/admin/")
    print("   - API Health: http://localhost:8000/api/health/")
    print("\n👤 Credenciales de acceso:")
    print("   - Usuario: piero")
    print("   - Contraseña: piero12345")
    print("\n📚 Para más información, consulta el README.md")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
