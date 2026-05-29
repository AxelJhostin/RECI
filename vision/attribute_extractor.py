# vision/attribute_extractor.py
# Extractor de atributos visuales usando Google Gemini (actual) o Teachable Machine (producción)
# Módulo de visión del sistema experto RECI

import os
import json
import base64
import httpx
from pathlib import Path


class AttributeExtractor:
    """
    Extrae atributos visuales de una imagen usando Google Gemini.
    Convierte una imagen en el diccionario de atributos que
    necesita el motor de inferencia del sistema experto RECI.

    Cuando el equipo ML entregue el modelo Teachable Machine,
    usar analizar_imagen_tm() en lugar de analizar_imagen().
    El resto del sistema no cambia.
    """

    GEMINI_URL = (
        "https://generativelanguage.googleapis.com/v1beta/models"
        "/gemini-2.5-flash:generateContent"
    )

    PROMPT = """Eres el módulo de visión del sistema experto RECI, un tacho inteligente de reciclaje universitario en Ecuador.

Tu tarea es analizar la imagen y extraer exactamente estos atributos visuales del objeto principal:

ATRIBUTOS REQUERIDOS (usa EXACTAMENTE estos valores):

- objeto_reconocido: botella_agua | botella_gaseosa | botella_energizante | botella_alcoholica_plastico | vaso_plastico | vaso_carton | yogur_plastico | funda_plastico | botella_mocachino | botella_cerveza_vidrio | botella_salsa_vidrio | frasco_vidrio | botella_jugo_vidrio | cascara_fruta | restos_comida | papel_servilleta | carton | lata | desconocido

- confianza_ml: alta | media | baja

- transparencia: alta | media | baja | ninguna

- color: transparente | ambar | verde_oscuro | blanco_opaco | negro | variado_vivo | marron_tierra | metalico

- forma: cilindrica_delgada | cilindrica_estandar | cilindrica_ancha | conica | rectangular_plana | irregular

- brillo: alto_nitido | medio_difuso | bajo | metalico

- tapa: rosca_plastico | corona_metalica | twist_off_metalica | tapa_ancha_metalica | domo_plastico | sin_tapa | sellado

- textura: lisa_brillante | lisa_sin_brillo | rugosa | fibrosa

- rigidez: rigido | flexible | indefinido

REGLAS DE ANÁLISIS:
- Analiza SOLO el objeto principal de la imagen
- Si no puedes determinar un atributo con certeza, usa el valor más cercano
- confianza_ml refleja qué tan seguro estás de tu análisis general
- Si el objeto no está claro o es muy ambiguo, usa confianza_ml = baja y objeto_reconocido = desconocido

Responde ÚNICAMENTE con un JSON válido, sin texto adicional, sin markdown, sin explicaciones:
{
  "objeto_reconocido": "...",
  "confianza_ml": "...",
  "transparencia": "...",
  "color": "...",
  "forma": "...",
  "brillo": "...",
  "tapa": "...",
  "textura": "...",
  "rigidez": "..."
}"""

    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY no configurada. "
                "Agrega GEMINI_API_KEY=tu_key en el archivo .env"
            )

    def _imagen_a_base64(self, ruta_imagen: str) -> tuple:
        """Convierte imagen a base64 y detecta el tipo MIME."""
        ruta = Path(ruta_imagen)
        extension = ruta.suffix.lower()
        mime_types = {
            ".jpg":  "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png":  "image/png",
            ".webp": "image/webp",
            ".gif":  "image/gif"
        }
        mime_type = mime_types.get(extension, "image/jpeg")
        with open(ruta_imagen, "rb") as f:
            datos = base64.b64encode(f.read()).decode("utf-8")
        return datos, mime_type

    def analizar_imagen(self, ruta_imagen: str) -> dict:
        """
        Analiza una imagen con Gemini y retorna los 9 atributos.
        Versión actual (prototipo) — funciona sin modelo entrenado.
        """
        print(f"  🔍 Analizando imagen con Gemini: {ruta_imagen}")

        imagen_b64, mime_type = self._imagen_a_base64(ruta_imagen)

        payload = {
            "contents": [{
                "parts": [
                    {"text": self.PROMPT},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data":      imagen_b64
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature":     0.1,
                "topP":            0.8,
                "maxOutputTokens": 2048
            }
        }

        url = f"{self.GEMINI_URL}?key={self.api_key}"
        response = httpx.post(url, json=payload, timeout=60.0)
        response.raise_for_status()
        data = response.json()

        texto = data["candidates"][0]["content"]["parts"][0]["text"]
        texto = texto.strip()

        # Limpiar markdown si Gemini lo agrega
        if "```" in texto:
            partes = texto.split("```")
            for parte in partes:
                if "{" in parte:
                    texto = parte
                    if texto.startswith("json"):
                        texto = texto[4:]
                    break

        # Extraer solo el JSON entre llaves
        inicio = texto.find("{")
        fin    = texto.rfind("}") + 1
        if inicio != -1 and fin > inicio:
            texto = texto[inicio:fin]

        texto = texto.strip()
        print(f"  📝 Respuesta Gemini: {texto}")

        atributos = json.loads(texto)
        print(f"  ✅ Atributos extraídos: {atributos}")
        return atributos

    def analizar_imagen_tm(self, ruta_imagen: str, clf=None) -> dict:
        """
        Analiza una imagen con Teachable Machine (.tflite) y retorna los 9 atributos.
        Versión producción — requiere model/model.tflite y model/labels.txt.

        clf: instancia de TeachableMachineClassifier ya cargada (opcional).
             Si se pasa, evita recargar el modelo en cada llamada.

        Si el modelo no está disponible, hace fallback automático a Gemini.
        """
        try:
            if clf is None:
                from vision.tm_classifier import TeachableMachineClassifier
                clf = TeachableMachineClassifier()
            return clf.analizar_imagen(ruta_imagen)
        except FileNotFoundError as e:
            print(f"  ⚠ Modelo TM no disponible, usando Gemini como fallback...")
            print(f"  ⚠ Detalle: {e}")
            return self.analizar_imagen(ruta_imagen)

    def analizar_y_clasificar(self, ruta_imagen: str) -> dict:
        """
        Flujo completo con Gemini: imagen → atributos → sistema experto → decisión.
        """
        import sys
        import os
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

    def analizar_y_clasificar_tm(self, ruta_imagen: str, clf=None) -> dict:
        """
        Flujo completo con Teachable Machine: imagen → atributos → sistema experto → decisión.

        clf: instancia de TeachableMachineClassifier ya cargada (opcional).
             Si se pasa, el modelo no se recarga en cada clasificación — mucho más rápido.
        """
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        from expert_system.inference_engine import InferenceEngine
        from expert_system.explanation import ExplanationReport

        atributos = self.analizar_imagen_tm(ruta_imagen, clf=clf)

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
        return f"AttributeExtractor(Gemini API, key={'configurada' if self.api_key else 'NO configurada'})"


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python3 vision/attribute_extractor.py <ruta_imagen>")
        print("Ejemplo: python3 vision/attribute_extractor.py foto.jpg")
        sys.exit(1)

    ruta = sys.argv[1]
    extractor = AttributeExtractor()
    resultado = extractor.analizar_y_clasificar(ruta)

    print(f"\n{'═'*60}")
    print(f"  RESULTADO FINAL: {resultado['conclusion']}")
    print(f"  CONFIANZA:       {resultado['confianza']*100:.1f}%")
    print(f"  COMPUERTA:       {resultado['hardware']['compuerta']}")
    print(f"{'═'*60}")