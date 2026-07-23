"""Fusión conservadora del proveedor visual y el MobileNetV2 local."""

from __future__ import annotations

from typing import Any

MATERIALS = ("plastico", "vidrio")


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _binary_scores(material: str, confidence: float) -> dict[str, float]:
    confidence = _clamp(confidence)
    if material not in MATERIALS:
        return {"plastico": 0.5, "vidrio": 0.5}
    other = "vidrio" if material == "plastico" else "plastico"
    return {material: confidence, other: 1.0 - confidence}


def fuse_material_predictions(
    provider_material: str,
    provider_confidence: float,
    local_prediction: dict[str, Any] | None,
    *,
    provider_weight: float = 0.70,
    local_weight: float = 0.30,
    minimum_confidence: float = 0.70,
) -> dict[str, Any]:
    """
    Combina dos señales binarias, dando mayor peso al proveedor.

    El modelo local no puede reconocer lata, orgánico u otros rechazos. Por
    eso nunca reemplaza un ``desconocido`` emitido por proveedor + sistema
    experto. Tampoco puede contradecir por sí solo al proveedor: un conflicto
    fuerte produce ``desconocido``.
    """
    if provider_weight <= 0 or local_weight < 0:
        raise ValueError("Los pesos de fusión no son válidos")
    total_weight = provider_weight + local_weight
    provider_weight /= total_weight
    local_weight /= total_weight
    minimum_confidence = _clamp(minimum_confidence)

    provider = {
        "material": provider_material,
        "confidence": round(_clamp(provider_confidence), 6),
        "weight": round(provider_weight, 4),
    }

    if local_prediction is None:
        return {
            "material": provider_material,
            "confidence": round(_clamp(provider_confidence), 6),
            "agreement": None,
            "method": "solo_proveedor",
            "provider": provider,
            "local": None,
            "scores": None,
            "minimum_confidence": minimum_confidence,
        }

    local_material = str(local_prediction.get("material", "desconocido"))
    local_confidence = _clamp(local_prediction.get("confidence", 0.0))
    local_scores = local_prediction.get("probabilities")
    if not isinstance(local_scores, dict) or not all(
        material in local_scores for material in MATERIALS
    ):
        local_scores = _binary_scores(local_material, local_confidence)
    else:
        local_scores = {
            material: _clamp(local_scores[material]) for material in MATERIALS
        }

    local = {
        **local_prediction,
        "material": local_material,
        "confidence": round(local_confidence, 6),
        "weight": round(local_weight, 4),
    }
    agreement = provider_material == local_material

    # El proveedor + sistema experto puede detectar materiales que el modelo
    # binario nunca vio. Esos rechazos se conservan sin excepción.
    if provider_material not in MATERIALS:
        return {
            "material": "desconocido",
            "confidence": round(_clamp(provider_confidence), 6),
            "agreement": False,
            "method": "rechazo_conservador_proveedor",
            "provider": provider,
            "local": local,
            "scores": None,
            "minimum_confidence": minimum_confidence,
        }

    provider_scores = _binary_scores(provider_material, provider_confidence)
    scores = {
        material: (
            provider_weight * provider_scores[material]
            + local_weight * local_scores[material]
        )
        for material in MATERIALS
    }
    winner = max(scores, key=scores.get)
    winner_confidence = scores[winner]

    # OpenAI + sistema experto conservan autoridad. El modelo propio puede
    # reforzar o vetar por incertidumbre, pero no abrir la otra compuerta.
    safe = winner == provider_material and winner_confidence >= minimum_confidence
    return {
        "material": winner if safe else "desconocido",
        "confidence": round(winner_confidence if safe else 0.0, 6),
        "agreement": agreement,
        "method": "fusion_ponderada" if safe else "conflicto_sin_mayoria_segura",
        "provider": provider,
        "local": local,
        "scores": {key: round(value, 6) for key, value in scores.items()},
        "minimum_confidence": minimum_confidence,
    }
