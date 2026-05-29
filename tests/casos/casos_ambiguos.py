# tests/casos/casos_ambiguos.py
# Casos difíciles donde el sistema experto debe desempatar correctamente

CASOS_AMBIGUOS = [
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
    {
        "id": "T44", "nombre": "DIFÍCIL — Sprite verde plástico vs Club verde vidrio",
        "esperado": "PLASTICO", "categoria": "AMBIGUO",
        "atributos": {
            "objeto_reconocido": "botella_gaseosa", "confianza_ml": "media",
            "transparencia": "media", "color": "variado_vivo",
            "forma": "cilindrica_estandar", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T45", "nombre": "DIFÍCIL — Botella alcohólica pequeña confianza media",
        "esperado": "PLASTICO", "categoria": "AMBIGUO",
        "atributos": {
            "objeto_reconocido": "botella_alcoholica_plastico", "confianza_ml": "media",
            "transparencia": "alta", "color": "variado_vivo",
            "forma": "cilindrica_delgada", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T46", "nombre": "DIFÍCIL — Snack metálico vs lata",
        "esperado": "PLASTICO", "categoria": "AMBIGUO",
        "atributos": {
            "objeto_reconocido": "desconocido", "confianza_ml": "media",
            "transparencia": "ninguna", "color": "metalico",
            "forma": "rectangular_plana", "brillo": "metalico",
            "tapa": "sellado", "textura": "lisa_brillante", "rigidez": "flexible"
        }
    },
    {
        "id": "T47", "nombre": "DIFÍCIL — Yogur blanco vs frasco vidrio blanco",
        "esperado": "PLASTICO", "categoria": "AMBIGUO",
        "atributos": {
            "objeto_reconocido": "yogur_plastico", "confianza_ml": "media",
            "transparencia": "ninguna", "color": "blanco_opaco",
            "forma": "cilindrica_ancha", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T48", "nombre": "DIFÍCIL — Botella vidrio transparente sin etiqueta",
        "esperado": "VIDRIO", "categoria": "AMBIGUO",
        "atributos": {
            "objeto_reconocido": "desconocido", "confianza_ml": "media",
            "transparencia": "alta", "color": "transparente",
            "forma": "cilindrica_estandar", "brillo": "alto_nitido",
            "tapa": "twist_off_metalica", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "T49", "nombre": "DIFÍCIL — Cáscara oscura vs funda negra",
        "esperado": "ORGANICO", "categoria": "AMBIGUO",
        "atributos": {
            "objeto_reconocido": "cascara_fruta", "confianza_ml": "media",
            "transparencia": "ninguna", "color": "marron_tierra",
            "forma": "irregular", "brillo": "bajo",
            "tapa": "sin_tapa", "textura": "rugosa", "rigidez": "flexible"
        }
    },
]