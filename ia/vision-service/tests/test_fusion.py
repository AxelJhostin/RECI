"""Pruebas de la fusión ponderada proveedor + MobileNetV2."""

from vision.fusion import fuse_material_predictions


def _local(material: str, confidence: float) -> dict:
    other = "vidrio" if material == "plastico" else "plastico"
    return {
        "material": material,
        "confidence": confidence,
        "probabilities": {material: confidence, other: 1.0 - confidence},
        "model": "model.tflite",
    }


def test_acuerdo_refuerza_resultado():
    result = fuse_material_predictions(
        "plastico", 0.90, _local("plastico", 0.80)
    )

    assert result["material"] == "plastico"
    assert result["confidence"] == 0.86
    assert result["agreement"] is True
    assert result["method"] == "fusion_ponderada"


def test_conflicto_fuerte_rechaza_en_vez_de_abrir_compuerta():
    result = fuse_material_predictions(
        "plastico", 0.90, _local("vidrio", 0.99)
    )

    assert result["material"] == "desconocido"
    assert result["confidence"] == 0.0
    assert result["agreement"] is False
    assert result["method"] == "conflicto_sin_mayoria_segura"


def test_modelo_binario_no_revierte_rechazo_del_sistema_experto():
    result = fuse_material_predictions(
        "desconocido", 1.0, _local("plastico", 0.999)
    )

    assert result["material"] == "desconocido"
    assert result["method"] == "rechazo_conservador_proveedor"


def test_fallback_conserva_flujo_actual_si_modelo_no_esta_disponible():
    result = fuse_material_predictions("vidrio", 0.93, None)

    assert result["material"] == "vidrio"
    assert result["confidence"] == 0.93
    assert result["method"] == "solo_proveedor"

