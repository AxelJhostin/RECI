# vision/tm_classifier.py
# Clasificador con modelo entrenado en Google Colab (MobileNetV2) exportado como TFLite
# Misma interfaz que AttributeExtractor para intercambio transparente

import numpy as np
import cv2
from pathlib import Path

from vision.visual_heuristics import refinar_atributos, refinar_atributos_api


class TeachableMachineClassifier:
    """
    Carga un modelo .tflite y retorna los 9 atributos
    que espera InferenceEngine.cargar_hechos().
    """

    MAPA_CLASES = {

        # ── Clases generales entrenadas en Colab ──────────────────────
        "plastico": {
            "objeto_reconocido": "botella_agua",
            "transparencia":     "alta",
            "color":             "transparente",
            "forma":             "cilindrica_estandar",
            "brillo":            "medio_difuso",
            "tapa":              "rosca_plastico",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "vidrio": {
            "objeto_reconocido": "botella_cerveza_vidrio",
            "transparencia":     "ninguna",
            "color":             "ambar",
            "forma":             "cilindrica_estandar",
            "brillo":            "alto_nitido",
            "tapa":              "corona_metalica",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "lata": {
            "objeto_reconocido": "lata",
            "transparencia":     "ninguna",
            "color":             "metalico",
            "forma":             "cilindrica_estandar",
            "brillo":            "metalico",
            "tapa":              "sellado",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "organico": {
            "objeto_reconocido": "cascara_fruta",
            "transparencia":     "ninguna",
            "color":             "marron_tierra",
            "forma":             "irregular",
            "brillo":            "bajo",
            "tapa":              "sin_tapa",
            "textura":           "rugosa",
            "rigidez":           "flexible",
        },

        # ── Clases específicas del campus PUCE Manabí ─────────────────
        "lata_cocacola": {
            "objeto_reconocido": "lata",
            "transparencia":     "ninguna",
            "color":             "metalico",
            "forma":             "cilindrica_estandar",
            "brillo":            "metalico",
            "tapa":              "sellado",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "vidrio_mocaccino": {
            "objeto_reconocido": "botella_mocachino",
            "transparencia":     "media",
            "color":             "variado_vivo",
            "forma":             "cilindrica_estandar",
            "brillo":            "alto_nitido",
            "tapa":              "twist_off_metalica",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "plastico_choco_latada": {
            "objeto_reconocido": "yogur_plastico",
            "transparencia":     "ninguna",
            "color":             "blanco_opaco",
            "forma":             "cilindrica_ancha",
            "brillo":            "medio_difuso",
            "tapa":              "rosca_plastico",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "pomo_agua_puce": {
            "objeto_reconocido": "botella_agua",
            "transparencia":     "alta",
            "color":             "transparente",
            "forma":             "cilindrica_estandar",
            "brillo":            "medio_difuso",
            "tapa":              "rosca_plastico",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "botella_jugo": {
            "objeto_reconocido": "botella_jugo_vidrio",
            "transparencia":     "media",
            "color":             "variado_vivo",
            "forma":             "cilindrica_estandar",
            "brillo":            "alto_nitido",
            "tapa":              "twist_off_metalica",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },

        # ── Clases específicas por objeto ──────────────────────────────
        "botella_agua": {
            "objeto_reconocido": "botella_agua",
            "transparencia":     "alta",
            "color":             "transparente",
            "forma":             "cilindrica_delgada",
            "brillo":            "medio_difuso",
            "tapa":              "rosca_plastico",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "botella_gaseosa": {
            "objeto_reconocido": "botella_gaseosa",
            "transparencia":     "alta",
            "color":             "transparente",
            "forma":             "cilindrica_estandar",
            "brillo":            "medio_difuso",
            "tapa":              "rosca_plastico",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "botella_energizante": {
            "objeto_reconocido": "botella_energizante",
            "transparencia":     "baja",
            "color":             "variado_vivo",
            "forma":             "cilindrica_delgada",
            "brillo":            "alto_nitido",
            "tapa":              "rosca_plastico",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "botella_alcoholica_plastico": {
            "objeto_reconocido": "botella_alcoholica_plastico",
            "transparencia":     "alta",
            "color":             "variado_vivo",
            "forma":             "cilindrica_delgada",
            "brillo":            "medio_difuso",
            "tapa":              "rosca_plastico",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "vaso_plastico": {
            "objeto_reconocido": "vaso_plastico",
            "transparencia":     "alta",
            "color":             "transparente",
            "forma":             "conica",
            "brillo":            "medio_difuso",
            "tapa":              "sin_tapa",
            "textura":           "lisa_brillante",
            "rigidez":           "flexible",
        },
        "vaso_plastico_con_tapa": {
            "objeto_reconocido": "vaso_plastico",
            "transparencia":     "alta",
            "color":             "transparente",
            "forma":             "conica",
            "brillo":            "medio_difuso",
            "tapa":              "domo_plastico",
            "textura":           "lisa_brillante",
            "rigidez":           "flexible",
        },
        "yogur_plastico": {
            "objeto_reconocido": "yogur_plastico",
            "transparencia":     "ninguna",
            "color":             "blanco_opaco",
            "forma":             "cilindrica_ancha",
            "brillo":            "medio_difuso",
            "tapa":              "tapa_ancha_metalica",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "funda_plastico": {
            "objeto_reconocido": "funda_plastico",
            "transparencia":     "alta",
            "color":             "transparente",
            "forma":             "irregular",
            "brillo":            "medio_difuso",
            "tapa":              "sin_tapa",
            "textura":           "lisa_brillante",
            "rigidez":           "flexible",
        },
        "botella_mocachino": {
            "objeto_reconocido": "botella_mocachino",
            "transparencia":     "ninguna",
            "color":             "ambar",
            "forma":             "cilindrica_estandar",
            "brillo":            "alto_nitido",
            "tapa":              "twist_off_metalica",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "botella_cerveza_vidrio": {
            "objeto_reconocido": "botella_cerveza_vidrio",
            "transparencia":     "baja",
            "color":             "ambar",
            "forma":             "cilindrica_delgada",
            "brillo":            "alto_nitido",
            "tapa":              "corona_metalica",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "botella_cerveza_club": {
            "objeto_reconocido": "botella_cerveza_vidrio",
            "transparencia":     "ninguna",
            "color":             "verde_oscuro",
            "forma":             "cilindrica_delgada",
            "brillo":            "alto_nitido",
            "tapa":              "corona_metalica",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "frasco_vidrio": {
            "objeto_reconocido": "frasco_vidrio",
            "transparencia":     "alta",
            "color":             "transparente",
            "forma":             "cilindrica_ancha",
            "brillo":            "alto_nitido",
            "tapa":              "tapa_ancha_metalica",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "frasco_vidrio_2": {
            "objeto_reconocido": "frasco_vidrio",
            "transparencia":     "media",
            "color":             "transparente",
            "forma":             "cilindrica_ancha",
            "brillo":            "alto_nitido",
            "tapa":              "tapa_ancha_metalica",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "botella_salsa_vidrio": {
            "objeto_reconocido": "botella_salsa_vidrio",
            "transparencia":     "media",
            "color":             "variado_vivo",
            "forma":             "cilindrica_estandar",
            "brillo":            "alto_nitido",
            "tapa":              "twist_off_metalica",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "botella_jugo_vidrio": {
            "objeto_reconocido": "botella_jugo_vidrio",
            "transparencia":     "media",
            "color":             "variado_vivo",
            "forma":             "cilindrica_estandar",
            "brillo":            "alto_nitido",
            "tapa":              "twist_off_metalica",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "cascara_fruta": {
            "objeto_reconocido": "cascara_fruta",
            "transparencia":     "ninguna",
            "color":             "marron_tierra",
            "forma":             "irregular",
            "brillo":            "bajo",
            "tapa":              "sin_tapa",
            "textura":           "rugosa",
            "rigidez":           "flexible",
        },
        "restos_comida": {
            "objeto_reconocido": "restos_comida",
            "transparencia":     "ninguna",
            "color":             "marron_tierra",
            "forma":             "irregular",
            "brillo":            "bajo",
            "tapa":              "sin_tapa",
            "textura":           "fibrosa",
            "rigidez":           "indefinido",
        },
        "papel_servilleta": {
            "objeto_reconocido": "papel_servilleta",
            "transparencia":     "ninguna",
            "color":             "blanco_opaco",
            "forma":             "rectangular_plana",
            "brillo":            "bajo",
            "tapa":              "sin_tapa",
            "textura":           "lisa_sin_brillo",
            "rigidez":           "flexible",
        },
        "carton": {
            "objeto_reconocido": "carton",
            "transparencia":     "ninguna",
            "color":             "marron_tierra",
            "forma":             "rectangular_plana",
            "brillo":            "bajo",
            "tapa":              "sin_tapa",
            "textura":           "lisa_sin_brillo",
            "rigidez":           "rigido",
        },
        "vaso_carton": {
            "objeto_reconocido": "vaso_carton",
            "transparencia":     "ninguna",
            "color":             "blanco_opaco",
            "forma":             "conica",
            "brillo":            "bajo",
            "tapa":              "sin_tapa",
            "textura":           "lisa_sin_brillo",
            "rigidez":           "rigido",
        },

        # ── Nuevos objetos: vasos blancos, vasos de vidrio, platos, recipientes ──
        "vaso_plastico_blanco": {
            "objeto_reconocido": "vaso_plastico_blanco",
            "transparencia":     "ninguna",
            "color":             "blanco_opaco",
            "forma":             "conica",
            "brillo":            "medio_difuso",
            "tapa":              "sin_tapa",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "vaso_plastico_blanco_con_tapa": {
            "objeto_reconocido": "vaso_plastico_blanco",
            "transparencia":     "ninguna",
            "color":             "blanco_opaco",
            "forma":             "conica",
            "brillo":            "medio_difuso",
            "tapa":              "domo_plastico",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "vaso_vidrio": {
            "objeto_reconocido": "vaso_vidrio",
            "transparencia":     "alta",
            "color":             "transparente",
            "forma":             "cilindrica_ancha",
            "brillo":            "alto_nitido",
            "tapa":              "sin_tapa",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "plato_plastico": {
            "objeto_reconocido": "plato_plastico",
            "transparencia":     "ninguna",
            "color":             "blanco_opaco",
            "forma":             "rectangular_plana",
            "brillo":            "medio_difuso",
            "tapa":              "sin_tapa",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "recipiente_plastico": {
            "objeto_reconocido": "recipiente_plastico",
            "transparencia":     "ninguna",
            "color":             "blanco_opaco",
            "forma":             "cilindrica_ancha",
            "brillo":            "medio_difuso",
            "tapa":              "sin_tapa",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "cubierto_plastico": {
            "objeto_reconocido": "cubierto_plastico",
            "transparencia":     "ninguna",
            "color":             "blanco_opaco",
            "forma":             "irregular",
            "brillo":            "bajo",
            "tapa":              "sin_tapa",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
        "snack_plastico": {
            "objeto_reconocido": "snack_plastico",
            "transparencia":     "ninguna",
            "color":             "variado_vivo",
            "forma":             "irregular",
            "brillo":            "metalico",
            "tapa":              "sellado",
            "textura":           "lisa_brillante",
            "rigidez":           "flexible",
        },
        "pitillo": {
            "objeto_reconocido": "pitillo",
            "transparencia":     "media",
            "color":             "transparente",
            "forma":             "cilindrica_delgada",
            "brillo":            "medio_difuso",
            "tapa":              "sin_tapa",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
        },
    }

    def __init__(self, model_path: str = "model/model.tflite",
                       labels_path: str = "model/labels.txt"):

        model_path  = Path(model_path)
        labels_path = Path(labels_path)

        if not model_path.exists():
            raise FileNotFoundError(
                f"Modelo no encontrado: {model_path}\n"
                f"Colocar model.tflite en la carpeta model/"
            )
        if not labels_path.exists():
            raise FileNotFoundError(f"labels.txt no encontrado: {labels_path}")

        # Cargar etiquetas
        with open(labels_path, "r", encoding="utf-8") as f:
            self.labels = []
            for line in f:
                line = line.strip()
                if line:
                    partes = line.split(" ", 1)
                    self.labels.append(partes[1] if len(partes) > 1 else partes[0])

        # Cargar intérprete TFLite
        try:
            import tflite_runtime.interpreter as tflite
        except ImportError:
            import tensorflow.lite as tflite

        self.interpreter = tflite.Interpreter(model_path=str(model_path))
        self.interpreter.allocate_tensors()
        self.input_details  = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        shape       = self.input_details[0]['shape']
        self.altura = shape[1]
        self.ancho  = shape[2]

        print(f"[TM] Modelo cargado: {model_path.name}")
        print(f"[TM] Clases ({len(self.labels)}): {self.labels}")
        print(f"[TM] Resolución de entrada: {self.altura}×{self.ancho}")

    def _nivel_confianza(self, prob: float) -> str:
        if prob >= 0.80:
            return "alta"
        elif prob >= 0.55:
            return "media"
        else:
            return "baja"

    def _inferir(self, imagen_bgr: np.ndarray) -> tuple:
        img = cv2.resize(imagen_bgr, (self.ancho, self.altura))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32)
        img = np.expand_dims(img, axis=0)

        self.interpreter.set_tensor(self.input_details[0]['index'], img)
        self.interpreter.invoke()
        probs = self.interpreter.get_tensor(self.output_details[0]['index'])[0]

        idx_max  = int(np.argmax(probs))
        clase    = self.labels[idx_max]
        prob_max = float(probs[idx_max])
        todas    = {self.labels[i]: float(probs[i]) for i in range(len(self.labels))}

        return clase, prob_max, todas

    def analizar_imagen(self, ruta_imagen: str) -> dict:
        """
        Interfaz idéntica a AttributeExtractor.analizar_imagen().
        Recibe ruta de imagen, retorna dict con los 9 atributos
        listos para InferenceEngine.cargar_hechos().
        """
        print(f"  🔍 Analizando imagen con TM: {ruta_imagen}")

        img = cv2.imread(ruta_imagen)
        if img is None:
            raise ValueError(f"No se pudo cargar la imagen: {ruta_imagen}")

        clase, prob, todas = self._inferir(img)
        confianza_nivel    = self._nivel_confianza(prob)

        print(f"  🤖 TM detectó: {clase} ({prob:.1%})")
        print(f"  📊 Top 3: {sorted(todas.items(), key=lambda x: x[1], reverse=True)[:3]}")

        atributos_base = self.MAPA_CLASES.get(clase)

        if atributos_base is None:
            print(f"  ⚠ Clase '{clase}' no tiene mapeo definido → DESCONOCIDO")
            atributos = {
                "objeto_reconocido": "desconocido",
                "confianza_ml":      "baja",
                "transparencia":     "ninguna",
                "color":             "variado_vivo",
                "forma":             "irregular",
                "brillo":            "bajo",
                "tapa":              "sin_tapa",
                "textura":           "rugosa",
                "rigidez":           "indefinido",
            }
        else:
            atributos = dict(atributos_base)
            atributos["confianza_ml"] = confianza_nivel

        atributos = refinar_atributos(atributos, img, clase_tm=clase, prob_tm=prob)
        prob_vidrio = float(todas.get("vidrio", 0.0))
        atributos = refinar_atributos_api(
            atributos, img, clase_tm=clase, prob_tm=prob, prob_vidrio=prob_vidrio
        )
        print(f"  ✅ Atributos extraídos: {atributos}")
        return atributos

    def analizar_frame(self, frame_bgr: np.ndarray):
        """
        Versión para cámara en tiempo real — recibe frame OpenCV directamente.
        """
        clase, prob, todas = self._inferir(frame_bgr)
        confianza_nivel = self._nivel_confianza(prob)
        prob_vidrio = float(todas.get("vidrio", 0.0))

        atributos_base = self.MAPA_CLASES.get(clase)
        if atributos_base is None:
            atributos = {
                "objeto_reconocido": "desconocido",
                "confianza_ml":      "baja",
                "transparencia":     "ninguna",
                "color":             "variado_vivo",
                "forma":             "irregular",
                "brillo":            "bajo",
                "tapa":              "sin_tapa",
                "textura":           "rugosa",
                "rigidez":           "indefinido",
            }
        else:
            atributos = dict(atributos_base)
            atributos["confianza_ml"] = confianza_nivel

        atributos = refinar_atributos(atributos, frame_bgr, clase_tm=clase, prob_tm=prob)
        atributos = refinar_atributos_api(
            atributos, frame_bgr, clase_tm=clase, prob_tm=prob, prob_vidrio=prob_vidrio
        )
        return atributos, clase, prob, prob_vidrio

    def analizar_y_clasificar(self, ruta_imagen: str) -> dict:
        """
        Flujo completo idéntico a AttributeExtractor.analizar_y_clasificar().
        """
        import sys, os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from expert_system.inference_engine import InferenceEngine
        from expert_system.explanation import ExplanationReport

        atributos = self.analizar_imagen(ruta_imagen)

        engine = InferenceEngine()
        engine.cargar_hechos(atributos)
        conclusion, confianza, reglas = engine.ejecutar()

        reporte = ExplanationReport(engine)
        print(engine.obtener_explicacion())

        decision = engine.decision_hardware()
        print(f"\n  ACCIÓN HARDWARE:")
        print(f"    Compuerta : {decision['compuerta']}")
        print(f"    LED       : {decision['led']}")
        print(f"    Servo     : {decision['angulo_servo']}°")
        print(f"    Mensaje   : {decision['mensaje']}")

        return {
            "atributos":  atributos,
            "conclusion": conclusion,
            "confianza":  confianza,
            "hardware":   decision,
            "reporte":    reporte.a_dict()
        }

    def __repr__(self):
        return f"TeachableMachineClassifier(clases={len(self.labels)}, entrada={self.altura}×{self.ancho})"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python3 vision/tm_classifier.py <ruta_imagen>")
        sys.exit(1)

    clf = TeachableMachineClassifier()
    resultado = clf.analizar_y_clasificar(sys.argv[1])
    print(f"\n{'═'*60}")
    print(f"  RESULTADO FINAL: {resultado['conclusion']}")
    print(f"  CONFIANZA:       {resultado['confianza']*100:.1f}%")
    print(f"  COMPUERTA:       {resultado['hardware']['compuerta']}")
    print(f"{'═'*60}")