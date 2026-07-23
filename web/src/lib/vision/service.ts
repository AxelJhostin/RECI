import type { MaterialType } from '@/lib/supabase/types'

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']

export type VisionClassifyResult = {
  material: MaterialType
  confidence: number
  rule_applied: string
  vision_provider_result?: {
    material: MaterialType
    confidence: number
  }
  vision_local_result?: {
    material: 'vidrio' | 'plastico'
    confidence: number
    probabilities?: Record<string, number>
    model?: string
  } | null
  vision_fusion?: {
    agreement: boolean | null
    method: string
  }
}

// Llama a ia/vision-service (proveedor + MobileNetV2 + heurísticas OpenCV +
// sistema experto + fusión). Ver docs/DECISION-SERVICIO-VISION.md.
export async function classifyMaterial(image: File): Promise<VisionClassifyResult> {
  if (!ALLOWED_TYPES.includes(image.type)) throw new Error('Solo se aceptan imágenes JPEG, PNG o WebP')

  const serviceUrl = process.env.VISION_SERVICE_URL?.replace(/\/$/, '')
  const serviceKey = process.env.VISION_SERVICE_API_KEY
  if (!serviceUrl || !serviceKey) throw new Error('El servicio de visión no está configurado')

  const formData = new FormData()
  formData.set('image', image, image.name || 'residuo.jpg')

  let response: Response
  try {
    response = await fetch(`${serviceUrl}/v1/classify`, {
      method: 'POST',
      headers: { 'x-vision-service-key': serviceKey },
      body: formData,
      // Claude/Gemini puede tardar unos segundos, más un reintento del lado
      // del servicio de visión — dale margen antes de darlo por caído.
      signal: AbortSignal.timeout(25_000),
    })
  } catch {
    throw new Error('No se pudo contactar al servicio de visión')
  }

  const body: unknown = await response.json().catch(() => null)
  if (!response.ok || !body || typeof body !== 'object') {
    const detail = body && typeof body === 'object' && 'detail' in body && typeof body.detail === 'string'
      ? body.detail
      : 'No se pudo clasificar la imagen'
    throw new Error(detail)
  }

  const material = (body as { material?: unknown }).material
  const confidence = (body as { confidence?: unknown }).confidence
  const ruleApplied = (body as { rule_applied?: unknown }).rule_applied
  const providerResult = (body as { vision_provider_result?: unknown }).vision_provider_result
  const localResult = (body as { vision_local_result?: unknown }).vision_local_result
  const fusion = (body as { vision_fusion?: unknown }).vision_fusion

  if (material !== 'vidrio' && material !== 'plastico' && material !== 'desconocido') {
    throw new Error('El servicio de visión devolvió un material inválido')
  }
  if (typeof confidence !== 'number' || !Number.isFinite(confidence)) {
    throw new Error('El servicio de visión devolvió una confianza inválida')
  }

  const result: VisionClassifyResult = {
    material,
    confidence,
    rule_applied: typeof ruleApplied === 'string' ? ruleApplied : 'desconocido',
  }

  if (providerResult && typeof providerResult === 'object') {
    const providerMaterial = (providerResult as { material?: unknown }).material
    const providerConfidence = (providerResult as { confidence?: unknown }).confidence
    if (
      (providerMaterial === 'vidrio' || providerMaterial === 'plastico' || providerMaterial === 'desconocido')
      && typeof providerConfidence === 'number'
      && Number.isFinite(providerConfidence)
    ) {
      result.vision_provider_result = {
        material: providerMaterial,
        confidence: providerConfidence,
      }
    }
  }

  if (localResult === null) {
    result.vision_local_result = null
  } else if (localResult && typeof localResult === 'object') {
    const localMaterial = (localResult as { material?: unknown }).material
    const localConfidence = (localResult as { confidence?: unknown }).confidence
    const probabilities = (localResult as { probabilities?: unknown }).probabilities
    const model = (localResult as { model?: unknown }).model
    if (
      (localMaterial === 'vidrio' || localMaterial === 'plastico')
      && typeof localConfidence === 'number'
      && Number.isFinite(localConfidence)
    ) {
      result.vision_local_result = {
        material: localMaterial,
        confidence: localConfidence,
        ...(probabilities && typeof probabilities === 'object'
          ? { probabilities: probabilities as Record<string, number> }
          : {}),
        ...(typeof model === 'string' ? { model } : {}),
      }
    }
  }

  if (fusion && typeof fusion === 'object') {
    const agreement = (fusion as { agreement?: unknown }).agreement
    const method = (fusion as { method?: unknown }).method
    if (
      (typeof agreement === 'boolean' || agreement === null)
      && typeof method === 'string'
    ) {
      result.vision_fusion = { agreement, method }
    }
  }

  return result
}
