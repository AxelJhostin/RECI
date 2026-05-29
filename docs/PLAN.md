# Reci — Plan maestro

> Documento vivo. Se actualiza cada vez que cerramos una fase o cambiamos una decisión.
> Última actualización: 2026-05-28 · semana 0 (pre-arranque oficial).

Este documento responde a tres preguntas en orden:

1. ¿Qué ya está hecho? → [Estado actual](#estado-actual)
2. ¿Qué decisiones tomamos y por qué? → [Decisiones técnicas](#decisiones-técnicas)
3. ¿Qué falta y quién lo hace? → [Roadmap](#roadmap-por-fases) + [Backlog por subsistema](#backlog-por-subsistema)

Si buscas el alcance, los criterios de aceptación o los riesgos, eso vive en [`ACTA.md`](ACTA.md).

---

## Estado actual

### Hecho

- ✅ Acta de constitución aprobada (RECI-2026-PI v1.0).
- ✅ Repo en GitHub: [`PaulaMarquezM/Reci`](https://github.com/PaulaMarquezM/Reci) (privado).
- ✅ Estructura del repo: `web/`, `firmware/`, `ia/`, `docs/`.
- ✅ `web/` scaffolded con **Next.js 16.2 + React 19 + Tailwind 4 + TypeScript** (App Router, Turbopack, `src/` layout). Build y lint limpios.
- ✅ Landing en español (`/`) con el branding Reci y las funcionalidades destacadas.
- ✅ `firmware/` y `ia/` reservadas con README de stack y responsables.

### En curso

Nada por ahora — terminamos la semana 0 con la base lista.

### Bloqueado / pendiente de decidir

| Tema | Quién decide | Cuándo |
| --- | --- | --- |
| Proveedor de mapas (Leaflet+OSM gratis vs Mapbox token) | Paula | Antes de Fase 6 |
| Protocolo robot↔cloud (Supabase Realtime vs MQTT con HiveMQ) | Paula + Axel | Antes de Fase 5 |
| Dataset propio: cómo etiquetamos y dónde lo guardamos | Axel | Antes de Fase 3 |
| Puntos fijos del campus (coordenadas y nombres) | Paula con Decanato | Antes de Fase 2 |
| Proveedor de hardware final (Mercado Libre EC / local) | Leonela + Andrea | Semana 1 |

---

## Decisiones técnicas

Las decisiones del acta dejaban algunos "A o B" abiertos. Esto es lo que cerramos:

| Tema | Decisión | Razón |
| --- | --- | --- |
| Stack de la app | **Next.js PWA + Tailwind** | Un solo repo / stack para app + dashboard admin. Sin App Store/Play Store. La app vive como PWA instalable. |
| Stack del backend | **Supabase + Next.js API routes** | Auth, Postgres, Realtime y Storage en un solo proveedor. Sin servidor adicional que mantener. |
| Estructura del repo | Monorepo simple con carpetas por subsistema (`web/`, `firmware/`, `ia/`) | Cada persona trabaja en su carpeta sin pisar al resto. Una sola fuente de verdad. |
| Versión de Next | **Next 16.2** (lo que instaló `create-next-app` hoy) | Tiene Turbopack estable y React 19. La doc local en `node_modules/next/dist/docs/` es la fuente autoritativa porque trae breaking changes vs Next 15. |
| Idioma de la UI | Español (Ecuador) | Es para el campus PUCE Manabí. Solo el código y los commits van en inglés. |
| Hosting | **Vercel** para el front + Supabase Cloud para DB | Deploy automático desde main. Free tier alcanza para el piloto. |

---

## Roadmap por fases

Las 8 fases del acta, traducidas a entregables concretos y quién los hace. Las semanas son del cronograma del acta.

### Fase 1 — Diseño y planificación · semanas 1–2

**Objetivo:** todo el equipo entiende lo mismo y existe arquitectura detallada antes de teclear código.

- [x] Acta firmada
- [x] Repo creado + scaffold web
- [ ] **Paula** · arquitectura detallada (diagrama C4 nivel 1 y 2)
- [ ] **Paula** · wireframes de la app (5 pantallas: home/mapa, llamar, historial, cupones, ajustes)
- [ ] **Paula** · wireframe del dashboard admin
- [ ] **Axel** · plan del dataset (qué fotos, cuántas, cómo etiquetamos)
- [ ] **Leonela + Andrea** · diseño del circuito (Fritzing o KiCad) y BOM final con precios reales del proveedor
- [ ] **Todo el equipo** · acordar puntos fijos del campus con coordenadas GPS

### Fase 2 — Prototipo físico base · semanas 3–4

**Objetivo:** un chasis que se mueve entre dos puntos sin compuertas ni IA.

- [ ] **Leonela** · ensamble chasis + ruedas + driver L298N + motores DC
- [ ] **Leonela** · firmware ESP32 base con `forward / backward / stop`
- [ ] **Leonela** · sensores HC-SR04 con parada automática a ≤ 20 cm
- [ ] **Andrea** · batería LiPo + reguladores + cableado
- [ ] **Andrea** · prueba de movimiento punto-a-punto sobre cinta marcada

### Fase 3 — Sistema IA y experto · semanas 4–6

**Objetivo:** clasificación vidrio/plástico ≥ 85% en condiciones del campus.

- [ ] **Axel** · captura del dataset propio (≥ 500 imgs por clase) en el campus
- [ ] **Axel** · transfer learning de MobileNet v2 (Google Colab o Raspberry directo)
- [ ] **Axel** · conversión a TF Lite y prueba en Raspberry Pi 4
- [ ] **Axel** · base de reglas IF-THEN con umbral de confianza y memoria de sesión
- [ ] **Axel** · CLI de prueba que clasifica una imagen y devuelve `{material, confianza, decision}`

### Fase 4 — Integración Reci físico · semanas 6–8

**Objetivo:** el robot completo funciona standalone (sin nube).

- [ ] **Axel + Leonela** · protocolo UART Raspberry↔ESP32 (comando + payload + checksum)
- [ ] **Leonela** · servos MG996R abren la compuerta correcta según comando UART
- [ ] **Andrea** · OLED SSD1306 con animaciones de personalidad (cara feliz / triste / pensando)
- [ ] **Andrea** · WS2812B direccionales + DFPlayer con set de sonidos
- [ ] **Axel** · reconocimiento facial opt-in funcionando local (sin nube todavía)
- [ ] **Equipo** · demo: deposito botella → clasifica → abre compuerta correcta → emoji feliz + sonido

### Fase 5 — Backend y nube · semanas 7–10

**Objetivo:** API y base de datos listas para que la app y el robot conversen.

- [ ] **Paula** · proyecto Supabase creado + schema v1 (ver [Backlog cloud](#cloud--apppwa--paula))
- [ ] **Paula** · migraciones SQL versionadas en `web/supabase/migrations/`
- [ ] **Paula** · cliente Supabase tipado en `web/src/lib/supabase/`
- [ ] **Paula** · auth con magic link (Supabase Auth) + Google opcional
- [ ] **Paula** · API routes: `POST /api/events/recycle`, `POST /api/robot/position`, `GET /api/robot/current`, `POST /api/coupons/redeem`
- [ ] **Paula** · sistema de recompensas: trigger SQL que suma puntos al insertar `recycle_events`
- [ ] **Paula** · Storage policy para embeddings faciales cifrados (opt-in)
- [ ] **Paula** · deploy en Vercel con secretos en panel Vercel

### Fase 6 — App móvil · semanas 9–12

**Objetivo:** la app es usable end-to-end.

- [ ] **Paula** · mapa del campus con Leaflet (o Mapbox) + 2–3 puntos fijos
- [ ] **Paula** · posición de Reci en tiempo real via Supabase Realtime
- [ ] **Paula** · botón "Llamar a Reci" → POST al backend, animación de loading
- [ ] **Paula** · historial personal de reciclajes con paginación
- [ ] **Paula** · pantalla de cupones y canje con confirmación
- [ ] **Paula** · UI del opt-in facial + subida de foto + revocación de consentimiento
- [ ] **Paula** · PWA: `manifest.webmanifest`, service worker, instalable en home screen
- [ ] **Paula** · Push notifications (Web Push API + worker)

### Fase 7 — Integración end-to-end · semanas 12–14

**Objetivo:** los 3 flujos (A, B, C del acta) funcionan sin intervención manual.

- [ ] **Axel** · cliente Reci Cloud desde la Raspberry Pi (POST eventos, GET comandos)
- [ ] **Paula** · webhook o canal Realtime que despacha el comando "ven al punto X" hacia el robot
- [ ] **Equipo** · prueba completa de Flujo A (reciclaje estándar)
- [ ] **Equipo** · prueba completa de Flujo B (llamada desde la app)
- [ ] **Equipo** · prueba completa de Flujo C (facial opt-in)
- [ ] **Paula** · testing de carga del API con `k6` o `artillery`
- [ ] **Paula + Axel** · ajuste fino de umbrales de confianza con datos reales

### Fase 8 — Piloto en campus + cierre · semanas 14–16

**Objetivo:** Reci opera en el campus durante una semana y entregamos el proyecto.

- [ ] **Equipo** · despliegue real en 2 puntos del campus durante 5 días
- [ ] **Paula** · dashboard admin con métricas del piloto en `/admin` (Realtime)
- [ ] **Paula** · notificación a limpieza cuando un compartimento supera 80%
- [ ] **Equipo** · informe final con métricas vs criterios de aceptación
- [ ] **Equipo** · presentación a docentes

---

## Backlog por subsistema

### Cloud + App/PWA · Paula

Schema mínimo v1 a crear en Supabase (Fase 5):

| Tabla | Para qué | Campos clave |
| --- | --- | --- |
| `profiles` | Datos públicos del usuario (extiende `auth.users`) | `id (uuid)`, `display_name`, `avatar_url`, `facial_opt_in (bool)`, `created_at` |
| `recycle_events` | Cada reciclaje registrado | `id`, `user_id`, `material (vidrio\|plastico\|desconocido)`, `confidence (numeric)`, `robot_point_id`, `created_at` |
| `points_ledger` | Puntos por evento (append-only para auditoría) | `id`, `user_id`, `delta`, `reason`, `event_id`, `created_at` |
| `streaks` | Racha actual del usuario | `user_id`, `current_streak`, `longest_streak`, `last_recycle_at` |
| `coupons` | Catálogo de cupones canjeables | `id`, `title`, `description`, `cost_points`, `stock`, `active` |
| `coupon_redemptions` | Canjes hechos | `id`, `user_id`, `coupon_id`, `redeemed_at`, `code` |
| `robot_points` | Puntos fijos del campus | `id`, `name`, `lat`, `lng`, `notes` |
| `robot_positions` | Tracking de Reci (snapshot por segundo) | `robot_id`, `lat`, `lng`, `status (idle\|moving\|charging)`, `recorded_at` |
| `compartments` | Estado de los dos tachos | `id (vidrio\|plastico)`, `fill_percent`, `last_updated`, `last_emptied_at` |
| `call_requests` | Llamadas pendientes "ven aquí" | `id`, `user_id`, `point_id`, `status`, `created_at`, `resolved_at` |
| `face_embeddings` | Embeddings opt-in cifrados (Storage referenciado) | `user_id`, `storage_path`, `consent_signed_at` |
| `push_tokens` | Tokens Web Push del usuario | `user_id`, `endpoint`, `keys`, `created_at` |

Endpoints REST mínimos (Next.js Route Handlers en `web/src/app/api/`):

- `POST /api/events/recycle` — IA notifica que clasificó algo.
- `POST /api/robot/position` — Robot publica su posición.
- `GET /api/robot/current` — App pregunta dónde está Reci ahora.
- `POST /api/calls` — App pide que Reci venga a un punto.
- `POST /api/coupons/redeem` — Usuario canjea un cupón.
- `POST /api/compartments/update` — Robot reporta fill %.
- `POST /api/face/enroll` — Usuario activa facial y sube foto.
- `DELETE /api/face` — Usuario revoca consentimiento facial.

### Firmware · Leonela + Andrea

- ESP32 con PlatformIO. Lenguaje C++.
- Modos: `manual` (testing) y `commanded` (recibe órdenes UART desde Raspberry).
- Comandos básicos: `MOVE <forward|backward|left|right> <ms>`, `STOP`, `OPEN <vidrio|plastico>`, `LED <patrón>`, `SOUND <id>`.
- Hardware abstrahido en libs: `Motors.h`, `Servos.h`, `Ultrasonic.h`, `Leds.h`, `Audio.h`.

### IA · Axel

- Python 3.11 en Raspberry Pi 4 (64-bit OS).
- Pipeline: captura cámara → preprocess → MobileNet v2 (TF Lite) → reglas experto → decisión.
- Cliente UART hacia ESP32.
- Cliente HTTPS hacia Reci Cloud (Supabase REST + Realtime).
- Modo offline: si no hay red, encolar eventos en SQLite local y reintentar al reconectar.

---

## Métricas de éxito (recordatorio del acta)

| # | Criterio | Cómo lo medimos |
| --- | --- | --- |
| 1 | Clasificación ≥ 85% | Confusion matrix sobre 100 muestras reales en el piloto |
| 2 | Respuesta de la app ≤ 3 s | Lighthouse + log de la API |
| 3 | Recompensas en tiempo real | Trigger SQL inserta puntos en la misma transacción del evento |
| 4 | Dashboard admin ≤ 5 s de latencia | Supabase Realtime sub |
| 5 | Match facial ≥ 70% (≥ 90% en producción) | Score reportado por el modelo |
| 6 | Notificación de 80% lleno en ≤ 20 s | Timestamp del evento vs timestamp de la notif |
| 7 | Dashboard sin errores en navegadores modernos | Manual + Sentry o LogRocket |
| 8 | Canje descuenta y genera comprobante | E2E test con Playwright |
| 9 | Robot frena a ≤ 20 cm | Sensor + test físico con obstáculo |
| 10 | App en Android 10+, iOS 15+ | PWA + BrowserStack |

---

## Próximos pasos inmediatos (semana 1)

Por orden:

1. **Paula** — crear el proyecto Supabase y meter el schema v1 como migraciones SQL.
2. **Paula** — instalar `@supabase/supabase-js`, generar tipos y armar el cliente en `web/src/lib/supabase/`.
3. **Paula** — Auth con magic link funcionando + página `/app` protegida.
4. **Leonela + Andrea** — pedir el hardware al proveedor.
5. **Axel** — empezar la captura del dataset (mínimo 200 fotos en semana 1 para no llegar tarde a la fase 3).
6. **Equipo** — primer stand-up: lunes 09:00, 15 min, definir puntos fijos del campus.
