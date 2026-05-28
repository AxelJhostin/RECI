# Reci · IA + Sistema Experto

Código que corre en la **Raspberry Pi 4** del robot:

- Captura de cámara y clasificación de residuos con **MobileNet v2** (TensorFlow Lite).
- **Sistema experto** handcrafted con reglas IF-THEN para confirmar la decisión (umbrales de confianza, historial de la sesión, fallback a "desconocido").
- Reconocimiento facial opt-in (`face_recognition` o DeepFace) cuando el feature está activado por el usuario.
- Driver UART hacia el ESP32 para enviar comandos de compuerta y movimiento.
- Cliente del backend Reci Cloud para enviar telemetría y eventos de reciclaje.

## Stack

- Python 3.11 + TensorFlow Lite Runtime.
- Comunicación con el firmware vía UART.
- Comunicación con el cloud vía HTTPS / Supabase Realtime (o MQTT cuando se confirme).

## Responsables

Axel Hernández (apoyo: Andrea Campaña).

## Estado

Pendiente — se inicia en la **Fase 3** del cronograma (semanas 4–6).
