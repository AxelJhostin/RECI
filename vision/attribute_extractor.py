# vision/attribute_extractor.py
# Extractor de atributos visuales usando Google Gemini
# Analiza imágenes y extrae los atributos que necesita el sistema experto
# Módulo temporal — será reemplazado por MobileNet v2 entrenado

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
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif"
        }
        mime_type = mime_types.get(extension, "image/jpeg")
        with open(ruta_imagen, "rb") as f:
            datos = base64.b64encode(f.read()).decode("utf-8")
        return datos, mime_type

    def analizar_imagen(self, ruta_imagen: str) -> dict:
        """
        Analiza una imagen y retorna los atributos del objeto.
        """
        print(f"  🔍 Analizando imagen: {ruta_imagen}")

        # Convertir imagen a base64
        imagen_b64, mime_type = self._imagen_a_base64(ruta_imagen)

        # Construir payload para Gemini
        payload = {
            "contents": [{
                "parts": [
                    {"text": self.PROMPT},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": imagen_b64
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

        # Llamar a Gemini API
        url = f"{self.GEMINI_URL}?key={self.api_key}"
        response = httpx.post(
            url,
            json=payload,
            timeout=60.0
        )
        response.raise_for_status()
        data = response.json()

        # Extraer texto de respuesta
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

        # Parsear JSON
        atributos = json.loads(texto)
        print(f"  ✅ Atributos extraídos: {atributos}")
        return atributos

    def analizar_y_clasificar(self, ruta_imagen: str) -> dict:
        """
        Flujo completo: imagen → atributos → sistema experto → decisión.
        """
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        from expert_system.inference_engine import InferenceEngine
        from expert_system.explanation import ExplanationReport

        # 1. Extraer atributos con Gemini
        atributos = self.analizar_imagen(ruta_imagen)

        # 2. Pasar al sistema experto
        engine = InferenceEngine()
        engine.cargar_hechos(atributos)
        conclusion, confianza, reglas = engine.ejecutar()

        # 3. Generar reporte
        reporte = ExplanationReport(engine)

        # 4. Mostrar resultado
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