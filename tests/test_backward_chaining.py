# tests/test_backward_chaining.py
# Pruebas dedicadas al motor de encadenamiento hacia atrás (BackwardChainingEngine)
#
# El runner de tests/test_cases.py solo valida la conclusión final del sistema
# experto (forward chaining + meta-reglas + CF). Una discrepancia entre forward
# y backward chaining solo genera una ADVERTENCIA, no hace fallar esos tests —
# por eso un goal mal calibrado en backward_chaining.py puede pasar
# desapercibido. Estas pruebas verifican directamente los goals de cada
# categoría.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from expert_system.backward_chaining import BackwardChainingEngine

CASOS = [
    {
        "id": "BC01",
        "nombre": "Botella de agua PET (tapa rosca plástica) — regresión",
        "hechos": {
            "objeto_reconocido": "botella_agua", "confianza_ml": "alta",
            "transparencia": "media", "color": "variado_vivo",
            "forma": "cilindrica_estandar", "brillo": "alto_nitido",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        },
        "mejor_esperado":  "PLASTICO",
        "no_confirmados":  ["VIDRIO"],
        "confirmados":     ["PLASTICO"],
    },
    {
        "id": "BC02",
        "nombre": "Objeto rígido/opaco color metálico sin brillo metálico — regresión",
        "hechos": {
            "transparencia": "ninguna", "color": "metalico",
            "forma": "cilindrica_delgada", "brillo": "medio_difuso",
            "tapa": "sin_tapa", "textura": "lisa_brillante", "rigidez": "rigido"
        },
        # El color metálico por sí solo no basta: sin brillo metálico,
        # LATA queda descartada (eliminatoria) aunque otra categoría
        # termine ganando por descarte.
        "mejor_esperado":  "PLASTICO",
        "no_confirmados":  ["LATA"],
        "confirmados":     [],
    },
    {
        "id": "BC03",
        "nombre": "Lata de aluminio típica",
        "hechos": {
            "transparencia": "ninguna", "color": "metalico",
            "forma": "cilindrica_delgada", "brillo": "metalico",
            "tapa": "sin_tapa", "textura": "lisa_brillante", "rigidez": "rigido"
        },
        "mejor_esperado":  "LATA",
        "no_confirmados":  [],
        "confirmados":     ["LATA"],
    },
    {
        "id": "BC04",
        "nombre": "Botella de vidrio típica (tapa corona metálica)",
        "hechos": {
            "transparencia": "ninguna", "color": "ambar",
            "forma": "cilindrica_estandar", "brillo": "alto_nitido",
            "tapa": "corona_metalica", "textura": "lisa_brillante", "rigidez": "rigido"
        },
        "mejor_esperado":  "VIDRIO",
        "no_confirmados":  [],
        "confirmados":     ["VIDRIO"],
    },
    {
        "id": "BC05",
        "nombre": "Tetra Pak / cartón rígido (orgánico-papel)",
        "hechos": {
            "transparencia": "ninguna", "color": "blanco_opaco",
            "forma": "rectangular_plana", "brillo": "bajo",
            "tapa": "sellado", "textura": "lisa_sin_brillo", "rigidez": "rigido"
        },
        "mejor_esperado":  "ORGANICO",
        "no_confirmados":  [],
        "confirmados":     ["ORGANICO"],
    },
    {
        "id": "BC06",
        "nombre": "Funda plástica negra flexible — no debe ganar ORGANICO",
        "hechos": {
            "transparencia": "ninguna", "color": "negro",
            "forma": "irregular", "brillo": "medio_difuso",
            "tapa": "sin_tapa", "textura": "lisa_sin_brillo", "rigidez": "flexible"
        },
        "mejor_esperado":  "PLASTICO",
        "no_confirmados":  [],
        "confirmados":     ["PLASTICO"],
    },
]


def ejecutar_pruebas(verbose=False):
    bc = BackwardChainingEngine()
    aprobados = 0
    fallidos  = 0

    print("\n" + "█" * 65)
    print("  BACKWARD CHAINING — PRUEBAS DE GOALS POR CATEGORÍA")
    print("█" * 65)

    for caso in CASOS:
        mejor, score, resultados = bc.ejecutar(caso["hechos"])

        errores = []

        if mejor != caso["mejor_esperado"]:
            errores.append(
                f"mejor={mejor!r} (esperado {caso['mejor_esperado']!r})")

        for cat in caso["confirmados"]:
            if not resultados[cat]["confirmado"]:
                errores.append(
                    f"{cat} debía estar confirmado "
                    f"(score: {resultados[cat]['score']*100:.1f}%)")

        for cat in caso["no_confirmados"]:
            if resultados[cat]["confirmado"]:
                errores.append(
                    f"{cat} NO debía estar confirmado "
                    f"(score: {resultados[cat]['score']*100:.1f}%)")

        aprobado = not errores
        estado   = "✅ PASS" if aprobado else "❌ FAIL"

        if aprobado:
            aprobados += 1
        else:
            fallidos += 1

        if verbose or not aprobado:
            print(f"\n  {estado} [{caso['id']}] {caso['nombre']}")
            print(f"         mejor: {mejor} (score: {score*100:.1f}%)")
            for err in errores:
                print(f"         ⚠ {err}")

    print("\n" + "─" * 65)
    total     = aprobados + fallidos
    pct_total = aprobados / total * 100
    print(f"  TOTAL: {aprobados}/{total} pruebas aprobadas ({pct_total:.1f}%)")

    if fallidos == 0:
        print("  🏆 BACKWARD CHAINING — TODAS LAS PRUEBAS APROBADAS")
    else:
        print(f"  ⚠ {fallidos} prueba(s) fallida(s) — revisar goals")

    print("█" * 65 + "\n")
    return aprobados, fallidos


if __name__ == "__main__":
    ejecutar_pruebas(verbose=True)
