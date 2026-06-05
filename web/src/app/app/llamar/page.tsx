import type { Metadata } from 'next'
import { ScreenPlaceholder } from '../screen-placeholder'

export const metadata: Metadata = {
  title: 'Llamar a Reci',
}

export default function LlamarPage() {
  return (
    <ScreenPlaceholder
      icon="📞"
      title="Llamar a Reci"
      subtitle="Pide que el robot venga a tu punto"
    >
      <ul className="space-y-2">
        <li>• Selector de punto del campus.</li>
        <li>• Botón &ldquo;Llamar a Reci&rdquo; → <code>POST /api/calls</code>.</li>
        <li>• Estado de la llamada con animación de carga.</li>
      </ul>
    </ScreenPlaceholder>
  )
}
