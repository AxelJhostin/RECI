import type { Metadata } from 'next'
import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import type { MaterialType } from '@/lib/supabase/types'

export const metadata: Metadata = {
  title: 'Historial',
}

const MATERIAL_META: Record<MaterialType, { icon: string; label: string; points: number }> = {
  vidrio: { icon: '🫙', label: 'Vidrio', points: 10 },
  plastico: { icon: '🧴', label: 'Plástico', points: 10 },
  desconocido: { icon: '❓', label: 'Desconocido', points: 0 },
}

export default async function HistorialPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

  const [{ data: events }, { data: streak }, { data: points }] = await Promise.all([
    supabase
      .from('recycle_events')
      .select('id, material, confidence, robot_point_id, created_at')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })
      .limit(30),
    supabase
      .from('streaks')
      .select('current_streak, longest_streak')
      .eq('user_id', user.id)
      .maybeSingle(),
    supabase.from('robot_points').select('id, name'),
  ])

  const pointNames = new Map((points ?? []).map((p) => [p.id, p.name]))

  return (
    <main className="mx-auto max-w-lg space-y-6 px-4 py-10">
      <header className="space-y-1">
        <span className="text-3xl">📋</span>
        <h1 className="text-xl font-bold text-zinc-900">Tu historial</h1>
        <p className="text-sm text-zinc-500">Tus reciclajes y la racha que llevas</p>
      </header>

      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-xl border border-zinc-200 bg-white p-4">
          <p className="text-xs text-zinc-400">Racha actual</p>
          <p className="mt-1 text-2xl font-bold text-zinc-900">
            {streak?.current_streak ?? 0} 🔥
          </p>
        </div>
        <div className="rounded-xl border border-zinc-200 bg-white p-4">
          <p className="text-xs text-zinc-400">Mejor racha</p>
          <p className="mt-1 text-2xl font-bold text-zinc-900">
            {streak?.longest_streak ?? 0}
          </p>
        </div>
      </div>

      {events && events.length > 0 ? (
        <ul className="space-y-2">
          {events.map((e) => {
            const meta = MATERIAL_META[e.material]
            return (
              <li
                key={e.id}
                className="flex items-center gap-3 rounded-xl border border-zinc-200 bg-white p-4"
              >
                <span className="text-2xl">{meta.icon}</span>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-zinc-900">{meta.label}</p>
                  <p className="truncate text-xs text-zinc-400">
                    {e.robot_point_id
                      ? (pointNames.get(e.robot_point_id) ?? 'Punto del campus')
                      : 'Reci'}
                    {' · '}
                    {new Date(e.created_at).toLocaleDateString('es-EC', {
                      day: 'numeric',
                      month: 'short',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
                {meta.points > 0 ? (
                  <span className="shrink-0 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-600">
                    +{meta.points}
                  </span>
                ) : null}
              </li>
            )
          })}
        </ul>
      ) : (
        <div className="rounded-2xl border border-dashed border-zinc-300 bg-white p-6 text-center text-sm text-zinc-500">
          Todavía no has reciclado nada. ¡Busca a Reci en el mapa! ♻️
        </div>
      )}
    </main>
  )
}
