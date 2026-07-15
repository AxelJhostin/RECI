# RECI — Entrenamiento del modelo MobileNetV2

Guía para agregar fotos y reentrenar **en tu computadora** (recomendado). Colab ya no es necesario.

---

## Flujo resumido

```
tomar_fotos.py  →  RECI_dataset_propio/  →  scripts/entrenar_modelo.py  →  verificar  →  model/
  fotos_dataset/      plastico/ + vidrio/         runs/run_.../              tests
```

---

## 0. Requisitos

```bash
pip3 install -r requirements.txt
```

| Plataforma | Aceleración |
|------------|-------------|
| **Mac Apple Silicon (M1–M4)** | `pip install tensorflow-metal` — usa GPU Metal (mucho más rápido que CPU) |
| **PC con NVIDIA** | TensorFlow 2.x + drivers CUDA/cuDNN |
| **Solo CPU** | Funciona, pero ~21k fotos pueden tardar **muchas horas** |

---

## 1. Tener el dataset en local

Copia desde Google Drive (una sola vez) la carpeta **`RECI_dataset_propio`** a tu disco, por ejemplo:

```
~/RECI_dataset_propio/
├── plastico/              ← fotos en bruto
├── vidrio/
├── dataset_organizado/    ← train/val (se actualiza al entrenar)
│   ├── train/plastico/
│   ├── train/vidrio/
│   ├── val/plastico/
│   └── val/vidrio/
└── runs/                  ← salida de cada entrenamiento
```

Variable opcional:

```bash
export RECI_DATASET_BASE=~/RECI_dataset_propio
```

---

## 2. Capturar fotos nuevas (campus)

```bash
python3 tomar_fotos.py plastico
python3 tomar_fotos.py vidrio
```

| Tecla | Acción |
|-------|--------|
| `ESPACIO` | Una foto |
| `R` | Ráfaga ~0.2 s/foto durante 60 s |
| `Q` | Salir |

Las fotos quedan en `fotos_dataset/` (gitignored). Al entrenar, usa `--sync-fotos-repo` para copiarlas a `plastico/` y `vidrio/`.

---

## 3. Entrenar en local (recomendado)

### Entrenamiento completo (Fase 1 + 2 + export TFLite)

```bash
cd /ruta/a/RECI
python3 scripts/entrenar_modelo.py --sync-fotos-repo
```

### Opciones útiles

```bash
# Dataset en otra ruta
python3 scripts/entrenar_modelo.py --dataset-base /Volumes/Disco/RECI_dataset_propio

# Menos RAM / CPU lento
python3 scripts/entrenar_modelo.py --batch-size 16

# Al terminar, copiar a model/ si accuracy ≥ 90%
python3 scripts/entrenar_modelo.py --instalar-modelo

python3 scripts/entrenar_modelo.py --help
```

**Tiempo estimado (referencia):**

| Hardware | Fase 1 + 2 (~21k fotos) |
|----------|---------------------------|
| Colab GPU T4 | ~2–4 h |
| Mac M4 + tensorflow-metal | ~4–8 h (estimado) |
| CPU sola | 12–24+ h |

Puedes dejar la terminal abierta; si se interrumpe, ver [Reanudar](#reanudar-si-se-interrumpe-o-si-colab-se-desconectó).

---

## 4. Dónde quedan los archivos

Cada run **no sobrescribe** el modelo anterior:

```
RECI_dataset_propio/runs/run_YYYYMMDD_HHMM/
├── mejor_modelo.keras          ← mejor Fase 1
├── mejor_modelo_ft.keras       ← mejor Fase 2
├── model.tflite                ← para RECI
├── labels.txt
├── entrenamiento_manifest.json ← métricas, matriz de confusión
├── training_state.json         ← progreso para reanudar
├── fase1_history.csv
└── fase2_history.csv
```

Revisa `entrenamiento_manifest.json` antes de producción (meta: ≥ 90% val accuracy, buen recall en `vidrio`).

---

## 5. Reanudar si se interrumpe (o si Colab se desconectó)

Colab puede cortar la sesión en Fase 1 (como en época 7/15). **No pierdes todo**: `ModelCheckpoint` guarda el mejor modelo (ej. época 3 con ~91.6% val).

### Caso A — Colab falló en Fase 1; ya tienes `mejor_modelo.keras` en Drive

1. Descarga la carpeta `runs/run_20260715_1437/` (o la tuya) a `~/RECI_dataset_propio/runs/`
2. Asegúrate de tener `dataset_organizado/` en local (mismo Drive)
3. **Continúa con Fase 2** (fine-tuning):

```bash
python3 scripts/entrenar_modelo.py \
  --solo-fase 2 \
  --checkpoint ~/RECI_dataset_propio/runs/run_20260715_1437/mejor_modelo.keras \
  --dataset-base ~/RECI_dataset_propio
```

### Caso B — Reanudar Fase 1 en la misma carpeta de run

```bash
python3 scripts/entrenar_modelo.py \
  --solo-fase 1 \
  --resume \
  --output-dir ~/RECI_dataset_propio/runs/run_20260715_1437 \
  --dataset-base ~/RECI_dataset_propio
```

### Caso C — Solo exportar TFLite (Fase 2 ya terminó)

```bash
python3 scripts/entrenar_modelo.py \
  --solo-fase 6 \
  --checkpoint ~/RECI_dataset_propio/runs/run_XXXX/mejor_modelo_ft.keras \
  --dataset-base ~/RECI_dataset_propio
```

---

## 6. Instalar el nuevo modelo en RECI

```bash
cp ~/RECI_dataset_propio/runs/run_XXXX/model.tflite model/model.tflite
cp ~/RECI_dataset_propio/runs/run_XXXX/labels.txt   model/labels.txt

python3 tests/test_imagenes_completo.py
python3 vision/tm_classifier.py images/prueba10.jpeg
```

Solo usa en demo/hardware cuando los tests pasen.

---

## Colab (legacy, opcional)

Los notebooks `RECI_entrenar_automatico.ipynb` y `RECI_entrenar_modelo.ipynb` siguen en el repo por si los necesitas, pero **pueden desconectarse** y son más difíciles de reanudar. Preferir **`scripts/entrenar_modelo.py`**.

---

## Hiperparámetros (igual que Colab)

| Parámetro | Valor |
|-----------|-------|
| Arquitectura | MobileNetV2 + transfer learning |
| Entrada | 224×224 RGB |
| Batch size | 32 (ajustable) |
| Fase 1 | 15 épocas max, LR 0.001, base congelada |
| Fase 2 | 10 épocas max, LR 0.00005, últimas 30 capas |
| Augmentation | flip, rotación ±10%, zoom ±10%, brillo ±10% |
| Split | 85% train / 15% val, `RANDOM_SEED=42` |
| Desbalance | `class_weight` automático (~1.75:1 plástico:vidrio) |

---

## Ver también

- [README — Modelo de ML](../README.md#modelo-de-machine-learning)
- [FLUJO_RECONOCIMIENTO.md](FLUJO_RECONOCIMIENTO.md)
