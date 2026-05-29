# RECI — Tacho Inteligente de Reciclaje con IA y Sistema Experto

> Proyecto integrador — Pontificia Universidad Católica del Ecuador, Sede Manabí
> Carrera de Software | Materia: Sistemas Expertos (IS502) | Período 2026-01
> Docente: Ing. Josselyn Tatiana Gómez Bravo, MSc

---

## Descripción general

RECI es un tacho inteligente de reciclaje universitario que clasifica residuos automáticamente usando visión artificial e inteligencia artificial. El usuario coloca el objeto frente a la cámara, presiona ESPACIO (o el sensor lo detecta automáticamente), y el sistema decide a qué compartimento dirigirlo sin intervención humana.

El proyecto combina tres tecnologías:
- **Sistema experto** con encadenamiento hacia adelante y hacia atrás (materia IS502)
- **Modelo MobileNetV2** entrenado con dataset propio del campus PUCE Manabí (99.7% precisión)
- **Gemini API** como respaldo inteligente cuando el modelo tiene baja confianza
- **Hardware** con Raspberry Pi 4, sensor ultrasónico, servo y LEDs

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
   SÍ → resultado inmediato (rápido)
   NO → Gemini API confirma (maneja objetos no permitidos)
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
│   ├── knowledge_base.py      # 111+ reglas de producción en 5 niveles
│   ├── inference_engine.py    # Motor principal: coordina todos los módulos
│   ├── working_memory.py      # Memoria de trabajo — hechos activos por ciclo
│   ├── backward_chaining.py   # Encadenamiento hacia atrás — verificación
│   ├── certainty_factor.py    # Factor de Certeza estilo MYCIN
│   ├── meta_rules.py          # 10 meta-reglas
│   ├── validator.py           # Validador de atributos
│   ├── statistics.py          # Estadísticas + payload para Supabase
│   └── explanation.py         # Reporte técnico exportable a JSON
├── vision/
│   ├── attribute_extractor.py # Extractor con Gemini API (fallback)
│   ├── tm_classifier.py       # Clasificador MobileNetV2 (.tflite)
│   └── camera.py              # Captura en tiempo real — modo demo + producción
├── model/                     # Modelo entrenado (excluido del repo con .gitignore)
│   ├── model.tflite           # MobileNetV2 entrenado (99.7% precisión)
│   ├── labels.txt             # Clases: 0 plastico, 1 vidrio
│   └── .gitkeep
├── api/
│   ├── __init__.py
│   └── app.py                 # FastAPI — endpoints REST
├── tests/
│   ├── test_cases.py          # 50 pruebas formales — 100% aprobadas
│   └── test_imagenes.py       # Prueba con imágenes reales
├── images/
│   ├── capturas/              # Fotos capturadas por la cámara en tiempo real
│   ├── api_uploads/           # Fotos subidas por la API
│   └── prueba1-8.jpeg         # Imágenes de prueba
├── fotos_dataset/             # Fotos tomadas con tomar_fotos.py (local)
├── main.py                    # Punto de entrada principal
├── tomar_fotos.py             # Script para recolectar fotos del dataset
├── requirements.txt           # Dependencias del proyecto
├── .env                       # Variables de entorno (NO subir a GitHub)
└── .gitignore
```

---

## Modelo de Machine Learning

### Especificaciones
- **Arquitectura:** MobileNetV2 con transfer learning (ImageNet → RECI)
- **Formato de exportación:** TensorFlow Lite (.tflite)
- **Resolución de entrada:** 224×224 px, color RGB
- **Clases:** plastico, vidrio
- **Precisión:** 99.7% en dataset de validación
- **Tamaño del modelo:** 8.5 MB

### Dataset de entrenamiento
El modelo fue entrenado con un dataset propio recolectado en el campus PUCE Manabí:

| Clase | Fotos de entrenamiento | Fotos de validación |
|-------|----------------------|-------------------|
| plastico | ~2,700 | ~476 |
| vidrio | ~2,170 | ~383 |
| **Total** | **~4,870** | **~859** |

Las fotos incluyen objetos reales del campus con fondos variados, distintos ángulos, iluminaciones y distancias — lo que le da al modelo robustez en condiciones reales.

### Proceso de entrenamiento
El entrenamiento se realizó en Google Colab con GPU Tesla T4:
- **Fase 1** (capas nuevas): 13 épocas, precisión 99.1%
- **Fase 2** (fine-tuning últimas 30 capas): 8 épocas, precisión 99.7%
- **Tiempo total:** ~3 horas

### Reentrenar el modelo
Para agregar más fotos y mejorar el modelo:

```bash
# 1. Tomar fotos nuevas con la cámara del Mac
python3 tomar_fotos.py plastico   # modo ráfaga con tecla R
python3 tomar_fotos.py vidrio

# 2. Subir fotos a Google Drive en:
#    Mi unidad/RECI_dataset_propio/plastico/
#    Mi unidad/RECI_dataset_propio/vidrio/

# 3. Abrir RECI_entrenar_modelo.ipynb en Google Colab
#    Ejecutar: Paso 1 → Paso 2 → Paso 3 → Paso 4 → ... → Paso 10

# 4. Descargar model.tflite y labels.txt → copiar a model/
cp ~/Downloads/model.tflite model/model.tflite
cp ~/Downloads/labels.txt model/labels.txt
```

---

## Sistema experto — detalle técnico

### Componentes

| Módulo | Función |
|--------|---------|
| `KnowledgeBase` | 111+ reglas IF-THEN en 5 niveles de prioridad |
| `InferenceEngine` | Motor principal — forward chaining, CF MYCIN, meta-reglas |
| `WorkingMemory` | Almacena hechos activos durante un ciclo de inferencia |
| `BackwardChainingEngine` | Verifica hipótesis — 4 goals definidos |
| `CertaintyFactor` | Combina evidencia de múltiples reglas con fórmula MYCIN |
| `MetaRuleEngine` | 10 meta-reglas que ajustan el razonamiento |
| `AttributeValidator` | Valida atributos antes de razonar |
| `RECIStatistics` | Registra clasificaciones y genera payload para dashboard |
| `ExplanationReport` | Reporte técnico completo exportable a JSON |

### Atributos del sistema

| Atributo | Valores posibles |
|----------|-----------------|
| `objeto_reconocido` | botella_agua, botella_gaseosa, botella_mocachino, botella_cerveza_vidrio, frasco_vidrio, lata, cascara_fruta, etc. |
| `confianza_ml` | alta, media, baja |
| `transparencia` | alta, media, baja, ninguna |
| `color` | transparente, ambar, verde_oscuro, blanco_opaco, negro, variado_vivo, marron_tierra, metalico |
| `forma` | cilindrica_delgada, cilindrica_estandar, cilindrica_ancha, conica, rectangular_plana, irregular |
| `brillo` | alto_nitido, medio_difuso, bajo, metalico |
| `tapa` | rosca_plastico, corona_metalica, twist_off_metalica, tapa_ancha_metalica, domo_plastico, sin_tapa, sellado |
| `textura` | lisa_brillante, lisa_sin_brillo, rugosa, fibrosa |
| `rigidez` | rigido, flexible, indefinido |

### Niveles de reglas

- **Nivel 1:** Reconocimiento directo con alta confianza ML
- **Nivel 2:** Razonamiento por atributos visuales
- **Nivel 3:** Desempate en casos ambiguos (plástico transparente vs vidrio)
- **Nivel 4:** Reglas de seguridad (baja confianza, objetos desconocidos)
- **Nivel 5:** Casos específicos del campus Manabí (mocachino, Switch, Currimcho, etc.)

### Meta-reglas (10)

| ID | Descripción |
|----|-------------|
| MR01 | Si ML tiene baja confianza → potenciar backward chaining |
| MR02 | Objeto delgado transparente → sesgar hacia plástico |
| MR03 | Tapa corona detectada → priorizar VIDRIO ×1.10 |
| MR04 | Objeto flexible → excluir VIDRIO completamente |
| MR05 | Brillo metálico cilíndrico → priorizar LATA ×1.15 |
| MR06 | Alta confianza ML con objeto reconocido → potenciar reglas nivel 1 |
| MR07 | Forma irregular no rígida → sesgar hacia ORGÁNICO |
| MR08 | Tapa twist-off metálica → priorizar VIDRIO ×1.08 |
| MR09 | Metálico rectangular → excluir LATA, es snack plástico |
| MR10 | Objeto desconocido confianza media → modo cauteloso, umbral CF 0.70 |

### Factor de Certeza MYCIN

```
CF_combinado = CF1 + CF2 * (1 - CF1)  # ambos positivos

# Bonus de especificidad automática:
CF_final = CF_base + (num_condiciones - 1) * 0.01
```

---

## Flujo de visión híbrido

```
Cámara captura imagen
        ↓
MobileNetV2 analiza (~0.1 segundos)
        ↓
¿Confianza >= 90%?
   SÍ → 🟢 Resultado rápido sin Gemini
         plastico (92%) → PLASTICO → compuerta derecha
         vidrio   (95%) → VIDRIO   → compuerta izquierda
         
   NO → 🔵 Gemini confirma (~3 segundos)
         Maneja: latas, cartón, manos, objetos no permitidos
         → DESCONOCIDO → "Objeto no permitido en este tacho"
```

Este diseño garantiza velocidad para los casos comunes (plástico/vidrio) y precisión para los casos edge.

---

## API REST

Ejecutar: `uvicorn api.app:app --reload --port 8000`

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Info general de la API |
| `/health` | GET | Estado del sistema + modo de visión activo |
| `/reglas` | GET | Total de reglas cargadas por categoría |
| `/clasificar/atributos` | POST | Clasificar con atributos manuales |
| `/clasificar/imagen` | POST | Clasificar desde imagen (TM o Gemini automático) |
| `/estadisticas` | GET | Estadísticas de la sesión actual |
| `/historial` | GET | Historial de clasificaciones |
| `/reset` | POST | Resetear estadísticas |

El endpoint `/clasificar/imagen` detecta automáticamente si el modelo `.tflite` está disponible y usa TM o Gemini según corresponda.

---

## Pruebas

### Pruebas formales del sistema experto
```bash
python3 tests/test_cases.py
```

**Resultado:** 50/50 pruebas aprobadas (100%)

| Categoría | Resultado |
|-----------|-----------|
| VIDRIO | 9/9 (100%) |
| PLÁSTICO | 18/18 (100%) |
| ORGÁNICO | 8/8 (100%) |
| LATA | 3/3 (100%) |
| AMBIGUO | 10/10 (100%) |
| EXTREMO | 2/2 (100%) |

### Prueba con cámara en tiempo real
```bash
python3 vision/camera.py
```

---

## Instalación y ejecución

### Requisitos
- Python 3.9+
- Cámara (laptop o módulo Raspberry Pi)
- TensorFlow (para el modelo .tflite)

### Instalación
```bash
git clone https://github.com/AxelJhostin/RECI.git
cd RECI
pip3 install -r requirements.txt
```

### Configuración
Crear archivo `.env` en la raíz del proyecto:
```
GEMINI_API_KEY=tu_api_key_aqui
```

Obtener API key gratis en: https://aistudio.google.com/apikey

### Ejecución

```bash
# Cámara en tiempo real (modo principal)
python3 vision/camera.py

# API REST
uvicorn api.app:app --reload --port 8000

# Pruebas formales del sistema experto
python3 tests/test_cases.py

# Clasificar una imagen específica
python3 vision/tm_classifier.py images/foto.jpg

# Tomar fotos para el dataset
python3 tomar_fotos.py plastico
python3 tomar_fotos.py vidrio
```

---

## Objetos reconocidos

### Plástico → compuerta derecha
Botellas de agua (Tesalia, Pure Water, Güitig, Dasani), gaseosas (Coca-Cola, Pepsi, Sprite, Fanta), energizantes (Volt, 220V, Profit, Powerade, Speed Max), bebidas alcohólicas (Switch, Currimcho, 24-7), vasos transparentes con/sin tapa domo, yogur (Toni, Rey Leche), chocolatada (Toni Chiqui), fundas plásticas, Monster negro

### Vidrio → compuerta izquierda
Botellas de mocachino (Caffe Lato Toni, Don Café), cervezas (Pilsener, Club), salsas (Gustadina), frascos de mermelada (Snob), jugos en vidrio, Güitig en vidrio

### No permitidos → mensaje de rechazo
Latas de aluminio, cartón, papel, orgánico, cualquier objeto no identificado

---

## Integración con hardware (pendiente)

### Raspberry Pi
```python
resultado = camara.capturar_y_clasificar(extractor, tm_classifier=clf)
angulo = resultado["hardware"]["angulo_servo"]
# VIDRIO   → 45°
# PLÁSTICO → 135°
# OTROS    → 0° (no abre)
```

### Payload para Supabase
```json
{
  "timestamp": "2026-05-29T12:54:22",
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

---

## División del equipo

| Responsable | Área |
|-------------|------|
| Axel | Sistema experto + modelo ML + integración IA + circuitos |
| Equipo ML | Recolección de fotos + reentrenamiento del modelo |
| Equipo Hardware | Raspberry Pi + sensores + servo + circuitos |
| Equipo Nube | FastAPI + Supabase + Dashboard Next.js + Gamificación |

---

## Alineación con sílabo IS502

| Resultado de aprendizaje | Cubierto en |
|--------------------------|-------------|
| Fundamentos de sistemas expertos | KnowledgeBase + InferenceEngine |
| Relación SE con IA | Arquitectura híbrida MobileNetV2 + SE + Gemini |
| Encadenamiento hacia adelante | InferenceEngine.ejecutar() |
| Encadenamiento hacia atrás | BackwardChainingEngine |
| Diseño e implementación de SE | Todo el módulo expert_system/ |
| Evaluación ética | Módulo de explicación + trazabilidad completa |

---

## Estado actual del proyecto

### Completado
- Sistema experto completo con 111+ reglas
- Forward y backward chaining
- Factor de Certeza MYCIN
- Especificidad automática de reglas
- 10 meta-reglas
- Validador de atributos
- Módulo de estadísticas + payload Supabase
- Reporte técnico exportable a JSON
- 50/50 pruebas formales (100%)
- Modelo MobileNetV2 propio entrenado (99.7% precisión)
- Dataset propio del campus PUCE Manabí
- Flujo híbrido TM + Gemini (velocidad + precisión)
- Cámara en tiempo real funcional
- API REST con FastAPI completa
- Script de recolección de fotos con modo ráfaga

### En progreso
- Reentrenamiento con más fotos del campus
- Pruebas con objetos variados en condiciones reales

### Pendiente
- Integración Raspberry Pi + servo
- Dashboard Next.js (equipo nube)
- Integración sensor ultrasónico (trigger automático)
- Lógica difusa

---

## Repositorio

https://github.com/AxelJhostin/RECI

---

*Última actualización: Mayo 2026*