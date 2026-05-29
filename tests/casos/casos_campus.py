# tests/casos/casos_campus.py
# Casos de prueba con objetos reales del campus PUCE Manabí
# Solo plástico y vidrio — todo lo demás es "no permitido"

CASOS_CAMPUS = [

    # ── PLÁSTICO del campus ───────────────────────────────────────

    {
        "id": "TC01", "nombre": "Powerade manzana clear plástico transparente",
        "esperado": "PLASTICO", "categoria": "CAMPUS_PLASTICO",
        "atributos": {
            "objeto_reconocido": "botella_gaseosa", "confianza_ml": "alta",
            "transparencia": "alta", "color": "transparente",
            "forma": "cilindrica_estandar", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "TC02", "nombre": "Dasani botella de agua plástico azul",
        "esperado": "PLASTICO", "categoria": "CAMPUS_PLASTICO",
        "atributos": {
            "objeto_reconocido": "botella_agua", "confianza_ml": "alta",
            "transparencia": "alta", "color": "transparente",
            "forma": "cilindrica_estandar", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "TC03", "nombre": "Chocolatada Toni Chiqui plástico blanco",
        "esperado": "PLASTICO", "categoria": "CAMPUS_PLASTICO",
        "atributos": {
            "objeto_reconocido": "yogur_plastico", "confianza_ml": "alta",
            "transparencia": "ninguna", "color": "blanco_opaco",
            "forma": "cilindrica_ancha", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "TC04", "nombre": "Colgate Plax enjuague bucal plástico",
        "esperado": "PLASTICO", "categoria": "CAMPUS_PLASTICO",
        "atributos": {
            "objeto_reconocido": "botella_gaseosa", "confianza_ml": "alta",
            "transparencia": "alta", "color": "variado_vivo",
            "forma": "cilindrica_estandar", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "TC05", "nombre": "Powerade confianza media — debe ser plástico",
        "esperado": "PLASTICO", "categoria": "CAMPUS_PLASTICO",
        "atributos": {
            "objeto_reconocido": "botella_gaseosa", "confianza_ml": "media",
            "transparencia": "alta", "color": "transparente",
            "forma": "cilindrica_estandar", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "TC06", "nombre": "Botella de agua pomo PUCE plástico",
        "esperado": "PLASTICO", "categoria": "CAMPUS_PLASTICO",
        "atributos": {
            "objeto_reconocido": "botella_agua", "confianza_ml": "alta",
            "transparencia": "alta", "color": "transparente",
            "forma": "cilindrica_delgada", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "TC07", "nombre": "Speed Max energizante plástico delgado",
        "esperado": "PLASTICO", "categoria": "CAMPUS_PLASTICO",
        "atributos": {
            "objeto_reconocido": "botella_energizante", "confianza_ml": "alta",
            "transparencia": "baja", "color": "variado_vivo",
            "forma": "cilindrica_delgada", "brillo": "alto_nitido",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "TC08", "nombre": "Vaso plástico cafetería PUCE con tapa",
        "esperado": "PLASTICO", "categoria": "CAMPUS_PLASTICO",
        "atributos": {
            "objeto_reconocido": "vaso_plastico", "confianza_ml": "alta",
            "transparencia": "alta", "color": "transparente",
            "forma": "conica", "brillo": "medio_difuso",
            "tapa": "domo_plastico", "textura": "lisa_brillante", "rigidez": "flexible"
        }
    },

    # ── VIDRIO del campus ─────────────────────────────────────────

    {
        "id": "TC09", "nombre": "Caffe Lato Mocachino Toni vidrio naranja",
        "esperado": "VIDRIO", "categoria": "CAMPUS_VIDRIO",
        "atributos": {
            "objeto_reconocido": "botella_mocachino", "confianza_ml": "alta",
            "transparencia": "media", "color": "variado_vivo",
            "forma": "cilindrica_estandar", "brillo": "alto_nitido",
            "tapa": "twist_off_metalica", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "TC10", "nombre": "Caffe Lato Mocachino confianza media — debe ser vidrio",
        "esperado": "VIDRIO", "categoria": "CAMPUS_VIDRIO",
        "atributos": {
            "objeto_reconocido": "botella_mocachino", "confianza_ml": "media",
            "transparencia": "media", "color": "variado_vivo",
            "forma": "cilindrica_estandar", "brillo": "alto_nitido",
            "tapa": "twist_off_metalica", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "TC11", "nombre": "Botella cerveza Pilsener campus ámbar",
        "esperado": "VIDRIO", "categoria": "CAMPUS_VIDRIO",
        "atributos": {
            "objeto_reconocido": "botella_cerveza_vidrio", "confianza_ml": "alta",
            "transparencia": "baja", "color": "ambar",
            "forma": "cilindrica_delgada", "brillo": "alto_nitido",
            "tapa": "corona_metalica", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "TC12", "nombre": "Frasco vidrio con etiqueta colorida campus",
        "esperado": "VIDRIO", "categoria": "CAMPUS_VIDRIO",
        "atributos": {
            "objeto_reconocido": "frasco_vidrio", "confianza_ml": "alta",
            "transparencia": "alta", "color": "transparente",
            "forma": "cilindrica_ancha", "brillo": "alto_nitido",
            "tapa": "tapa_ancha_metalica", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "TC13", "nombre": "DIFÍCIL campus — Mocachino sin etiqueta visible",
        "esperado": "VIDRIO", "categoria": "CAMPUS_VIDRIO",
        "atributos": {
            "objeto_reconocido": "desconocido", "confianza_ml": "media",
            "transparencia": "ninguna", "color": "ambar",
            "forma": "cilindrica_estandar", "brillo": "alto_nitido",
            "tapa": "twist_off_metalica", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "TC14", "nombre": "DIFÍCIL campus — Powerade vs botella vidrio transparente",
        "esperado": "PLASTICO", "categoria": "CAMPUS_PLASTICO",
        "atributos": {
            "objeto_reconocido": "botella_gaseosa", "confianza_ml": "media",
            "transparencia": "alta", "color": "transparente",
            "forma": "cilindrica_estandar", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
    {
        "id": "TC15", "nombre": "DIFÍCIL campus — Chocolatada vs frasco vidrio blanco",
        "esperado": "PLASTICO", "categoria": "CAMPUS_PLASTICO",
        "atributos": {
            "objeto_reconocido": "yogur_plastico", "confianza_ml": "media",
            "transparencia": "ninguna", "color": "blanco_opaco",
            "forma": "cilindrica_ancha", "brillo": "medio_difuso",
            "tapa": "rosca_plastico", "textura": "lisa_brillante", "rigidez": "rigido"
        }
    },
]