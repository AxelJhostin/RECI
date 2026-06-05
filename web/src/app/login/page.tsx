import { LoginForm } from './login-form'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Iniciar sesión',
}

export default function LoginPage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-zinc-50 px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-emerald-500 mb-4">
            <span className="text-3xl">♻️</span>
          </div>
          <h1 className="text-2xl font-bold text-zinc-900">Bienvenido a Reci</h1>
          <p className="text-sm text-zinc-500 mt-1">
            Ingresa tu correo y te enviamos un enlace para entrar
          </p>
        </div>

        <LoginForm />

        <p className="text-center text-xs text-zinc-400 mt-6">
          Solo para la comunidad PUCE Manabí
        </p>
      </div>
    </main>
  )
}
