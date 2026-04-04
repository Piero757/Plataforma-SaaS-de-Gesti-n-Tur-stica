import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: {
    default: 'Plataforma SaaS de Gestión Turística',
    template: '%s | SaaS Turismo',
  },
  description:
    'Plataforma SaaS profesional para la gestión integral de empresas de turismo y hotelería. Reservas, clientes, hoteles, paquetes turísticos y más.',
  keywords: ['turismo', 'hotelería', 'reservas', 'SaaS', 'gestión turística'],
  authors: [{ name: 'SaaS Turismo' }],
  robots: 'index, follow',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-background antialiased">
        {children}
      </body>
    </html>
  );
}
