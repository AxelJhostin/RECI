import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { SignOutButton } from './sign-out-button'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Inicio',
}

export default async function AppPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) redirect('/login')

  const { data: profile } = await supabase
    .from('profiles')
    .select('display_name, total_points')
    .eq('id', user.id)
    .single() as { data: { display_name: string | null; total_points: number } | null; error: unknown }

  return (
    <main className="max-w-lg mx-auto px-4 py-10 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-zinc-900">
            Hola, {profile?.display_name ?? user.email?.split('@')[0]} 👋
          </h1>
          <p className="text-sm text-zinc-500">Bienvenido a Reci</p>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/app/ajustes"
            className="text-sm text-zinc-400 transition-colors hover:text-zinc-700"
          >
            Ajustes
          </Link>
          <SignOutButton />
        </div>
      </div>

      <div className="rounded-2xl bg-emerald-500 p-6 text-white">
        <p className="text-sm font-medium opacity-80">Tus puntos</p>
        <p className="text-4xl font-bold mt-1">{profile?.total_points ?? 0}</p>
        <p className="text-sm opacity-70 mt-1">puntos acumulados</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {[
          { href: '/app/mapa', icon: '🗺️', label: 'Mapa', desc: 'Encuentra a Reci' },
          { href: '/app/llamar', icon: '📞', label: 'Llamar', desc: 'Llama a Reci aquí' },
          { href: '/app/historial', icon: '📋', label: 'Historial', desc: 'Tus reciclajes' },
          { href: '/app/cupones', icon: '🎟️', label: 'Cupones', desc: 'Canjea puntos' },
        ].map(({ href, icon, label, desc }) => (
          <Link
            key={label}
            href={href}
            className="rounded-xl border border-zinc-200 bg-white p-4 flex flex-col gap-1 hover:border-emerald-300 transition-colors"
          >
            <span className="text-2xl">{icon}</span>
            <p className="font-semibold text-zinc-900 text-sm">{label}</p>
            <p className="text-xs text-zinc-400">{desc}</p>
          </Link>
        ))}
      </div>
    </main>
  )
}
