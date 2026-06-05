import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import type { ReactNode } from 'react'
import { BottomNav } from './bottom-nav'

export default async function AppLayout({ children }: { children: ReactNode }) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) redirect('/login')

  return (
    <div className="min-h-screen bg-zinc-50">
      {/* pb-20 leaves room for the fixed bottom nav */}
      <div className="pb-20">{children}</div>
      <BottomNav />
    </div>
  )
}
