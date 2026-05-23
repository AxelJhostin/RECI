# main.py
# Punto de entrada del sistema experto RECI
# Simula el flujo completo: recibe atributos del ML y clasifica el objeto

from expert_system.inference_engine import InferenceEngine

def clasificar_objeto(atributos: dict):
    """
    Función principal de clasificación.
    Recibe los atributos detectados por el modelo ML
    y retorna la decisión del sistema experto.
    """
    engine = InferenceEngine()
    engine.cargar_hechos(atributos)
    conclusion, confianza, reglas = engine.ejecutar()

    print(engine.obtener_explicacion())

    decision = engine.decision_hardware()
    print(f"\n  ACCIÓN HARDWARE:")
    print(f"    Compuerta : {decision['compuerta']}")
    print(f"    LED       : {decision['led']}")
    print(f"    Servo     : {decision['angulo_servo']}°")
    print(f"    Mensaje   : {decision['mensaje']}")
    print()

    return {
        "conclusion":  conclusion,
        "confianza":   confianza,
        "hardware":    decision
    }


# ─────────────────────────────────────────────
# CASOS DE PRUEBA SIMULADOS
# Estos simulan lo que el modelo ML entregaría
# ─────────────────────────────────────────────

if __name__ == "__main__":

    casos = [
        {
            "nombre": "Botella de mocachino Don Café",
            "atributos": {
                "objeto_reconocido": "botella_mocachino",
                "confianza_ml":      "alta",
                "transparencia":     "ninguna",
                "color":             "ambar",
                "forma":             "cilindrica_estandar",
                "brillo":            "alto_nitido",
                "tapa":              "twist_off_metalica",
                "textura":           "lisa_brillante",
                "rigidez":           "rigido"
            }
        },
        {
            "nombre": "Botella de agua Tesalia",
            "atributos": {
                "objeto_reconocido": "botella_agua",
                "confianza_ml":      "alta",
                "transparencia":     "alta",
                "color":             "transparente",
                "forma":             "cilindrica_delgada",
                "brillo":            "medio_difuso",
                "tapa":              "rosca_plastico",
                "textura":           "lisa_brillante",
                "rigidez":           "rigido"
            }
        },
        {
            "nombre": "Botella de Coca-Cola plástico",
            "atributos": {
                "objeto_reconocido": "botella_gaseosa",
                "confianza_ml":      "alta",
                "transparencia":     "alta",
                "color":             "variado_vivo",
                "forma":             "cilindrica_estandar",
                "brillo":            "medio_difuso",
                "tapa":              "rosca_plastico",
                "textura":           "lisa_brillante",
                "rigidez":           "rigido"
            }
        },
        {
            "nombre": "Vaso plástico transparente con tapa domo",
            "atributos": {
                "objeto_reconocido": "vaso_plastico",
                "confianza_ml":      "alta",
                "transparencia":     "alta",
                "color":             "transparente",
                "forma":             "conica",
                "brillo":            "medio_difuso",
                "tapa":              "domo_plastico",
                "textura":           "lisa_brillante",
                "rigidez":           "rigido"
            }
        },
        {
            "nombre": "CASO DIFÍCIL — Botella PET transparente (podría confundirse con vidrio)",
            "atributos": {
                "objeto_reconocido": "botella_agua",
                "confianza_ml":      "media",
                "transparencia":     "alta",
                "color":             "transparente",
                "forma":             "cilindrica_estandar",
                "brillo":            "medio_difuso",
                "tapa":              "rosca_plastico",
                "textura":           "lisa_brillante",
                "rigidez":           "rigido"
            }
        },
        {
            "nombre": "CASO DIFÍCIL — Frasco de vidrio transparente",
            "atributos": {
                "objeto_reconocido": "frasco_vidrio",
                "confianza_ml":      "media",
                "transparencia":     "alta",
                "color":             "transparente",
                "forma":             "cilindrica_ancha",
                "brillo":            "alto_nitido",
                "tapa":              "tapa_ancha_metalica",
                "textura":           "lisa_brillante",
                "rigidez":           "rigido"
            }
        },
        {
            "nombre": "Cáscara de naranja",
            "atributos": {
                "objeto_reconocido": "cascara_fruta",
                "confianza_ml":      "alta",
                "transparencia":     "ninguna",
                "color":             "variado_vivo",
                "forma":             "irregular",
                "brillo":            "bajo",
                "tapa":              "sin_tapa",
                "textura":           "rugosa",
                "rigidez":           "flexible"
            }
        },
        {
            "nombre": "Lata de Red Bull",
            "atributos": {
                "objeto_reconocido": "lata",
                "confianza_ml":      "alta",
                "transparencia":     "ninguna",
                "color":             "metalico",
                "forma":             "cilindrica_delgada",
                "brillo":            "metalico",
                "tapa":              "sellado",
                "textura":           "lisa_brillante",
                "rigidez":           "rigido"
            }
        },
        {
            "nombre": "CASO EXTREMO — Objeto desconocido con baja confianza",
            "atributos": {
                "objeto_reconocido": "desconocido",
                "confianza_ml":      "baja",
                "transparencia":     "media",
                "color":             "variado_vivo",
                "forma":             "irregular",
                "brillo":            "bajo",
                "tapa":              "sin_tapa",
                "textura":           "rugosa",
                "rigidez":           "indefinido"
            }
        },
        {
            "nombre": "CASO AMBIGUO — Botella transparente sin tapa (¿vidrio o plástico?)",
            "atributos": {
                "objeto_reconocido": "desconocido",
                "confianza_ml":      "media",
                "transparencia":     "alta",
                "color":             "transparente",
                "forma":             "cilindrica_estandar",
                "brillo":            "alto_nitido",
                "tapa":              "sin_tapa",
                "textura":           "lisa_brillante",
                "rigidez":           "rigido"
            }
        },
    ]

    print("\n" + "█" * 60)
    print("  SISTEMA EXPERTO RECI — PRUEBAS DE CLASIFICACIÓN")
    print("█" * 60 + "\n")

    resultados = []
    for i, caso in enumerate(casos, 1):
        print(f"{'─' * 60}")
        print(f"  CASO {i}: {caso['nombre']}")
        print(f"{'─' * 60}")
        resultado = clasificar_objeto(caso["atributos"])
        resultados.append({
            "caso":       caso["nombre"],
            "conclusion": resultado["conclusion"],
            "confianza":  resultado["confianza"]
        })

    # Resumen final
    print("\n" + "█" * 60)
    print("  RESUMEN DE CLASIFICACIONES")
    print("█" * 60)
    for r in resultados:
        emoji = {"VIDRIO": "🔵", "PLASTICO": "🟢", "ORGANICO": "🟡",
                 "LATA": "🔴", "DESCONOCIDO": "⚪"}.get(r["conclusion"], "⚪")
        print(f"  {emoji} {r['caso'][:45]:45} → {r['conclusion']:12} ({r['confianza']*100:.1f}%)")
    print("█" * 60 + "\n")