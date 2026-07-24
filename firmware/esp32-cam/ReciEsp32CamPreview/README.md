# Reci ESP32-CAM Preview

Sketch **solo para diagnóstico**. Reutiliza el flujo de clasificación de
`ReciEsp32Cam` y agrega una página local para ver la cámara mientras se envía
`C` por el Monitor Serial.

No modifica `ReciEsp32Cam.ino` ni el ejemplo `CameraWebServer` de Arduino.
Toma las credenciales existentes desde
`../ReciEsp32Cam/ReciEsp32CamSecrets.h`, por lo que primero debe estar
configurado el sketch normal de Reci.

## Uso

1. Abre `ReciEsp32CamPreview.ino` en Arduino IDE.
2. Selecciona **AI Thinker ESP32-CAM**, carga el sketch y abre el Monitor
   Serial a `115200`.
3. Abre la URL `http://IP_DE_LA_ESP32` que aparece como `Vista previa lista`.
4. Deja Safari mostrando el stream y escribe `C` + Enter en el Monitor Serial.
5. Observa simultáneamente las tres capturas y el resultado de clasificación.

`/capture` devuelve una sola foto JPEG y sirve para el script de dataset.
Al terminar las pruebas, vuelve a cargar `ReciEsp32Cam.ino` para usar el
firmware normal sin servidor de vista previa.
