# tests/test_refinar_api.py
# Pruebas unitarias del refinamiento post-API (lata, vidrio, metal)

import sys
import os
import numpy as np
import cv2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.visual_heuristics import refinar_atributos_api
from expert_system.inference_engine import InferenceEngine


def _img_metal_plateado():
    """Simula superficie aluminio plateado con brillo."""
    img = np.full((224, 224, 3), 180, dtype=np.uint8)
    cv2.rectangle(img, (70, 40), (154, 184), (210, 210, 215), -1)
    cv2.line(img, (80, 50), (145, 55), (240, 240, 255), 2)
    return img


def _img_opaca_roja():
    """Simula lata roja opaca (sin transparencia)."""
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    cv2.rectangle(img, (75, 50), (149, 174), (20, 20, 180), -1)
    return img


def test_metal_detectado_como_lata():
    attrs = {
        "objeto_reconocido": "botella_gaseosa",
        "confianza_ml": "alta",
        "transparencia": "ninguna",
        "color": "variado_vivo",
        "forma": "cilindrica_estandar",
        "brillo": "medio_difuso",
        "tapa": "rosca_plastico",
        "textura": "lisa_brillante",
        "rigidez": "rigido",
    }
    out = refinar_atributos_api(attrs, _img_metal_plateado(), "plastico", 0.99)
    assert out["objeto_reconocido"] == "lata", out
    assert out["brillo"] == "metalico", out


def test_lata_roja_api_confundio_con_botella():
    attrs = {
        "objeto_reconocido": "botella_agua",
        "confianza_ml": "alta",
        "transparencia": "alta",
        "color": "transparente",
        "forma": "cilindrica_estandar",
        "brillo": "alto_nitido",
        "tapa": "rosca_plastico",
        "textura": "lisa_brillante",
        "rigidez": "rigido",
    }
    out = refinar_atributos_api(attrs, _img_opaca_roja(), "plastico", 1.0)
    assert out["objeto_reconocido"] == "lata", out


def test_tm_vidrio_corrige_rosca_plastico():
    attrs = {
        "objeto_reconocido": "botella_agua",
        "confianza_ml": "alta",
        "transparencia": "alta",
        "color": "transparente",
        "forma": "cilindrica_estandar",
        "brillo": "alto_nitido",
        "tapa": "rosca_plastico",
        "textura": "lisa_brillante",
        "rigidez": "rigido",
    }
    img = np.full((224, 224, 3), 120, dtype=np.uint8)
    cv2.rectangle(img, (90, 30), (134, 190), (200, 220, 230), -1)
    cv2.line(img, (95, 40), (128, 45), (255, 255, 255), 2)
    out = refinar_atributos_api(attrs, img, "vidrio", 0.95)
    assert out["tapa"] == "twist_off_metalica", out
    assert "vidrio" in out["objeto_reconocido"], out


def test_lata_pasa_por_sistema_experto():
    engine = InferenceEngine()
    engine.cargar_hechos({
        "objeto_reconocido": "lata", "confianza_ml": "media",
        "transparencia": "ninguna", "color": "variado_vivo",
        "forma": "cilindrica_estandar", "brillo": "medio_difuso",
        "tapa": "sellado", "textura": "lisa_brillante", "rigidez": "rigido",
    })
    conclusion, _, _ = engine.ejecutar()
    hw = engine.decision_hardware()
    assert conclusion == "LATA", conclusion
    assert "no permitido" in hw["mensaje"].lower()


if __name__ == "__main__":
    test_metal_detectado_como_lata()
    test_lata_roja_api_confundio_con_botella()
    test_tm_vidrio_corrige_rosca_plastico()
    test_lata_pasa_por_sistema_experto()
    print("✅ test_refinar_api: 4/4 OK")
