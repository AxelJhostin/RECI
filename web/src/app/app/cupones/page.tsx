import type { Metadata } from 'next'
import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import { CouponList } from './coupon-list'

export const metadata: Metadata = {
  title: 'Cupones',
}

export default async function CuponesPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

  const [{ data: coupons }, { data: profile }] = await Promise.all([
    supabase
      .from('coupons')
      .select('id, title, description, cost_points, stock')
      .eq('active', true)
      .order('cost_points'),
    supabase.from('profiles').select('total_points').eq('id', user.id).single(),
  ])

  return (
    <main className="mx-auto max-w-lg space-y-6 px-4 py-10">
      <header className="flex items-start justify-between">
        <div className="space-y-1">
          <span className="text-3xl">🎟️</span>
          <h1 className="text-xl font-bold text-zinc-900">Cupones</h1>
          <p className="text-sm text-zinc-500">Canjea tus puntos por recompensas</p>
        </div>
        <div className="rounded-xl bg-emerald-500 px-4 py-2 text-right text-white">
          <p className="text-xs opacity-80">Tus puntos</p>
          <p className="text-xl font-bold">{profile?.total_points ?? 0}</p>
        </div>
      </header>

      <CouponList
        coupons={coupons ?? []}
        initialPoints={profile?.total_points ?? 0}
      />
    </main>
  )
}
