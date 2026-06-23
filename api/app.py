# api/app.py
# API REST del sistema experto RECI
# Conecta el sistema experto con el dashboard y el equipo de nube
# Ejecutar: uvicorn api.app:app --reload --port 8000

import os
import sys
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from expert_system.inference_engine import InferenceEngine
from expert_system.explanation import ExplanationReport
from expert_system.statistics import RECIStatistics

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    filename="logs/reci.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
logger = logging.getLogger("reci")


# ─────────────────────────────────────────────
# ENCODING UTF-8 — para caracteres en español
# ─────────────────────────────────────────────

class UTF8JSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":")
        ).encode("utf-8")


# ─────────────────────────────────────────────
# CONFIGURACIÓN DE LA APP
# ─────────────────────────────────────────────

app = FastAPI(
    title="RECI — Sistema Experto de Reciclaje",
    description="""
    API REST del sistema experto RECI.
    Clasifica residuos en VIDRIO, PLÁSTICO, ORGÁNICO o LATA
    usando un sistema experto con encadenamiento hacia adelante y hacia atrás.

    **Repositorio:** https://github.com/AxelJhostin/RECI

    **Sede:** PUCE Manabí — Portoviejo y Manta
    """,
    version="1.0.0",
    default_response_class=UTF8JSONResponse
)

# CORS — permite que el dashboard de Next.js consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Motor de inferencia compartido — se crea una vez al iniciar la API
# cargar_hechos() limpia el estado interno antes de cada clasificación,
# por lo que es seguro reutilizarlo (RECI procesa un objeto a la vez)
engine_global = InferenceEngine()

# Estadísticas globales de la sesión
stats = RECIStatistics()

# Carpeta temporal para imágenes subidas
UPLOAD_DIR = Path("images/api_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

_MAX_UPLOADS = 50  # máximo de archivos que se conservan en disco

def _limpiar_uploads() -> None:
    """Mantiene solo los _MAX_UPLOADS archivos más recientes en UPLOAD_DIR."""
    archivos = sorted(UPLOAD_DIR.glob("upload_*"), key=lambda p: p.stat().st_mtime)
    sobrantes = len(archivos) - _MAX_UPLOADS
    for archivo in archivos[:sobrantes]:
        archivo.unlink(missing_ok=True)

# ─────────────────────────────────────────────
# DETECCIÓN AUTOMÁTICA DE MODO DE VISIÓN
# Prioriza flujo híbrido TM+Gemini si el modelo existe,
# cae a Gemini solo si no está disponible.
# ─────────────────────────────────────────────

def _modelo_tm_disponible() -> bool:
    return Path("model/model.tflite").exists() and Path("model/labels.txt").exists()

# Cargar TM una sola vez al iniciar la API — evita recargar el modelo
# en cada petición (4x más rápido en Raspberry Pi).
tm_global = None
if _modelo_tm_disponible():
    try:
        from vision.tm_classifier import TeachableMachineClassifier
        tm_global = TeachableMachineClassifier()
        MODO_VISION = "hibrido_tm_gemini"
        logger.info("API iniciada | modo=HIBRIDO_TM_GEMINI")
    except Exception as _e:
        MODO_VISION = "gemini"
        logger.warning("TM no disponible (%s) — modo=GEMINI", _e)
else:
    MODO_VISION = "gemini"
    logger.info("API iniciada | modo=GEMINI")

print(f"[RECI API] Modo de visión: {MODO_VISION.upper()}")


# ─────────────────────────────────────────────
# MODELOS DE DATOS
# ─────────────────────────────────────────────

class AtributosInput(BaseModel):
    """Input manual de atributos para el sistema experto."""
    objeto_reconocido: str
    confianza_ml: str
    transparencia: str
    color: str
    forma: str
    brillo: str
    tapa: str
    textura: str
    rigidez: str


# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/", tags=["Info"])
def raiz():
    """Info general de la API."""
    return {
        "proyecto":    "RECI — Tacho Inteligente de Reciclaje",
        "version":     "2.2.0",
        "sede":        "PUCE Manabí",
        "status":      "activo",
        "modo_vision": MODO_VISION,
        "endpoints": {
            "POST /clasificar/atributos":  "Clasificar con atributos manuales",
            "POST /clasificar/imagen":     "Clasificar desde imagen (Gemini o TM)",
            "GET  /estadisticas":          "Estadísticas resumen de la sesión",
            "GET  /estadisticas/detalle":  "Estadísticas detalladas con desglose por objeto",
            "GET  /estadisticas/objetos":  "Top objetos más frecuentes detectados",
            "GET  /historial":             "Últimas clasificaciones",
            "POST /reset":                 "Resetear estadísticas",
            "GET  /health":                "Estado del sistema",
            "GET  /reglas":                "Total de reglas cargadas",
        }
    }


@app.get("/health", tags=["Info"])
def health():
    """Verifica que el sistema experto esté funcionando."""
    try:
        return {
            "status":          "ok",
            "sistema_experto": "activo",
            "total_reglas":    len(engine_global.kb.obtener_reglas()),
            "modo_vision":     MODO_VISION,
            "modelo_tm":       _modelo_tm_disponible(),
            "timestamp":       datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reglas", tags=["Info"])
def obtener_reglas():
    """Retorna información sobre las reglas cargadas."""
    reglas = engine_global.kb.obtener_reglas()

    por_conclusion = {}
    for r in reglas:
        cat = r.conclusion
        if cat not in por_conclusion:
            por_conclusion[cat] = 0
        por_conclusion[cat] += 1

    return {
        "total_reglas":  len(reglas),
        "por_categoria": por_conclusion,
        "timestamp":     datetime.now().isoformat()
    }


@app.post("/clasificar/atributos", tags=["Clasificación"])
def clasificar_atributos(atributos: AtributosInput):
    """
    Clasifica un objeto dado sus atributos visuales.
    Ideal para cuando el modelo ML ya extrajo los atributos.
    Este es el endpoint que usará el Raspberry Pi en producción.
    """
    try:
        datos  = atributos.model_dump()
        engine_global.cargar_hechos(datos)
        conclusion, confianza, reglas = engine_global.ejecutar()
        reporte  = ExplanationReport(engine_global)
        hardware = engine_global.decision_hardware()

        stats.registrar(
            conclusion        = conclusion,
            confianza         = confianza,
            objeto_reconocido = datos.get("objeto_reconocido"),
            reglas_disparadas = len(reglas)
        )

        logger.info("clasificar_atributos | %s %.1f%% | objeto=%s",
                    conclusion, confianza * 100, datos.get("objeto_reconocido"))

        backward = None
        if engine_global.resultado_backward:
            backward = {
                "conclusion":  engine_global.resultado_backward,
                "score":       engine_global.score_backward,
                "consistente": engine_global.resultado_backward == conclusion
            }

        return {
            "success":               True,
            "timestamp":             datetime.now().isoformat(),
            "clasificacion":         conclusion,
            "confianza":             confianza,
            "confianza_pct":         round(confianza * 100, 1),
            "es_reciclable":         conclusion in ["VIDRIO", "PLASTICO"],
            "hardware":              hardware,
            "atributos":             datos,
            "reglas_disparadas":     len(reglas),
            "backward_chaining":     backward,
            "meta_reglas_aplicadas": engine_global.contexto_meta.get(
                "meta_reglas_aplicadas", []),
            "advertencias":          [str(a) for a in engine_global.advertencias_validacion],
            "payload_supabase":      reporte.payload_supabase()
        }

    except Exception as e:
        logger.error("clasificar_atributos ERROR | %s: %s", type(e).__name__, e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clasificar/imagen", tags=["Clasificación"])
async def clasificar_imagen(file: UploadFile = File(...)):
    """
    Clasifica un objeto desde una imagen.

    Modo automático:
    - Si existe model/model.tflite → usa Teachable Machine (producción)
    - Si no existe               → usa Gemini API (desarrollo/fallback)

    El sistema experto y el JSON de respuesta son idénticos en ambos modos.
    """
    try:
        from vision.attribute_extractor import AttributeExtractor

        # Limpiar uploads antiguos antes de guardar el nuevo
        _limpiar_uploads()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = Path(file.filename).suffix or ".jpg"
        ruta_temp = UPLOAD_DIR / f"upload_{timestamp}{extension}"

        with open(ruta_temp, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extractor = AttributeExtractor()

        # ── Flujo híbrido: TM da contexto → Gemini analiza → SE decide ──
        vision_usada = MODO_VISION
        if tm_global is not None:
            # TM corre en ~0.1 s y pasa su voto como contexto a Gemini
            try:
                import cv2
                img = cv2.imread(str(ruta_temp))
                if img is not None:
                    _, clase_tm, prob_tm = tm_global.analizar_frame(img)
                else:
                    clase_tm = prob_tm = None
            except Exception as _te:
                logger.warning("TM falló en API (%s) — Gemini sin contexto", _te)
                clase_tm = prob_tm = None

            try:
                atributos    = extractor.analizar_imagen_hibrido(
                    str(ruta_temp), clase_tm, prob_tm)
                vision_usada = "hibrido_tm_gemini"
            except Exception as _ge:
                logger.warning("Gemini falló (%s) — fallback a TM", _ge)
                atributos    = tm_global.analizar_imagen(str(ruta_temp))
                vision_usada = "tm_fallback"
        else:
            atributos    = extractor.analizar_imagen(str(ruta_temp))
            vision_usada = "gemini"
        # ──────────────────────────────────────────────────────────────

        engine_global.cargar_hechos(atributos)
        conclusion, confianza, reglas = engine_global.ejecutar()
        reporte  = ExplanationReport(engine_global)
        hardware = engine_global.decision_hardware()

        stats.registrar(
            conclusion        = conclusion,
            confianza         = confianza,
            objeto_reconocido = atributos.get("objeto_reconocido"),
            reglas_disparadas = len(reglas)
        )

        logger.info("clasificar_imagen | %s %.1f%% | vision=%s | archivo=%s",
                    conclusion, confianza * 100, vision_usada, file.filename)

        backward = None
        if engine_global.resultado_backward:
            backward = {
                "conclusion":  engine_global.resultado_backward,
                "score":       engine_global.score_backward,
                "consistente": engine_global.resultado_backward == conclusion
            }

        return {
            "success":               True,
            "timestamp":             datetime.now().isoformat(),
            "clasificacion":         conclusion,
            "confianza":             confianza,
            "confianza_pct":         round(confianza * 100, 1),
            "es_reciclable":         conclusion in ["VIDRIO", "PLASTICO"],
            "hardware":              hardware,
            "atributos":             atributos,
            "reglas_disparadas":     len(reglas),
            "backward_chaining":     backward,
            "meta_reglas_aplicadas": engine_global.contexto_meta.get(
                "meta_reglas_aplicadas", []),
            "advertencias":          [str(a) for a in engine_global.advertencias_validacion],
            "payload_supabase":      reporte.payload_supabase(),
            "imagen_procesada":      file.filename,
            "vision_usada":          vision_usada
        }

    except Exception as e:
        logger.error("clasificar_imagen ERROR | %s: %s", type(e).__name__, e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/estadisticas", tags=["Dashboard"])
def obtener_estadisticas():
    """
    Retorna estadísticas de la sesión actual.
    El dashboard de Next.js consume este endpoint.
    """
    payload = stats.payload_dashboard()
    return {
        "success":   True,
        "timestamp": datetime.now().isoformat(),
        "datos":     payload,
        "historial_reciente": [
            {
                "timestamp":     e["timestamp"],
                "clasificacion": e["conclusion"],
                "confianza":     e["confianza"],
                "exitosa":       e["exitosa"]
            }
            for e in stats.historial[-10:]
        ]
    }


@app.get("/estadisticas/detalle", tags=["Dashboard"])
def obtener_estadisticas_detalle():
    """
    Estadísticas detalladas de la sesión.
    Incluye desglose por objeto reconocido y confianza promedio por categoría.
    Ideal para el dashboard de análisis del equipo.
    """
    return {
        "success":   True,
        "timestamp": datetime.now().isoformat(),
        "datos":     stats.payload_detalle(),
        "historial_reciente": [
            {
                "timestamp":         e["timestamp"],
                "clasificacion":     e["conclusion"],
                "objeto_reconocido": e["objeto_reconocido"],
                "confianza_pct":     round(e["confianza"] * 100, 1),
                "reglas_disparadas": e["reglas_disparadas"],
                "exitosa":           e["exitosa"]
            }
            for e in stats.historial[-20:]
        ]
    }


@app.get("/estadisticas/objetos", tags=["Dashboard"])
def obtener_estadisticas_objetos(top: int = 10):
    """
    Top de objetos reconocidos más frecuentes en la sesión.
    Útil para saber qué objetos se depositan más en RECI.
    """
    return {
        "success":           True,
        "timestamp":         datetime.now().isoformat(),
        "total_sesion":      stats.total_clasificaciones,
        "top_objetos":       stats.objetos_reconocidos_frecuentes(top),
        "confianza_por_cat": stats.confianza_promedio_por_categoria()
    }


@app.get("/historial", tags=["Dashboard"])
def obtener_historial(limite: int = 20):
    """Retorna el historial de clasificaciones."""
    historial = stats.historial[-limite:]
    return {
        "success":   True,
        "timestamp": datetime.now().isoformat(),
        "total":     len(stats.historial),
        "mostrando": len(historial),
        "historial": list(reversed(historial))
    }


@app.post("/reset", tags=["Dashboard"])
def resetear_estadisticas():
    """Resetea las estadísticas de la sesión actual."""
    stats.resetear()
    return {
        "success":   True,
        "mensaje":   "Estadísticas reseteadas correctamente",
        "timestamp": datetime.now().isoformat()
    }