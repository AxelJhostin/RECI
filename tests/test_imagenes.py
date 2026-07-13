# tests/test_imagenes.py
# Prueba masiva del sistema completo con imágenes reales
# Gemini analiza cada imagen y el sistema experto clasifica

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.attribute_extractor import AttributeExtractor
from pathlib import Path

def probar_imagenes(carpeta="images"):
    """Prueba todas las imágenes de una carpeta."""

    extractor = AttributeExtractor(mostrar_banner=False)
    carpeta_path = Path(carpeta)

    # Buscar todas las imágenes
    extensiones = [".jpg", ".jpeg", ".png", ".webp"]
    imagenes = []
    for ext in extensiones:
        imagenes.extend(carpeta_path.glob(f"*{ext}"))
        imagenes.extend(carpeta_path.glob(f"*{ext.upper()}"))

    if not imagenes:
        print(f"No se encontraron imágenes en {carpeta}/")
        return

    imagenes = sorted(imagenes)

    print(f"\n{'█'*60}")
    print(f"  PRUEBA MASIVA — {len(imagenes)} imágenes encontradas")
    print(f"{'█'*60}\n")

    resultados = []
    for i, imagen in enumerate(imagenes, 1):
        print(f"{'─'*60}")
        print(f"  IMAGEN {i}/{len(imagenes)}: {imagen.name}")
        print(f"{'─'*60}")

        try:
            resultado = extractor.analizar_y_clasificar(str(imagen))
            resultados.append({
                "imagen":     imagen.name,
                "conclusion": resultado["conclusion"],
                "confianza":  resultado["confianza"],
                "objeto":     resultado["atributos"]["objeto_reconocido"],
                "error":      None
            })
        except Exception as e:
            print(f"  ❌ Error: {e}")
            resultados.append({
                "imagen":     imagen.name,
                "conclusion": "ERROR",
                "confianza":  0.0,
                "objeto":     "N/A",
                "error":      str(e)
            })

        # Esperar entre imágenes para evitar rate limiting
        if i < len(imagenes):
            print(f"  ⏳ Esperando 4 segundos...")
            time.sleep(4)
        print()

    # Resumen final
    print(f"\n{'█'*60}")
    print(f"  RESUMEN DE RESULTADOS")
    print(f"{'█'*60}")

    emojis = {
        "VIDRIO":      "🔵",
        "PLASTICO":    "🟢",
        "ORGANICO":    "🟡",
        "LATA":        "🔴",
        "DESCONOCIDO": "⚪",
        "ERROR":       "❌"
    }

    for r in resultados:
        emoji = emojis.get(r["conclusion"], "⚪")
        print(f"  {emoji} {r['imagen']:30} → {r['conclusion']:12} "
              f"({r['confianza']*100:.1f}%) [{r['objeto']}]")

    # Estadísticas
    exitosos  = [r for r in resultados if r["conclusion"] in ["VIDRIO", "PLASTICO"]]
    errores   = [r for r in resultados if r["conclusion"] == "ERROR"]
    rechazados = [r for r in resultados
                  if r["conclusion"] in ["ORGANICO", "LATA", "DESCONOCIDO"]]

    print(f"\n  Total imágenes  : {len(resultados)}")
    print(f"  ✅ Reciclables  : {len(exitosos)}")
    print(f"  ⚠  Rechazados   : {len(rechazados)}")
    print(f"  ❌ Errores      : {len(errores)}")
    if len(resultados) - len(errores) > 0:
        tasa = len(exitosos) / (len(resultados) - len(errores)) * 100
        print(f"  Tasa de éxito  : {tasa:.1f}% (sin contar errores)")
    print(f"{'█'*60}\n")


if __name__ == "__main__":
    carpeta = sys.argv[1] if len(sys.argv) > 1 else "images"
    probar_imagenes(carpeta)