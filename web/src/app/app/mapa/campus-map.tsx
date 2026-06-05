'use client'

import { useEffect, useMemo, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { createClient } from '@/lib/supabase/client'
import type { Database } from '@/lib/supabase/types'

type RobotPoint = Pick<
  Database['public']['Tables']['robot_points']['Row'],
  'id' | 'name' | 'lat' | 'lng' | 'notes'
>
type RobotPosition = Pick<
  Database['public']['Tables']['robot_positions']['Row'],
  'lat' | 'lng' | 'status' | 'recorded_at'
>

// PUCE Manabí (Chone) — fallback si todavía no hay puntos cargados.
const CAMPUS_FALLBACK: [number, number] = [-0.6979, -80.0959]

const STATUS_LABEL: Record<RobotPosition['status'], string> = {
  idle: 'Disponible',
  moving: 'En camino',
  charging: 'Cargando',
}

// Marcadores como divIcon con emoji: sin assets que se rompan con el bundler.
const pointIcon = L.divIcon({
  html: '<span class="reci-pin">♻️</span>',
  className: 'reci-marker',
  iconSize: [30, 30],
  iconAnchor: [15, 15],
})
const robotIcon = L.divIcon({
  html: '<span class="reci-pin reci-pin--robot">🤖</span>',
  className: 'reci-marker',
  iconSize: [40, 40],
  iconAnchor: [20, 20],
})

export default function CampusMap({
  points,
  initialPosition,
}: {
  points: RobotPoint[]
  initialPosition: RobotPosition | null
}) {
  const [position, setPosition] = useState<RobotPosition | null>(initialPosition)

  // Centro: promedio de los puntos del campus, o fallback.
  const center = useMemo<[number, number]>(() => {
    if (points.length === 0) return CAMPUS_FALLBACK
    const avgLat = points.reduce((s, p) => s + p.lat, 0) / points.length
    const avgLng = points.reduce((s, p) => s + p.lng, 0) / points.length
    return [avgLat, avgLng]
  }, [points])

  // Posición de Reci en tiempo real (Supabase Realtime).
  useEffect(() => {
    const supabase = createClient()
    const channel = supabase
      .channel('robot-position')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'robot_positions' },
        (payload) => setPosition(payload.new as RobotPosition),
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  return (
    <MapContainer
      center={center}
      zoom={17}
      scrollWheelZoom
      className="h-full w-full"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {points.map((p) => (
        <Marker key={p.id} position={[p.lat, p.lng]} icon={pointIcon}>
          <Popup>
            <strong>{p.name}</strong>
            {p.notes ? <p className="m-0 text-zinc-500">{p.notes}</p> : null}
          </Popup>
        </Marker>
      ))}

      {position ? (
        <Marker position={[position.lat, position.lng]} icon={robotIcon}>
          <Popup>
            <strong>Reci</strong>
            <p className="m-0 text-zinc-500">{STATUS_LABEL[position.status]}</p>
          </Popup>
        </Marker>
      ) : null}
    </MapContainer>
  )
}
