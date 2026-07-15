# Documentación RECI

Índice de referencia del proyecto. El README principal sigue siendo la guía completa; aquí están los documentos temáticos.

| Documento | Contenido |
|-----------|-----------|
| [FLUJO_RECONOCIMIENTO.md](FLUJO_RECONOCIMIENTO.md) | Pipeline visión híbrido (TM + API + OpenCV + SE), costos API, checklist demo |
| [ENTRENAMIENTO_MODELO.md](ENTRENAMIENTO_MODELO.md) | Captura de fotos + entrenar MobileNetV2 **en local** (`scripts/entrenar_modelo.py`) |
| [AGENTE_ENTRENAMIENTO_LOCAL.md](AGENTE_ENTRENAMIENTO_LOCAL.md) | **Handoff para agente** — entrenamiento largo en Windows, dataset local, checklist |
| [diagramas/arquitectura_reci.png](diagramas/arquitectura_reci.png) | Diagrama de arquitectura del sistema (PNG para informes) |
| [diagramas/arquitectura_reci.mmd](diagramas/arquitectura_reci.mmd) | Fuente Mermaid del diagrama |

## Scripts relacionados (`../scripts/`)

| Script | Uso |
|--------|-----|
| **`entrenar_modelo.py`** | **Recomendado** — entrenar / reanudar MobileNetV2 en tu PC |
| `estimar_costo_gemini.py` | Estimar costo por imagen con Gemini |
| `generar_diagrama_arquitectura.py` | Regenerar `diagramas/arquitectura_reci.png` |

## Notebooks de entrenamiento (legacy Colab)

| Notebook | Cuándo usarlo |
|----------|----------------|
| `RECI_entrenar_automatico.ipynb` | Legacy — puede desconectarse; preferir `entrenar_modelo.py` |
| `RECI_entrenar_modelo.ipynb` | Legacy manual celda por celda |
