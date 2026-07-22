"""Regresiones del refinamiento de atributos aportadas desde RECI2."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from expert_system.inference_engine import InferenceEngine
from vision.visual_heuristics import (
    _corregir_enjuague_y_atomizador,
    _corregir_vaso_espuma_como_carton,
)


def _clasificar(atributos: dict) -> str:
    engine = InferenceEngine()
    engine.cargar_hechos(atributos)
    conclusion, _, _ = engine.ejecutar()
    return conclusion


def test_enjuague_sin_tapa_no_va_a_vidrio():
    atributos = {
        "objeto_reconocido": "botella_enjuague_bucal", "confianza_ml": "alta",
        "transparencia": "alta", "color": "variado_vivo",
        "forma": "cilindrica_estandar", "brillo": "alto_nitido",
        "tapa": "sin_tapa", "textura": "lisa_brillante", "rigidez": "rigido",
    }
    assert _clasificar(atributos) == "PLASTICO"
    corregidos = _corregir_enjuague_y_atomizador(atributos)
    assert corregidos["tapa"] == "rosca_plastico"
    assert _clasificar(corregidos) == "PLASTICO"


def test_atomizador_transparente_es_plastico():
    atributos = {
        "objeto_reconocido": "botella_atomizador", "confianza_ml": "alta",
        "transparencia": "alta", "color": "transparente",
        "forma": "cilindrica_estandar", "brillo": "medio_difuso",
        "tapa": "sin_tapa", "textura": "lisa_brillante", "rigidez": "rigido",
    }
    corregidos = _corregir_enjuague_y_atomizador(atributos)
    assert corregidos["tapa"] == "rosca_plastico"
    assert _clasificar(corregidos) == "PLASTICO"


def test_vaso_espuma_blanco_no_se_mantiene_como_carton():
    atributos = {
        "objeto_reconocido": "vaso_carton", "confianza_ml": "alta",
        "transparencia": "ninguna", "color": "blanco_opaco",
        "forma": "conica", "brillo": "bajo",
        "tapa": "sin_tapa", "textura": "fibrosa", "rigidez": "rigido",
    }
    corregidos = _corregir_vaso_espuma_como_carton(atributos)
    assert corregidos["objeto_reconocido"] == "vaso_plastico_blanco"
    assert _clasificar(corregidos) == "PLASTICO"


if __name__ == "__main__":
    test_enjuague_sin_tapa_no_va_a_vidrio()
    test_atomizador_transparente_es_plastico()
    test_vaso_espuma_blanco_no_se_mantiene_como_carton()
    print("test_refinar_api: 3/3 OK")
