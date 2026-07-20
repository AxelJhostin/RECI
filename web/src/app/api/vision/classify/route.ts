import { type NextRequest } from 'next/server'
import { ok, err, requireRobotAuth, createServiceClient } from '@/lib/api'
import { classifyMaterial, type VisionClassifyResult } from '@/lib/vision/service'

// POST /api/vision/classify
// Llamado por el ESP32-CAM con la imagen del residuo.
// Body: multipart/form-data con campo "image" (JPEG/PNG) y opcional "robot_point_id".
//
// Retorna: { material, confidence, rule_applied }
// El ESP32-CAM usa este resultado para reenviar el CMD al Arduino Mega.
export async function POST(request: NextRequest) {
  if (!requireRobotAuth(request)) return err('No autorizado', 401)

  let formData: FormData
  try { formData = await request.formData() } catch { return err('Body inválido', 400) }

  const image = formData.get('image')
  const robotPointId = formData.get('robot_point_id')?.toString() ?? null
  const userId = formData.get('user_id')?.toString() ?? null

  if (!(image instanceof File)) return err('Se requiere el campo "image"', 400)

  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowedTypes.includes(image.type)) return err('Solo se aceptan imágenes JPEG, PNG o WebP', 415)

  if (image.size > 2 * 1024 * 1024) return err('La imagen no puede superar 2 MB', 413)

  const result = await classifyImage(image)

  // Registrar el evento en la base de datos
  if (result.material !== 'desconocido') {
    const supabase = createServiceClient()
    await supabase.from('recycle_events').insert({
      user_id: userId,
      material: result.material,
      confidence: result.confidence,
      robot_point_id: robotPointId,
    })
  }

  return ok(result)
}

// ─── Clasificador ────────────────────────────────────────────────────────
// Llama a ia/vision-service: Claude/Gemini + heurísticas OpenCV + sistema
// experto (174 reglas, portado de dev/RECI). Ver
// docs/DECISION-SERVICIO-VISION.md.
async function classifyImage(image: File): Promise<VisionClassifyResult> {
  try {
    return await classifyMaterial(image)
  } catch (error) {
    // Si el servicio de visión no responde, se rechaza en vez de adivinar —
    // misma política conservadora que el sistema experto (más vale un
    // "material no permitido" que abrir la compuerta equivocada).
    const detail = error instanceof Error ? error.message : 'error desconocido'
    console.error('vision classify:', detail)
    return {
      material: 'desconocido',
      confidence: 0,
      rule_applied: `servicio de visión no disponible — ${detail}`,
    }
  }
}
