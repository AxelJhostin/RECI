'use server'

import { createClient } from '@/lib/supabase/server'
import { headers } from 'next/headers'

type State = { message: string; success: boolean } | null

export async function sendMagicLink(_: State, formData: FormData): Promise<State> {
  const email = formData.get('email')?.toString().trim().toLowerCase()

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return { success: false, message: 'Ingresa un correo válido.' }
  }

  const supabase = await createClient()
  const headersList = await headers()
  const origin = headersList.get('origin') ?? 'http://localhost:3000'

  const { error } = await supabase.auth.signInWithOtp({
    email,
    options: {
      emailRedirectTo: `${origin}/auth/callback`,
    },
  })

  if (error) {
    console.error('Magic link error:', error.message)
    return { success: false, message: 'No pudimos enviar el enlace. Intenta de nuevo.' }
  }

  return { success: true, message: `Enlace enviado a ${email}. Revisa tu bandeja de entrada.` }
}
