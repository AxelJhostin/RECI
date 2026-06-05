import { type NextRequest } from 'next/server'
import { ok, err, requireRobotAuth, createServiceClient } from '@/lib/api'

// POST /api/robot/position
// Llamado por la Raspberry Pi periódicamente para reportar posición
// Body: { lat, lng, status? }
export async function POST(request: NextRequest) {
  if (!requireRobotAuth(request)) return err('No autorizado', 401)

  let body: unknown
  try { body = await request.json() } catch { return err('Body inválido', 400) }

  const { lat, lng, status = 'idle' } = body as Record<string, unknown>

  if (typeof lat !== 'number' || typeof lng !== 'number') {
    return err('lat y lng son requeridos y deben ser números', 400)
  }

  if (!['idle', 'moving', 'charging'].includes(status as string)) {
    return err('status debe ser idle | moving | charging', 400)
  }

  const supabase = createServiceClient()
  const { data, error } = await supabase
    .from('robot_positions')
    .insert({ lat, lng, status: status as 'idle' | 'moving' | 'charging' })
    .select('id, lat, lng, status, recorded_at')
    .single()

  if (error) {
    console.error('robot position insert:', error.message)
    return err('Error al registrar posición', 500)
  }

  return ok({ position: data }, 201)
}
