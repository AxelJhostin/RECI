import type { Metadata } from 'next'
import { createClient } from '@/lib/supabase/server'
import { MapView } from './map-view'

export const metadata: Metadata = {
  title: 'Mapa',
}

export default async function MapaPage() {
  const supabase = await createClient()

  const [{ data: points }, { data: lastPosition }] = await Promise.all([
    supabase
      .from('robot_points')
      .select('id, name, lat, lng, notes')
      .eq('active', true),
    supabase
      .from('robot_positions')
      .select('lat, lng, status, recorded_at')
      .order('recorded_at', { ascending: false })
      .limit(1)
      .maybeSingle(),
  ])

  return (
    <div className="flex h-[calc(100vh-5rem)] flex-col">
      <header className="space-y-0.5 px-4 pt-6 pb-3">
        <h1 className="text-xl font-bold text-zinc-900">Mapa del campus</h1>
        <p className="text-sm text-zinc-500">
          Encuentra a Reci y los puntos de reciclaje
        </p>
      </header>

      <div className="relative flex-1 overflow-hidden">
        <MapView points={points ?? []} initialPosition={lastPosition ?? null} />
      </div>
    </div>
  )
}
