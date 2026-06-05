'use client'

import { useActionState } from 'react'
import { sendMagicLink } from './actions'

export function LoginForm() {
  const [state, action, pending] = useActionState(sendMagicLink, null)

  if (state?.success) {
    return (
      <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-6 text-center">
        <div className="text-3xl mb-3">📬</div>
        <p className="font-medium text-emerald-800">{state.message}</p>
        <p className="text-sm text-emerald-600 mt-2">
          Haz clic en el enlace del correo para continuar.
        </p>
      </div>
    )
  }

  return (
    <form action={action} className="space-y-4">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-zinc-700 mb-1.5">
          Correo institucional
        </label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          required
          placeholder="tu.nombre@puce.edu.ec"
          className="w-full rounded-lg border border-zinc-300 bg-white px-4 py-2.5 text-sm text-zinc-900 placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition"
        />
      </div>

      {state?.message && !state.success && (
        <p className="text-sm text-red-600 bg-red-50 rounded-lg px-4 py-2.5 border border-red-200">
          {state.message}
        </p>
      )}

      <button
        type="submit"
        disabled={pending}
        className="w-full rounded-lg bg-emerald-500 hover:bg-emerald-600 disabled:opacity-60 disabled:cursor-not-allowed px-4 py-2.5 text-sm font-semibold text-white transition-colors"
      >
        {pending ? 'Enviando enlace...' : 'Enviar enlace de acceso'}
      </button>
    </form>
  )
}
