import { type NextRequest } from 'next/server'
import { ok, err } from '@/lib/api'
import { createClient } from '@/lib/supabase/server'

const fileExtension = (photo: File) => {
  if (photo.type === 'image/png') return 'png'
  if (photo.type === 'image/webp') return 'webp'
  return 'jpg'
}

// POST /api/face
// El usuario activa el reconocimiento facial y sube su foto al Storage
// Body: FormData con campo "photo" (File)
export async function POST(request: NextRequest) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return err('No autenticado', 401)

  let formData: FormData
  try { formData = await request.formData() } catch { return err('Body inválido', 400) }

  const photo = formData.get('photo')
  if (!(photo instanceof File)) return err('Se requiere un archivo en el campo "photo"', 400)

  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowedTypes.includes(photo.type)) return err('Solo se aceptan imágenes JPEG, PNG o WebP', 415)

  const maxSize = 5 * 1024 * 1024 // 5 MB
  if (photo.size > maxSize) return err('La imagen no puede superar 5 MB', 413)

  const { data: currentEmbedding } = await supabase
    .from('face_embeddings')
    .select('storage_path')
    .eq('user_id', user.id)
    .maybeSingle()

  const storagePath = `faces/${user.id}/${Date.now()}.${fileExtension(photo)}`
  const arrayBuffer = await photo.arrayBuffer()

  const { error: uploadError } = await supabase.storage
    .from('face-embeddings')
    .upload(storagePath, arrayBuffer, {
      contentType: photo.type,
      upsert: true,
    })

  if (uploadError) {
    console.error('face upload:', uploadError.message)
    return err('Error al subir la imagen', 500)
  }

  // Registrar o actualizar el embedding en la tabla
  const { error: dbError } = await supabase
    .from('face_embeddings')
    .upsert({ user_id: user.id, storage_path: storagePath, consent_signed_at: new Date().toISOString() })

  if (dbError) {
    await supabase.storage.from('face-embeddings').remove([storagePath])
    console.error('face_embeddings upsert:', dbError.message)
    return err('Error al registrar el consentimiento', 500)
  }

  if (currentEmbedding?.storage_path && currentEmbedding.storage_path !== storagePath) {
    await supabase.storage.from('face-embeddings').remove([currentEmbedding.storage_path])
  }

  // Marcar opt-in en el perfil
  await supabase.from('profiles').update({ facial_opt_in: true }).eq('id', user.id)

  return ok({ enrolled: true, storage_path: storagePath }, 201)
}

// DELETE /api/face
// El usuario revoca su consentimiento facial y se elimina la foto
export async function DELETE() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return err('No autenticado', 401)

  const { data: embedding } = await supabase
    .from('face_embeddings')
    .select('storage_path')
    .eq('user_id', user.id)
    .single()

  if (embedding) {
    await supabase.storage.from('face-embeddings').remove([(embedding as { storage_path: string }).storage_path])
    await supabase.from('face_embeddings').delete().eq('user_id', user.id)
  }

  await supabase.from('profiles').update({ facial_opt_in: false }).eq('id', user.id)

  return ok({ revoked: true })
}
