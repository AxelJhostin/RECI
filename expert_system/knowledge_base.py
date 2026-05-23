# expert_system/knowledge_base.py
# Base de conocimiento del sistema experto RECI
# Define los atributos, valores posibles y todas las reglas de producción

# ─────────────────────────────────────────────
# ATRIBUTOS Y VALORES POSIBLES
# ─────────────────────────────────────────────

ATRIBUTOS = {
    "transparencia":        ["alta", "media", "baja", "ninguna"],
    "color":                ["transparente", "ambar", "verde_oscuro", "blanco_opaco",
                             "negro", "variado_vivo", "marron_tierra", "metalico"],
    "forma":                ["cilindrica_delgada", "cilindrica_estandar", "cilindrica_ancha",
                             "conica", "rectangular_plana", "irregular"],
    "brillo":               ["alto_nitido", "medio_difuso", "bajo", "metalico"],
    "tapa":                 ["rosca_plastico", "corona_metalica", "twist_off_metalica",
                             "tapa_ancha_metalica", "domo_plastico", "sin_tapa", "sellado"],
    "textura":              ["lisa_brillante", "lisa_sin_brillo", "rugosa", "fibrosa"],
    "rigidez":              ["rigido", "flexible", "indefinido"],
    "confianza_ml":         ["alta", "media", "baja"],
    "objeto_reconocido":    ["botella_agua", "botella_gaseosa", "botella_energizante",
                             "botella_alcoholica_plastico", "vaso_plastico", "vaso_carton",
                             "yogur_plastico", "funda_plastico", "botella_mocachino",
                             "botella_cerveza_vidrio", "botella_salsa_vidrio",
                             "frasco_vidrio", "botella_jugo_vidrio", "cascara_fruta",
                             "restos_comida", "papel_servilleta", "carton", "lata",
                             "desconocido"]
}

# ─────────────────────────────────────────────
# CLASE RULE — representa una regla IF-THEN
# ─────────────────────────────────────────────

class Rule:
    def __init__(self, nombre, condiciones, conclusion, confianza, explicacion, cf=None):
        """
        nombre      : identificador único de la regla
        condiciones : dict con atributo:valor que deben cumplirse
        conclusion  : resultado ("VIDRIO", "PLASTICO", "ORGANICO", "LATA", "DESCONOCIDO")
        confianza   : peso base de la regla (0.0 a 1.0)
        explicacion : texto legible que justifica la regla
        cf          : factor de certeza explícito (si None, usa confianza como CF)
        
        ESPECIFICIDAD AUTOMÁTICA:
        Reglas con más condiciones reciben un bonus automático de CF.
        Una regla con 5 condiciones es más confiable que una con 2
        del mismo CF base — refleja el principio de "longest matching strategy".
        Bonus: (num_condiciones - 1) * 0.01, máximo CF = 1.0
        """
        self.nombre        = nombre
        self.condiciones   = condiciones
        self.conclusion    = conclusion
        self.confianza     = confianza
        self.explicacion   = explicacion
        self.especificidad = len(condiciones)

        # CF base
        cf_base = cf if cf is not None else confianza

        # Bonus por especificidad — más condiciones = más específica = más confiable
        bonus_especificidad = (self.especificidad - 1) * 0.01
        self.cf = round(min(1.0, cf_base + bonus_especificidad), 4)

    def evaluar(self, hechos):
        """
        Retorna True si todos los atributos de la condición
        están presentes en los hechos actuales con el valor correcto.
        """
        for atributo, valor in self.condiciones.items():
            if hechos.get(atributo) != valor:
                return False
        return True

    def __repr__(self):
        conds = " Y ".join(f"{k}={v}" for k, v in self.condiciones.items())
        return (f"[{self.nombre}] SI {conds} → {self.conclusion} "
                f"(CF: {self.cf}, especificidad: {self.especificidad})")

# ─────────────────────────────────────────────
# BASE DE CONOCIMIENTO
# ─────────────────────────────────────────────

class KnowledgeBase:
    def __init__(self):
        self.reglas = []
        self._cargar_reglas()

    def _cargar_reglas(self):

        # ── NIVEL 1: ML con alta confianza ──────────────────────────────
        # Cuando el modelo reconoce el objeto con certeza, confiamos en él

        self.reglas += [
            Rule("R01", {"objeto_reconocido": "botella_mocachino",    "confianza_ml": "alta"}, "VIDRIO",    0.98, "Botella de mocachino identificada con alta confianza — es vidrio ámbar pequeño"),
            Rule("R02", {"objeto_reconocido": "botella_cerveza_vidrio","confianza_ml": "alta"}, "VIDRIO",    0.98, "Botella de cerveza (Pilsener/Club) identificada — vidrio con tapa corona"),
            Rule("R03", {"objeto_reconocido": "botella_salsa_vidrio",  "confianza_ml": "alta"}, "VIDRIO",    0.97, "Botella de salsa (Gustadina) identificada — vidrio con cuello largo"),
            Rule("R04", {"objeto_reconocido": "frasco_vidrio",         "confianza_ml": "alta"}, "VIDRIO",    0.97, "Frasco de mermelada o conserva identificado — vidrio ancho con tapa metálica"),
            Rule("R05", {"objeto_reconocido": "botella_jugo_vidrio",   "confianza_ml": "alta"}, "VIDRIO",    0.96, "Botella de jugo en vidrio identificada"),

            Rule("R06", {"objeto_reconocido": "botella_agua",          "confianza_ml": "alta"}, "PLASTICO",  0.98, "Botella de agua (Tesalia/Pure Water) identificada — PET transparente"),
            Rule("R07", {"objeto_reconocido": "botella_gaseosa",       "confianza_ml": "alta"}, "PLASTICO",  0.98, "Botella de gaseosa (Coca-Cola/Pepsi/Sprite) identificada — PET con etiqueta"),
            Rule("R08", {"objeto_reconocido": "botella_energizante",   "confianza_ml": "alta"}, "PLASTICO",  0.97, "Botella energizante (Volt/220V/Profit) identificada — plástico con etiqueta llamativa"),
            Rule("R09", {"objeto_reconocido": "botella_alcoholica_plastico","confianza_ml":"alta"},"PLASTICO",0.97, "Bebida alcohólica (Switch/Currimcho/24-7) identificada — plástico pequeño"),
            Rule("R10", {"objeto_reconocido": "vaso_plastico",         "confianza_ml": "alta"}, "PLASTICO",  0.98, "Vaso plástico transparente de cafetería identificado"),
            Rule("R11", {"objeto_reconocido": "yogur_plastico",        "confianza_ml": "alta"}, "PLASTICO",  0.97, "Envase de yogur (Toni/Rey Leche) identificado — plástico blanco opaco"),
            Rule("R12", {"objeto_reconocido": "funda_plastico",        "confianza_ml": "alta"}, "PLASTICO",  0.96, "Funda plástica identificada — flexible e irregular"),

            Rule("R13", {"objeto_reconocido": "cascara_fruta",         "confianza_ml": "alta"}, "ORGANICO",  0.98, "Cáscara de fruta identificada — residuo orgánico"),
            Rule("R14", {"objeto_reconocido": "restos_comida",         "confianza_ml": "alta"}, "ORGANICO",  0.98, "Restos de comida identificados — residuo orgánico"),
            Rule("R15", {"objeto_reconocido": "papel_servilleta",      "confianza_ml": "alta"}, "ORGANICO",  0.95, "Servilleta o papel identificado — va a orgánico/papel"),
            Rule("R16", {"objeto_reconocido": "carton",                "confianza_ml": "alta"}, "ORGANICO",  0.95, "Cartón o vaso de cartón identificado — va a orgánico/papel"),
            Rule("R17", {"objeto_reconocido": "vaso_carton",           "confianza_ml": "alta"}, "ORGANICO",  0.94, "Vaso de cartón de cafetería identificado"),

            Rule("R18", {"objeto_reconocido": "lata",                  "confianza_ml": "alta"}, "LATA",      1.00, "Lata de aluminio identificada — no pertenece a ningún compartimento"),
        ]

        # ── NIVEL 2: Razonamiento por atributos visuales ─────────────────
        # Cuando la confianza del ML es media o baja, el SE razona por características

        self.reglas += [

            # VIDRIO — señales visuales fuertes
            Rule("R20", {"transparencia": "ninguna", "color": "ambar",        "tapa": "twist_off_metalica"}, "VIDRIO", 0.97, "Opaco ámbar con tapa metálica twist-off → botella de mocachino o similar"),
            Rule("R21", {"transparencia": "ninguna", "color": "ambar",        "tapa": "corona_metalica"},    "VIDRIO", 0.97, "Opaco ámbar con tapa corona → cerveza Pilsener"),
            Rule("R22", {"transparencia": "ninguna", "color": "verde_oscuro", "tapa": "corona_metalica"},    "VIDRIO", 0.97, "Verde oscuro con tapa corona → cerveza Club"),
            Rule("R23", {"transparencia": "alta",    "brillo": "alto_nitido", "forma": "cilindrica_estandar","tapa": "twist_off_metalica"}, "VIDRIO", 0.93, "Transparente con brillo nítido y tapa metálica → frasco o botella de vidrio"),
            Rule("R24", {"transparencia": "alta",    "brillo": "alto_nitido", "forma": "cilindrica_ancha",   "tapa": "tapa_ancha_metalica"}, "VIDRIO", 0.95, "Cilíndrico ancho transparente con tapa ancha metálica → frasco de mermelada"),
            Rule("R25", {"brillo": "alto_nitido",    "tapa": "corona_metalica"}, "VIDRIO", 0.90, "Brillo nítido de vidrio con tapa corona metálica → botella de vidrio"),

            # PLÁSTICO — señales visuales fuertes
            Rule("R30", {"transparencia": "alta",    "forma": "conica",        "tapa": "sin_tapa"},          "PLASTICO", 0.97, "Cónico transparente sin tapa → vaso plástico de cafetería"),
            Rule("R31", {"transparencia": "alta",    "forma": "conica",        "tapa": "domo_plastico"},      "PLASTICO", 0.98, "Cónico con tapa domo → vaso plástico con tapa de cafetería"),
            Rule("R32", {"transparencia": "alta",    "brillo": "medio_difuso", "tapa": "rosca_plastico"},     "PLASTICO", 0.92, "Transparente con brillo difuso y tapa rosca plástica → botella PET"),
            Rule("R33", {"color": "variado_vivo",    "tapa": "rosca_plastico", "forma": "cilindrica_delgada"},"PLASTICO", 0.93, "Etiqueta muy colorida en botella delgada → energizante o alcohólica en plástico"),
            Rule("R34", {"transparencia": "ninguna", "color": "blanco_opaco",  "forma": "cilindrica_ancha"},  "PLASTICO", 0.94, "Blanco opaco cilíndrico ancho → yogur plástico"),
            Rule("R35", {"rigidez": "flexible",      "color": "negro"},                                       "PLASTICO", 0.93, "Flexible y negro → funda plástica"),
            Rule("R36", {"transparencia": "ninguna", "color": "negro",         "brillo": "medio_difuso"},     "PLASTICO", 0.88, "Negro opaco con brillo medio → Monster o botella plástica oscura"),

            # ORGÁNICO — señales visuales
            Rule("R40", {"forma": "irregular",       "textura": "rugosa",      "color": "marron_tierra"},     "ORGANICO", 0.95, "Irregular rugoso marrón → resto de comida u orgánico"),
            Rule("R41", {"color": "marron_tierra",   "textura": "fibrosa"},                                   "ORGANICO", 0.94, "Marrón fibroso → cartón o material orgánico"),
            Rule("R42", {"forma": "rectangular_plana","textura": "lisa_sin_brillo","color": "blanco_opaco"},  "ORGANICO", 0.93, "Plano blanco sin brillo → papel o servilleta"),
            Rule("R43", {"textura": "fibrosa",        "rigidez": "flexible"},                                 "ORGANICO", 0.91, "Fibroso y flexible → papel, cartón o residuo orgánico"),

            # LATA — señal muy fuerte
            Rule("R50", {"brillo": "metalico",       "forma": "cilindrica_delgada"},                          "LATA",     0.99, "Brillo metálico en cilindro → lata de aluminio (Red Bull, atún, etc.)"),
            Rule("R51", {"color": "metalico"},                                                                 "LATA",     0.97, "Color metálico → lata de aluminio"),
        ]

        # ── NIVEL 3: Desempate — casos ambiguos ─────────────────────────
        # Plástico transparente vs vidrio transparente (el caso más difícil)

        self.reglas += [
            Rule("R60", {"transparencia": "alta", "brillo": "alto_nitido", "tapa": "rosca_plastico"}, "PLASTICO", 0.88,
                 "Transparente con brillo alto PERO tapa rosca plástica → es PET no vidrio"),
            Rule("R61", {"transparencia": "alta", "brillo": "medio_difuso","tapa": "rosca_plastico"}, "PLASTICO", 0.93,
                 "Transparente con brillo difuso y tapa rosca → claramente plástico PET"),
            Rule("R62", {"transparencia": "alta", "brillo": "alto_nitido", "tapa": "twist_off_metalica"}, "VIDRIO", 0.95,
                 "Transparente con brillo nítido y tapa metálica → vidrio, no plástico"),

            # Vaso cartón vs vaso plástico
            Rule("R63", {"forma": "conica", "textura": "fibrosa",  "transparencia": "ninguna"}, "ORGANICO", 0.95,
                 "Cónico fibroso opaco → vaso de cartón, va a orgánico"),
            Rule("R64", {"forma": "conica", "textura": "lisa_brillante", "transparencia": "alta"}, "PLASTICO", 0.97,
                 "Cónico liso brillante transparente → vaso de plástico"),

            # Funda negra vs cáscara oscura
            Rule("R65", {"color": "negro", "rigidez": "flexible", "textura": "lisa_brillante"}, "PLASTICO", 0.95,
                 "Negro flexible y liso brillante → funda plástica, no orgánico"),
            Rule("R66", {"color": "marron_tierra", "rigidez": "flexible", "textura": "rugosa"}, "ORGANICO", 0.95,
                 "Marrón flexible y rugoso → cáscara de fruta u orgánico"),
        ]

        # ── NIVEL 4: Reglas de seguridad ────────────────────────────────
        # Cuando no hay suficiente información para decidir con certeza

        self.reglas += [
            Rule("R70", {"confianza_ml": "baja", "forma": "irregular"},          "ORGANICO",    0.60,
                 "Baja confianza y forma irregular → probablemente orgánico, decisión conservadora"),
            Rule("R71", {"confianza_ml": "baja", "forma": "cilindrica_estandar"},"PLASTICO",    0.55,
                 "Baja confianza y forma cilíndrica → probablemente plástico por ser el más común"),
            Rule("R72", {"objeto_reconocido": "desconocido", "confianza_ml": "baja"}, "DESCONOCIDO", 0.00,
                 "Objeto no reconocido con baja confianza → solicitar segunda captura"),
        # ── Reglas por brillo sin tapa conocida ─────────────────
            Rule("R80", {"transparencia": "alta", "brillo": "alto_nitido",
                        "forma": "cilindrica_estandar", "rigidez": "rigido"}, "VIDRIO", 0.75,
                "Transparente con brillo nítido de vidrio y cilíndrico rígido → probable vidrio"),

            Rule("R81", {"transparencia": "alta", "brillo": "medio_difuso",
                        "forma": "cilindrica_estandar", "rigidez": "rigido"}, "PLASTICO", 0.75,
                "Transparente con brillo difuso cilíndrico rígido → probable plástico PET"),

            Rule("R82", {"transparencia": "alta", "brillo": "alto_nitido",
                        "forma": "cilindrica_delgada", "rigidez": "rigido"}, "PLASTICO", 0.70,
                "Transparente nítido pero delgado → más probable plástico que vidrio"),
        ]

        # ── NIVEL 5: Reglas para casos específicos del campus ────────────
        # Objetos comunes en Manabí que necesitan reglas propias

        self.reglas += [

            # Sprite / 7UP — verde transparente plástico vs Club verde vidrio
            Rule("R90", {"transparencia": "media", "color": "variado_vivo",
                         "brillo": "medio_difuso", "tapa": "rosca_plastico"},
                 "PLASTICO", 0.96,
                 "Verde transparente con brillo difuso y tapa rosca → Sprite o 7UP plástico"),

            Rule("R91", {"transparencia": "ninguna", "color": "verde_oscuro",
                         "brillo": "alto_nitido", "tapa": "corona_metalica"},
                 "VIDRIO", 0.97,
                 "Verde oscuro opaco con brillo nítido y tapa corona → cerveza Club vidrio"),

            Rule("R92", {"transparencia": "media", "color": "variado_vivo",
                         "brillo": "alto_nitido", "tapa": "corona_metalica"},
                 "VIDRIO", 0.94,
                 "Verde con brillo nítido y tapa corona → probable vidrio aunque sea claro"),

            # Pepsi azul oscuro — no confundir con vidrio oscuro
            Rule("R93", {"color": "variado_vivo", "tapa": "rosca_plastico",
                         "brillo": "medio_difuso", "rigidez": "rigido"},
                 "PLASTICO", 0.93,
                 "Color vivo con tapa rosca y brillo difuso → plástico con etiqueta (Pepsi, Fanta)"),

            # Envase de snack metálico — no confundir con lata
            Rule("R94", {"brillo": "metalico", "forma": "rectangular_plana",
                         "rigidez": "flexible"},
                 "PLASTICO", 0.91,
                 "Metálico pero rectangular y flexible → envase de snack plástico metalizado"),

            Rule("R95", {"brillo": "metalico", "forma": "cilindrica_estandar",
                         "rigidez": "rigido", "tapa": "sellado"},
                 "LATA", 0.98,
                 "Metálico cilíndrico rígido sellado → lata de aluminio, no snack"),

            # Pitillo / sorbete solo
            Rule("R96", {"forma": "cilindrica_delgada", "transparencia": "media",
                         "rigidez": "rigido", "textura": "lisa_brillante",
                         "tapa": "sin_tapa"},
                 "PLASTICO", 0.89,
                 "Cilíndrico muy delgado semitransparente sin tapa → pitillo o sorbete plástico"),

            # Yogur con tapa de aluminio — no confundir con lata
            Rule("R97", {"color": "blanco_opaco", "forma": "cilindrica_ancha",
                         "brillo": "medio_difuso", "rigidez": "rigido"},
                 "PLASTICO", 0.95,
                 "Blanco opaco cilíndrico ancho con brillo medio → yogur plástico (Toni/Rey Leche)"),

            # Botella de salsa con contenido visible
            Rule("R98", {"transparencia": "media", "color": "variado_vivo",
                         "forma": "cilindrica_estandar", "tapa": "twist_off_metalica",
                         "brillo": "alto_nitido"},
                 "VIDRIO", 0.93,
                 "Semitransparente con contenido de color y tapa twist-off → salsa en vidrio"),

            # Objeto muy pequeño — casi nunca es vidrio
            Rule("R99", {"forma": "cilindrica_delgada", "confianza_ml": "baja",
                         "transparencia": "alta"},
                 "PLASTICO", 0.72,
                 "Objeto pequeño y delgado transparente con baja confianza → más probable plástico"),

            # Botella de agua grande — mismo material que pequeña
            Rule("R100", {"objeto_reconocido": "botella_agua", "forma": "cilindrica_ancha",
                          "confianza_ml": "alta"},
                 "PLASTICO", 0.97,
                 "Botella de agua grande (1L-2L) identificada → plástico PET"),

            # Currimcho / 24-7 / Switch — botellas alcohólicas pequeñas
            Rule("R101", {"objeto_reconocido": "botella_alcoholica_plastico",
                          "confianza_ml": "media", "tapa": "rosca_plastico"},
                 "PLASTICO", 0.94,
                 "Botella alcohólica económica con tapa rosca → Switch/Currimcho/24-7 plástico"),

            Rule("R102", {"color": "variado_vivo", "forma": "cilindrica_delgada",
                          "tapa": "rosca_plastico", "transparencia": "alta"},
                 "PLASTICO", 0.92,
                 "Botella delgada transparente con etiqueta colorida → bebida alcohólica o energizante plástico"),

            # Monster negro — plástico opaco oscuro
            Rule("R103", {"color": "negro", "brillo": "medio_difuso",
                          "forma": "cilindrica_estandar", "tapa": "rosca_plastico"},
                 "PLASTICO", 0.94,
                 "Negro opaco con tapa rosca → Monster u otra bebida en plástico oscuro"),

            # Funda transparente — no confundir con botella
            Rule("R104", {"transparencia": "alta", "rigidez": "flexible",
                          "forma": "irregular"},
                 "PLASTICO", 0.93,
                 "Transparente flexible e irregular → funda plástica transparente"),

            # Cartón de jugo — rectangular, no cilíndrico
            Rule("R105", {"forma": "rectangular_plana", "textura": "lisa_sin_brillo",
                          "rigidez": "rigido", "transparencia": "ninguna"},
                 "ORGANICO", 0.91,
                 "Rectangular liso sin brillo y rígido → cartón de jugo o caja de cartón"),

            # Cáscara de banano específica — marrón oscuro
            Rule("R106", {"color": "marron_tierra", "forma": "irregular",
                          "textura": "rugosa", "rigidez": "flexible"},
                 "ORGANICO", 0.97,
                 "Marrón irregular rugoso y flexible → cáscara de banano u orgánico"),

            # Refuerzo: vidrio siempre rígido — si es flexible no puede ser vidrio
            Rule("R107", {"rigidez": "flexible", "brillo": "alto_nitido"},
                 "PLASTICO", 0.88,
                 "Flexible aunque tenga brillo alto → no puede ser vidrio, es plástico flexible"),

            # Refuerzo: tapa corona = casi siempre vidrio
            Rule("R108", {"tapa": "corona_metalica"},
                 "VIDRIO", 0.90,
                 "Tapa corona metálica → casi exclusivamente botellas de vidrio"),

            # Refuerzo: tapa rosca plástica = nunca vidrio
            Rule("R109", {"tapa": "rosca_plastico", "rigidez": "rigido"},
                 "PLASTICO", 0.88,
                 "Tapa rosca plástica con objeto rígido → plástico PET, nunca vidrio"),

          # Frasco vidrio con contenido visible de color
            Rule("R110", {"objeto_reconocido": "frasco_vidrio",
                          "tapa": "tapa_ancha_metalica",
                          "brillo": "alto_nitido", "rigidez": "rigido"},
                 "VIDRIO", 0.96,
                 "Frasco con tapa ancha metálica y brillo nítido → vidrio aunque tenga contenido de color"),

            # Snack metálico rectangular flexible — nunca es lata
            Rule("R111", {"brillo": "metalico", "forma": "rectangular_plana",
                          "rigidez": "flexible", "tapa": "sellado"},
                 "PLASTICO", 0.97,
                 "Metálico rectangular flexible sellado → envase de snack plástico metalizado, no lata"),
        # Vaso de cartón cilíndrico — no siempre es cónico
            Rule("R112", {"objeto_reconocido": "vaso_carton",
                          "textura": "lisa_sin_brillo", "rigidez": "rigido"},
                 "ORGANICO", 0.95,
                 "Vaso de cartón con textura sin brillo → orgánico/papel sin importar forma"),
        ]

    def obtener_reglas(self):
        return self.reglas

    def __repr__(self):
        return f"KnowledgeBase con {len(self.reglas)} reglas cargadas"