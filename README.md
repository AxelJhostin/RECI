# RECI — Tacho Inteligente de Reciclaje con IA y Sistema Experto

> Proyecto integrador — Pontificia Universidad Católica del Ecuador, Sede Manabí  
> Carrera de Software | Materia: Sistemas Expertos (IS502) | Período 2026-01  
> Docente: Ing. Josselyn Tatiana Gómez Bravo, MSc  
> Repositorio: https://github.com/AxelJhostin/RECI

---

## ¿Qué es RECI?

RECI es un tacho inteligente de reciclaje universitario que clasifica residuos automáticamente usando visión artificial e inteligencia artificial. El usuario coloca el objeto frente a la cámara y el sistema decide a qué compartimento dirigirlo sin intervención humana.

El sistema acepta **únicamente plástico y vidrio**. Cualquier otro objeto es rechazado con mensaje al usuario.

**Tecnologías combinadas:**
- Sistema experto con encadenamiento hacia adelante y hacia atrás (materia IS502)
- Modelo MobileNetV2 entrenado con dataset propio del campus PUCE Manabí (99.7% precisión)
- Gemini API como respaldo inteligente cuando el modelo tiene baja confianza
- Hardware con Raspberry Pi 4, sensor ultrasónico, servo y LEDs

---

## Contexto de competencia

Este proyecto participa en una competencia entre las sedes de Portoviejo y Manta de la PUCE Manabí. El mejor proyecto obtiene la nota máxima y puede ser patentado.

---

## Arquitectura del sistema

```
Sensor ultrasónico → detecta objeto
        ↓
Cámara (Raspberry Pi / laptop)
        ↓
MobileNetV2 (.tflite) → clasifica objeto
        ↓
¿Confianza >= 90%?
   SÍ → resultado inmediato (~0.1 segundos)
   NO → Gemini API confirma (~3 segundos) — maneja objetos no permitidos
        ↓
Sistema Experto RECI → razona con 111+ reglas
        ↓
Decisión: VIDRIO | PLÁSTICO | DESCONOCIDO
        ↓
Servo → abre compuerta correspondiente
        ↓
FastAPI → Supabase → Dashboard → Gamificación
```

**Dos compartimentos físicos:**
- Compuerta izquierda → VIDRIO (servo 45°, LED azul)
- Compuerta derecha → PLÁSTICO (servo 135°, LED verde)
- Sin compuerta → objeto no permitido (servo 0°, LED rojo, mensaje al usuario)

---

## Estructura del proyecto

```
RECI/
├── expert_system/
│   ├── knowledge_base.py        # 111+ reglas de producción en 5 niveles
│   ├── inference_engine.py      # Motor principal: forward chaining, CF MYCIN, meta-reglas
│   ├── working_memory.py        # Memoria de trabajo — hechos activos por ciclo
│   ├── backward_chaining.py     # Encadenamiento hacia atrás — verificación de hipótesis
│   ├── certainty_factor.py      # Factor de Certeza estilo MYCIN
│   ├── meta_rules.py            # 10 meta-reglas
│   ├── validator.py             # Validador de atributos antes de razonar
│   ├── statistics.py            # Estadísticas de sesión + payload para Supabase
│   └── explanation.py           # Reporte técnico exportable a JSON
├── vision/
│   ├── attribute_extractor.py   # Extractor con Gemini API (fallback inteligente)
│   ├── tm_classifier.py         # Clasificador MobileNetV2 (.tflite) — módulo principal
│   └── camera.py                # Captura en tiempo real — modo demo + producción
├── model/                       # Modelo entrenado — NO está en el repo (ver sección modelo)
│   ├── model.tflite             # MobileNetV2 entrenado (99.7% precisión) — descargar aparte
│   ├── labels.txt               # Clases: 0 plastico, 1 vidrio
│   └── .gitkeep                 # Mantiene la carpeta en el repo vacía
├── api/
│   ├── __init__.py
│   └── app.py                   # FastAPI — todos los endpoints REST
├── tests/
│   ├── test_cases.py            # Runner principal — 56 pruebas formales
│   └── casos/                   # Casos organizados por categoría
│       ├── __init__.py
│       ├── casos_vidrio.py      # 9 casos de vidrio
│       ├── casos_plastico.py    # 18 casos de plástico
│       ├── casos_ambiguos.py    # 10 casos difíciles de desempate
│       ├── casos_extremos.py    # 4 casos extremos (baja confianza, desconocidos)
│       └── casos_campus.py      # 15 casos con objetos reales del campus PUCE
├── images/
│   ├── capturas/                # Fotos capturadas por la cámara en tiempo real
│   ├── api_uploads/             # Fotos subidas por la API
│   └── prueba1-8.jpeg           # Imágenes de prueba incluidas en el repo
├── fotos_dataset/               # Fotos tomadas con tomar_fotos.py — solo local, no en repo
├── RECI_entrenar_modelo.ipynb   # Notebook de Google Colab para entrenar el modelo
├── main.py                      # Punto de entrada principal
├── tomar_fotos.py               # Script para recolectar fotos del dataset con modo ráfaga
├── requirements.txt             # Dependencias del proyecto
├── .env                         # Variables de entorno — NO subir a GitHub
└── .gitignore
```

---

## Instalación desde cero

### 1. Requisitos previos
- Python 3.9+
- Cámara (integrada en laptop o módulo Raspberry Pi)
- Cuenta de Google (para Gemini API y Google Colab)

### 2. Clonar e instalar
```bash
git clone https://github.com/AxelJhostin/RECI.git
cd RECI
pip3 install -r requirements.txt
```

### 3. Configurar variables de entorno
Crear archivo `.env` en la raíz del proyecto:
```
GEMINI_API_KEY=tu_api_key_aqui
```

Obtener API key gratis en: https://aistudio.google.com/apikey

> Si no tienes API key de Gemini, el sistema funciona igualmente con el modelo TFLite
> para plástico y vidrio. Gemini solo se usa cuando la confianza del modelo es < 90%.

### 4. Obtener el modelo entrenado
El modelo `.tflite` no está en el repositorio por su tamaño (8.5 MB).

**Opción A — Descargar desde Google Drive del equipo:**
```bash
# El equipo ML comparte el modelo en Drive
# Descargar model.tflite y labels.txt → copiar a model/
cp ~/Downloads/model.tflite model/model.tflite
cp ~/Downloads/labels.txt model/labels.txt
```

**Opción B — Entrenar el modelo desde cero:**
```bash
# Ver sección "Reentrenar el modelo" más abajo
# Usar RECI_entrenar_modelo.ipynb en Google Colab
```

**Opción C — Sin modelo (solo Gemini):**
Si no hay `model.tflite`, el sistema usa Gemini automáticamente como fallback.
No se necesita hacer nada — `camera.py` detecta automáticamente qué usar.

### 5. Verificar instalación
```bash
# Verificar sistema experto
python3 tests/test_cases.py

# Verificar API
uvicorn api.app:app --reload --port 8000
# Abrir: http://localhost:8000/health
```

---

## Ejecución

```bash
# Modo principal — cámara en tiempo real
python3 vision/camera.py

# API REST
uvicorn api.app:app --reload --port 8000

# Pruebas formales del sistema experto
python3 tests/test_cases.py

# Clasificar una imagen específica
python3 vision/tm_classifier.py images/prueba7.jpeg

# Tomar fotos para el dataset
python3 tomar_fotos.py plastico   # ESPACIO=una foto | R=ráfaga 60s
python3 tomar_fotos.py vidrio
```

---

## Modelo de Machine Learning

### Especificaciones
- **Arquitectura:** MobileNetV2 con transfer learning (ImageNet → RECI)
- **Formato:** TensorFlow Lite (.tflite) — 8.5 MB
- **Resolución de entrada:** 224×224 px, color RGB
- **Clases:** plastico, vidrio
- **Precisión:** 99.7% en dataset de validación
- **Hardware recomendado:** cualquier dispositivo con Python — Mac, Windows, Raspberry Pi 4

### Dataset de entrenamiento
El modelo fue entrenado con un dataset propio recolectado en el campus PUCE Manabí:

| Clase | Entrenamiento | Validación |
|-------|--------------|------------|
| plastico | ~2,700 fotos | ~476 fotos |
| vidrio | ~2,170 fotos | ~383 fotos |
| **Total** | **~4,870** | **~859** |

Las fotos fueron tomadas con objetos reales del campus — fondos variados, distintos ángulos, iluminaciones y distancias. Esto le da robustez en condiciones reales.

### Proceso de entrenamiento (Google Colab)
Archivo: `RECI_entrenar_modelo.ipynb`

El entrenamiento se realizó con GPU Tesla T4 en Google Colab:
- **Fase 1** (capas nuevas, 13 épocas): 99.1% precisión
- **Fase 2** (fine-tuning últimas 30 capas, 8 épocas): 99.7% precisión
- **Tiempo total:** ~3 horas

### Reentrenar el modelo con más fotos

```bash
# Paso 1: Tomar fotos nuevas
python3 tomar_fotos.py plastico
python3 tomar_fotos.py vidrio
# Presionar R para ráfaga automática (1 foto cada 0.3s durante 60s)
# Variar ángulos, distancias, fondos e iluminación

# Paso 2: Subir fotos a Google Drive en:
#   Mi unidad/RECI_dataset_propio/plastico/
#   Mi unidad/RECI_dataset_propio/vidrio/
# (Las fotos nuevas se mezclan con las existentes automáticamente)

# Paso 3: Abrir RECI_entrenar_modelo.ipynb en Google Colab
#   colab.research.google.com → Archivo → Subir notebook
#   Activar GPU: Entorno de ejecución → Cambiar tipo → GPU T4
#   Ejecutar: Paso 1 → Paso 2 → Paso 3 → ... → Paso 10

# Paso 4: Descargar y reemplazar el modelo
cp ~/Downloads/model.tflite model/model.tflite
cp ~/Downloads/labels.txt model/labels.txt

# Paso 5: Verificar
python3 vision/tm_classifier.py images/prueba7.jpeg
```

> El notebook detecta automáticamente las fotos nuevas y solo copia las que
> no estaban antes — no reprocesa fotos ya entrenadas.

---

## Sistema experto — detalle técnico

### Cómo funciona
El sistema experto recibe un diccionario de 9 atributos visuales y razona sobre ellos usando reglas IF-THEN para determinar si el objeto es VIDRIO, PLÁSTICO o no permitido.

```python
from expert_system.inference_engine import InferenceEngine

engine = InferenceEngine()
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
```

### Atributos del sistema

| Atributo | Valores posibles |
|----------|-----------------|
| `objeto_reconocido` | botella_agua, botella_gaseosa, botella_mocachino, botella_cerveza_vidrio, frasco_vidrio, yogur_plastico, vaso_plastico, funda_plastico, lata, cascara_fruta, restos_comida, papel_servilleta, carton, vaso_carton, desconocido, etc. |
| `confianza_ml` | alta, media, baja |
| `transparencia` | alta, media, baja, ninguna |
| `color` | transparente, ambar, verde_oscuro, blanco_opaco, negro, variado_vivo, marron_tierra, metalico |
| `forma` | cilindrica_delgada, cilindrica_estandar, cilindrica_ancha, conica, rectangular_plana, irregular |
| `brillo` | alto_nitido, medio_difuso, bajo, metalico |
| `tapa` | rosca_plastico, corona_metalica, twist_off_metalica, tapa_ancha_metalica, domo_plastico, sin_tapa, sellado |
| `textura` | lisa_brillante, lisa_sin_brillo, rugosa, fibrosa |
| `rigidez` | rigido, flexible, indefinido |

### Componentes

| Módulo | Función |
|--------|---------|
| `KnowledgeBase` | 111+ reglas IF-THEN en 5 niveles de prioridad |
| `InferenceEngine` | Motor principal — coordina todo el proceso de inferencia |
| `WorkingMemory` | Almacena hechos activos durante un ciclo |
| `BackwardChainingEngine` | Verifica hipótesis desde la conclusión hacia los hechos |
| `CertaintyFactor` | Combina evidencia de múltiples reglas (fórmula MYCIN) |
| `MetaRuleEngine` | 10 meta-reglas que ajustan el razonamiento antes de inferir |
| `AttributeValidator` | Valida que los atributos sean valores permitidos |
| `RECIStatistics` | Registra clasificaciones y genera payload para Supabase |
| `ExplanationReport` | Reporte técnico completo exportable a JSON |

### Niveles de reglas

- **Nivel 1:** Reconocimiento directo — objeto conocido con alta confianza ML
- **Nivel 2:** Razonamiento visual — cuando ML tiene confianza media
- **Nivel 3:** Desempate — plástico transparente vs vidrio (el caso más difícil)
- **Nivel 4:** Seguridad — baja confianza, objetos desconocidos → pide segunda captura
- **Nivel 5:** Campus Manabí — mocachino, Switch, Currimcho, Powerade, Chocolatada Toni, etc.

### Meta-reglas (10)

| ID | Descripción |
|----|-------------|
| MR01 | ML baja confianza → potenciar backward chaining |
| MR02 | Objeto delgado transparente → sesgar hacia plástico |
| MR03 | Tapa corona detectada → priorizar VIDRIO ×1.10 |
| MR04 | Objeto flexible → excluir VIDRIO completamente |
| MR05 | Brillo metálico cilíndrico → priorizar LATA ×1.15 |
| MR06 | Alta confianza ML + objeto reconocido → potenciar reglas nivel 1 |
| MR07 | Forma irregular no rígida → sesgar hacia ORGÁNICO |
| MR08 | Tapa twist-off metálica → priorizar VIDRIO ×1.08 |
| MR09 | Metálico rectangular → excluir LATA (es snack plástico) |
| MR10 | Objeto desconocido confianza media → modo cauteloso, umbral CF 0.70 |

### Factor de Certeza MYCIN
```
CF_combinado = CF1 + CF2 * (1 - CF1)   # cuando ambos son positivos

# Bonus automático por especificidad:
CF_final = CF_base + (num_condiciones - 1) * 0.01
# Una regla con 5 condiciones es más confiable que una con 2 del mismo CF base
```

---

## Flujo de visión híbrido

```
Cámara captura imagen
        ↓
MobileNetV2 analiza (~0.1 segundos)
        ↓
¿Confianza >= 90%?
   SÍ → Resultado rápido sin Gemini
         plastico (92%) → atributos plástico → sistema experto → PLASTICO
         vidrio   (96%) → atributos vidrio   → sistema experto → VIDRIO

   NO → Gemini API confirma (~3 segundos)
         Casos: latas, cartón, manos, adaptadores, objetos raros
         → DESCONOCIDO → "Objeto no permitido en este tacho"
```

El modelo TFLite solo tiene 2 clases (plastico/vidrio). Cuando la confianza es baja significa que el objeto probablemente no es ninguna de las dos — Gemini lo confirma y el sistema rechaza correctamente.

---

## API REST

Ejecutar: `uvicorn api.app:app --reload --port 8000`

Documentación interactiva: `http://localhost:8000/docs`

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Info general + modo de visión activo |
| `/health` | GET | Estado del sistema, reglas cargadas, modo TM o Gemini |
| `/reglas` | GET | Total y distribución de reglas por categoría |
| `/clasificar/atributos` | POST | Clasificar enviando los 9 atributos directamente |
| `/clasificar/imagen` | POST | Clasificar enviando una imagen (TM o Gemini automático) |
| `/estadisticas` | GET | Estadísticas de la sesión actual para el dashboard |
| `/historial` | GET | Historial de clasificaciones (parámetro: `?limite=20`) |
| `/reset` | POST | Resetear estadísticas de la sesión |

### Ejemplo de uso desde Raspberry Pi
```python
import requests

# El Raspberry Pi envía los atributos extraídos por su propio módulo de visión
response = requests.post("http://localhost:8000/clasificar/atributos", json={
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

resultado = response.json()
angulo_servo = resultado["hardware"]["angulo_servo"]   # 135
compuerta    = resultado["hardware"]["compuerta"]      # "derecha"
led          = resultado["hardware"]["led"]            # "verde"
```

### Estructura del JSON de respuesta
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
  "atributos": { ... },
  "reglas_disparadas": 5,
  "backward_chaining": {
    "conclusion": "PLASTICO",
    "score": 1.0,
    "consistente": true
  },
  "meta_reglas_aplicadas": ["MR06"],
  "payload_supabase": { ... }
}
```

---

## Pruebas formales

```bash
python3 tests/test_cases.py
```

**Resultado actual: 56/56 pruebas aprobadas (100%)**

| Categoría | Resultado | Descripción |
|-----------|-----------|-------------|
| VIDRIO | 9/9 (100%) | Mocachino, cerveza, frasco, salsa, jugo |
| PLASTICO | 18/18 (100%) | Agua, gaseosa, energizante, vaso, yogur, funda, Monster |
| AMBIGUO | 10/10 (100%) | Casos difíciles de desempate PET vs vidrio |
| EXTREMO | 4/4 (100%) | Baja confianza, desconocidos, atributos incompletos |
| CAMPUS_PLASTICO | 10/10 (100%) | Powerade, Dasani, Chocolatada, Colgate, Speed Max |
| CAMPUS_VIDRIO | 5/5 (100%) | Caffe Lato Mocachino, Pilsener campus, frasco vidrio |

Para agregar nuevos casos de prueba, editar el archivo correspondiente en `tests/casos/` sin tocar el runner principal.

---

## Integración por equipo

### Equipo Hardware (Raspberry Pi + servo)
El código de la cámara ya está listo para producción. Solo necesitan:

```python
# En el código del Raspberry Pi:
import sys
sys.path.append('/ruta/a/RECI')

from vision.camera import Camera
from vision.attribute_extractor import AttributeExtractor
from vision.tm_classifier import TeachableMachineClassifier

extractor     = AttributeExtractor()
tm_classifier = TeachableMachineClassifier()
camara        = Camera(camara_index=0)  # ajustar índice según módulo RPi
camara.iniciar()

# Cuando el sensor ultrasónico detecte un objeto:
resultado = camara.capturar_y_clasificar(
    extractor,
    tm_classifier=tm_classifier,
    delay=1  # segundos de espera antes de capturar
)

angulo = resultado["hardware"]["angulo_servo"]
# VIDRIO   → 45°  → compuerta izquierda
# PLASTICO → 135° → compuerta derecha
# OTROS    → 0°   → no abre nada
```

**Ángulos del servo:**
- 0° → posición neutral (objeto no permitido)
- 45° → compuerta izquierda (VIDRIO)
- 135° → compuerta derecha (PLÁSTICO)

### Equipo Nube (FastAPI + Supabase + Dashboard)
La API ya está corriendo. Para consumirla desde Next.js:

```javascript
// Enviar imagen desde el dashboard
const formData = new FormData()
formData.append('file', imagenBlob, 'objeto.jpg')

const response = await fetch('http://localhost:8000/clasificar/imagen', {
  method: 'POST',
  body: formData
})
const resultado = await response.json()

// Estadísticas para el dashboard
const stats = await fetch('http://localhost:8000/estadisticas').then(r => r.json())
```

**Payload que la API envía a Supabase** (disponible en cada clasificación):
```json
{
  "timestamp": "2026-05-29T14:30:00",
  "clasificacion": "PLASTICO",
  "confianza": 0.998,
  "objeto_reconocido": "botella_agua",
  "reglas_disparadas": 5,
  "backward_consistente": true,
  "es_reciclable": true,
  "compuerta": "derecha",
  "sede": "PUCE Manabí"
}
```

### Equipo ML (reentrenamiento del modelo)
Ver sección "Reentrenar el modelo" más arriba. Los nombres de clase en Teachable Machine o Colab deben ser exactamente `plastico` y `vidrio` — así el `tm_classifier.py` los reconoce automáticamente sin cambios de código.

---

## Objetos reconocidos

### Plástico → compuerta derecha
Botellas de agua (Tesalia, Pure Water, Güitig, Dasani, pomo PUCE), gaseosas (Coca-Cola, Pepsi, Sprite, Fanta), energizantes (Volt, 220V, Profit, Powerade, Speed Max), bebidas alcohólicas (Switch, Currimcho, 24-7), vasos transparentes con/sin tapa domo, yogur (Toni, Rey Leche), chocolatada (Toni Chiqui), enjuague bucal (Colgate Plax), fundas plásticas, Monster negro

### Vidrio → compuerta izquierda
Botellas de mocachino (Caffe Lato Toni, Don Café), cervezas (Pilsener, Club), salsas (Gustadina), frascos de mermelada (Snob), jugos en vidrio, Güitig en vidrio, botella salsa soya

### No permitidos → mensaje de rechazo, servo no abre
Latas de aluminio (Red Bull, Monster, Coca-Cola lata, atún), cartón, papel, servilletas, residuos orgánicos, cualquier objeto no identificado

---

## Troubleshooting

### El modelo no carga
```
FileNotFoundError: Modelo no encontrado: model/model.tflite
```
**Solución:** El modelo no está en el repo. Ver sección "Obtener el modelo entrenado".

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
**Solución:**
```
Ajustes del Sistema → Privacidad y Seguridad → Cámara → Activar Terminal
```

### Gemini da error 503
```
Server error '503 Service Unavailable'
```
**Solución:** El servidor de Google está caído temporalmente. Esperar unos minutos y reintentar. El sistema usa TM mientras tanto.

### Gemini da error 429
```
429 Too Many Requests
```
**Solución:** Rate limit alcanzado. Esperar 60 segundos. La API key gratuita tiene límite de requests por minuto.

### Las pruebas fallan después de cambiar reglas
```bash
python3 tests/test_cases.py
```
Si algún caso falla, el output muestra exactamente qué reglas se dispararon y por qué. Revisar `knowledge_base.py` en el nivel de regla correspondiente.

---

## Alineación con sílabo IS502

| Resultado de aprendizaje | Implementado en |
|--------------------------|-----------------|
| Fundamentos de sistemas expertos | `knowledge_base.py` + `inference_engine.py` |
| Relación SE con IA | Arquitectura híbrida MobileNetV2 + SE + Gemini |
| Encadenamiento hacia adelante | `InferenceEngine.ejecutar()` — forward chaining |
| Encadenamiento hacia atrás | `BackwardChainingEngine` — verificación de hipótesis |
| Diseño e implementación de SE | Todo el módulo `expert_system/` |
| Evaluación ética | `ExplanationReport` — trazabilidad completa de decisiones |

---

## División del equipo

| Responsable | Área |
|-------------|------|
| Axel | Sistema experto + modelo ML + integración IA + parte de circuitos |
| Equipo ML | Recolección de fotos + reentrenamiento del modelo |
| Equipo Hardware | Raspberry Pi + sensores + servo + circuitos |
| Equipo Nube | FastAPI + Supabase + Dashboard Next.js + Gamificación |

---

## Estado actual del proyecto

### Completado
- Sistema experto: 111+ reglas, forward + backward chaining, CF MYCIN, 10 meta-reglas
- Validador de atributos, estadísticas, reporte técnico JSON
- 56/56 pruebas formales (100%) — incluyendo casos del campus
- Modelo MobileNetV2 propio (99.7% precisión) con dataset campus PUCE Manabí
- Flujo híbrido TM + Gemini (velocidad + precisión + manejo de objetos no permitidos)
- Cámara en tiempo real con modo demo funcional
- API REST completa con FastAPI
- Script de recolección de fotos con modo ráfaga automática
- Notebook de entrenamiento Google Colab listo y documentado
- Pruebas modulares organizadas por categoría

### En progreso
- Reentrenamiento con más fotos del campus para subir confianza en botellas transparentes

### Pendiente
- Integración Raspberry Pi + servo (equipo hardware)
- Dashboard Next.js + Supabase (equipo nube)
- Integración sensor ultrasónico — trigger automático sin botón
- Lógica difusa para valores continuos de confianza

---

*Última actualización: Mayo 2026*