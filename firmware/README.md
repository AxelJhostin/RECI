# Reci · Firmware

Código del **ESP32** que controla la parte de bajo nivel del robot:

- Motores DC (driver L298N) para tracción punto a punto.
- Servos MG996R para las dos compuertas (vidrio / plástico).
- Sensores ultrasónicos HC-SR04 para detección de obstáculos.
- Tira LED WS2812B para señalización direccional.
- DFPlayer Mini para audio de personalidad.

## Stack

- C++ con framework Arduino sobre [PlatformIO](https://platformio.org/).
- Comunicación con la Raspberry Pi vía UART (protocolo propio liviano definido junto al equipo de IA).

## Responsables

Leonela Sornoza, Andrea Campaña (apoyo: Axel Hernández).

## Estado

Pendiente — se inicia en la **Fase 2** del cronograma (semanas 3–4).
