"""Smoke test del artefacto TFLite portado desde RECI2."""

import numpy as np

from vision.local_model import LocalMaterialClassifier


def test_modelo_local_carga_y_entrega_probabilidades_binarias():
    classifier = LocalMaterialClassifier()
    prediction = classifier.predict(np.zeros((240, 320, 3), dtype=np.uint8))

    assert prediction["material"] in {"plastico", "vidrio"}
    assert 0.0 <= prediction["confidence"] <= 1.0
    assert set(prediction["probabilities"]) == {"plastico", "vidrio"}
    assert abs(sum(prediction["probabilities"].values()) - 1.0) < 1e-4
