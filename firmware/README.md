# Reci · Firmware

Código de los dos microcontroladores del robot:

## Arduino Mega 2560 — cerebro de control

Gestiona toda la lógica de bajo nivel:

- **Movimiento**: 4 motorreductores TT via 2 drivers L298N.
- **Compuertas**: 2 servomotores SG5010 (una por compartimento vidrio/plástico).
- **Obstáculos**: sensores ultrasónicos HC-SR04 — parada automática a ≤ 20 cm.
- **Interfaz**: pantalla OLED 0.96" I2C con animaciones de estado.
- **Comunicación**: Serial/UART con el ESP32-CAM para recibir la decisión de clasificación.

## ESP32-CAM + OV2640 — sistema de visión

- Captura la imagen del residuo con la cámara OV2640.
- Envía la imagen vía WiFi al endpoint `POST /api/vision/classify` del cloud.
- Recibe la respuesta `{material, confidence}` del servidor.
- Reenvía la decisión al Arduino Mega por Serial/UART.
- También publica la posición y eventos al cloud directamente.

## Stack

- **Arduino Mega**: C++ con framework Arduino (Arduino IDE o PlatformIO).
- **ESP32-CAM**: C++ con framework Arduino + `HTTPClient` + `ArduinoJson`.
- Comunicación interna: UART entre ESP32-CAM (TX/RX) y Arduino Mega (Serial1).
- Comunicación externa: HTTPS desde ESP32-CAM → Reci Cloud.

## Protocolo UART interno (ESP32-CAM → Arduino Mega)

```
CMD:<accion>:<parametro>\n
```

Ejemplos:
- `CMD:OPEN:vidrio\n` — abrir compuerta de vidrio
- `CMD:OPEN:plastico\n` — abrir compuerta de plástico
- `CMD:OLED:Clasificando...\n` — mostrar mensaje en pantalla
- `CMD:STOP\n` — detener motores

## Energía

- **Power Bank 10,000 mAh** → 5V constantes para Arduino Mega, ESP32-CAM y OLED.
- **Batería LiPo** → potencia para motores DC via L298N.
- **Módulo LM2596** → regula LiPo a 5V para proteger la lógica.

## Responsables

Leonela Sornoza, Andrea Campaña (apoyo: Axel Hernández).

## Estado

Pendiente — se inicia en la **Fase 2** del cronograma (semanas 3–4).
