# vision/clasificacion_log.py
# Registro JSONL por clasificación (trazabilidad para depuración — roadmap A6)

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

LOG_PATH = Path("logs/clasificaciones.jsonl")


def registrar_clasificacion(
    *,
    origen: str,
    imagen: str | None = None,
    tm_clase: str | None = None,
    tm_prob: float | None = None,
    proveedor: str | None = None,
    modelo: str | None = None,
    vision_modo: str | None = None,
    fallback: bool = False,
    fallback_motivo: str | None = None,
    atributos_api: dict | None = None,
    atributos_finales: dict | None = None,
    conclusion: str | None = None,
    confianza: float | None = None,
    reglas_disparadas: int | None = None,
    backward: dict | None = None,
    hardware: dict | None = None,
    extra: dict | None = None,
) -> None:
    """Append una línea JSON al log de clasificaciones."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entrada: dict[str, Any] = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "origen": origen,
        "imagen": imagen,
        "tm": {
            "clase": tm_clase,
            "prob": round(tm_prob, 4) if tm_prob is not None else None,
        },
        "vision": {
            "proveedor": proveedor,
            "modelo": modelo,
            "modo": vision_modo,
            "fallback": fallback,
            "fallback_motivo": fallback_motivo,
        },
        "atributos_api": atributos_api,
        "atributos_finales": atributos_finales,
        "conclusion": conclusion,
        "confianza": round(confianza, 4) if confianza is not None else None,
        "reglas_disparadas": reglas_disparadas,
        "backward": backward,
        "hardware": hardware,
    }
    if extra:
        entrada["extra"] = extra

    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entrada, ensure_ascii=False) + "\n")
