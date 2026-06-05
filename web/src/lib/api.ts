import { createServiceClient } from '@/lib/supabase/server'
import type { NextRequest } from 'next/server'

export const ok = (data: unknown, status = 200) =>
  Response.json(data, { status })

export const err = (message: string, status: number) =>
  Response.json({ error: message }, { status })

// Para rutas del robot/IA: valida que venga el service role key como Bearer token
export function requireRobotAuth(request: NextRequest): boolean {
  const auth = request.headers.get('authorization') ?? ''
  const token = auth.replace('Bearer ', '').trim()
  return token === process.env.SUPABASE_SERVICE_ROLE_KEY
}

// Para rutas de usuario: devuelve el user autenticado vía sesión
export async function requireUserAuth(request: NextRequest) {
  // Importación dinámica para evitar uso accidental en contextos browser
  const { createClient } = await import('@/lib/supabase/server')
  const supabase = await createClient()
  const { data: { user }, error } = await supabase.auth.getUser()
  if (error || !user) return null
  return user
}

export { createServiceClient }
