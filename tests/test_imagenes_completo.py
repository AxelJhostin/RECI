# tests/test_imagenes_completo.py
# Prueba todas las imágenes con el flujo completo TM + Gemini
# Uso: python3 tests/test_imagenes_completo.py

import sys
import os
import cv2
import io
import contextlib
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # suprimir logs de TensorFlow
warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.tm_classifier import TeachableMachineClassifier
from vision.attribute_extractor import AttributeExtractor
from expert_system.inference_engine import InferenceEngine

# ─────────────────────────────────────────────
# IMÁGENES DE PRUEBA CON RESULTADOS ESPERADOS
# Para agregar nuevas imágenes, agrega una línea aquí:
# ("images/pruebaN.jpeg", "descripción", "PLASTICO" o "VIDRIO" o "DESCONOCIDO")
# ─────────────────────────────────────────────

IMAGENES = [
    ("images/prueba1.jpeg",  "Botella agua plástico",           "PLASTICO"),
    ("images/prueba2.jpeg",  "Botella plástico con atomizador", "PLASTICO"),
    ("images/prueba3.jpeg",  "Papel",                           "DESCONOCIDO"),
    ("images/prueba4.jpeg",  "Botella perfume plástico",        "PLASTICO"),
    ("images/prueba5.jpeg",  "Colgate Plax plástico",           "PLASTICO"),
    ("images/prueba6.jpeg",  "Colgate Plax por atrás",          "PLASTICO"),
    ("images/prueba7.jpeg",  "Powerade plástico",               "PLASTICO"),
    ("images/prueba8.jpeg",  "Vaso plástico rojo",              "PLASTICO"),
    ("images/prueba9.jpeg",  "Caffe Lato vidrio",               "VIDRIO"),
    ("images/prueba10.jpeg", "Gatorade vidrio",                 "VIDRIO"),
    ("images/prueba11.jpeg", "Botella agua plástico",           "PLASTICO"),
    ("images/prueba12.jpeg", "Gatorade plástico",               "PLASTICO"),
    ("images/prueba13.jpeg", "Vaso plástico blanco",            "PLASTICO"),
    ("images/prueba14.jpeg", "Coca Cola plástico",              "PLASTICO"),
    ("images/prueba15.jpeg", "Vaso café/chocolate plástico",    "PLASTICO"),
    ("images/prueba16.jpeg", "Fue Tea plástico",                "PLASTICO"),
]

UMBRAL_TM = 0.95


def clasificar_imagen(ruta, clf, extractor):
    """Flujo TM + Gemini. Retorna info detallada para debug."""
    img = cv2.imread(ruta)
    if img is None:
        return "ERROR", 0.0, "error", 0.0, "—", {}

    # TM silencioso
    with contextlib.redirect_stdout(io.StringIO()):
        atributos_tm, clase_tm, prob_tm = clf.analizar_frame(img)

    gemini_objeto = "—"

    if prob_tm >= UMBRAL_TM:
        with contextlib.redirect_stdout(io.StringIO()):
            atributos = extractor.analizar_imagen_tm(ruta, clf=clf)
        metodo = "TM"
    else:
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                atributos = extractor.analizar_imagen(ruta)
            gemini_objeto = atributos.get("objeto_reconocido", "—")
            metodo = "Gemini"
        except Exception as e:
            with contextlib.redirect_stdout(io.StringIO()):
                atributos = atributos_tm
            metodo = "TM-fb"

    engine = InferenceEngine()
    engine.cargar_hechos(atributos)
    conclusion, confianza, reglas = engine.ejecutar()

    return conclusion, confianza, metodo, prob_tm, gemini_objeto, atributos


def ejecutar_pruebas():
    # Cargar modelos suprimiendo warnings
    with contextlib.redirect_stderr(io.StringIO()):
        with contextlib.redirect_stdout(io.StringIO()):
            clf = TeachableMachineClassifier()

    try:
        extractor = AttributeExtractor()
        gemini_ok = True
    except Exception:
        extractor = None
        gemini_ok = False

    print("\n" + "█" * 72)
    print("  RECI — PRUEBA COMPLETA TM + GEMINI")
    print(f"  Umbral TM: {UMBRAL_TM:.0%}  |  Imágenes: {len(IMAGENES)}  |  "
          f"Gemini: {'✅ disponible' if gemini_ok else '❌ no disponible'}")
    print("█" * 72)

    aprobados      = 0
    fallidos       = 0
    con_gemini     = 0
    fallidos_lista = []

    for ruta, descripcion, esperado in IMAGENES:
        nombre = os.path.basename(ruta)

        print(f"\n  {'─'*68}")
        print(f"  🖼  {nombre}  —  {descripcion}")

        if not os.path.exists(ruta):
            print(f"  ⚠ Archivo no encontrado: {ruta}")
            continue

        conclusion, confianza, metodo, prob_tm, gemini_obj, atributos = \
            clasificar_imagen(ruta, clf, extractor)

        aprobado = conclusion == esperado
        estado   = "✅ PASS" if aprobado else "❌ FAIL"

        if aprobado:
            aprobados += 1
        else:
            fallidos += 1
            fallidos_lista.append((nombre, descripcion, esperado, conclusion,
                                   metodo, prob_tm, atributos))
        if metodo == "Gemini":
            con_gemini += 1

        # Detalle del análisis
        print(f"  TM detectó     : {atributos.get('objeto_reconocido','?')} "
              f"(confianza TM: {prob_tm:.1%})")

        if metodo == "Gemini":
            print(f"  Gemini detectó : {gemini_obj}  ← TM confianza baja, Gemini confirmó")
        elif metodo == "TM-fb":
            print(f"  Gemini         : ❌ falló, se usó TM como fallback")

        print(f"  Método usado   : {metodo}")
        print(f"  Objeto reconocido → {atributos.get('objeto_reconocido','?')} | "
              f"Confianza ML → {atributos.get('confianza_ml','?')}")
        print(f"  Resultado SE   : {conclusion} ({confianza*100:.1f}%)")
        print(f"  Esperado       : {esperado}")
        print(f"  {estado}  {'✓ Correcto' if aprobado else '✗ Error — revisar'}")

    # ── Resumen final ─────────────────────────────────────────
    total = aprobados + fallidos
    pct   = aprobados / total * 100 if total > 0 else 0

    print(f"\n{'█'*72}")
    print(f"  RESULTADOS FINALES")
    print(f"{'─'*72}")
    print(f"  Total     : {aprobados}/{total} ({pct:.1f}%)")
    print(f"  Solo TM   : {total - con_gemini} imágenes")
    print(f"  Con Gemini: {con_gemini} imágenes")

    if fallidos_lista:
        print(f"\n  ❌ FALLIDOS ({len(fallidos_lista)}):")
        print(f"  {'─'*68}")
        for nombre, desc, esp, obt, met, prob, atrib in fallidos_lista:
            print(f"  • {nombre} — {desc}")
            print(f"    Esperado : {esp}")
            print(f"    Obtenido : {obt}")
            print(f"    Método   : {met} (TM prob: {prob:.1%})")
            print(f"    Obj. rec.: {atrib.get('objeto_reconocido','?')} | "
                  f"Conf ML: {atrib.get('confianza_ml','?')}")

    if fallidos == 0:
        print("\n  🏆 TODAS LAS PRUEBAS APROBADAS")

    print("█" * 72 + "\n")


if __name__ == "__main__":
    ejecutar_pruebas()