"""Votos independientes por cada captura de la ESP32-CAM.

El proveedor (OpenAI + heurísticas + sistema experto) y el modelo TFLite no
se combinan dentro de una misma foto. Cada uno aporta un voto visible; el
firmware reúne los votos de las tres capturas y decide por mayoría simple.
"""

from __future__ import annotations

from typing import Any

MATERIALS = ("plastico", "vidrio")


def _clamp(value: object) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def build_photo_votes(
    provider_material: str,
    provider_confidence: float,
    local_prediction: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Construye los votos de una foto sin ponderarlos ni fusionarlos.

    ``desconocido`` se conserva como diagnóstico, pero ``counts_as_vote`` es
    falso: es una abstención y no favorece a plástico ni a vidrio.
    """
    provider_material = str(provider_material)
    votes: list[dict[str, Any]] = [
        {
            "source": "openai_sistema_experto",
            "material": provider_material,
            "confidence": round(_clamp(provider_confidence), 6),
            "counts_as_vote": provider_material in MATERIALS,
        }
    ]

    if local_prediction is None:
        return votes

    local_material = str(local_prediction.get("material", "desconocido"))
    votes.append(
        {
            "source": "modelo_local",
            "material": local_material,
            "confidence": round(_clamp(local_prediction.get("confidence", 0.0)), 6),
            "counts_as_vote": local_material in MATERIALS,
        }
    )
    return votes
