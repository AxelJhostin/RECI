'use client'

import { useState } from 'react'
import type { Database } from '@/lib/supabase/types'

type Coupon = Pick<
  Database['public']['Tables']['coupons']['Row'],
  'id' | 'title' | 'description' | 'cost_points' | 'stock'
>

type Redemption = {
  id: string
  code: string
  redeemed_at: string
  coupon_title: string
}

export function CouponList({
  coupons,
  initialPoints,
}: {
  coupons: Coupon[]
  initialPoints: number
}) {
  const [points, setPoints] = useState(initialPoints)
  const [stocks, setStocks] = useState<Record<string, number>>(
    Object.fromEntries(coupons.map((c) => [c.id, c.stock])),
  )
  const [redeemingId, setRedeemingId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<Redemption | null>(null)

  async function handleRedeem(coupon: Coupon) {
    setRedeemingId(coupon.id)
    setError(null)
    setSuccess(null)

    try {
      const res = await fetch('/api/coupons/redeem', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ coupon_id: coupon.id }),
      })
      const data = await res.json()

      if (!res.ok) {
        setError(data.error ?? 'No se pudo canjear el cupón')
        return
      }

      setSuccess(data.redemption as Redemption)
      setPoints((p) => p - coupon.cost_points)
      setStocks((s) => ({ ...s, [coupon.id]: (s[coupon.id] ?? 1) - 1 }))
    } catch {
      setError('Error de conexión. Inténtalo de nuevo.')
    } finally {
      setRedeemingId(null)
    }
  }

  if (coupons.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-zinc-300 bg-white p-6 text-center text-sm text-zinc-500">
        No hay cupones disponibles por ahora.
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {success ? (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">
          <p className="text-sm font-semibold text-emerald-700">
            ¡Canjeaste {success.coupon_title}! 🎉
          </p>
          <p className="mt-2 text-xs text-emerald-600">Tu código:</p>
          <p className="mt-1 font-mono text-lg font-bold tracking-widest text-emerald-800">
            {success.code}
          </p>
        </div>
      ) : null}

      {error ? (
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>
      ) : null}

      <ul className="space-y-3">
        {coupons.map((c) => {
          const stock = stocks[c.id] ?? 0
          const affordable = points >= c.cost_points
          const available = stock > 0
          const disabled = !affordable || !available || redeemingId !== null

          return (
            <li
              key={c.id}
              className="rounded-xl border border-zinc-200 bg-white p-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="font-semibold text-zinc-900">{c.title}</p>
                  {c.description ? (
                    <p className="mt-0.5 text-sm text-zinc-500">{c.description}</p>
                  ) : null}
                  <p className="mt-1 text-xs text-zinc-400">
                    {available ? `${stock} disponibles` : 'Agotado'}
                  </p>
                </div>
                <span className="shrink-0 rounded-full bg-zinc-100 px-2.5 py-1 text-sm font-semibold text-zinc-700">
                  {c.cost_points} pts
                </span>
              </div>

              <button
                onClick={() => handleRedeem(c)}
                disabled={disabled}
                className="mt-3 w-full rounded-lg bg-emerald-600 py-2 text-sm font-semibold text-white transition-colors hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {redeemingId === c.id
                  ? 'Canjeando…'
                  : !available
                    ? 'Agotado'
                    : !affordable
                      ? `Te faltan ${c.cost_points - points} pts`
                      : 'Canjear'}
              </button>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
