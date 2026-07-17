# RECI — Contrato HTTP del robot ↔ cloud

> Para **Andrea** (cliente C++ en la ESP32-CAM) y **Leonela** (qué llega por UART).
> Versión: 1.0 · Julio 2026 · Fase 7

Todo lo que el robot le pide al cloud y le reporta al cloud. Si algo aquí no
coincide con el código, gana el código: `web/src/app/api/robot/`.

---

## Lo básico

**Base URL**

```
Producción:  https://<tu-app>.vercel.app
Desarrollo:  http://<ip-de-tu-compu>:3000
```

En desarrollo el ESP32 no puede usar `localhost` — eso apunta al propio ESP32.
Usa la IP de la máquina en la red del campus (la que sale como `Network:` cuando
arranca `npm run dev`).

**Autenticación** — todas las rutas de aquí van con la misma cabecera:

```
Authorization: Bearer <ROBOT_API_KEY>
```

Sin ella, o con una llave que no cuadra, la respuesta es `401 {"error":"No autorizado"}`.

> ⚠️ La `ROBOT_API_KEY` NO es la service role key de Supabase. Es una llave aparte
> que solo abre estas 4 rutas. Si el robot se pierde o alguien le lee el flash, se
> revoca esta llave sola y la base de datos no queda expuesta. **Nunca grabes la
> service role key en el firmware.**

**Formato** — todo JSON. Errores siempre `{"error": "mensaje en español"}`.

---

## El ciclo de vida de una llamada (Flujo B)

```
   APP (Paula)              CLOUD                    ROBOT (Andrea)
        │                     │                            │
        │  "ven a Biblioteca" │                            │
        ├────────────────────>│ call_requests              │
        │                     │   status: pending          │
        │                     │                            │
        │                     │<───────────────────────────┤  GET /calls/next
        │                     │  {call: {...}}             │  (cada 3s)
        │                     ├───────────────────────────>│
        │                     │                            │
        │                     │<───────────────────────────┤  POST /calls/update
        │                     │   status: in_progress      │  {status: in_progress}
        │  "Reci aceptó" 🚀   │                            │
        │<────────────────────┤ (Realtime)                 │
        │                     │                            │
        │                     │<───────────────────────────┤  POST /position
        │                     │   robot_positions          │  {status: moving}
        │  el mapa se mueve   │                            │
        │<────────────────────┤ (Realtime)                 │
        │                     │                            │
        │                     │         ... el robot maneja hasta el punto ...
        │                     │                            │
        │                     │<───────────────────────────┤  POST /calls/update
        │                     │   status: resolved         │  {status: resolved}
        │  "Reci llegó" 🎉    │                            │
        │<────────────────────┤ (Realtime)                 │
        │                     │<───────────────────────────┤  POST /position
        │                     │   status: idle             │
```

---

## 1 · ¿Me llamaron?

```
GET /api/robot/calls/next
```

El corazón del loop. Pregunta cada ~3 segundos.

**Nadie llamó** → `200`

```json
{ "call": null }
```

**Hay una llamada** → `200`

```json
{
  "call": {
    "id": "8f14e45f-ceea-467a-9c1e-3a0f8b2d4c11",
    "status": "pending",
    "point_id": "c9f0f895-fb98-4b1f-bcb0-1a2b3c4d5e6f",
    "point_name": "Biblioteca",
    "lat": -1.0512345,
    "lng": -80.4512345
  }
}
```

Notas para el firmware:

- El JSON es **plano a propósito** para que ArduinoJson no sufra: la cámara ya se
  come casi toda la RAM. `StaticJsonDocument<384>` alcanza de sobra.
- Devuelve la llamada más antigua primero (el que llamó antes, se atiende antes).
- **También devuelve llamadas que ya están en `in_progress`.** Si el ESP32 se
  reinicia a media ruta, al volver encuentra su viaje ahí y lo retoma. Revisa el
  campo `status`: si ya dice `in_progress`, no vuelvas a mandar el update de
  aceptación, sigue manejando.
- `lat`/`lng` son las del punto destino, sacadas de la tabla `robot_points`.

---

## 2 · Voy en camino / Ya llegué

```
POST /api/robot/calls/update
```

**Body**

```json
{ "call_id": "8f14e45f-...", "status": "in_progress" }
```

`status` solo acepta dos valores:

| valor | significa | cuándo mandarlo |
| --- | --- | --- |
| `in_progress` | "la acepté, voy" | apenas la tomas de `/calls/next` |
| `resolved` | "llegué al punto" | cuando el robot está físicamente ahí |

**OK** → `200`

```json
{ "call": { "id": "8f14e45f-...", "status": "resolved", "resolved_at": "2026-07-16T20:14:05.123Z" } }
```

**Respuestas que el firmware debe manejar**

| código | qué pasó | qué hacer |
| --- | --- | --- |
| `404` | la llamada no existe | suéltala, vuelve a `/calls/next` |
| `409` | la llamada cambió de estado | **el usuario la canceló.** Suéltala, frena, vuelve a `/calls/next`. No reintentes en bucle. |

El `409` es el caso real más importante: alguien llama a Reci, se aburre y
cancela mientras el robot va en camino. El robot tiene que enterarse y no seguir
manejando hacia un punto que ya nadie pidió.

---

## 3 · ¿Dónde estoy?

```
POST /api/robot/position
```

**Body**

```json
{ "point_id": "c9f0f895-...", "status": "moving" }
```

| campo | valores | nota |
| --- | --- | --- |
| `point_id` | uuid de `robot_points` | obligatorio |
| `status` | `idle` · `moving` · `charging` | opcional, default `idle` |

**Reci no tiene GPS.** Solo se mueve entre puntos fijos, así que no reporta
coordenadas: reporta **en qué punto está**, y el cloud resuelve lat/lng desde la
tabla. Por eso:

- `status: "moving"` + `point_id: X` significa **"voy hacia X"**, no "estoy en X".
- `status: "idle"` + `point_id: X` significa **"estoy en X"**.

**Manda esto solo cuando el estado CAMBIA** (salgo de un punto / llego a otro),
no en cada vuelta del `loop()`. Cada POST inserta una fila nueva y dispara un
evento de Realtime a todas las apps abiertas. Un robot que reporta cada 2
segundos durante 5 días son ~200.000 filas de basura.

**OK** → `201`

```json
{ "position": { "id": "...", "point_id": "...", "lat": -1.05, "lng": -80.45, "status": "moving", "recorded_at": "..." } }
```

---

## 4 · Las otras dos rutas (ya existían)

Mismo `Authorization: Bearer <ROBOT_API_KEY>`.

```
POST /api/vision/classify        → clasificar la foto (Fase 3, hoy es un stub)
POST /api/compartments/update    → {"id": "vidrio"|"plastico", "fill_percent": 0-100}
POST /api/events/recycle         → registrar el reciclaje y dar puntos
```

---

## Esqueleto del loop (pseudocódigo)

```cpp
String llamadaActual = "";

void loop() {
  if (llamadaActual == "") {
    // Ocioso: ¿me llamaron?
    Llamada c = getSiguienteLlamada();        // GET /calls/next
    if (c.existe) {
      llamadaActual = c.id;
      if (c.status == "pending") {
        actualizarLlamada(c.id, "in_progress");   // POST /calls/update
      }
      reportarPosicion(c.point_id, "moving");     // POST /position
      Serial1.print("CMD:FACE:moving\n");
      Serial1.print("CMD:OLED:Voy a " + c.point_name + "\n");
      empezarAManejarHacia(c.lat, c.lng);
    }
    delay(3000);                                  // polling cada 3s
    return;
  }

  // Ocupado: manejando hacia el punto
  manejarUnPaso();                                // ultrasonidos, motores, etc.

  if (llegueAlDestino()) {
    int r = actualizarLlamada(llamadaActual, "resolved");
    if (r == 409) { /* la cancelaron: soltar sin drama */ }
    reportarPosicion(puntoDestino, "idle");
    Serial1.print("CMD:FACE:happy\n");
    Serial1.print("CMD:OLED:Llegue! Deposita tu residuo\n");
    llamadaActual = "";
  }
}
```

---

## Antes de que esto funcione

- [ ] Aplicar la migración `20260716000001_robot_calls_dispatch.sql` en Supabase.
- [ ] Cargar los puntos del campus en `robot_points` — **hoy la tabla está vacía**
      y sin puntos no hay a dónde llamar a Reci ni de dónde sacar lat/lng.
- [ ] Poner `ROBOT_API_KEY` en el panel de Vercel (ya está en `web/.env.local` local).
- [ ] Andrea: WiFi del campus + `HTTPClient` + `ArduinoJson` en la ESP32-CAM.

---

*Proyecto RECI · PUCE Sede Manabí · PAO 2026-01*
