# tests/test_imagenes_completo.py
# Prueba todas las imágenes con el flujo completo TM + Gemini
# Uso: python3 tests/test_imagenes_completo.py

import sys
import os
import cv2
import io
import time
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

def clasificar_imagen(ruta, clf, extractor):
    """
    Flujo híbrido: TM da contexto → Gemini analiza siempre → SE decide.
    Retorna info detallada para debug.
    """
    img = cv2.imread(ruta)
    if img is None:
        return "ERROR", 0.0, "error", 0.0, "—", {}

    # TM silencioso — solo para obtener el contexto
    with contextlib.redirect_stdout(io.StringIO()):
        _, clase_tm, prob_tm = clf.analizar_frame(img)

    # Gemini SIEMPRE analiza con el contexto del TM
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            atributos = extractor.analizar_imagen_hibrido(ruta, clase_tm, prob_tm)
        metodo = "Hibrido"
    except Exception:
        # Fallback: TM solo si Gemini falla (sin internet, rate limit, etc.)
        with contextlib.redirect_stdout(io.StringIO()):
            atributos, _, _ = clf.analizar_frame(img)
        metodo = "TM-solo"

    engine = InferenceEngine()
    engine.cargar_hechos(atributos)
    conclusion, confianza, _ = engine.ejecutar()

    gemini_objeto = atributos.get("objeto_reconocido", "—")
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
    print("  RECI — PRUEBA COMPLETA  FLUJO HÍBRIDO TM + GEMINI + SE")
    print(f"  Imágenes: {len(IMAGENES)}  |  "
          f"Gemini: {'✅ disponible' if gemini_ok else '❌ no disponible'}")
    print(f"  Flujo: TM (contexto) → Gemini (análisis) → Sistema Experto (decisión)")
    print("█" * 72)

    aprobados      = 0
    fallidos       = 0
    con_gemini     = 0
    fallidos_lista = []
    tiempos        = []

    for ruta, descripcion, esperado in IMAGENES:
        nombre = os.path.basename(ruta)

        print(f"\n  {'─'*68}")
        print(f"  🖼  {nombre}  —  {descripcion}")

        if not os.path.exists(ruta):
            print(f"  ⚠ Archivo no encontrado: {ruta}")
            continue

        t_inicio = time.time()
        conclusion, confianza, metodo, prob_tm, gemini_obj, atributos = \
            clasificar_imagen(ruta, clf, extractor)
        t_total = time.time() - t_inicio
        tiempos.append(t_total)

        aprobado = conclusion == esperado
        estado   = "✅ PASS" if aprobado else "❌ FAIL"

        if aprobado:
            aprobados += 1
        else:
            fallidos += 1
            fallidos_lista.append((nombre, descripcion, esperado, conclusion,
                                   metodo, prob_tm, atributos, t_total))
        if metodo == "Hibrido":
            con_gemini += 1

        # Detalle del análisis
        print(f"  TM contexto    : {atributos.get('objeto_reconocido','?')} "
              f"(TM prob: {prob_tm:.1%})")

        if metodo == "Hibrido":
            print(f"  Gemini detectó : {gemini_obj}")
        elif metodo == "TM-solo":
            print(f"  Gemini         : ❌ falló — se usó TM como fallback")

        print(f"  Objeto → {atributos.get('objeto_reconocido','?')} | "
              f"Confianza ML → {atributos.get('confianza_ml','?')}")
        print(f"  Resultado SE   : {conclusion} ({confianza*100:.1f}%)")
        print(f"  Esperado       : {esperado}")
        print(f"  ⏱  Tiempo      : {t_total:.2f}s")
        print(f"  {estado}  {'✓ Correcto' if aprobado else '✗ Error — revisar'}")

    # ── Resumen final ─────────────────────────────────────────
    total = aprobados + fallidos
    pct   = aprobados / total * 100 if total > 0 else 0

    t_promedio = sum(tiempos) / len(tiempos) if tiempos else 0
    t_min      = min(tiempos) if tiempos else 0
    t_max      = max(tiempos) if tiempos else 0
    t_total_g  = sum(tiempos)

    print(f"\n{'█'*72}")
    print(f"  RESULTADOS FINALES")
    print(f"{'─'*72}")
    print(f"  Precisión     : {aprobados}/{total} ({pct:.1f}%)")
    print(f"  Híbrido TM+Gemini : {con_gemini} imágenes")
    print(f"  Solo TM (fallback): {total - con_gemini} imágenes")
    print(f"{'─'*72}")
    print(f"  ⏱  TIEMPOS")
    print(f"  Promedio  : {t_promedio:.2f}s por imagen")
    print(f"  Mínimo    : {t_min:.2f}s")
    print(f"  Máximo    : {t_max:.2f}s")
    print(f"  Total     : {t_total_g:.1f}s ({len(tiempos)} imágenes)")

    if fallidos_lista:
        print(f"\n  ❌ FALLIDOS ({len(fallidos_lista)}):")
        print(f"  {'─'*68}")
        for nombre, desc, esp, obt, met, prob, atrib, t in fallidos_lista:
            print(f"  • {nombre} — {desc}")
            print(f"    Esperado : {esp}")
            print(f"    Obtenido : {obt}")
            print(f"    Método   : {met} (TM prob: {prob:.1%})  ⏱ {t:.2f}s")
            print(f"    Obj. rec.: {atrib.get('objeto_reconocido','?')} | "
                  f"Conf ML: {atrib.get('confianza_ml','?')}")

    if fallidos == 0:
        print("\n  🏆 TODAS LAS PRUEBAS APROBADAS")

    print("█" * 72 + "\n")


if __name__ == "__main__":
    ejecutar_pruebas()