import type { Metadata } from 'next'
import { ScreenPlaceholder } from '../screen-placeholder'

export const metadata: Metadata = {
  title: 'Cupones',
}

export default function CuponesPage() {
  return (
    <ScreenPlaceholder
      icon="🎟️"
      title="Cupones"
      subtitle="Canjea tus puntos por recompensas"
    >
      <ul className="space-y-2">
        <li>• Catálogo de <code>coupons</code> activos con costo en puntos.</li>
        <li>• Canje → <code>POST /api/coupons/redeem</code> con confirmación.</li>
        <li>• Comprobante con código en <code>coupon_redemptions</code>.</li>
      </ul>
    </ScreenPlaceholder>
  )
}
