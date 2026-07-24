"""Pruebas de los votos sin fusión entre proveedor y modelo local."""

from vision.voting import build_photo_votes


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
