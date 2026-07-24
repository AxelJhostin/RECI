"""Votos independientes por cada captura de la ESP32-CAM.

El proveedor (OpenAI + heurísticas + sistema experto) y el modelo TFLite no
se combinan dentro de una misma foto. Cada uno aporta un voto visible; el
firmware reúne los votos de las tres capturas. OpenAI es la señal primaria
porque la validación actual demuestra mayor precisión; el modelo local queda
como respaldo cuando OpenAI no logra mayoría.
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


def majority_material(materials: list[str]) -> str:
    """Devuelve mayoría estricta de una señal o ``desconocido``."""
    plastic = materials.count("plastico")
    glass = materials.count("vidrio")
    if max(plastic, glass) < 2 or plastic == glass:
        return "desconocido"
    return "plastico" if plastic > glass else "vidrio"


def decide_material(
    provider_votes: list[dict[str, Any]],
    local_votes: list[dict[str, Any]],
) -> dict[str, str]:
    """Aplica la política primaria OpenAI + respaldo local.

    Un empate global 3–3 se resuelve por la mayoría interna del proveedor si
    existe. Si OpenAI no tiene mayoría, se consulta la mayoría del modelo
    local. Si ninguna señal tiene mayoría estricta, se conserva el rechazo.
    """
    provider = majority_material([
        str(vote.get("material", "desconocido"))
        for vote in provider_votes
        if vote.get("counts_as_vote", vote.get("material") in MATERIALS)
    ])
    if provider != "desconocido":
        return {"material": provider, "source": "openai_sistema_experto"}

    local = majority_material([
        str(vote.get("material", "desconocido"))
        for vote in local_votes
        if vote.get("counts_as_vote", vote.get("material") in MATERIALS)
    ])
    if local != "desconocido":
        return {"material": local, "source": "modelo_local_respaldo"}
    return {"material": "desconocido", "source": "sin_mayoria"}
