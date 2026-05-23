# tests/test_cases.py
# Pruebas formales del sistema experto RECI
# Valida que cada caso produzca el resultado esperado

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from expert_system.inference_engine import InferenceEngine

# ─────────────────────────────────────────────
# DEFINICIÓN DE CASOS DE PRUEBA
# ─────────────────────────────────────────────

CASOS_DE_PRUEBA = [

    # ── VIDRIO ───────────────────────────────
    {
        "id": "T01", "nombre": "Botella mocachino Don Café",
        "esperado": "VIDRIO", "categoria": "VIDRIO",
        "atributos": {
            "objeto_reconocido": "botella_mocachino", "confianza_ml": "alta",
            "transparencia": "ninguna", "color": "ambar",
            "forma": "cilindrica_estandar", "brillo": "alto_nitido",
            "tapa": "twist_off_metalica", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T02", "nombre": "Botella cerveza Pilsener vidrio",
        "esperado": "VIDRIO", "categoria": "VIDRIO",
        "atributos": {
            "objeto_reconocido": "botella_cerveza_vidrio", "confianza_ml": "alta",
            "transparencia": "ninguna", "color": "ambar",
            "forma": "cilindrica_estandar", "brillo": "alto_nitido",
            "tapa": "corona_metalica", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T03", "nombre": "Botella cerveza Club vidrio verde",
        "esperado": "VIDRIO", "categoria": "VIDRIO",
        "atributos": {
            "objeto_reconocido": "botella_cerveza_vidrio", "confianza_ml": "alta",
            "transparencia": "ninguna", "color": "verde_oscuro",
            "forma": "cilindrica_estandar", "brillo": "alto_nitido",
            "tapa": "corona_metalica", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T04", "nombre": "Frasco mermelada Snob vidrio",
        "esperado": "VIDRIO", "categoria": "VIDRIO",
        "atributos": {
            "objeto_reconocido": "frasco_vidrio", "confianza_ml": "alta",
            "transparencia": "alta", "color": "transparente",
            "forma": "cilindrica_ancha", "brillo": "alto_nitido",
            "tapa": "tapa_ancha_metalica", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T05", "nombre": "Botella salsa Gustadina vidrio",
        "esperado": "VIDRIO", "categoria": "VIDRIO",
        "atributos": {
            "objeto_reconocido": "botella_salsa_vidrio", "confianza_ml": "alta",
            "transparencia": "media", "color": "transparente",
            "forma": "cilindrica_estandar", "brillo": "alto_nitido",
            "tapa": "twist_off_metalica", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },

    # ── PLÁSTICO ─────────────────────────────
    {
        "id": "T06", "nombre": "Botella agua Tesalia",
        "esperado": "PLASTICO", "categoria": "PLASTICO",
        "atributos": {
            "objeto_reconocido": "botella_agua", "confianza_ml": "alta",
            "transparencia": "alta", "color": "transparente",
            "forma": "cilindrica_delgada", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T07", "nombre": "Botella Coca-Cola plástico",
        "esperado": "PLASTICO", "categoria": "PLASTICO",
        "atributos": {
            "objeto_reconocido": "botella_gaseosa", "confianza_ml": "alta",
            "transparencia": "alta", "color": "variado_vivo",
            "forma": "cilindrica_estandar", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T08", "nombre": "Botella Sprite verde plástico",
        "esperado": "PLASTICO", "categoria": "PLASTICO",
        "atributos": {
            "objeto_reconocido": "botella_gaseosa", "confianza_ml": "alta",
            "transparencia": "media", "color": "variado_vivo",
            "forma": "cilindrica_estandar", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T09", "nombre": "Vaso plástico con tapa domo",
        "esperado": "PLASTICO", "categoria": "PLASTICO",
        "atributos": {
            "objeto_reconocido": "vaso_plastico", "confianza_ml": "alta",
            "transparencia": "alta", "color": "transparente",
            "forma": "conica", "brillo": "medio_difuso",
            "tapa": "domo_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T10", "nombre": "Vaso plástico sin tapa",
        "esperado": "PLASTICO", "categoria": "PLASTICO",
        "atributos": {
            "objeto_reconocido": "vaso_plastico", "confianza_ml": "alta",
            "transparencia": "alta", "color": "transparente",
            "forma": "conica", "brillo": "medio_difuso",
            "tapa": "sin_tapa", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T11", "nombre": "Botella energizante Volt",
        "esperado": "PLASTICO", "categoria": "PLASTICO",
        "atributos": {
            "objeto_reconocido": "botella_energizante", "confianza_ml": "alta",
            "transparencia": "alta", "color": "variado_vivo",
            "forma": "cilindrica_delgada", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T12", "nombre": "Botella alcohólica Switch plástico",
        "esperado": "PLASTICO", "categoria": "PLASTICO",
        "atributos": {
            "objeto_reconocido": "botella_alcoholica_plastico", "confianza_ml": "alta",
            "transparencia": "alta", "color": "variado_vivo",
            "forma": "cilindrica_delgada", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T13", "nombre": "Yogur Toni plástico blanco",
        "esperado": "PLASTICO", "categoria": "PLASTICO",
        "atributos": {
            "objeto_reconocido": "yogur_plastico", "confianza_ml": "alta",
            "transparencia": "ninguna", "color": "blanco_opaco",
            "forma": "cilindrica_ancha", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T14", "nombre": "Funda plástica negra",
        "esperado": "PLASTICO", "categoria": "PLASTICO",
        "atributos": {
            "objeto_reconocido": "funda_plastico", "confianza_ml": "alta",
            "transparencia": "ninguna", "color": "negro",
            "forma": "irregular", "brillo": "medio_difuso",
            "tapa": "sin_tapa", "textura": "lisa_brillante", "rigidez": "flexible"
        }
    },

    # ── ORGÁNICO ─────────────────────────────
    {
        "id": "T15", "nombre": "Cáscara de naranja",
        "esperado": "ORGANICO", "categoria": "ORGANICO",
        "atributos": {
            "objeto_reconocido": "cascara_fruta", "confianza_ml": "alta",
            "transparencia": "ninguna", "color": "variado_vivo",
            "forma": "irregular", "brillo": "bajo",
            "tapa": "sin_tapa", "textura": "rugosa", "rigidez": "flexible"
        }
    },
    {
        "id": "T16", "nombre": "Cáscara de banano",
        "esperado": "ORGANICO", "categoria": "ORGANICO",
        "atributos": {
            "objeto_reconocido": "cascara_fruta", "confianza_ml": "alta",
            "transparencia": "ninguna", "color": "marron_tierra",
            "forma": "irregular", "brillo": "bajo",
            "tapa": "sin_tapa", "textura": "rugosa", "rigidez": "flexible"
        }
    },
    {
        "id": "T17", "nombre": "Servilleta de papel",
        "esperado": "ORGANICO", "categoria": "ORGANICO",
        "atributos": {
            "objeto_reconocido": "papel_servilleta", "confianza_ml": "alta",
            "transparencia": "ninguna", "color": "blanco_opaco",
            "forma": "irregular", "brillo": "bajo",
            "tapa": "sin_tapa", "textura": "fibrosa", "rigidez": "flexible"
        }
    },
    {
        "id": "T18", "nombre": "Vaso de cartón cafetería",
        "esperado": "ORGANICO", "categoria": "ORGANICO",
        "atributos": {
            "objeto_reconocido": "vaso_carton", "confianza_ml": "alta",
            "transparencia": "ninguna", "color": "blanco_opaco",
            "forma": "conica", "brillo": "bajo",
            "tapa": "sin_tapa", "textura": "fibrosa", "rigidez": "rigido"
        }
    },

    # ── LATA ─────────────────────────────────
    {
        "id": "T19", "nombre": "Lata Red Bull aluminio",
        "esperado": "LATA", "categoria": "LATA",
        "atributos": {
            "objeto_reconocido": "lata", "confianza_ml": "alta",
            "transparencia": "ninguna", "color": "metalico",
            "forma": "cilindrica_delgada", "brillo": "metalico",
            "tapa": "sellado", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T20", "nombre": "Lata Monster aluminio",
        "esperado": "LATA", "categoria": "LATA",
        "atributos": {
            "objeto_reconocido": "lata", "confianza_ml": "alta",
            "transparencia": "ninguna", "color": "metalico",
            "forma": "cilindrica_estandar", "brillo": "metalico",
            "tapa": "sellado", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },

    # ── CASOS DIFÍCILES ───────────────────────
    {
        "id": "T21", "nombre": "DIFÍCIL — PET transparente vs vidrio (tapa rosca)",
        "esperado": "PLASTICO", "categoria": "AMBIGUO",
        "atributos": {
            "objeto_reconocido": "botella_agua", "confianza_ml": "media",
            "transparencia": "alta", "color": "transparente",
            "forma": "cilindrica_estandar", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T22", "nombre": "DIFÍCIL — Frasco vidrio transparente (tapa metálica)",
        "esperado": "VIDRIO", "categoria": "AMBIGUO",
        "atributos": {
            "objeto_reconocido": "frasco_vidrio", "confianza_ml": "media",
            "transparencia": "alta", "color": "transparente",
            "forma": "cilindrica_ancha", "brillo": "alto_nitido",
            "tapa": "tapa_ancha_metalica", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T23", "nombre": "DIFÍCIL — Vaso cartón vs vaso plástico",
        "esperado": "ORGANICO", "categoria": "AMBIGUO",
        "atributos": {
            "objeto_reconocido": "vaso_carton", "confianza_ml": "media",
            "transparencia": "ninguna", "color": "blanco_opaco",
            "forma": "conica", "brillo": "bajo",
            "tapa": "sin_tapa", "textura": "fibrosa", "rigidez": "rigido"
        }
    },
    {
        "id": "T24", "nombre": "DIFÍCIL — Funda negra vs cáscara oscura",
        "esperado": "PLASTICO", "categoria": "AMBIGUO",
        "atributos": {
            "objeto_reconocido": "funda_plastico", "confianza_ml": "media",
            "transparencia": "ninguna", "color": "negro",
            "forma": "irregular", "brillo": "medio_difuso",
            "tapa": "sin_tapa", "textura": "lisa_brillante", "rigidez": "flexible"
        }
    },

    # ── CASOS EXTREMOS ────────────────────────
    {
        "id": "T25", "nombre": "EXTREMO — Objeto desconocido baja confianza",
        "esperado": "DESCONOCIDO", "categoria": "EXTREMO",
        "atributos": {
            "objeto_reconocido": "desconocido", "confianza_ml": "baja",
            "transparencia": "media", "color": "variado_vivo",
            "forma": "irregular", "brillo": "bajo",
            "tapa": "sin_tapa", "textura": "rugosa", "rigidez": "indefinido"
        }
    },
]


# ─────────────────────────────────────────────
# EJECUTOR DE PRUEBAS
# ─────────────────────────────────────────────

def ejecutar_pruebas(verbose=False):
    engine = InferenceEngine()
    resultados = []
    aprobados = 0
    fallidos = 0

    print("\n" + "█" * 65)
    print("  SISTEMA EXPERTO RECI — PRUEBAS FORMALES")
    print("█" * 65)

    categorias = {}

    for caso in CASOS_DE_PRUEBA:
        engine.cargar_hechos(caso["atributos"])
        conclusion, confianza, _ = engine.ejecutar()

        aprobado = conclusion == caso["esperado"]
        estado   = "✅ PASS" if aprobado else "❌ FAIL"

        if aprobado:
            aprobados += 1
        else:
            fallidos += 1

        cat = caso["categoria"]
        if cat not in categorias:
            categorias[cat] = {"pass": 0, "fail": 0}
        if aprobado:
            categorias[cat]["pass"] += 1
        else:
            categorias[cat]["fail"] += 1

        resultados.append({
            "id":        caso["id"],
            "nombre":    caso["nombre"],
            "esperado":  caso["esperado"],
            "obtenido":  conclusion,
            "confianza": confianza,
            "aprobado":  aprobado
        })

        if verbose or not aprobado:
            print(f"\n  {estado} [{caso['id']}] {caso['nombre']}")
            print(f"         Esperado: {caso['esperado']:12} | "
                  f"Obtenido: {conclusion:12} | "
                  f"Confianza: {confianza*100:.1f}%")
            if not aprobado:
                print(f"         ⚠ FALLO — revisar reglas para este caso")
                if verbose:
                    print(engine.obtener_explicacion())

    # ── Resumen por categoría ─────────────────
    print("\n" + "─" * 65)
    print("  RESULTADOS POR CATEGORÍA")
    print("─" * 65)
    for cat, datos in categorias.items():
        total = datos["pass"] + datos["fail"]
        pct   = datos["pass"] / total * 100
        barra = "█" * datos["pass"] + "░" * datos["fail"]
        print(f"  {cat:10} [{barra:20}] "
              f"{datos['pass']}/{total} ({pct:.0f}%)")

    # ── Resumen final ─────────────────────────
    total   = aprobados + fallidos
    pct_total = aprobados / total * 100
    print("\n" + "─" * 65)
    print(f"  TOTAL: {aprobados}/{total} pruebas aprobadas ({pct_total:.1f}%)")

    if fallidos == 0:
        print("  🏆 SISTEMA EXPERTO — TODAS LAS PRUEBAS APROBADAS")
    else:
        print(f"  ⚠ {fallidos} prueba(s) fallida(s) — revisar reglas")

    print("█" * 65 + "\n")
    return aprobados, fallidos, resultados


if __name__ == "__main__":
    # verbose=True muestra detalle de cada caso
    # verbose=False muestra solo los que fallan
    ejecutar_pruebas(verbose=True)