import { type NextRequest } from 'next/server'
import { ok, err, requireRobotAuth, createServiceClient } from '@/lib/api'
import type { MaterialType } from '@/lib/supabase/types'

// POST /api/events/recycle
// Llamado por la IA de la Raspberry Pi cuando clasifica un objeto
// Body: { user_id?, material, confidence, robot_point_id? }
export async function POST(request: NextRequest) {
  if (!requireRobotAuth(request)) return err('No autorizado', 401)

  let body: unknown
  try { body = await request.json() } catch { return err('Body inválido', 400) }

  const { user_id, material, confidence, robot_point_id } = body as Record<string, unknown>

  if (!material || !['vidrio', 'plastico', 'desconocido'].includes(material as string)) {
    return err('material debe ser vidrio | plastico | desconocido', 400)
  }

  if (confidence !== undefined && (typeof confidence !== 'number' || confidence < 0 || confidence > 1)) {
    return err('confidence debe ser un número entre 0 y 1', 400)
  }

  const supabase = createServiceClient()
  const { data, error } = await supabase
    .from('recycle_events')
    .insert({
      user_id: (user_id as string) ?? null,
      material: material as MaterialType,
      confidence: (confidence as number) ?? null,
      robot_point_id: (robot_point_id as string) ?? null,
    })
    .select('id, material, confidence, created_at')
    .single()

  if (error) {
    console.error('recycle event insert:', error.message)
    return err('Error al registrar el evento', 500)
  }

  return ok({ event: data }, 201)
}
