#!/usr/bin/env python3
"""
Estima tokens y costo USD por petición a Gemini en el flujo RECI.
Uso:
  python3 scripts/estimar_costo_gemini.py
  python3 scripts/estimar_costo_gemini.py images/prueba10.jpeg
  python3 scripts/estimar_costo_gemini.py --peticiones 500
"""

import argparse
import base64
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vision.attribute_extractor import AttributeExtractor

# Precios gemini-2.5-flash tier pago (USD por 1M tokens)
# Fuente: https://ai.google.dev/gemini-api/docs/pricing
PRECIO_INPUT  = 0.30
PRECIO_OUTPUT = 2.50

IMAGEN_DEFAULT = ROOT / "images" / "prueba1.jpeg"


def estimar_tokens_imagen(ancho: int, alto: int) -> int:
    """Aproximación Google: ~258 tokens por tile 768×768."""
    tiles_w = max(1, (ancho + 767) // 768)
    tiles_h = max(1, (alto + 767) // 768)
    return tiles_w * tiles_h * 258


def construir_prompt(clase_tm: str = "plastico", prob_tm: float = 0.99) -> str:
    contexto = (
        f"\nCONTEXTO DEL CLASIFICADOR RÁPIDO (MobileNetV2):\n"
        f"El modelo detectó '{clase_tm}' con {prob_tm:.0%} de confianza.\n"
        f"Úsalo como referencia inicial, pero confía en tu análisis visual "
        f"si ves algo diferente — especialmente en material, brillo de tapa y textura.\n"
    )
    return AttributeExtractor.PROMPT_BASE.replace(
        "REGLAS DE ANÁLISIS:", contexto + "\nREGLAS DE ANÁLISIS:"
    )


def analizar(ruta_imagen: Path, peticiones: int):
    if not ruta_imagen.exists():
        print(f"❌ No existe: {ruta_imagen}")
        sys.exit(1)

    raw = ruta_imagen.read_bytes()
    b64 = base64.b64encode(raw).decode()
    prompt = construir_prompt()

    # Dimensiones vía OpenCV si está disponible
    ancho, alto = 1280, 720
    try:
        import cv2
        img = cv2.imread(str(ruta_imagen))
        if img is not None:
            alto, ancho = img.shape[:2]
    except ImportError:
        pass

    prompt_tokens = len(prompt) // 4
    image_tokens  = estimar_tokens_imagen(ancho, alto)
    output_tokens = 130  # JSON típico RECI
    input_total   = prompt_tokens + image_tokens

    costo_uno = (
        input_total * PRECIO_INPUT / 1_000_000
        + output_tokens * PRECIO_OUTPUT / 1_000_000
    )

    print("=" * 60)
    print("  RECI — Estimación de costo Gemini (gemini-2.5-flash)")
    print("=" * 60)
    print(f"\n  Imagen          : {ruta_imagen.name}")
    print(f"  Tamaño archivo  : {len(raw) / 1024:.1f} KB")
    print(f"  Resolución      : {ancho}×{alto} px")
    print(f"  Base64 en JSON  : {len(b64) / 1024:.1f} KB")
    print()
    print("  ── Qué envía el TM a Gemini ──")
    print("  Solo texto en el prompt:")
    print("    • clase_tm  → 'plastico' o 'vidrio'")
    print("    • prob_tm   → ej. 99%")
    print("  NO envía: MAPA_CLASES, atributos TM, reglas del SE")
    print("  La imagen JPG completa va aparte en inline_data (base64)")
    print()
    print("  ── Tokens estimados ──")
    print(f"    Prompt (~{len(prompt)} chars) : ~{prompt_tokens:,}")
    print(f"    Imagen ({ancho}×{alto})       : ~{image_tokens:,}")
    print(f"    Entrada total                 : ~{input_total:,}")
    print(f"    Salida JSON (max 256)         : ~{output_tokens:,}")
    print()
    print("  ── Costo tier pago ──")
    print(f"    Por petición  : ${costo_uno:.6f}  ({costo_uno * 100:.4f} centavos USD)")
    for n in [50, 100, 500, 1000, 2000]:
        print(f"    {n:>5} fotos    : ${costo_uno * n:.3f}")
    if peticiones != 100:
        print(f"    {peticiones:>5} fotos    : ${costo_uno * peticiones:.3f}  (tu --peticiones)")
    print()
    print("  Nota: tier gratuito = $0 hasta límites diarios (~1 500 req/día")
    print("        con billing vinculado). Ver docs/FLUJO_RECONOCIMIENTO.md")
    print("=" * 60)

    # Verificar API key si existe .env
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("GEMINI_API_KEY=") and len(line) > 20:
                print("\n  ✅ GEMINI_API_KEY encontrada en .env")
                return
    print("\n  ⚠ GEMINI_API_KEY no configurada — copia .env.example → .env")


def main():
    parser = argparse.ArgumentParser(description="Estimar costo Gemini por petición RECI")
    parser.add_argument("imagen", nargs="?", default=str(IMAGEN_DEFAULT),
                        help="Ruta a imagen de prueba (default: images/prueba1.jpeg)")
    parser.add_argument("--peticiones", type=int, default=100,
                        help="Número de peticiones para mostrar costo total")
    args = parser.parse_args()
    analizar(Path(args.imagen), args.peticiones)


if __name__ == "__main__":
    main()
