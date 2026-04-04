import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Iniciando seed de la base de datos...');

  // =====================
  // 1. PLANES DE SUSCRIPCIÓN
  // =====================
  const planBasico = await prisma.planSuscripcion.upsert({
    where: { nombre: 'Básico' },
    update: {},
    create: {
      nombre: 'Básico',
      descripcion: 'Ideal para pequeñas agencias y negocios que inician',
      precioMensual: 49.00,
      maxUsuarios: 5,
      maxReservasMes: 100,
      maxHoteles: 2,
      caracteristicas: [
        'Gestión de clientes',
        'Reservas de hotel',
        'Reportes básicos',
        'Soporte por email',
      ],
    },
  });

  const planProfesional = await prisma.planSuscripcion.upsert({
    where: { nombre: 'Profesional' },
    update: {},
    create: {
      nombre: 'Profesional',
      descripcion: 'Para agencias medianas con mayor volumen de reservas',
      precioMensual: 149.00,
      maxUsuarios: 20,
      maxReservasMes: 500,
      maxHoteles: 10,
      caracteristicas: [
        'Todo lo del plan Básico',
        'Paquetes turísticos',
        'Portal de reservas online',
        'Reportes avanzados',
        'Integración con Stripe',
        'Chat de soporte',
      ],
    },
  });

  const planEmpresarial = await prisma.planSuscripcion.upsert({
    where: { nombre: 'Empresarial' },
    update: {},
    create: {
      nombre: 'Empresarial',
      descripcion: 'Solución completa para grandes operadores turísticos',
      precioMensual: 399.00,
      maxUsuarios: null as any,  // ilimitado
      maxReservasMes: null as any,
      maxHoteles: null as any,
      caracteristicas: [
        'Todo lo del plan Profesional',
        'Usuarios ilimitados',
        'Hoteles y reservas ilimitados',
        'White-label (marca propia)',
        'API de integración',
        'Soporte dedicado 24/7',
        'Reportes personalizados',
      ],
    },
  });

  // =====================
  // 2. PERMISOS DEL SISTEMA
  // =====================
  const modulos = [
    'clientes', 'hoteles', 'habitaciones', 'reservas',
    'paquetes', 'pagos', 'empleados', 'usuarios',
    'roles', 'reportes', 'empresa', 'notificaciones', 'facturas'
  ];
  const acciones = ['crear', 'leer', 'actualizar', 'eliminar', 'exportar'];

  for (const modulo of modulos) {
    for (const accion of acciones) {
      await prisma.permiso.upsert({
        where: { modulo_accion: { modulo, accion } },
        update: {},
        create: { modulo, accion, descripcion: `Permiso para ${accion} ${modulo}` },
      });
    }
  }
  console.log('✅ Permisos creados');

  // =====================
  // 3. EMPRESA DEMO
  // =====================
  const empresaDemo = await prisma.empresa.upsert({
    where: { slug: 'demo-tours' },
    update: {},
    create: {
      nombre: 'Demo Tours & Hoteles',
      slug: 'demo-tours',
      email: 'admin@demotours.com',
      telefono: '+1 555-0100',
      direccion: 'Av. Principal 123',
      ciudad: 'Ciudad de México',
      pais: 'México',
    },
  });

  // =====================
  // 4. ROL ADMIN (demo)
  // =====================
  const rolAdmin = await prisma.rol.upsert({
    where: { empresaId_nombre: { empresaId: empresaDemo.id, nombre: 'admin' } },
    update: {},
    create: {
      empresaId: empresaDemo.id,
      nombre: 'admin',
      descripcion: 'Administrador con acceso completo',
      esSistema: true,
    },
  });

  // Asignar TODOS los permisos al admin
  const todosLosPermisos = await prisma.permiso.findMany();
  for (const permiso of todosLosPermisos) {
    await prisma.rolPermiso.upsert({
      where: { rolId_permisoId: { rolId: rolAdmin.id, permisoId: permiso.id } },
      update: {},
      create: { rolId: rolAdmin.id, permisoId: permiso.id },
    });
  }

  // Rol Recepcionista
  const rolRecepcionista = await prisma.rol.upsert({
    where: { empresaId_nombre: { empresaId: empresaDemo.id, nombre: 'recepcionista' } },
    update: {},
    create: {
      empresaId: empresaDemo.id,
      nombre: 'recepcionista',
      descripcion: 'Recepcionista con acceso a reservas y clientes',
      esSistema: true,
    },
  });

  // Rol Agente
  await prisma.rol.upsert({
    where: { empresaId_nombre: { empresaId: empresaDemo.id, nombre: 'agente' } },
    update: {},
    create: {
      empresaId: empresaDemo.id,
      nombre: 'agente',
      descripcion: 'Agente de viajes',
      esSistema: true,
    },
  });

  // =====================
  // 5. USUARIO ADMIN DEMO
  // =====================
  const passwordHash = await bcrypt.hash('Admin123!', 12);

  const usuarioAdmin = await prisma.usuario.upsert({
    where: { empresaId_email: { empresaId: empresaDemo.id, email: 'admin@demotours.com' } },
    update: {},
    create: {
      empresaId: empresaDemo.id,
      rolId: rolAdmin.id,
      nombre: 'Admin',
      email: 'admin@demotours.com',
      passwordHash,
    },
  });

  // Usuario Recepcionista
  const hashRecep = await bcrypt.hash('Recep123!', 12);
  await prisma.usuario.upsert({
    where: { empresaId_email: { empresaId: empresaDemo.id, email: 'recepcion@demotours.com' } },
    update: {},
    create: {
      empresaId: empresaDemo.id,
      rolId: rolRecepcionista.id,
      nombre: 'María López',
      email: 'recepcion@demotours.com',
      passwordHash: hashRecep,
    },
  });

  // =====================
  // 6. HOTEL DEMO
  // =====================
  const hotelDemo = await prisma.hotel.upsert({
    where: { id: 'hotel-demo-unique-id-001' },
    update: {},
    create: {
      id: 'hotel-demo-unique-id-001',
      empresaId: empresaDemo.id,
      nombre: 'Hotel Grand Plaza',
      descripcion: 'Hotel de lujo en el centro de la ciudad con todas las comodidades',
      estrellas: 5,
      email: 'info@grandplaza.com',
      telefono: '+1 555-0200',
      pais: 'México',
      ciudad: 'Ciudad de México',
      direccion: 'Paseo de la Reforma 500',
    },
  });

  // Habitaciones del hotel demo
  const tiposHabitacion = [
    { numero: '101', tipo: 'simple', capacidad: 1, precioNoche: 80, amenidades: ['WiFi', 'TV', 'AC'] },
    { numero: '102', tipo: 'simple', capacidad: 1, precioNoche: 80, amenidades: ['WiFi', 'TV', 'AC'] },
    { numero: '201', tipo: 'doble', capacidad: 2, precioNoche: 130, amenidades: ['WiFi', 'TV', 'AC', 'Minibar'] },
    { numero: '202', tipo: 'doble', capacidad: 2, precioNoche: 130, amenidades: ['WiFi', 'TV', 'AC', 'Minibar'] },
    { numero: '301', tipo: 'suite', capacidad: 3, precioNoche: 250, amenidades: ['WiFi', 'TV', 'AC', 'Jacuzzi', 'Minibar', 'Vista al mar'] },
    { numero: '401', tipo: 'presidencial', capacidad: 4, precioNoche: 500, amenidades: ['WiFi', 'TV', 'AC', 'Jacuzzi', 'Minibar', 'Sala', 'Cocina'] },
  ];

  for (const hab of tiposHabitacion) {
    await prisma.habitacion.upsert({
      where: { hotelId_numero: { hotelId: hotelDemo.id, numero: hab.numero } },
      update: {},
      create: {
        hotelId: hotelDemo.id,
        empresaId: empresaDemo.id,
        numero: hab.numero,
        tipo: hab.tipo,
        capacidad: hab.capacidad,
        precioNoche: hab.precioNoche,
        amenidades: hab.amenidades,
      },
    });
  }

  // =====================
  // 7. PAQUETES TURÍSTICOS DEMO
  // =====================
  await prisma.paqueteTuristico.upsert({
    where: { id: 'paquete-demo-001' },
    update: {},
    create: {
      id: 'paquete-demo-001',
      empresaId: empresaDemo.id,
      nombre: 'Escapada a Cancún 5 días',
      descripcion: 'Disfruta de las playas de Cancún con todo incluido',
      duracionDias: 5,
      precio: 1200.00,
      precioIncluye: 'Vuelo, hotel 4 estrellas, desayuno y cena, traslados',
      maxPersonas: 10,
      destinosPaises: ['México'],
      itinerario: [
        { dia: 1, actividades: 'Llegada y check-in en hotel' },
        { dia: 2, actividades: 'Tour a Chichén Itzá' },
        { dia: 3, actividades: 'Día libre en la playa' },
        { dia: 4, actividades: 'Snorkel en el arrecife' },
        { dia: 5, actividades: 'Check-out y regreso' },
      ],
    },
  });

  await prisma.paqueteTuristico.upsert({
    where: { id: 'paquete-demo-002' },
    update: {},
    create: {
      id: 'paquete-demo-002',
      empresaId: empresaDemo.id,
      nombre: 'Ruta Colonial — Oaxaca & Puebla',
      descripcion: 'Descubre la cultura y gastronomía del centro de México',
      duracionDias: 7,
      precio: 950.00,
      precioIncluye: 'Hotel, desayunos, tours guiados, transporte',
      maxPersonas: 15,
      destinosPaises: ['México'],
    },
  });

  // =====================
  // 8. CLIENTES DEMO
  // =====================
  const clientes = [
    { nombre: 'Juan', apellido: 'García', email: 'juan.garcia@email.com', documentoTipo: 'DNI', documentoNum: '12345678', pais: 'México' },
    { nombre: 'Ana', apellido: 'Martínez', email: 'ana.m@email.com', documentoTipo: 'Pasaporte', documentoNum: 'AB123456', pais: 'España' },
    { nombre: 'Carlos', apellido: 'Rodríguez', email: 'carlos.r@email.com', documentoTipo: 'DNI', documentoNum: '87654321', pais: 'Argentina' },
    { nombre: 'Laura', apellido: 'Sánchez', email: 'laura.s@email.com', documentoTipo: 'Cédula', documentoNum: '1098765432', pais: 'Colombia' },
    { nombre: 'Pedro', apellido: 'López', email: 'pedro.l@email.com', documentoTipo: 'DNI', documentoNum: '11223344', pais: 'México' },
  ];

  for (const cliente of clientes) {
    await prisma.cliente.upsert({
      where: {
        empresaId_documentoTipo_documentoNum: {
          empresaId: empresaDemo.id,
          documentoTipo: cliente.documentoTipo,
          documentoNum: cliente.documentoNum,
        },
      },
      update: {},
      create: { empresaId: empresaDemo.id, ...cliente },
    });
  }

  // =====================
  // 9. SUSCRIPCIÓN DEMO
  // =====================
  await prisma.suscripcion.upsert({
    where: { id: 'suscripcion-demo-001' },
    update: {},
    create: {
      id: 'suscripcion-demo-001',
      empresaId: empresaDemo.id,
      planId: planProfesional.id,
      estado: 'activa',
      fechaInicio: new Date('2024-01-01'),
      precioPagado: 149.00,
    },
  });

  // =====================
  // 10. EMPLEADOS DEMO
  // =====================
  await prisma.empleado.upsert({
    where: { id: 'empleado-demo-001' },
    update: {},
    create: {
      id: 'empleado-demo-001',
      empresaId: empresaDemo.id,
      usuarioId: usuarioAdmin.id,
      nombre: 'Admin',
      apellido: 'Principal',
      cargo: 'Gerente General',
      departamento: 'Dirección',
      email: 'admin@demotours.com',
      fechaIngreso: new Date('2024-01-01'),
    },
  });

  console.log('✅ Seed completado exitosamente');
  console.log('');
  console.log('📧 Credenciales de acceso:');
  console.log('   Email:    admin@demotours.com');
  console.log('   Password: Admin123!');
}

main()
  .catch((e) => {
    console.error('❌ Error en seed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
