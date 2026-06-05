import type { Metadata } from 'next'
import { ScreenPlaceholder } from '../screen-placeholder'

export const metadata: Metadata = {
  title: 'Historial',
}

export default function HistorialPage() {
  return (
    <ScreenPlaceholder
      icon="📋"
      title="Tu historial"
      subtitle="Todos tus reciclajes y puntos ganados"
    >
      <ul className="space-y-2">
        <li>• Lista de <code>recycle_events</code> del usuario, paginada.</li>
        <li>• Material, confianza y puntos por evento.</li>
        <li>• Racha actual desde <code>streaks</code>.</li>
      </ul>
    </ScreenPlaceholder>
  )
}
