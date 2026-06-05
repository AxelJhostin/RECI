# Reci · IA + Sistema Experto

Módulo de clasificación de residuos que corre **en el cloud** (Next.js API Route).

La imagen viaja desde la ESP32-CAM al servidor, que ejecuta la inferencia y devuelve la decisión. No hay procesamiento local en el robot.

## Flujo

```
ESP32-CAM captura imagen
    ↓  POST /api/vision/classify  (multipart/form-data, campo "image")
Servidor recibe imagen
    ↓
Pipeline de clasificación (ver abajo)
    ↓
{ material: "vidrio"|"plastico"|"desconocido", confidence: 0.0–1.0 }
    ↓  respuesta HTTP JSON
ESP32-CAM reenvía decisión por UART → Arduino Mega
```

## Pipeline de clasificación (`src/app/api/vision/classify/`)

1. **Preprocesamiento**: resize a 224×224, normalización.
2. **Modelo**: MobileNet v2 fine-tuned en dataset propio (vidrio / plástico / fondo).
3. **Sistema experto**: reglas IF-THEN sobre la salida del modelo:
   - Si `confidence < 0.65` → `desconocido`.
   - Si la clase predicha y la segunda difieren menos de 0.10 → `desconocido`.
   - Si el historial de los últimos 3 eventos del mismo punto coincide → boost de +0.05.
4. **Respuesta**: `{ material, confidence, rule_applied }`.

## Stack

- **Modelo**: TensorFlow.js (`@tensorflow/tfjs-node`) o ONNX Runtime (`onnxruntime-node`) — a confirmar con Axel según el entorno de entrenamiento.
- **Entrenamiento**: Google Colab (exportar a SavedModel / ONNX).
- **Dataset**: capturas propias del campus (≥ 500 imágenes por clase).
- **Inferencia**: corre dentro del Route Handler de Next.js en Vercel (serverless).

## Reconocimiento facial (opt-in)

- El usuario sube su foto desde la app (`POST /api/face`).
- La foto se almacena en Supabase Storage (`face-embeddings/`).
- La ESP32-CAM envía una foto de la persona junto con el evento.
- El servidor compara embeddings (FaceAPI.js o similar) y asocia el reciclaje al usuario.

## Responsables

Axel Hernández.

## Estado

Pendiente — se inicia en la **Fase 3** del cronograma (semanas 4–6).  
El endpoint `/api/vision/classify` existe con un stub; Axel integra el modelo real en Fase 3.
