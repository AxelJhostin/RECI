import type { Metadata } from 'next'
import { ScreenPlaceholder } from '../screen-placeholder'

export const metadata: Metadata = {
  title: 'Mapa',
}

export default function MapaPage() {
  return (
    <ScreenPlaceholder
      icon="🗺️"
      title="Mapa del campus"
      subtitle="Encuentra a Reci y los puntos de reciclaje"
    >
      <ul className="space-y-2">
        <li>• Mapa con Leaflet + OpenStreetMap (sin token).</li>
        <li>• Puntos fijos del campus desde <code>robot_points</code>.</li>
        <li>• Posición de Reci en tiempo real (Supabase Realtime).</li>
      </ul>
    </ScreenPlaceholder>
  )
}
