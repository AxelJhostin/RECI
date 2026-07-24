"""Pruebas de los votos sin fusión entre proveedor y modelo local."""

from vision.voting import build_photo_votes, decide_material


def _local(material: str, confidence: float) -> dict:
    return {"material": material, "confidence": confidence, "model": "model.tflite"}


def test_dos_modelos_generan_dos_votos_independientes():
    votes = build_photo_votes("plastico", 0.90, _local("vidrio", 0.80))

    assert votes == [
        {
            "source": "openai_sistema_experto",
            "material": "plastico",
            "confidence": 0.9,
            "counts_as_vote": True,
        },
        {
            "source": "modelo_local",
            "material": "vidrio",
            "confidence": 0.8,
            "counts_as_vote": True,
        },
    ]


def test_desconocido_es_abstencion_y_no_bloquea_el_voto_local():
    votes = build_photo_votes("desconocido", 1.0, _local("vidrio", 0.93))

    assert votes[0]["counts_as_vote"] is False
    assert votes[1]["counts_as_vote"] is True
    assert votes[1]["material"] == "vidrio"


def test_fallo_del_modelo_local_conserva_el_voto_del_proveedor():
    votes = build_photo_votes("vidrio", 0.93, None)

    assert len(votes) == 1
    assert votes[0]["material"] == "vidrio"
    assert votes[0]["counts_as_vote"] is True


def _votes(materials: list[str]) -> list[dict]:
    return [{"material": material, "counts_as_vote": material in {"plastico", "vidrio"}}
            for material in materials]


def test_mayoria_de_openai_gana_el_desempate_global_3_a_3():
    result = decide_material(_votes(["plastico", "plastico", "vidrio"]),
                             _votes(["vidrio", "vidrio", "plastico"]))

    assert result == {"material": "plastico", "source": "openai_sistema_experto"}


def test_modelo_local_es_respaldo_si_openai_no_tiene_mayoria():
    result = decide_material(_votes(["desconocido", "vidrio", "desconocido"]),
                             _votes(["plastico", "plastico", "vidrio"]))

    assert result == {"material": "plastico", "source": "modelo_local_respaldo"}


def test_sin_mayoria_en_ninguna_señal_conserva_desconocido():
    result = decide_material(_votes(["plastico", "vidrio", "desconocido"]),
                             _votes(["vidrio", "plastico", "desconocido"]))

    assert result == {"material": "desconocido", "source": "sin_mayoria"}
