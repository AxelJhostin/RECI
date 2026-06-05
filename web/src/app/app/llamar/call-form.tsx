'use client'

import { useState } from 'react'
import type { Database } from '@/lib/supabase/types'

type RobotPoint = Pick<
  Database['public']['Tables']['robot_points']['Row'],
  'id' | 'name' | 'notes'
>
type PendingCall = Pick<
  Database['public']['Tables']['call_requests']['Row'],
  'id' | 'point_id' | 'status' | 'created_at'
>

export function CallForm({
  points,
  initialPending,
}: {
  points: RobotPoint[]
  initialPending: PendingCall | null
}) {
  const [selected, setSelected] = useState<string>(
    initialPending?.point_id ?? points[0]?.id ?? '',
  )
  const [pending, setPending] = useState<PendingCall | null>(initialPending)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const pendingPoint = pending
    ? points.find((p) => p.id === pending.point_id)
    : null

  async function handleCall() {
    if (!selected) return
    setLoading(true)
    setError(null)

    try {
      const res = await fetch('/api/calls', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ point_id: selected }),
      })
      const data = await res.json()

      if (!res.ok) {
        setError(data.error ?? 'No se pudo llamar a Reci')
        return
      }

      setPending(data.call as PendingCall)
    } catch {
      setError('Error de conexión. Inténtalo de nuevo.')
    } finally {
      setLoading(false)
    }
  }

  if (points.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-zinc-300 bg-white p-6 text-sm text-zinc-500">
        Todavía no hay puntos del campus configurados.
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {pending ? (
        <div className="rounded-2xl bg-emerald-500 p-5 text-white">
          <p className="text-sm font-medium opacity-80">Reci está en camino 🚀</p>
          <p className="mt-1 text-lg font-bold">
            {pendingPoint?.name ?? 'Punto del campus'}
          </p>
          <p className="text-sm opacity-70">
            Solicitado a las{' '}
            {new Date(pending.created_at).toLocaleTimeString('es-EC', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
        </div>
      ) : null}

      <fieldset className="space-y-2" disabled={loading}>
        <legend className="mb-2 text-sm font-medium text-zinc-700">
          {pending ? 'Cambiar a otro punto' : 'Punto de recogida'}
        </legend>

        {points.map((p) => (
          <label
            key={p.id}
            className={`flex cursor-pointer items-start gap-3 rounded-xl border p-4 transition-colors ${
              selected === p.id
                ? 'border-emerald-400 bg-emerald-50'
                : 'border-zinc-200 bg-white hover:border-emerald-200'
            }`}
          >
            <input
              type="radio"
              name="point"
              value={p.id}
              checked={selected === p.id}
              onChange={() => setSelected(p.id)}
              className="mt-1 accent-emerald-500"
            />
            <span>
              <span className="block text-sm font-semibold text-zinc-900">
                {p.name}
              </span>
              {p.notes ? (
                <span className="block text-xs text-zinc-400">{p.notes}</span>
              ) : null}
            </span>
          </label>
        ))}
      </fieldset>

      {error ? (
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
          {error}
        </p>
      ) : null}

      <button
        onClick={handleCall}
        disabled={loading || !selected}
        className="w-full rounded-xl bg-emerald-600 py-3 font-semibold text-white transition-colors hover:bg-emerald-700 disabled:opacity-50"
      >
        {loading
          ? 'Llamando…'
          : pending
            ? 'Actualizar punto'
            : 'Llamar a Reci'}
      </button>
    </div>
  )
}
