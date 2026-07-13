# api/app.py
# API REST del sistema experto RECI
# Conecta el sistema experto con el dashboard y el equipo de nube
# Ejecutar: uvicorn api.app:app --reload --port 8000

import os
import sys
import json
import logging
import shutil
import contextlib
import io
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
# Prioriza flujo híbrido TM + API (Claude o Gemini) si el modelo existe.
# ─────────────────────────────────────────────

from dotenv import load_dotenv
load_dotenv()

from vision.vision_config import (
    imprimir_banner_vision,
    resolver_config_vision,
    resumen_para_health,
)

try:
    VISION_CONFIG = resolver_config_vision()
    imprimir_banner_vision(VISION_CONFIG)
    VISION_PROVIDER = VISION_CONFIG["vision_api"]
except ValueError as _cfg_err:
    VISION_CONFIG = None
    VISION_PROVIDER = os.environ.get("VISION_API", "gemini").lower().strip() or "gemini"
    print(f"[RECI API] ⚠ Configuración visión incompleta: {_cfg_err}")

def _modelo_tm_disponible() -> bool:
    return Path("model/model.tflite").exists() and Path("model/labels.txt").exists()

# Cargar TM una sola vez al iniciar la API — evita recargar el modelo
# en cada petición (4x más rápido en Raspberry Pi).
tm_global = None
if _modelo_tm_disponible():
    try:
        from vision.tm_classifier import TeachableMachineClassifier
        tm_global = TeachableMachineClassifier()
        MODO_VISION = f"hibrido_tm_{VISION_PROVIDER}"
        logger.info("API iniciada | modo=HIBRIDO_TM_%s", VISION_PROVIDER.upper())
    except Exception as _e:
        MODO_VISION = VISION_PROVIDER
        logger.warning("TM no disponible (%s) — modo=%s", _e, VISION_PROVIDER.upper())
else:
    MODO_VISION = VISION_PROVIDER
    logger.info("API iniciada | modo=%s", VISION_PROVIDER.upper())

if VISION_CONFIG:
    print(f"[RECI API] Proveedor activo: {VISION_CONFIG['proveedor_label']} · {VISION_CONFIG['modelo_primario']}")
else:
    print(f"[RECI API] Modo de visión: {MODO_VISION.upper()} (sin validación completa)")


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
            "POST /clasificar/imagen":     "Clasificar desde imagen (Claude, Gemini o TM)",
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
        payload = {
            "status":          "ok",
            "sistema_experto": "activo",
            "total_reglas":    len(engine_global.kb.obtener_reglas()),
            "modo_vision":     MODO_VISION,
            "modelo_tm":       _modelo_tm_disponible(),
            "timestamp":       datetime.now().isoformat(),
        }
        if VISION_CONFIG:
            payload["vision"] = resumen_para_health(VISION_CONFIG)
        else:
            payload["vision"] = {
                "proveedor": VISION_PROVIDER,
                "modelo": None,
                "modo_flujo": MODO_VISION,
                "tm_disponible": _modelo_tm_disponible(),
                "advertencias": ["Configuración de visión no validada — revisa .env"],
            }
        return payload
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
    - Si existe model/model.tflite → flujo híbrido TM + Claude/Gemini
    - Si no existe               → solo API de visión (Claude o Gemini)

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

        extractor = AttributeExtractor(mostrar_banner=False)

        with contextlib.redirect_stdout(io.StringIO()):
            resultado = extractor.analizar_y_clasificar_hibrido(
                str(ruta_temp), clf=tm_global
            )

        atributos = resultado["atributos"]
        conclusion = resultado["conclusion"]
        confianza = resultado["confianza"]
        reporte = resultado["reporte"]
        hardware = resultado["hardware"]
        vision_usada = resultado.get("vision_modo", MODO_VISION)
        vision_fallback = resultado.get("vision_fallback", False)
        vision_fallback_motivo = resultado.get("vision_fallback_motivo")
        razonamiento = reporte.get("razonamiento", {})
        reglas_count = razonamiento.get("total_reglas_disparadas", 0)

        if vision_fallback:
            logger.warning(
                "clasificar_imagen FALLBACK | motivo=%s | archivo=%s",
                vision_fallback_motivo, file.filename,
            )

        stats.registrar(
            conclusion        = conclusion,
            confianza         = confianza,
            objeto_reconocido = atributos.get("objeto_reconocido"),
            reglas_disparadas = reglas_count
        )

        logger.info(
            "clasificar_imagen | %s %.1f%% | vision=%s | fallback=%s | archivo=%s",
            conclusion, confianza * 100, vision_usada, vision_fallback, file.filename,
        )

        return {
            "success":               True,
            "timestamp":             datetime.now().isoformat(),
            "clasificacion":         conclusion,
            "confianza":             confianza,
            "confianza_pct":         round(confianza * 100, 1),
            "es_reciclable":         conclusion in ["VIDRIO", "PLASTICO"],
            "hardware":              hardware,
            "atributos":             atributos,
            "reglas_disparadas":     reglas_count,
            "backward_chaining":     razonamiento.get("backward_chaining"),
            "meta_reglas_aplicadas": razonamiento.get("meta_reglas_aplicadas", []),
            "advertencias":          razonamiento.get("advertencias", []),
            "payload_supabase":      reporte.get("payload_supabase"),
            "imagen_procesada":      file.filename,
            "vision_usada":          vision_usada,
            "vision_proveedor":      resultado.get("vision_proveedor"),
            "vision_modelo":         resultado.get("vision_modelo"),
            "vision_fallback":       vision_fallback,
            "vision_fallback_motivo": vision_fallback_motivo,
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