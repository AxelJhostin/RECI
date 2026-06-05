import type { Metadata } from 'next'
import { ScreenPlaceholder } from '../screen-placeholder'

export const metadata: Metadata = {
  title: 'Ajustes',
}

export default function AjustesPage() {
  return (
    <ScreenPlaceholder
      icon="⚙️"
      title="Ajustes"
      subtitle="Tu perfil y preferencias"
    >
      <ul className="space-y-2">
        <li>• Editar nombre y avatar del <code>profile</code>.</li>
        <li>• Opt-in facial: subir foto y revocar consentimiento.</li>
        <li>• Notificaciones push (Web Push).</li>
      </ul>
    </ScreenPlaceholder>
  )
}
