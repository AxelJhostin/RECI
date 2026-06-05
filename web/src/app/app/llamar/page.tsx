import type { Metadata } from 'next'
import { createClient } from '@/lib/supabase/server'
import { CallForm } from './call-form'

export const metadata: Metadata = {
  title: 'Llamar a Reci',
}

export default async function LlamarPage() {
  const supabase = await createClient()

  const [{ data: points }, { data: pending }] = await Promise.all([
    supabase
      .from('robot_points')
      .select('id, name, notes')
      .eq('active', true)
      .order('name'),
    supabase
      .from('call_requests')
      .select('id, point_id, status, created_at')
      .eq('status', 'pending')
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle(),
  ])

  return (
    <main className="mx-auto max-w-lg space-y-6 px-4 py-10">
      <header className="space-y-1">
        <span className="text-3xl">📞</span>
        <h1 className="text-xl font-bold text-zinc-900">Llamar a Reci</h1>
        <p className="text-sm text-zinc-500">
          Elige un punto del campus y pide que el robot vaya hacia allá.
        </p>
      </header>

      <CallForm points={points ?? []} initialPending={pending ?? null} />
    </main>
  )
}
