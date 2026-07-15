# RECI — Guía para agente: entrenamiento local en Windows

> **Audiencia:** Cursor Agent (u otro asistente) en la **PC de escritorio Windows**.  
> **Objetivo:** Entrenar MobileNetV2 (plástico / vidrio) **100% local**, sin Google Colab ni dependencia de Drive en tiempo de ejecución.  
> **Usuario:** dejará descargada la carpeta `RECI_dataset_propio` en disco antes de empezar.

---

## Resumen del plan (aprobado por el equipo)

1. Dataset **ya descargado** desde Google Drive → carpeta local en Windows.
2. Repo RECI clonado en la misma máquina.
3. Entrenar con `scripts/entrenar_modelo.py` (puede tardar **muchas horas** en CPU; menos con GPU NVIDIA).
4. Dejar el proceso corriendo **sin suspender** el PC.
5. Al terminar: verificar métricas, copiar `model.tflite` a `model/`, correr tests.

**Ventajas:** no se desconecta Colab, no expira el enlace de Drive durante el entrenamiento, reanudable si se interrumpe.

---

## Checklist del agente (marcar al avanzar)

- [ ] **0** — Confirmar rutas locales con el usuario (ver sección 1)
- [ ] **1** — `git pull` en repo RECI
- [ ] **2** — Crear/activar venv e instalar `requirements.txt`
- [ ] **3** — Verificar que existe `RECI_dataset_propio` con estructura correcta
- [ ] **4** — Verificar TensorFlow (+ GPU si hay NVIDIA)
- [ ] **5** — Decidir: ¿continuar run Colab (`--solo-fase 2`) o entrenamiento completo?
- [ ] **6** — Ejecutar `scripts/entrenar_modelo.py`
- [ ] **7** — Revisar `entrenamiento_manifest.json` (accuracy, recall vidrio)
- [ ] **8** — Copiar `model.tflite` + `labels.txt` → `model/`
- [ ] **9** — `python tests/test_imagenes_completo.py` (meta: 16/16)
- [ ] **10** — Reportar al usuario: rutas, accuracy, tiempo total, próximos pasos

---

## 1. Rutas que debe confirmar el usuario

Preguntar o asumir (y ajustar comandos) estas dos rutas:

| Variable | Ejemplo Windows | Descripción |
|----------|-----------------|-------------|
| `RECI_REPO` | `C:\Users\Axel\RECI` | Carpeta del proyecto clonado |
| `RECI_DATASET` | `C:\Users\Axel\RECI_dataset_propio` | Carpeta **descargada de Drive** |

El script usa por defecto `%USERPROFILE%\RECI_dataset_propio` si no se pasa `--dataset-base`.  
**Siempre** pasar `--dataset-base` con la ruta real que dejó el usuario.

---

## 2. Estructura esperada del dataset local

```
RECI_DATASET/
├── plastico/                    ← fotos en bruto (jpg, jpeg, png, webp)
├── vidrio/
├── dataset_organizado/          ← OBLIGATORIO para entrenar
│   ├── train/
│   │   ├── plastico/
│   │   └── vidrio/
│   └── val/
│       ├── plastico/
│       └── vidrio/
└── runs/                        ← salida de entrenamientos
    └── run_20260715_1437/       ← (opcional) run interrumpido en Colab
        └── mejor_modelo.keras   ← checkpoint Fase 1 si existe
```

**Verificación rápida (PowerShell):**

```powershell
$DATA = "C:\Users\TU_USUARIO\RECI_dataset_propio"
Get-ChildItem "$DATA\dataset_organizado\train\plastico" | Measure-Object
Get-ChildItem "$DATA\dataset_organizado\train\vidrio" | Measure-Object
Get-ChildItem "$DATA\dataset_organizado\val\plastico" | Measure-Object
Get-ChildItem "$DATA\dataset_organizado\val\vidrio" | Measure-Object
```

Referencia histórica (~21k fotos): train ~18k, val ~3k. Si los conteos son 0 → dataset incompleto o ruta incorrecta.

---

## 3. Preparar entorno (Windows + VS Code)

```powershell
cd C:\Users\TU_USUARIO\RECI
git pull

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

Si `Activate.ps1` falla por política de ejecución:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**TensorFlow + GPU (opcional NVIDIA):**

```powershell
python -c "import tensorflow as tf; print('TF', tf.__version__); print('GPU', tf.config.list_physical_devices('GPU'))"
```

- GPU listada → entrenamiento acelerado.
- `GPU []` → solo CPU; avisar al usuario que puede tardar **12–24+ horas** en dataset completo.

---

## 4. Qué comando ejecutar (elegir UNO)

### Opción A — Continuar desde Colab (recomendado si existe `mejor_modelo.keras`)

Colab se desconectó en Fase 1 (~época 7/15). El mejor checkpoint suele estar en época 3 (~91.6% val). **Saltar a Fase 2:**

```powershell
cd C:\Users\TU_USUARIO\RECI
.\.venv\Scripts\Activate.ps1

python scripts\entrenar_modelo.py `
  --solo-fase 2 `
  --dataset-base C:\Users\TU_USUARIO\RECI_dataset_propio `
  --checkpoint C:\Users\TU_USUARIO\RECI_dataset_propio\runs\run_20260715_1437\mejor_modelo.keras
```

Ajustar `run_20260715_1437` si el usuario tiene otro nombre de carpeta en `runs/`.

**Salida esperada:** `mejor_modelo_ft.keras`, `model.tflite`, `labels.txt`, `entrenamiento_manifest.json` en la misma carpeta del run.

---

### Opción B — Entrenamiento completo desde cero (Fase 1 + 2 + export)

Usar si no hay checkpoint útil o el usuario quiere reentrenar todo con fotos nuevas.

```powershell
python scripts\entrenar_modelo.py `
  --sync-fotos-repo `
  --dataset-base C:\Users\TU_USUARIO\RECI_dataset_propio
```

`--sync-fotos-repo` copia fotos de `fotos_dataset/` del repo a `plastico/` y `vidrio/` antes del split.

---

### Opción C — Reanudar Fase 1 interrumpida en local

```powershell
python scripts\entrenar_modelo.py `
  --solo-fase 1 `
  --resume `
  --output-dir C:\Users\TU_USUARIO\RECI_dataset_propio\runs\run_20260715_1437 `
  --dataset-base C:\Users\TU_USUARIO\RECI_dataset_propio
```

---

## 5. Parámetros útiles si hay problemas

| Problema | Solución |
|----------|----------|
| Poca RAM / error OOM | `--batch-size 16` o `--batch-size 8` |
| Entrenamiento muy lento | Normal en CPU; no cerrar VS Code ni suspender PC |
| Proceso interrumpido | Repetir con `--resume` y mismo `--output-dir` |
| Solo exportar TFLite (Fase 2 ya hecha) | `--solo-fase 6 --checkpoint ...\mejor_modelo_ft.keras` |

Ver todas las opciones:

```powershell
python scripts\entrenar_modelo.py --help
```

---

## 6. Durante el entrenamiento (dejar trabajando de largo)

**Instrucciones para el usuario / agente:**

1. Desactivar **suspensión** y **apagado de pantalla** en Windows (Configuración → Sistema → Energía).
2. Mantener VS Code / terminal abierta.
3. El script imprime progreso por época (`PASO 4/6`, `PASO 5/6`, etc.).
4. Checkpoints se guardan en `runs/run_.../mejor_modelo.keras` y `mejor_modelo_ft.keras`.
5. Historial en `fase1_history.csv`, `fase2_history.csv`, estado en `training_state.json`.

**No usar Colab ni montar Drive durante el entrenamiento.**

---

## 7. Al terminar — validar e instalar modelo

### 7.1 Leer manifest

Abrir:

```
RECI_DATASET\runs\run_XXXX\entrenamiento_manifest.json
```

Criterios antes de producción:

| Métrica | Umbral recomendado |
|---------|-------------------|
| `accuracy` (val) | ≥ 0.90 (90%) |
| `metricas_por_clase.vidrio.recall` | ≥ 0.85 |
| `metricas_por_clase.plastico.recall` | ≥ 0.85 |

### 7.2 Copiar a RECI

```powershell
$RUN = "C:\Users\TU_USUARIO\RECI_dataset_propio\runs\run_20260715_1437"
copy "$RUN\model.tflite" C:\Users\TU_USUARIO\RECI\model\model.tflite
copy "$RUN\labels.txt"   C:\Users\TU_USUARIO\RECI\model\labels.txt
```

Crear `model\` si no existe. El contenido de `model/` suele estar en `.gitignore`.

### 7.3 Tests

```powershell
cd C:\Users\TU_USUARIO\RECI
python tests\test_imagenes_completo.py
python tests\test_cases.py
```

Meta: **16/16** imágenes, **110/110** sistema experto.

### 7.4 Instalación automática (alternativa)

Si accuracy ≥ 90% al exportar:

```powershell
python scripts\entrenar_modelo.py `
  --solo-fase 6 `
  --checkpoint C:\Users\TU_USUARIO\RECI_dataset_propio\runs\run_XXXX\mejor_modelo_ft.keras `
  --dataset-base C:\Users\TU_USUARIO\RECI_dataset_propio `
  --instalar-modelo
```

---

## 8. Reporte final para el usuario

Al cerrar la tarea, el agente debe informar:

1. **Ruta del run:** `...\runs\run_YYYYMMDD_HHMM\`
2. **Accuracy final** y recall por clase (vidrio / plástico)
3. **Tiempo total** aproximado
4. **Tests:** 16/16 y 110/110 sí/no
5. **Si el modelo quedó en** `model/model.tflite`
6. **Próximo paso:** roadmap A1–A8 en README (demo cámara con Claude) si aplica

---

## 9. Errores frecuentes

| Error | Causa | Acción |
|-------|-------|--------|
| `No existe ...\plastico` | Ruta `--dataset-base` incorrecta | Corregir ruta a carpeta descargada de Drive |
| `Dataset vacío` | Falta `dataset_organizado` | Verificar descarga completa de Drive |
| `No module named tensorflow` | venv no activado | `.\.venv\Scripts\Activate.ps1` + pip install |
| `checkpoint no encontrado` | Run Colab no descargado | Usar Opción B (entrenamiento completo) |
| Entrenamiento extremadamente lento | CPU sin GPU | Esperar o instalar drivers CUDA si hay NVIDIA |

---

## 10. Archivos de referencia en el repo

| Archivo | Contenido |
|---------|-----------|
| `scripts/entrenar_modelo.py` | Script principal de entrenamiento |
| `docs/ENTRENAMIENTO_MODELO.md` | Guía humana detallada |
| `README.md` | Arquitectura, roadmap demo A1–C3 |
| `RECI_entrenar_automatico.ipynb` | Legacy Colab — **no usar** en Windows |

---

## Mensaje inicial sugerido para el agente en la otra PC

Copiar y pegar al abrir el chat en la PC Windows:

```
Proyecto RECI en Windows. Lee y ejecuta en orden:
docs/AGENTE_ENTRENAMIENTO_LOCAL.md

Rutas locales (ajustar):
- RECI_REPO: C:\Users\___\RECI
- RECI_DATASET: C:\Users\___\RECI_dataset_propio  (carpeta ya descargada de Drive)

Objetivo: entrenar MobileNetV2 100% local con scripts/entrenar_modelo.py.
Si existe runs/run_20260715_1437/mejor_modelo.keras → Opción A (solo Fase 2).
Si no → Opción B (entrenamiento completo).

Dejar corriendo de largo. Al terminar: manifest, copiar model.tflite a model/, tests 16/16.
Marca el checklist del doc y reporta resultados.
```

---

*Última actualización: Julio 2026 — entrenamiento local Windows, post-Colab run_20260715_1437*
