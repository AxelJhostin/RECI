# Modelo local de materiales

Este directorio contiene el MobileNetV2 entrenado por Axel Hernández en
RECI2 y exportado a TensorFlow Lite.

- `model.tflite`: modelo binario `plastico | vidrio`.
- `labels.txt`: orden de las salidas.
- `entrenamiento_manifest.json`: métricas y procedencia del entrenamiento.

El run original es `RECI2/runs/run_20260721_2129`:

- entrenamiento: 13,258 imágenes de plástico y 13,043 de vidrio;
- validación: 2,343 imágenes de plástico y 2,304 de vidrio;
- `val_accuracy`: 98.43 %.

Estas métricas corresponden al dataset anterior. No garantizan el mismo
resultado con la ESP32-CAM; el modelo debe evaluarse con fotos de esa cámara
antes de modificar la política de votación.

Como prueba de portabilidad, el artefacto integrado acertó 13/15 imágenes
reales etiquetadas de `RECI2/images/`. Los dos errores fueron el par ambiguo
de Gatorade vidrio/plástico (`prueba10.jpeg` y `prueba12.jpeg`). Esta
evidencia justifica que el modelo local no decida a partir de una sola foto:
su resultado aporta un voto dentro de la mayoría de seis señales.

La evaluación más relevante disponible usa 201 capturas QVGA reales de la
ESP32-CAM etiquetadas como vidrio: **141/201 (70.15 %)** fueron correctas.
Todavía no existen capturas guardadas de plástico con esa cámara. El reporte
completo y el protocolo de continuación están en
[`docs/VALIDACION-MODELO-LOCAL-ESP32-CAM.md`](../../../docs/VALIDACION-MODELO-LOCAL-ESP32-CAM.md).

El servicio carga el modelo una sola vez. Intenta usar, en orden,
`ai-edge-litert`, `tflite-runtime` o `tensorflow`. Si ninguno está disponible
o el archivo falla, mantiene el flujo existente del proveedor visual y el
sistema experto.
