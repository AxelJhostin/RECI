# RECI — Sistema Experto de Reciclaje Inteligente
# Dependencias del proyecto
# Instalar con: pip3 install -r requirements.txt

# API de visión artificial
anthropic>=0.104.1

# HTTP client para Gemini API
httpx>=0.28.1

# Variables de entorno
python-dotenv>=1.0.0

# Visión por computadora y cámara
opencv-python>=4.5.0

# Validación de datos
pydantic>=2.0.0
Guarda y verifica que funciona en un entorno limpio:
bashpip3 install -r requirements.txt
Luego hagamos commit:
bashgit add requirements.txt
git commit -m "docs: requirements.txt con dependencias del proyecto"
git push
Dime cuando esté listo y arrancamos con el modo automático.Dijiste: listo, aparte de otro que seria un archivo readme para que podamos ir las cosas que hemos hechos, los avances y lo que tenemos, uno demasiado completo por si t…listo, aparte de otro que seria un archivo readme para que podamos ir las cosas que hemos hechos, los avances y lo que tenemos, uno demasiado completo por si tienen que pasar lo que hemos hecho a una ia para que puedan seguir con lo que hemos hecho o lo puedan integrar correctamente a su parte de mi equipo1:17 p.m.Claude respondió: Perfecto, eso es exactamente lo que se necesita — un README que sea tan completo que cualquier persona o IA pueda entender el proyecto y continuar desde donde …Perfecto, eso es exactamente lo que se necesita — un README que sea tan completo que cualquier persona o IA pueda entender el proyecto y continuar desde donde lo dejamos.
Créalo:
bashtouch README.md
Y pega esto:
markdown# RECI — Tacho Inteligente de Reciclaje con IA y Sistema Experto

> Proyecto integrador — Pontificia Universidad Católica del Ecuador, Sede Manabí  
> Carrera de Software | Materia: Sistemas Expertos (IS502) | Período 2026-01  
> Docente: Ing. Josselyn Tatiana Gómez Bravo, MSc

---

## 📋 Descripción general

RECI es un tacho inteligente de reciclaje universitario que clasifica residuos automáticamente usando visión artificial e inteligencia artificial. El usuario simplemente coloca el objeto frente a la cámara y el sistema decide a qué compartimento dirigirlo, sin intervención humana.

El proyecto combina tres tecnologías:
- **Sistema experto** con encadenamiento hacia adelante y hacia atrás (materia IS502)
- **Visión artificial** con Gemini API (temporal) → MobileNet v2 entrenado (producción)
- **Hardware** con Raspberry Pi 4, sensor ultrasónico, servo y LEDs

---

## 🎯 Contexto de competencia

Este proyecto participa en una competencia entre las sedes de Portoviejo y Manta de la PUCE Manabí. El mejor proyecto obtiene la nota máxima y puede ser patentado. Por eso el nivel de detalle y calidad del sistema experto es de nivel profesional.

---

## 🏗️ Arquitectura del sistema
Sensor ultrasónico → detecta objeto
↓
Cámara (Raspberry Pi / laptop)
↓
Gemini API / MobileNet v2 → extrae atributos visuales
↓
Sistema Experto RECI → razona y clasifica
↓
Decisión: VIDRIO | PLÁSTICO | ORGÁNICO | LATA | DESCONOCIDO
↓
Servo → abre compuerta correspondiente
↓
FastAPI → Supabase → Dashboard → Gamificación

**Dos tachos físicos:**
- Compuerta izquierda → VIDRIO
- Compuerta derecha → PLÁSTICO
- Sin compuerta → ORGÁNICO / LATA / DESCONOCIDO (avisa al usuario)

---

## 📁 Estructura del proyecto
RECI/
├── expert_system/
│   ├── knowledge_base.py      # 111+ reglas de producción organizadas en 5 niveles
│   ├── inference_engine.py    # Motor principal: coordina todos los módulos
│   ├── working_memory.py      # Memoria de trabajo — hechos activos por ciclo
│   ├── backward_chaining.py   # Encadenamiento hacia atrás — verificación de hipótesis
│   ├── certainty_factor.py    # Factor de Certeza estilo MYCIN
│   ├── meta_rules.py          # 10 meta-reglas — razonamiento sobre el razonamiento
│   ├── validator.py           # Validador de atributos — detecta errores e inconsistencias
│   ├── statistics.py          # Estadísticas de sesión + payload para Supabase
│   └── explanation.py         # Reporte técnico completo exportable a JSON
├── vision/
│   ├── attribute_extractor.py # Extractor de atributos con Gemini API
│   └── camera.py              # Captura en tiempo real desde cámara
├── tests/
│   ├── test_cases.py          # 50 pruebas formales — 100% aprobadas
│   └── test_imagenes.py       # Prueba masiva con imágenes reales
├── images/
│   └── capturas/              # Fotos capturadas por la cámara en tiempo real
├── main.py                    # Punto de entrada principal
├── requirements.txt           # Dependencias del proyecto
├── .env                       # Variables de entorno (NO subir a GitHub)
└── .gitignore                 # Archivos ignorados por git

---

## 🧠 Sistema experto — detalle técnico

### Componentes

| Módulo | Función |
|--------|---------|
| `KnowledgeBase` | 111+ reglas IF-THEN organizadas en 5 niveles de prioridad |
| `InferenceEngine` | Motor principal — coordina forward chaining, CF MYCIN y meta-reglas |
| `WorkingMemory` | Almacena hechos activos durante un ciclo de inferencia |
| `BackwardChainingEngine` | Verifica hipótesis — 4 goals definidos (VIDRIO, PLÁSTICO, ORGÁNICO, LATA) |
| `CertaintyFactor` | Combina evidencia de múltiples reglas con fórmula de MYCIN |
| `MetaRuleEngine` | 10 meta-reglas que ajustan el razonamiento antes de inferir |
| `AttributeValidator` | Valida atributos recibidos del ML antes de razonar |
| `RECIStatistics` | Registra clasificaciones y genera payload para dashboard |
| `ExplanationReport` | Reporte técnico completo exportable a JSON para Supabase |

### Atributos del sistema

El sistema razona sobre 9 atributos visuales:

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

- **Nivel 1:** Reconocimiento directo con alta confianza ML (objetos conocidos)
- **Nivel 2:** Razonamiento por atributos visuales (cuando ML tiene confianza media)
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
CF_combinado = CF1 + CF2 * (1 - CF1)  # ambos positivos

Con bonus de especificidad automática:
CF_final = CF_base + (num_condiciones - 1) * 0.01

---

## 👁️ Módulo de visión

### Flujo actual (prototipo)
imagen → Gemini 2.5 Flash → JSON con 9 atributos → sistema experto

### Flujo producción (cuando ML esté entrenado)
imagen → MobileNet v2 (transfer learning) → 9 atributos → sistema experto

### Cómo reemplazar Gemini por MobileNet

En `vision/attribute_extractor.py`, solo cambiar el método `analizar_imagen()` para que llame al modelo local en vez de la API. El resto del sistema no cambia.

---

## 🧪 Pruebas

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

### Pruebas con imágenes reales
```bash
python3 tests/test_imagenes.py
```
**Resultado:** 85.7% de precisión con imágenes reales del campus

### Prueba con cámara en tiempo real
```bash
python3 vision/camera.py
```

---

## 🚀 Instalación y ejecución

### Requisitos
- Python 3.9+
- Cámara (laptop o módulo Raspberry Pi)

### Instalación
```bash
git clone https://github.com/AxelJhostin/RECI.git
cd RECI
pip3 install -r requirements.txt
```

### Configuración
Crear archivo `.env` en la raíz del proyecto:
GEMINI_API_KEY=tu_api_key_aqui

Obtener API key gratis en: https://aistudio.google.com/apikey

### Ejecución

```bash
# Sistema experto con casos simulados
python3 main.py

# Pruebas formales
python3 tests/test_cases.py

# Prueba con imágenes
python3 tests/test_imagenes.py

# Cámara en tiempo real
python3 vision/camera.py

# Clasificar una imagen específica
python3 vision/attribute_extractor.py images/mi_foto.jpg
```

---

## 📦 Objetos reconocidos

### Plástico
Botellas de agua (Tesalia, Pure Water, Güitig), gaseosas (Coca-Cola, Pepsi, Sprite, Fanta), energizantes (Volt, 220V, Profit, Speed Max), bebidas alcohólicas (Switch, Currimcho, 24-7), vasos transparentes con/sin tapa domo, yogur (Toni, Rey Leche), fundas plásticas, Monster negro

### Vidrio
Botellas de mocachino (Don Café, Café Vélez), cervezas (Pilsener, Club), salsas (Gustadina), frascos de mermelada (Snob), jugos en vidrio, Güitig en vidrio, botellas de salsa de soya

### Orgánico / Papel
Cáscaras de fruta (banano, naranja, manzana), restos de comida, servilletas, vasos de cartón, cajas de cartón, hojas de papel

### Rechazados (no reciclables en este tacho)
Latas de aluminio (Red Bull, Monster, atún), objetos orgánicos, papel

---

## 🔌 Integración con hardware (pendiente)

### Raspberry Pi
- El módulo `vision/camera.py` ya es compatible con Raspberry Pi
- Cambiar `camara_index=0` según el módulo de cámara conectado
- El método `capturar_y_clasificar()` es el que debe llamar el código del servo

### Sensor ultrasónico
- Cuando detecte objeto a menos de X cm → llamar `camara.capturar_y_clasificar(extractor)`
- El resultado incluye `angulo_servo` listo para enviarlo al servo

### Servo
```python
resultado = camara.capturar_y_clasificar(extractor)
angulo = resultado["hardware"]["angulo_servo"]
# VIDRIO   → 45°
# PLÁSTICO → 135°
# OTROS    → 0° (no abre)
```

---

## ☁️ Integración con nube (pendiente)

### Payload para Supabase
Cada clasificación genera automáticamente un payload JSON:
```json
{
  "timestamp": "2026-05-23T12:54:22",
  "clasificacion": "PLASTICO",
  "confianza": 0.998,
  "objeto_reconocido": "botella_energizante",
  "confianza_ml": "alta",
  "reglas_disparadas": 5,
  "backward_consistente": true,
  "es_reciclable": true,
  "compuerta": "derecha",
  "sede": "PUCE Manabí"
}
```

### FastAPI (pendiente)
Se implementará un endpoint REST para:
- `POST /clasificar` — recibe imagen, retorna clasificación
- `GET /estadisticas` — retorna estadísticas de sesión
- `GET /historial` — retorna historial de clasificaciones

---

## 🤝 División del equipo

| Responsable | Área |
|-------------|------|
| Axel | Sistema experto + integración IA + parte de circuitos |
| Equipo ML | Entrenamiento MobileNet v2 + recolección de fotos |
| Equipo Hardware | Raspberry Pi + sensores + servo + circuitos |
| Equipo Nube | FastAPI + Supabase + Dashboard Next.js + Gamificación |

---

## 📚 Alineación con sílabo IS502

| Resultado de aprendizaje | Cubierto en |
|--------------------------|-------------|
| Fundamentos de sistemas expertos | KnowledgeBase + InferenceEngine |
| Relación SE con IA | Arquitectura híbrida ML + SE |
| Encadenamiento hacia adelante | InferenceEngine.ejecutar() |
| Encadenamiento hacia atrás | BackwardChainingEngine |
| Diseño e implementación de SE | Todo el módulo expert_system/ |
| Evaluación ética | Módulo de explicación + trazabilidad |

---

## 📝 Estado actual del proyecto

### ✅ Completado
- Sistema experto completo con 111+ reglas
- Forward y backward chaining
- Factor de Certeza MYCIN
- Especificidad automática de reglas
- 10 meta-reglas
- Validador de atributos
- Módulo de estadísticas + payload Supabase
- Reporte técnico exportable a JSON
- 50/50 pruebas formales (100%)
- Extractor de atributos con Gemini API
- Cámara en tiempo real funcional
- 85.7% precisión con imágenes reales

### 🔄 En progreso
- Modo automático sin botón (trigger por sensor)

### ⏳ Pendiente
- API REST con FastAPI
- Entrenamiento MobileNet v2 (equipo ML)
- Integración Raspberry Pi + servo
- Dashboard Next.js (equipo nube)
- Lógica difusa (cuando MobileNet entregue valores continuos)

---

## 🔗 Repositorio

https://github.com/AxelJhostin/RECI

---

*Última actualización: Mayo 2026*