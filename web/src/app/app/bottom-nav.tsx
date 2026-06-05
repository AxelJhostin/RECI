'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const TABS = [
  { href: '/app', label: 'Inicio', icon: '🏠' },
  { href: '/app/mapa', label: 'Mapa', icon: '🗺️' },
  { href: '/app/llamar', label: 'Llamar', icon: '📞' },
  { href: '/app/historial', label: 'Historial', icon: '📋' },
  { href: '/app/cupones', label: 'Cupones', icon: '🎟️' },
] as const

export function BottomNav() {
  const pathname = usePathname()

  return (
    <nav className="fixed inset-x-0 bottom-0 z-10 border-t border-zinc-200 bg-white/95 backdrop-blur">
      <ul className="mx-auto flex max-w-lg items-stretch justify-around">
        {TABS.map(({ href, label, icon }) => {
          const isActive = href === '/app' ? pathname === href : pathname.startsWith(href)

          return (
            <li key={href} className="flex-1">
              <Link
                href={href}
                aria-current={isActive ? 'page' : undefined}
                className={`flex flex-col items-center gap-0.5 py-2 text-xs transition-colors ${
                  isActive ? 'text-emerald-600' : 'text-zinc-400 hover:text-zinc-600'
                }`}
              >
                <span className="text-xl leading-none">{icon}</span>
                <span className="font-medium">{label}</span>
              </Link>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
