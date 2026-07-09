# RECI — Entrenamiento del modelo MobileNetV2

Guía rápida para agregar fotos y reentrenar sin tocar el modelo en producción hasta verificar el nuevo.

---

## Flujo resumido

```
tomar_fotos.py (Mac)  →  subir a Drive  →  Colab automático  →  verificar  →  model/
     fotos_dataset/         plastico/          runs/run_.../          tests       producción
                            vidrio/
```

---

## 1. Capturar fotos en el campus

```bash
python3 tomar_fotos.py plastico
python3 tomar_fotos.py vidrio
```

| Tecla | Acción |
|-------|--------|
| `ESPACIO` | Una foto (recomendado para vidrio difícil) |
| `R` | Ráfaga ~0.2 s/foto durante 60 s (variar ángulos) |
| `Q` | Salir |

Las fotos se guardan en `fotos_dataset/plastico/` o `fotos_dataset/vidrio/` (local, no van al repo).

**Consejos:** fondo uniforme si puedes, buena luz, objeto centrado. Prioriza más fotos de **vidrio** (clase minoritaria, ratio ~1.75:1).

---

## 2. Subir a Google Drive

Copia el contenido de `fotos_dataset/` a:

```
Mi unidad/RECI_dataset_propio/plastico/
Mi unidad/RECI_dataset_propio/vidrio/
```

Las fotos nuevas se **mezclan** con las existentes; el notebook solo copia las que aún no están en `dataset_organizado/`.

---

## 3. Entrenar en Colab

### Opción A — Automático (recomendado)

1. Abrir **`RECI_entrenar_automatico.ipynb`** en [Google Colab](https://colab.research.google.com/)
2. **Entorno de ejecución → Cambiar tipo → GPU (T4)**
3. **Ejecución → Ejecutar todo** (`Ctrl+F9`)
4. Esperar ~2–4 h (puedes cerrar otras tareas; deja la pestaña abierta)

### Opción B — Manual

Abrir **`RECI_entrenar_modelo.ipynb`** y ejecutar celda por celda (útil para depurar).

---

## 4. Dónde quedan los archivos

El notebook automático **no sobrescribe** el modelo anterior. Guarda en:

```
RECI_dataset_propio/runs/run_YYYYMMDD_HHMM/
├── mejor_modelo.keras
├── mejor_modelo_ft.keras
├── model.tflite          ← el que necesitas
├── labels.txt
└── entrenamiento_manifest.json   ← accuracy, recall por clase, matriz
```

Revisa `entrenamiento_manifest.json` antes de reemplazar producción (meta: ≥ 90% val accuracy, buen recall en `vidrio`).

---

## 5. Instalar el nuevo modelo en RECI

Descarga desde Drive o copia desde Colab:

```bash
cp ~/Downloads/model.tflite model/model.tflite
cp ~/Downloads/labels.txt   model/labels.txt

python3 tests/test_imagenes_completo.py
python3 vision/tm_classifier.py images/prueba10.jpeg
```

Solo reemplaza en demo/hardware cuando los tests pasen.

---

## Dataset actual (referencia)

| Ubicación | Contenido |
|-----------|-----------|
| `plastico/` + `vidrio/` en Drive | Fotos en bruto (origen) |
| `dataset_organizado/train/` | 85% para entrenamiento |
| `dataset_organizado/val/` | 15% para validación |

Split reproducible: `RANDOM_SEED=42`, estratificado por clase.

| Clase | Total origen (último entrenamiento) |
|-------|-------------------------------------|
| plastico | ~13,580 |
| vidrio | ~7,767 |
| **Total** | **~21,347** |

Desbalance: ~**1.75:1** — compensado con `class_weight` en entrenamiento.

---

## Hiperparámetros (igual en ambos notebooks)

| Parámetro | Valor |
|-----------|-------|
| Arquitectura | MobileNetV2 + transfer learning |
| Entrada | 224×224 RGB |
| Batch size | 32 |
| Fase 1 | 15 épocas max, LR 0.001, base congelada |
| Fase 2 | 10 épocas max, LR 0.00005, últimas 30 capas |
| Augmentation | flip, rotación ±10%, zoom ±10%, brillo ±10% |

---

## Ver también

- [README — Modelo de ML](../README.md#modelo-de-machine-learning)
- [FLUJO_RECONOCIMIENTO.md](FLUJO_RECONOCIMIENTO.md) — cómo se usa el `.tflite` en runtime
