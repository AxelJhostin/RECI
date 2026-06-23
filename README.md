# RECI — Robot Inteligente de Reciclaje

> **Proyecto integrador — Pontificia Universidad Católica del Ecuador, Sede Manabí**  
> Carrera de Ingeniería de Software · Período PAO 2026-01  
> Materias: Sistemas Expertos (IS502) · Análisis y Circuitos Eléctricos · Tecnologías de Plataforma · Gestión de Proyectos  
> Repositorio: https://github.com/AxelJhostin/RECI

---

## Tabla de contenidos

1. [¿Qué es RECI?](#qué-es-reci)
2. [Arquitectura completa del sistema](#arquitectura-completa-del-sistema)
3. [Estructura de archivos](#estructura-de-archivos)
4. [Instalación desde cero](#instalación-desde-cero)
5. [Ejecución](#ejecución)
6. [Sistema experto — detalle técnico completo](#sistema-experto--detalle-técnico-completo)
7. [Modelo de Machine Learning](#modelo-de-machine-learning)
8. [Flujo de visión híbrido](#flujo-de-visión-híbrido)
9. [API REST](#api-rest)
10. [Integración hardware — pendiente](#integración-hardware--pendiente)
11. [Integración nube — guía para el equipo de plataforma](#integración-nube--guía-para-el-equipo-de-plataforma)
12. [Objetos reconocidos](#objetos-reconocidos)
13. [Pruebas formales](#pruebas-formales)
14. [Troubleshooting](#troubleshooting)
15. [Alineación académica IS502](#alineación-académica-is502)
16. [División del equipo](#división-del-equipo)
17. [Estado actual](#estado-actual)
18. [Changelog — historial de cambios](#changelog--historial-de-cambios)

---

## ¿Qué es RECI?

RECI es un **robot físico de reciclaje inteligente** diseñado para operar dentro del campus de la PUCE Sede Manabí. Es una plataforma rodante con dos compartimentos (vidrio / plástico) que, mediante visión artificial y un sistema experto, identifica el tipo de residuo que se deposita y abre únicamente la compuerta correcta.

**El sistema acepta únicamente plástico y vidrio.** Cualquier otro objeto es rechazado con mensaje al usuario.

### Subsistemas

| Subsistema | Descripción |
|---|---|
| **RECI Físico** | Plataforma rodante con 2 compartimentos, servo, sensores ultrasónicos, LEDs WS2812, pantalla OLED, audio, ESP32 |
| **RECI IA** | Módulo de visión (MobileNetV2 + Gemini) + sistema experto Python corriendo en Raspberry Pi 4 |
| **RECI Cloud** | Backend FastAPI + Supabase/PostgreSQL + dashboard admin Next.js |
| **RECI App** | Aplicación móvil (Next.js PWA o Flutter) con mapa en tiempo real, llamada al robot, sistema de recompensas |

### Contexto académico y competencia

Este proyecto participa en una **competencia entre las sedes de Portoviejo y Manta** de la PUCE Manabí. El mejor proyecto obtiene la nota máxima y puede ser patentado. El código fuente del sistema experto y el modelo ML son el núcleo diferenciador del proyecto.

---

## Arquitectura completa del sistema

### Diagrama de flujo — clasificación de un objeto

```
USUARIO deposita objeto frente a RECI
            ↓
Sensor detecta objeto
            ↓
Cámara captura imagen 1280×720 px
            ↓
MobileNetV2 (.tflite) — ~0.1 seg
Detecta clase (plastico/vidrio) + confianza
Da su "voto" como contexto para Gemini
            ↓
Gemini 2.5 Flash API — ~2 seg
Analiza la imagen visualmente con el contexto del TM
Extrae los 9 atributos del objeto real
(puede identificar papel, lata, cartón, etc.)
            ↓
  9 atributos visuales listos
          ↓
  Sistema Experto RECI
  (113 reglas · 12 meta-reglas · forward + backward chaining · CF MYCIN)
          ↓
  Conclusión: VIDRIO | PLÁSTICO | DESCONOCIDO | LATA | ORGÁNICO
          ↓
  Controlador físico ejecuta la acción:
  VIDRIO    → abre compuerta izquierda + LED azul
  PLASTICO  → abre compuerta derecha   + LED verde
  RECHAZADO → no abre nada             + LED rojo + mensaje
          ↓
  Evento enviado al backend en nube (FastAPI + Supabase)
          ↓
  App móvil recibe notificación con puntos ganados
```

### Capas del sistema

| Capa | Componente | Tecnología |
|---|---|---|
| Percepción | Cámara + MobileNetV2 | TensorFlow Lite, Python, Raspberry Pi 4 |
| IA / Experto | Motor de inferencia + 113 reglas IF-THEN | Python handcrafted (sin librerías de SE externas) |
| Control físico | Servomotores + sensores + cámara + LEDs + actuadores | Microcontrolador / placa (por definir) |
| Comunicación local | Controlador IA ↔ controlador físico | Protocolo por definir según hardware final |
| Backend / Nube | API REST + base de datos + eventos | FastAPI + Supabase (PostgreSQL) + Vercel |
| App móvil | Mapa, llamada al robot, recompensas | Next.js + Tailwind o Flutter + Dart |
| Dashboard admin | Panel de control web | Next.js + Supabase Realtime |

### Decisiones de hardware

```
Compuerta izquierda → VIDRIO   → servo 45°  → LED azul
Compuerta derecha   → PLÁSTICO → servo 135° → LED verde
Sin compuerta       → RECHAZADO→ servo 0°   → LED rojo  → mensaje audio + OLED
```

---

## Estructura de archivos

```
RECI/
├── expert_system/
│   ├── knowledge_base.py       # 113 reglas IF-THEN en 5 niveles + atributos válidos
│   ├── inference_engine.py     # Motor principal: forward chaining, CF MYCIN, meta-reglas
│   ├── working_memory.py       # Memoria de trabajo — hechos activos por ciclo de inferencia
│   ├── backward_chaining.py    # Encadenamiento hacia atrás — verificación de hipótesis
│   ├── certainty_factor.py     # Factor de Certeza estilo MYCIN (fórmula de combinación)
│   ├── meta_rules.py           # 12 meta-reglas que ajustan el razonamiento
│   ├── validator.py            # Validador de atributos antes de inferir
│   ├── statistics.py           # Estadísticas de sesión + payload para Supabase
│   └── explanation.py          # Reporte técnico completo exportable a JSON
│
├── vision/
│   ├── tm_classifier.py        # Clasificador MobileNetV2 (.tflite) — módulo principal
│   ├── attribute_extractor.py  # Extractor con Gemini API (fallback inteligente)
│   └── camera.py               # Captura en tiempo real — modo demo (ESPACIO) + producción
│
├── api/
│   ├── __init__.py
│   └── app.py                  # FastAPI — 8 endpoints REST, motor de inferencia compartido
│
├── tests/
│   ├── test_cases.py             # Runner principal — 74 pruebas formales
│   ├── test_backward_chaining.py # Pruebas dedicadas a los goals de backward chaining
│   └── casos/
│       ├── __init__.py
│       ├── casos_vidrio.py     # 9 casos de vidrio
│       ├── casos_plastico.py   # 18 casos de plástico
│       ├── casos_ambiguos.py   # 10 casos difíciles (PET vs vidrio)
│       ├── casos_extremos.py   # 4 casos extremos (baja confianza, desconocidos)
│       ├── casos_campus.py     # 26 casos con objetos reales del campus PUCE Manabí
│       └── casos_lata.py       # 7 casos de LATA y bordes con vidrio/plástico
│
├── model/                      # Modelo entrenado — NO está en el repo (ver instalación)
│   ├── model.tflite            # MobileNetV2 entrenado (99.7% precisión) — descargar aparte
│   ├── labels.txt              # Clases: 0 plastico / 1 vidrio
│   └── .gitkeep
│
├── images/
│   ├── capturas/               # Fotos capturadas por la cámara en tiempo real
│   ├── api_uploads/            # Fotos subidas por la API REST (gitignoreado — solo local)
│   └── prueba1-8.jpeg          # Imágenes de prueba incluidas en el repo
│
├── logs/                       # Logs de la API en producción — solo local, no en repo
│   └── reci.log                # Registro de clasificaciones, errores y eventos
├── fotos_dataset/              # Fotos tomadas con tomar_fotos.py — solo local, no en repo
├── RECI_entrenar_modelo.ipynb  # Notebook de Google Colab para entrenar el modelo
├── main.py                     # Punto de entrada principal — demo completo en consola
├── tomar_fotos.py              # Recolector de fotos con modo ráfaga automática
├── requirements.txt            # Dependencias Python del proyecto
├── .env                        # Variables de entorno — NO subir a GitHub
└── .gitignore
```

---

## Instalación desde cero

### Requisitos previos

- Python 3.9 o superior
- Cámara (integrada en laptop, módulo USB, o módulo Raspberry Pi Camera)
- Cuenta Google (para Gemini API y Google Colab)

### 1. Clonar e instalar dependencias

```bash
git clone https://github.com/AxelJhostin/RECI.git
cd RECI
pip3 install -r requirements.txt
```

**Dependencias principales:**

| Paquete | Versión mínima | Para qué sirve |
|---|---|---|
| fastapi | ≥ 0.128.0 | API REST |
| uvicorn | ≥ 0.39.0 | Servidor ASGI |
| opencv-python | ≥ 4.13.0 | Captura de cámara y procesamiento de imagen |
| tensorflow | ≥ 2.20.0 | Cargar y ejecutar el modelo .tflite |
| httpx | ≥ 0.28.0 | Llamadas async a la API de Gemini |
| pydantic | ≥ 2.13.0 | Validación de datos en la API |
| python-dotenv | ≥ 1.2.0 | Leer variables de entorno desde .env |
| numpy | ≥ 2.0.0 | Operaciones con arrays de imagen |

> **En Raspberry Pi:** reemplazar `tensorflow` por `tflite-runtime` para menor consumo de RAM:
> ```bash
> pip3 install tflite-runtime
> ```

### 2. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```
GEMINI_API_KEY=tu_api_key_aqui
```

Obtener API key gratuita en: https://aistudio.google.com/apikey

> Si no tienes API key de Gemini, el sistema funciona igualmente usando solo el modelo TFLite.
> Con la API configurada, Gemini **siempre** analiza la imagen visualmente (no solo como fallback) — ver sección [Flujo de visión híbrido](#flujo-de-visión-híbrido).

### 3. Obtener el modelo entrenado

El modelo `.tflite` no está en el repositorio por su tamaño (8.5 MB).

**Opción A — Descargar desde Google Drive del equipo:**
```bash
# El equipo comparte el modelo en Drive
# Descargar model.tflite y labels.txt → copiar a model/
cp ~/Downloads/model.tflite model/model.tflite
cp ~/Downloads/labels.txt   model/labels.txt
```

**Opción B — Entrenar el modelo desde cero:**
Ver sección [Reentrenar el modelo](#reentrenar-el-modelo).

**Opción C — Sin modelo (solo Gemini):**
Si no hay `model/model.tflite`, el sistema detecta su ausencia y usa Gemini automáticamente. No se necesita hacer nada adicional.

### 4. Verificar la instalación

```bash
# Verificar sistema experto (sin hardware, sin internet)
python3 tests/test_cases.py
# Resultado esperado: 74/74 pruebas aprobadas (100%)

# Verificar goals de backward chaining
python3 tests/test_backward_chaining.py
# Resultado esperado: 6/6 pruebas aprobadas (100%)

# Verificar API REST
uvicorn api.app:app --reload --port 8000
# Abrir en navegador: http://localhost:8000/health
# Debe responder: {"status": "ok", "total_reglas": 113, ...}
```

---

## Ejecución

```bash
# Modo cámara en tiempo real
python3 vision/camera.py
# ESPACIO = capturar y clasificar | P = corregir a PLÁSTICO | V = corregir a VIDRIO | Q = salir
# Requisito macOS: Ajustes del Sistema → Privacidad y Seguridad → Cámara → activar Terminal

# API REST completa
uvicorn api.app:app --reload --port 8000

# Pruebas formales del sistema experto
python3 tests/test_cases.py

# Clasificar una imagen directamente
python3 vision/tm_classifier.py images/prueba7.jpeg

# Tomar fotos para el dataset
python3 tomar_fotos.py plastico   # ESPACIO = 1 foto | R = ráfaga 60 seg
python3 tomar_fotos.py vidrio

# Demo completo en consola
python3 main.py
```

---

## Sistema experto — detalle técnico completo

### ¿Qué hace el sistema experto?

Recibe un diccionario de **9 atributos visuales** (extraídos por el modelo ML o por Gemini) y razona usando reglas IF-THEN para determinar si el objeto es VIDRIO, PLÁSTICO, o no permitido. Es la "inteligencia" del sistema que toma la decisión final.

### Uso básico

```python
from expert_system.inference_engine import InferenceEngine

engine = InferenceEngine()  # crear una sola vez — reutilizar para cada objeto
engine.cargar_hechos({
    "objeto_reconocido": "botella_agua",
    "confianza_ml":      "alta",
    "transparencia":     "alta",
    "color":             "transparente",
    "forma":             "cilindrica_estandar",
    "brillo":            "medio_difuso",
    "tapa":              "rosca_plastico",
    "textura":           "lisa_brillante",
    "rigidez":           "rigido"
})
conclusion, confianza, reglas = engine.ejecutar()
# conclusion = "PLASTICO", confianza = 0.998
print(engine.obtener_explicacion())  # trazabilidad completa
hardware = engine.decision_hardware()
# {"compuerta": "derecha", "led": "verde", "angulo_servo": 135, "mensaje": "..."}
```

> **Importante:** `cargar_hechos()` limpia el estado interno antes de cada clasificación.
> El motor se puede reutilizar sin reiniciarlo — de hecho así funciona la API para mayor eficiencia.

### Los 9 atributos visuales

Estos son los datos que el modelo ML extrae de la imagen y que el sistema experto recibe:

| Atributo | Valores posibles | Descripción |
|---|---|---|
| `objeto_reconocido` | Ver tabla completa abajo | Qué objeto identificó el modelo ML |
| `confianza_ml` | `alta` `media` `baja` | Qué tan seguro está el modelo ML |
| `transparencia` | `alta` `media` `baja` `ninguna` | Cuánto deja pasar la luz el objeto |
| `color` | `transparente` `ambar` `verde_oscuro` `blanco_opaco` `negro` `variado_vivo` `marron_tierra` `metalico` | Color predominante |
| `forma` | `cilindrica_delgada` `cilindrica_estandar` `cilindrica_ancha` `conica` `rectangular_plana` `irregular` | Forma geométrica |
| `brillo` | `alto_nitido` `medio_difuso` `bajo` `metalico` | Tipo de brillo en la superficie |
| `tapa` | `rosca_plastico` `corona_metalica` `twist_off_metalica` `tapa_ancha_metalica` `domo_plastico` `sin_tapa` `sellado` | Tipo de tapa o cierre |
| `textura` | `lisa_brillante` `lisa_sin_brillo` `rugosa` `fibrosa` | Textura de la superficie |
| `rigidez` | `rigido` `flexible` `indefinido` | Rigidez del material |

### Objetos reconocidos (`objeto_reconocido`)

| Valor | Categoría final | Descripción |
|---|---|---|
| `botella_agua` | PLASTICO | Tesalia, Pure Water, Güitig, Dasani, Cristal, BonAgua |
| `botella_gaseosa` | PLASTICO | Coca-Cola, Pepsi, Sprite, Fanta, 7UP, Powerade clear |
| `botella_energizante` | PLASTICO | Volt, 220V, Profit, Speed Max |
| `botella_alcoholica_plastico` | PLASTICO | Switch, Currimcho, 24-7 |
| `vaso_plastico` | PLASTICO | Vasos de cafetería, con o sin tapa domo |
| `yogur_plastico` | PLASTICO | Toni, Rey Leche, Chocolatada Toni Chiqui |
| `funda_plastico` | PLASTICO | Fundas negras o transparentes |
| `botella_fioravanti` | PLASTICO | Gaseosa ecuatoriana oscura |
| `botella_aceite_plastico` | PLASTICO | Alesol, El Cocinero, aceite en plástico |
| `botella_jugo_plastico` | PLASTICO | Pulp, Tampico, Frugos en plástico |
| `botella_enjuague_bucal` | PLASTICO | Colgate Plax, Listerine |
| `botella_cola_gallito` | PLASTICO | Cola Gallito — gaseosa ecuatoriana |
| `botella_gatorade` | PLASTICO | Gatorade — bebida deportiva boca ancha |
| `botella_mocachino` | VIDRIO | Caffe Lato Toni, Don Café |
| `botella_cerveza_vidrio` | VIDRIO | Pilsener, Club |
| `botella_salsa_vidrio` | VIDRIO | Gustadina, salsas en vidrio |
| `frasco_vidrio` | VIDRIO | Snob mermelada, frascos de conserva |
| `botella_jugo_vidrio` | VIDRIO | Jugos en vidrio, Natura vidrio |
| `botella_pony_malta` | VIDRIO | Pony Malta — malta ecuatoriana en vidrio |
| `vaso_carton` | ORGANICO | Vasos de cartón de cafetería |
| `tetra_pak` | ORGANICO | Del Valle, Sunny, Natura Tetra Pak |
| `cascara_fruta` | ORGANICO | Cáscaras de fruta |
| `restos_comida` | ORGANICO | Cualquier resto de comida |
| `papel_servilleta` | ORGANICO | Papel, servilletas |
| `carton` | ORGANICO | Cajas de cartón |
| `lata` | LATA | Red Bull, Monster lata, atún, Coca-Cola lata |
| `desconocido` | DESCONOCIDO | Objeto no identificable |

### Componentes del sistema experto

```
InferenceEngine
    ├── KnowledgeBase          → 113 reglas IF-THEN
    ├── WorkingMemory          → hechos activos del ciclo actual
    ├── AttributeValidator     → valida los 9 atributos antes de inferir
    ├── MetaRuleEngine         → 12 meta-reglas (ajustan EL CÓMO razonar)
    ├── CertaintyFactor        → combina evidencia de múltiples reglas (MYCIN)
    ├── BackwardChainingEngine → verifica la conclusión desde los hechos
    ├── RECIStatistics         → registra clasificaciones para el dashboard
    └── ExplanationReport      → reporte técnico exportable a JSON
```

### Ciclo de inferencia (orden de ejecución)

```
1. cargar_hechos()    → validar + cargar atributos en WorkingMemory
2. MetaRuleEngine     → 12 meta-reglas ajustan el contexto de razonamiento
3. Forward chaining   → evaluar las 113 reglas contra los hechos actuales
4. CF MYCIN           → combinar evidencia de las reglas disparadas por categoría
5. Ajustes meta       → aplicar exclusiones, prioridades y sesgos del contexto
6. BackwardChaining   → verificar la conclusión desde los hechos hacia atrás
7. decision_hardware()→ traducir conclusión a ángulo servo + LED + mensaje
```

### Niveles de reglas (113 reglas)

| Nivel | Cantidad | Descripción |
|---|---|---|
| **Nivel 1** | ~28 reglas | Reconocimiento directo: objeto conocido + confianza ML alta o media |
| **Nivel 2** | ~15 reglas | Razonamiento visual: ML con confianza media, se razona por atributos |
| **Nivel 3** | ~7 reglas | Desempate: plástico transparente vs vidrio transparente (el caso más difícil) |
| **Nivel 4** | ~6 reglas | Seguridad: baja confianza o desconocido → pide segunda captura |
| **Nivel 5** | ~57 reglas | Campus Manabí: productos ecuatorianos específicos con reglas propias |

### Meta-reglas (12)

Las meta-reglas no clasifican objetos. Ajustan **cómo** razona el sistema antes de evaluar las reglas normales:

| ID | Prioridad | Cuándo activa | Qué hace |
|---|---|---|---|
| MR01 | 10 | `confianza_ml = baja` | Potencia backward chaining, ignora objeto reconocido |
| MR02 | 9 | `forma = cilindrica_delgada` + `transparencia = alta` | Sesgo hacia PLÁSTICO +5% |
| MR03 | 10 | `tapa = corona_metalica` | Prioriza VIDRIO ×1.10 |
| MR04 | 10 | `rigidez = flexible` | Excluye VIDRIO completamente |
| MR05 | 9 | `brillo = metalico` + forma cilíndrica | Prioriza LATA ×1.15 |
| MR06 | 8 | `confianza_ml = alta` + objeto conocido | Potencia reglas de Nivel 1 ×1.20 |
| MR07 | 7 | `forma = irregular` + no rígido | Sesgo hacia ORGÁNICO +5% |
| MR08 | 9 | `tapa = twist_off_metalica` | Prioriza VIDRIO ×1.08 |
| MR09 | 10 | `color = metalico` + `forma = rectangular_plana` | Excluye LATA, sesgo PLÁSTICO +8% |
| MR10 | 6 | `objeto = desconocido` + `confianza_ml = media` | Modo cauteloso, umbral CF ≥ 0.70 |
| MR11 | 8 | `color = variado_vivo` + `brillo = bajo` + `transparencia = ninguna` | Sesgo PLÁSTICO +7% (Fioravanti, jugos) |
| MR12 | 9 | `forma = rectangular_plana` + `rigidez = rigido` + `transparencia = ninguna` | Excluye VIDRIO y LATA, sesgo ORGÁNICO +8% (Tetra Pak) |

### Factor de Certeza MYCIN

```
# Combinar dos CFs positivos:
CF_combinado = CF1 + CF2 × (1 - CF1)

# Bonus automático por especificidad (más condiciones = más confiable):
CF_final = CF_base + (num_condiciones - 1) × 0.01
# Regla con 5 condiciones: +0.04 de bonus sobre una regla con 1 condición

# Interpretación:
# CF ≥ 0.90 → CERTEZA MUY ALTA
# CF ≥ 0.75 → CERTEZA ALTA
# CF ≥ 0.55 → CERTEZA MEDIA
# CF ≥ 0.35 → CERTEZA BAJA
# CF < 0.10 → SIN CERTEZA
```

### Backward Chaining (verificación de hipótesis)

El backward chaining se ejecuta **después** del forward chaining como verificación. Parte de la conclusión obtenida y verifica si los hechos la sustentan desde atrás.

Cada categoría tiene un `Goal` con condiciones ponderadas:

**Condiciones eliminatorias:** algunas condiciones representan hechos "siempre/nunca" que no admiten excepción (ej. "una botella de vidrio siempre tiene tapa metálica"). Si una condición marcada `eliminatoria=True` falla, esa categoría queda **descartada por completo**, sin importar qué tan alto sea el score ponderado. Esto evita que una categoría "gane por puntaje" cuando le falta su rasgo más determinante.

**GOAL VIDRIO** (umbral: 60% de peso cumplido)

| Condición | Peso | Valores aceptados |
|---|---|---|
| rigidez | 1.00 | `rigido` |
| brillo | 0.95 | `alto_nitido` |
| tapa **[ELIMINATORIA]** | 0.90 | `corona_metalica` `twist_off_metalica` `tapa_ancha_metalica` |
| textura | 0.80 | `lisa_brillante` |
| color | 0.75 | `ambar` `verde_oscuro` `transparente` `variado_vivo` |
| forma | 0.70 | `cilindrica_estandar` `cilindrica_ancha` `cilindrica_delgada` |
| transparencia | 0.50 | `alta` `media` `baja` `ninguna` |

**GOAL PLÁSTICO** (umbral: 55%)

| Condición | Peso | Valores aceptados |
|---|---|---|
| tapa | 0.95 | `rosca_plastico` `domo_plastico` `sin_tapa` |
| brillo | 0.85 | `medio_difuso` `bajo` |
| textura | 0.75 | `lisa_brillante` `lisa_sin_brillo` |
| color | 0.70 | `transparente` `variado_vivo` `blanco_opaco` `negro` `ambar` |
| forma | 0.65 | `cilindrica_delgada` `cilindrica_estandar` `cilindrica_ancha` `conica` `irregular` |
| rigidez | 0.60 | `rigido` `flexible` |

**GOAL ORGÁNICO** (umbral: 55%)

| Condición | Peso | Valores aceptados |
|---|---|---|
| forma | 0.90 | `irregular` `rectangular_plana` |
| textura | 0.90 | `rugosa` `fibrosa` `lisa_sin_brillo` |
| brillo | 0.85 | `bajo` |
| color | 0.65 | `marron_tierra` `variado_vivo` `blanco_opaco` |
| transparencia | 0.60 | `ninguna` `baja` |

**GOAL LATA** (umbral: 70%)

| Condición | Peso | Valores aceptados |
|---|---|---|
| brillo **[ELIMINATORIA]** | 1.00 | `metalico` |
| color | 0.95 | `metalico` |
| rigidez | 0.85 | `rigido` |
| transparencia | 0.80 | `ninguna` |
| forma | 0.75 | `cilindrica_estandar` `cilindrica_delgada` |

LATA no tiene compuerta propia (va a tacho general junto con ORGÁNICO y DESCONOCIDO), pero su goal sí se evalúa: el riesgo real es que una regla de LATA le **robe** un caso a VIDRIO o PLASTICO, que sí tienen compuerta dedicada. Por eso "brillo metálico" — su rasgo más distintivo — es eliminatorio: sin él, LATA queda descartada aunque el resto del puntaje supere el umbral.

Si backward chaining contradice al forward chaining con score > 80%, el sistema genera una advertencia (no bloquea la decisión pero queda en el log). LATA está excluida de esta verificación de consistencia (junto con DESCONOCIDO), ya que no tiene compuerta propia.

---

## Modelo de Machine Learning

### Especificaciones

| Parámetro | Valor |
|---|---|
| Arquitectura | MobileNetV2 con transfer learning (ImageNet → RECI) |
| Formato | TensorFlow Lite (.tflite) — 8.5 MB |
| Resolución de entrada | 224 × 224 px, color RGB |
| Clases | `plastico`, `vidrio` |
| Precisión en validación | 98.2% |
| Tiempo de inferencia | ~0.1 segundos |
| Hardware compatible | Windows, Mac, Linux, Raspberry Pi 4 |

### Dataset de entrenamiento

Fotos tomadas en el campus PUCE Manabí con objetos reales, variando fondos, ángulos, distancias e iluminaciones:

| Clase | Total aprox. |
|---|---|
| plastico | ~14,900 fotos |
| vidrio | ~6,400 fotos |
| **Total** | **~21,347 fotos** |

### Proceso de entrenamiento (Google Colab)

Archivo: `RECI_entrenar_modelo.ipynb`  
Hardware: GPU Tesla T4 (gratuita en Colab)

- **Fase 1** — capas nuevas, 13 épocas: 99.1% de precisión
- **Fase 2** — fine-tuning últimas 30 capas, 8 épocas: 99.7% de precisión
- **Tiempo total:** ~3 horas

**Mejoras implementadas en el notebook (Junio 2026):**

| Mejora | Descripción |
|---|---|
| `RANDOM_SEED = 42` | Reproduce exactamente el mismo split en cada entrenamiento |
| `class_weight` automático | Calcula y aplica pesos para compensar que hay 2.3× más fotos de plástico que de vidrio |
| Semillas en capas de augmentation | `RandomFlip`, `RandomRotation`, `RandomZoom`, `RandomBrightness` ahora tienen `seed` fijo |
| Semillas en `image_dataset_from_directory` | El shuffle del dataset es reproducible entre ejecuciones |
| Métricas detalladas por clase | Cell 19 imprime precision, recall, F1-score y soporte para cada clase, además de la matriz de confusión |
| Carga explícita antes de exportar | Cell 21 carga `mejor_modelo_ft.keras` explícitamente antes de convertir a `.tflite`, con manejo de error si el archivo no existe |
| Path corregido | La ruta del dataset apunta a `RECI_dataset_propio/dataset_organizado` (path correcto en Drive) |

### Reentrenar el modelo con más fotos

```bash
# Paso 1 — Tomar fotos del campus con modo ráfaga
python3 tomar_fotos.py plastico   # R = ráfaga automática 1 foto/0.2s por 60s
python3 tomar_fotos.py vidrio
# Variar: ángulos, distancias, fondos, iluminación natural y artificial

# Paso 2 — Subir fotos a Google Drive en:
#   Mi unidad/RECI_dataset_propio/plastico/
#   Mi unidad/RECI_dataset_propio/vidrio/
# (Las fotos nuevas se mezclan con las existentes automáticamente)

# Paso 3 — Entrenar en Google Colab
#   colab.research.google.com → Abrir RECI_entrenar_modelo.ipynb
#   Activar GPU: Entorno de ejecución → Cambiar tipo de entorno → GPU T4
#   Ejecutar todos los pasos del notebook

# Paso 4 — Reemplazar el modelo
cp ~/Downloads/model.tflite model/model.tflite
cp ~/Downloads/labels.txt   model/labels.txt

# Paso 5 — Verificar
python3 vision/tm_classifier.py images/prueba7.jpeg
python3 tests/test_cases.py
```

> Los nombres de clase en el notebook deben ser exactamente `plastico` y `vidrio` (minúsculas, sin tilde). El `tm_classifier.py` los reconoce automáticamente.

---

## Flujo de visión híbrido

```
Cámara captura imagen (1280×720 px)
        ↓
MobileNetV2 (.tflite) — ~0.1 seg         ← siempre corre primero
Clasifica entre plastico/vidrio
Su resultado se pasa como CONTEXTO a Gemini
        ↓
Gemini 2.5 Flash API — ~2 seg             ← siempre se ejecuta
Analiza la imagen visualmente con el contexto del TM
Puede confirmar o corregir lo que dijo TM
Identifica el objeto real: botella PET, frasco de vidrio,
papel, lata, cartón, etc. — no solo las 2 clases del TM
Extrae los 9 atributos visuales
        ↓
9 atributos → Sistema Experto → Decisión final
```

**¿Por qué Gemini siempre actúa y no solo como fallback?**

El modelo TFLite solo conoce 2 clases: `plastico` y `vidrio`. Siempre elige una de las dos, incluso si el objeto es papel, una lata o cartón — y puede hacerlo con 100% de confianza aunque esté equivocado. Gemini ve la imagen real y puede identificar correctamente cualquier objeto, usando el voto del TM como referencia inicial pero sin estar limitado a esas dos clases.

Esto permite que el sistema experto produzca `DESCONOCIDO` (tacho general) para objetos que no son plástico ni vidrio, cumpliendo el alcance del proyecto.

**¿Cómo le habla el TM a Gemini?**

TM corre en ~0.1 seg y pasa su voto dentro del prompt de Gemini como contexto, así:

```
CONTEXTO DEL CLASIFICADOR RÁPIDO (MobileNetV2):
El modelo detectó 'plastico' con 99% de confianza.
Úsalo como referencia inicial, pero confía en tu análisis visual si ves algo diferente.
```

Gemini puede confirmar o ignorar ese voto si ve algo distinto — lo que importa es su análisis visual.

**Respuesta JSON estructurada:**

Gemini recibe la instrucción `responseMimeType: application/json`, por lo que devuelve JSON puro directamente, sin texto extra ni markdown. Esto lo hace más confiable y rápido de parsear.

**Fallback automático si Gemini no está disponible:**

Si Gemini falla (429 rate limit, 503 servicio caído, timeout u otro error de red), el sistema cae automáticamente al resultado del TM sin interrumpir la clasificación ni mostrar pantallas de error. Hay dos capas de protección:

1. **Dentro de `analizar_y_clasificar_hibrido()`** — cubre cualquier llamador: cámara, API y tests de imágenes.
2. **Dentro de `camera.py._analizar()`** — segunda línea de defensa específica para el modo demo.

**Tiempo total por clasificación:**
- Flujo híbrido TM + Gemini: ~2–5 seg
- Fallback solo TM: ~0.1 seg

### Modo demo — cámara en tiempo real

La ventana de cámara tiene 4 estados secuenciales:

| Estado | Lo que ocurre |
|---|---|
| **PREVIEW** | Cámara en vivo — colocar el objeto frente a la cámara |
| **COUNTDOWN** | Cuenta regresiva de 1 segundo — mantener el objeto quieto |
| **ANALIZANDO** | Pantalla oscura con barra de progreso animada real — TM + Gemini corren en hilo separado mientras la animación se mueve |
| **RESULTADO** | Clasificación mostrada 5 segundos con destino, confianza y barra de color |

**Controles:**
- `ESPACIO` — capturar y clasificar (funciona en PREVIEW o en RESULTADO para siguiente objeto)
- `P` — corregir manualmente a PLÁSTICO si el sistema se equivocó
- `V` — corregir manualmente a VIDRIO si el sistema se equivocó
- `Q` — salir del modo demo

**Destinos en pantalla:**
- `VIDRIO` → texto naranja, indica compuerta izquierda
- `PLASTICO` → texto verde, indica compuerta derecha
- `LATA` / `ORGANICO` / `DESCONOCIDO` → texto rojo, indica tacho general (corregible con P o V)

> En producción el sensor ultrasónico de la Raspberry Pi reemplaza el `ESPACIO`: detecta automáticamente cuando hay un objeto frente a la cámara y dispara la captura.

---

## API REST

### Iniciar el servidor

```bash
uvicorn api.app:app --reload --port 8000
```

Documentación interactiva (Swagger): `http://localhost:8000/docs`

### Endpoints

| Endpoint | Método | Descripción |
|---|---|---|
| `/` | GET | Info general + modo de visión activo (TM o Gemini) |
| `/health` | GET | Estado del sistema: reglas cargadas, modo visión, modelo TM disponible |
| `/reglas` | GET | Total y distribución de reglas por categoría |
| `/clasificar/atributos` | POST | Clasificar enviando los 9 atributos en JSON (usa el Raspberry Pi en producción) |
| `/clasificar/imagen` | POST | Clasificar desde una imagen (TM o Gemini automático según disponibilidad) |
| `/estadisticas` | GET | Estadísticas de la sesión para el dashboard |
| `/historial` | GET | Historial de clasificaciones (`?limite=20`) |
| `/reset` | POST | Resetear estadísticas de la sesión |

### Estructura completa del JSON de respuesta

```json
{
  "success": true,
  "timestamp": "2026-05-29T14:30:00",
  "clasificacion": "PLASTICO",
  "confianza": 0.998,
  "confianza_pct": 99.8,
  "es_reciclable": true,
  "hardware": {
    "compuerta": "derecha",
    "led": "verde",
    "angulo_servo": 135,
    "mensaje": "PLÁSTICO detectado — abriendo compartimento derecho"
  },
  "atributos": {
    "objeto_reconocido": "botella_agua",
    "confianza_ml": "alta",
    "transparencia": "alta",
    "color": "transparente",
    "forma": "cilindrica_estandar",
    "brillo": "medio_difuso",
    "tapa": "rosca_plastico",
    "textura": "lisa_brillante",
    "rigidez": "rigido"
  },
  "reglas_disparadas": 7,
  "backward_chaining": {
    "conclusion": "PLASTICO",
    "score": 1.0,
    "consistente": true
  },
  "meta_reglas_aplicadas": ["MR06"],
  "advertencias": [],
  "payload_supabase": {
    "timestamp": "2026-05-29T14:30:00",
    "clasificacion": "PLASTICO",
    "confianza": 0.998,
    "objeto_reconocido": "botella_agua",
    "reglas_disparadas": 7,
    "backward_consistente": true,
    "es_reciclable": true,
    "compuerta": "derecha",
    "sede": "PUCE Manabí"
  }
}
```

### Optimizaciones implementadas

El motor de inferencia (`InferenceEngine`) y el clasificador TM (`TeachableMachineClassifier`) se crean **una sola vez** al iniciar la API y se reutilizan en cada petición. Esto es crítico para el rendimiento en Raspberry Pi: crearlos desde cero en cada llamada tarda ~4x más que reutilizarlos.

El endpoint `/clasificar/imagen` usa el **mismo flujo híbrido TM+Gemini** que la cámara en tiempo real — no usa TM o Gemini por separado como antes.

Las imágenes subidas en `images/api_uploads/` se limpian automáticamente: el sistema conserva solo los 50 archivos más recientes para evitar que el almacenamiento de la Raspberry Pi se llene.

### Logging persistente

Cada clasificación, error y evento de inicio queda registrado en `logs/reci.log`:

```
2026-06-22 21:45:12 | INFO | API iniciada | modo=HIBRIDO_TM_GEMINI
2026-06-22 21:45:38 | INFO | clasificar_imagen | PLASTICO 99.8% | vision=hibrido_tm_gemini | archivo=foto.jpg
2026-06-22 21:45:41 | INFO | clasificar_atributos | VIDRIO 100.0% | objeto=botella_mocachino
2026-06-22 21:46:02 | WARNING | Gemini falló (ReadTimeout) — fallback a TM
```

Útil para diagnosticar errores en producción (Raspberry Pi) sin necesidad de conectar un monitor.

---

## Integración hardware — pendiente

> **Esta sección se completará una vez que el equipo defina los componentes físicos definitivos.**
>
> Lo que el software ya deja listo para cuando se conecte el hardware:
> - La API REST expone en cada respuesta: `hardware.angulo_servo`, `hardware.compuerta`, `hardware.led` y `hardware.mensaje` — los valores exactos que el controlador físico necesita para actuar.
> - El motor de inferencia ya toma la decisión final y la traduce a acción de hardware. El código de circuitos solo necesita leer ese resultado y ejecutarlo.
> - La lógica de clasificación es completamente independiente del hardware: el mismo sistema experto funciona con cualquier microcontrolador o placa que pueda comunicarse con Python.
>
> **Componentes que se van a usar (por confirmar):** cámara, servomotores, sensores ultrasónicos, y otros. Los detalles de conexión, pines, protocolos y código de hardware se documentarán aquí una vez que estén definidos.

---

## Integración nube — guía para el equipo de plataforma

### Consumir la API desde Next.js

```javascript
// Clasificar desde imagen (para el dashboard)
const formData = new FormData()
formData.append('file', imagenBlob, 'objeto.jpg')

const response = await fetch('http://localhost:8000/clasificar/imagen', {
  method: 'POST',
  body: formData
})
const resultado = await response.json()
// resultado.clasificacion, resultado.hardware, resultado.payload_supabase

// Estadísticas para el dashboard
const stats = await fetch('http://localhost:8000/estadisticas').then(r => r.json())
// stats.datos.total_vidrio, stats.datos.total_plastico, stats.datos.tasa_exito_pct

// Historial de clasificaciones
const historial = await fetch('http://localhost:8000/historial?limite=20').then(r => r.json())
```

### Payload para Supabase

Cada clasificación produce automáticamente un payload listo para insertar en Supabase:

```json
{
  "timestamp": "2026-05-29T14:30:00",
  "clasificacion": "PLASTICO",
  "confianza": 0.998,
  "objeto_reconocido": "botella_agua",
  "reglas_disparadas": 7,
  "backward_consistente": true,
  "es_reciclable": true,
  "compuerta": "derecha",
  "sede": "PUCE Manabí"
}
```

### Tabla sugerida en Supabase

```sql
CREATE TABLE clasificaciones (
  id              BIGSERIAL PRIMARY KEY,
  timestamp       TIMESTAMPTZ DEFAULT NOW(),
  clasificacion   TEXT NOT NULL,          -- VIDRIO / PLASTICO / DESCONOCIDO / etc.
  confianza       FLOAT,
  objeto_reconocido TEXT,
  reglas_disparadas INT,
  backward_consistente BOOLEAN,
  es_reciclable   BOOLEAN,
  compuerta       TEXT,
  sede            TEXT DEFAULT 'PUCE Manabí',
  usuario_id      UUID REFERENCES usuarios(id)  -- opcional para gamificación
);
```

---

## Objetos reconocidos

### Plástico → compuerta derecha (servo 135°, LED verde)

Botellas de agua: Tesalia, Pure Water, Güitig, Dasani, BonAgua, Cristal, pomo PUCE  
Gaseosas: Coca-Cola, Pepsi, Sprite, Fanta, 7UP, **Cola Gallito**  
Energizantes: Volt, **220V**, Profit, Speed Max, Powerade  
Deportivas: **Gatorade** (boca ancha)  
Alcohólicas en plástico: Switch, Currimcho, 24-7, **Zhumir**  
Vasos: vasos de cafetería transparentes con o sin tapa domo  
Lácteos: yogur Toni, Rey Leche, Chocolatada Toni Chiqui  
Higiene: Colgate Plax, Listerine  
Otros: fundas plásticas, Monster negro, **Fioravanti**, **Pulp**, **Tampico**, aceite de cocina en plástico

### Vidrio → compuerta izquierda (servo 45°, LED azul)

Mocachinos: Caffe Lato Toni, Don Café  
Cervezas: Pilsener, Club verde, Club negra  
Maltas: **Pony Malta**  
Salsas: Gustadina, salsa de soya  
Frascos: Snob mermelada, conservas  
Jugos en vidrio, aceite de cocina en vidrio, **Güitig vidrio**

### No permitidos → mensaje de rechazo, servo 0°, LED rojo

Latas de aluminio (Red Bull, Monster lata, Coca-Cola lata, atún), **Tetra Pak** (Del Valle, Sunny, Natura), cartón, papel, servilletas, cáscaras de fruta, restos de comida, cualquier objeto no identificado

---

## Pruebas formales

```bash
python3 tests/test_cases.py
```

**Resultado actual: 74/74 pruebas aprobadas (100%)**

| Categoría | Resultado | Objetos cubiertos |
|---|---|---|
| VIDRIO | 9/9 (100%) | Mocachino, Pilsener, Club, frasco, salsa, Güitig, salsa soya |
| PLASTICO | 18/18 (100%) | Agua, Coca-Cola, Sprite, vaso, energizante, Switch, yogur, funda, Monster, Pepsi, Fanta, 220V |
| AMBIGUO | 10/10 (100%) | PET vs vidrio transparente, vaso cartón vs plástico, funda vs cáscara |
| EXTREMO | 4/4 (100%) | Objeto desconocido baja confianza, atributos incompletos |
| CAMPUS_PLASTICO | 17/17 (100%) | Powerade, Dasani, Chocolatada, Colgate Plax, Speed Max, **Gatorade**, **Cola Gallito**, **Fioravanti** |
| CAMPUS_VIDRIO | 7/7 (100%) | Mocachino campus, Pilsener campus, **Pony Malta** |
| CAMPUS_ORGANICO | 2/2 (100%) | **Tetra Pak Del Valle**, Tetra Pak por atributos visuales |
| LATA | 7/7 (100%) | Lata de aluminio (ML y por atributos), lata aplastada, lata ancha (atún), y bordes con VIDRIO/PLASTICO ante color/brillo metálico |

Para agregar nuevos casos de prueba: editar el archivo correspondiente en `tests/casos/` sin tocar `test_cases.py`.

Además, `tests/test_backward_chaining.py` valida directamente los goals de `BackwardChainingEngine` (6/6 casos), incluyendo las condiciones eliminatorias de VIDRIO y LATA:

```bash
python3 tests/test_backward_chaining.py
```

---

## Troubleshooting

### El modelo no carga
```
FileNotFoundError: Modelo no encontrado: model/model.tflite
```
**Solución:** El modelo no está en el repo. Ver sección [Obtener el modelo entrenado](#3-obtener-el-modelo-entrenado).

### TensorFlow no instala en Mac
```
ERROR: Could not find a version that satisfies the requirement tflite-runtime
```
**Solución:** En Mac usar TensorFlow completo:
```bash
pip3 install tensorflow
```

### Cámara sin permisos en Mac
```
OpenCV: not authorized to capture video (status 0)
```
o bien (macOS bloquea silenciosamente y el sistema lo detecta):
```
❌ La cámara se abrió pero no entrega imágenes (ret=False).
  → En macOS, ve a Ajustes del Sistema → Privacidad y Seguridad → Cámara
    y habilita el permiso para tu Terminal/IDE. Luego reinicia la Terminal.
```
**Solución:**
```
Ajustes del Sistema → Privacidad y Seguridad → Cámara → Activar Terminal (o IDE)
Cerrar y reabrir la Terminal completamente.
```
El sistema detecta automáticamente el fallo silencioso de macOS donde `isOpened()` devuelve `True` pero `read()` falla, y muestra un mensaje claro con instrucciones.

### Cámara no abre en Raspberry Pi
```
Cannot open camera index 0
```
**Solución:** Verificar el índice correcto:
```python
# Probar índices 0, 1, 2... hasta encontrar la cámara
import cv2
for i in range(3):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Cámara encontrada en índice {i}")
        cap.release()
```
En la Raspberry Pi Camera Module usar `cv2.VideoCapture(0)` con el driver V4L2 activado.

### Gemini da error 503 / 429 / timeout

| Error | Causa |
|---|---|
| `429 Too Many Requests` | Rate limit por minuto (esperar 60s) o cupo diario agotado (esperar 00:00 UTC) |
| `503 Service Unavailable` | Servidor de Google temporalmente caído |
| `ReadTimeout` | La respuesta tardó más de 60 segundos |

**El sistema maneja todos estos errores automáticamente** — cae al modo TM-solo sin mostrar ningún error al usuario ni interrumpir la clasificación. La cámara y la API siguen funcionando con normalidad, con menor precisión en objetos ambiguos.

La API gratuita de Gemini 2.5 Flash tiene ~250 requests/día. Si se hacen muchas pruebas seguidas (ej. 16 imágenes × varias sesiones), el cupo puede agotarse. Para uso intensivo, considerar una API key de pago (Gemini o Claude API).

### Las pruebas fallan después de cambiar reglas
```bash
python3 tests/test_cases.py
```
Si algún caso falla, el output muestra exactamente qué reglas se dispararon. Revisar `knowledge_base.py` en el nivel de regla correspondiente. El ID de cada regla indica su nivel (R01-R19: nivel 1, R20-R51: nivel 2, etc.).

### La API da error al importar
```
ModuleNotFoundError: No module named 'expert_system'
```
**Solución:** Ejecutar la API siempre desde la raíz del proyecto:
```bash
cd /ruta/a/RECI
uvicorn api.app:app --reload --port 8000
```

---

## Alineación académica IS502

| Resultado de aprendizaje | Implementado en |
|---|---|
| Fundamentos de sistemas expertos | `knowledge_base.py` + `inference_engine.py` |
| Relación SE con IA | Arquitectura híbrida MobileNetV2 + SE handcrafted + Gemini |
| Encadenamiento hacia adelante | `InferenceEngine.ejecutar()` — loop sobre 113 reglas |
| Encadenamiento hacia atrás | `BackwardChainingEngine` — verificación de hipótesis por goals ponderados |
| Factor de Certeza MYCIN | `CertaintyFactor` — fórmula de combinación + bonus por especificidad |
| Meta-conocimiento | `MetaRuleEngine` — 12 meta-reglas que controlan el razonamiento |
| Diseño e implementación de SE | Todo el módulo `expert_system/` — 9 componentes independientes |
| Evaluación ética | `ExplanationReport` — trazabilidad completa de cada decisión con reglas y CFs |
| Validación del SE | 74 pruebas formales organizadas por categoría + 6 pruebas de backward chaining, 100% de aprobación |

---

## División del equipo

| Responsable | Área principal | Secundaria |
|---|---|---|
| **Axel Hernández** | Sistema experto + modelo ML + integración IA | Diseño de circuito |
| **Paula Márquez** | App móvil + nube | Gestión del proyecto + hardware |
| **Leonela Sornoza** | App móvil + nube | Hardware + testing |
| **Andrea Campaña** | Sistema experto + IA | Hardware + testing |

**Docentes evaluadores:**
- Ing. Alex Fernando Ricaurte Segovia — Gestión de Proyectos
- Ing. Josselyn Tatiana Gómez — Sistemas Expertos
- Ing. Alexander Mackenzie — Tecnologías de Plataforma

---

## Estado actual

### Completado ✅

**Sistema experto:**
- **113 reglas**, forward + backward chaining, CF MYCIN, **12 meta-reglas**
- Productos ecuatorianos: Fioravanti, Cola Gallito, Gatorade, Pony Malta, Tetra Pak, Güitig vidrio, Zhumir, Pulp/Tampico, aceite de cocina, Colgate Plax/Listerine
- Validador de atributos, estadísticas, reporte técnico JSON
- **74/74 pruebas formales (100%)** — campus, ambiguos, extremos, LATA
- Condiciones eliminatorias en backward chaining: VIDRIO requiere tapa metálica, LATA requiere brillo metálico — ambas con 6/6 pruebas dedicadas

**Modelo ML:**
- MobileNetV2 propio (**98.2% precisión**, **21,347 fotos** del campus PUCE Manabí)
- Notebook mejorado: semillas reproducibles (`RANDOM_SEED=42`), `class_weight` automático, métricas por clase (precision/recall/F1), matriz de confusión, path de dataset corregido

**Visión e IA:**
- Flujo híbrido TM + Gemini: TM da contexto → Gemini analiza visualmente → SE decide
- Gemini configurado con `responseMimeType: application/json` — respuesta JSON directa sin parseo manual
- Fallback automático y silencioso a TM-solo cuando Gemini falla (429, 503, timeout)

**Cámara:**
- Modo demo con 4 estados (PREVIEW → COUNTDOWN → ANALIZANDO → RESULTADO)
- Análisis TM+Gemini corre en **hilo separado (threading)** — la barra de progreso animada es real, la interfaz nunca se congela
- Corrección manual con `P`/`V` disponible en cualquier momento

**API REST:**
- Motor de inferencia **y** clasificador TM cargados globalmente — **4x más rápido** en Raspberry Pi
- `/clasificar/imagen` usa flujo híbrido TM+Gemini (igual que la cámara)
- Limpieza automática de `api_uploads/` — conserva solo los 50 más recientes
- **Logging persistente en `logs/reci.log`** — registro de clasificaciones, errores y eventos de producción

**Otros:**
- Prompts de Gemini con guía explícita de objetos no permitidos (papel, lata, cartón)
- Script de recolección de fotos con modo ráfaga automática
- Pruebas de imágenes reales con reporte de tiempo por imagen y promedio de sesión

### En progreso 🔄

- Pruebas de imágenes reales con flujo híbrido completo: 13/16 con Gemini disponible (2 fallos por TM sin clase de vidrio Gatorade, 1 fallo por ambigüedad visual papel/vaso) — mejorable reentrenando el modelo con más variedad de botellas de vidrio y vasos plásticos oscuros
- Integración con hardware físico

### Pendiente ⏳

- Integración con el hardware físico (equipo hardware — esperando definir componentes y tenerlos disponibles)
- Plataforma física: cámara, servomotores, sensores ultrasónicos y demás componentes (por definir)
- Movimiento autónomo entre 2-3 puntos fijos del campus
- Dashboard Next.js + Supabase Realtime (equipo nube)
- App móvil con mapa en tiempo real y sistema de recompensas
- Reconocimiento facial opt-in (fase 2)
- Notificación automática cuando compartimento supera 80% de capacidad

### Criterios de aceptación del proyecto

| Criterio | Umbral | Estado actual |
|---|---|---|
| Precisión clasificación vidrio/plástico | ≥ 85% | **98.2%** modelo · **81.2%** pruebas imagen (Gemini sin cupo) ✅ |
| Tiempo de respuesta flujo híbrido | ≤ 3 seg | ~2–2.5 seg ✅ |
| Tiempo de respuesta app al punto más cercano | ≤ 3 seg | Pendiente |
| Sistema de recompensas registra correctamente | — | Pendiente |
| Dashboard con latencia | ≤ 5 seg | Pendiente |
| Reconocimiento facial opt-in | ≥ 70% confianza | Pendiente |
| Notificación compartimento lleno | ≤ 20 seg | Pendiente |
| Robot detecta y se detiene ante obstáculos | ≤ 20 cm | Pendiente |

---

---

## Changelog — historial de cambios

### Junio 2026 — v2.1 (mejoras de producción)

**`vision/attribute_extractor.py`**
- Gemini ahora recibe `responseMimeType: application/json` y `maxOutputTokens: 256` → devuelve JSON puro, sin markdown ni texto extra. Elimina toda la lógica manual de limpieza de respuesta.
- Logging con `logger.info` en cada llamada a Gemini para trazabilidad en producción.
- Método `_parsear_json()` como fallback defensivo para parsear la respuesta de Gemini incluso si viene con texto extra (segunda línea de defensa).

**`vision/camera.py`**
- El análisis TM+Gemini ahora corre en un **hilo separado** (`threading.Thread`). Antes, la pantalla "Analizando..." se congelaba mientras se esperaba la respuesta de Gemini (2–5 seg). Ahora la barra de progreso se anima de verdad porque el hilo principal de OpenCV nunca se bloquea.
- Se usa `resultado_hilo = []` (lista compartida) para pasar el resultado del hilo de análisis al hilo de visualización de forma segura.

**`api/app.py`**
- `TeachableMachineClassifier` se carga **una sola vez al inicio** (variable `tm_global`) en lugar de en cada request. Mejora el tiempo de respuesta ~4x en Raspberry Pi.
- `/clasificar/imagen` ahora usa el flujo híbrido TM+Gemini completo, igual que la cámara. Antes usaba solo TM o Gemini por separado.
- `_limpiar_uploads()` limpia `images/api_uploads/` automáticamente conservando solo los 50 más recientes.
- Logging persistente configurado al arranque: todas las clasificaciones y errores se guardan en `logs/reci.log` con nivel INFO.

**`RECI_entrenar_modelo.ipynb`**
- `RANDOM_SEED = 42` aplicado globalmente → resultados reproducibles entre ejecuciones.
- `class_weight` calculado y aplicado en Fase 1 y Fase 2 → compensa el desbalance 2.3:1 entre plástico y vidrio.
- Métricas detalladas por clase (precision, recall, F1-score, support) y matriz de confusión en la celda de evaluación.
- Carga explícita de `mejor_modelo_ft.keras` antes de convertir a TFLite con manejo de `FileNotFoundError`.
- Path del dataset en Drive corregido: `RECI_dataset_propio/dataset_organizado`.

**`.gitignore`**
- Añadido `logs/` para que los logs de producción no se suban al repo.

### Antes — v2.0

- Sistema experto v2.0: 113 reglas, 12 meta-reglas, condiciones eliminatorias, 74/74 pruebas.
- Flujo híbrido TM+Gemini diseñado e implementado.
- Regla R51 endurecida (LATA requiere color + brillo metálico).

---

*Última actualización: Junio 2026 — v2.1 · Sistema experto v2.0 · Flujo híbrido TM+Gemini+SE · Threading en cámara · Logging persistente*
