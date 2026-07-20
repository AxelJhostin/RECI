# ESP32-CAM de Reci

Este sketch es para el módulo **AI Thinker ESP32-CAM**. Captura una foto cada
10 segundos, pide reconocimiento al backend y manda el saludo al Mega por UART.
No guarda fotos ni contiene credenciales de Supabase.

## Antes de compilar

1. Instala `esp32 by Espressif Systems` desde el Gestor de tarjetas de Arduino
   IDE y `ArduinoJson` desde el Gestor de bibliotecas.
2. Copia `ReciEsp32CamSecrets.h.example` a `ReciEsp32CamSecrets.h` y rellena
   Wi-Fi, IP local de la Mac y `ROBOT_API_KEY`.
3. En la Mac, ejecuta la web con acceso de red:

   ```bash
   cd web
   npm run dev -- -H 0.0.0.0
   ```

   `RECI_API_BASE_URL` debe usar la IP de la Mac, no `127.0.0.1`. Puedes ver la
   IP Wi-Fi de la Mac con `ipconfig getifaddr en0`.

## Cableado ESP32-CAM ↔ Mega

| ESP32-CAM AI Thinker | Arduino Mega | Nota |
| --- | --- | --- |
| GPIO14 (TX) | RX2, D17 | conexión directa: 3.3 V es leído como HIGH por Mega |
| GPIO13 (RX) | TX2, D16, mediante divisor | protege el RX de 3.3 V del ESP32 |
| GND | GND común | obligatorio |
| 5V | Power Bank 5 V estable | no alimentar desde el Mega |

El divisor para **D16 del Mega → GPIO13 del ESP32** es:

```text
Mega D16 ── 1kΩ ──┬── GPIO13 / RX ESP32
                  │
                 2kΩ
                  │
                 GND común
```

La OLED y LCD se conectan al **Mega**, no a la ESP32:

```text
Mega D20/SDA -> SDA de OLED + SDA de LCD
Mega D21/SCL -> SCL de OLED + SCL de LCD
Mega GND     -> GND de OLED + GND de LCD
Mega 5V      -> VCC de OLED* + VCC de LCD
```

\* Revisa la etiqueta de la OLED: algunos módulos requieren 3.3 V.

## Cargar la ESP32-CAM

Con el adaptador ESP32-CAM-MB por USB, selecciona **AI Thinker ESP32-CAM** y el
puerto correcto. Si no carga automáticamente: GPIO0 a GND, pulsa Upload, quita
GPIO0 de GND al terminar y pulsa Reset. Abre el monitor serial a 115200 para ver
el resultado de cada reconocimiento.
