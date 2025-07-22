import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AgentOS - Sistema de Agentes IA',
  description: 'Plataforma avanzada de agentes de inteligencia artificial',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  )
} 