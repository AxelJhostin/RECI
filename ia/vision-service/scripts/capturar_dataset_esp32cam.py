#!/usr/bin/env python3
"""Captura rondas etiquetadas desde el ejemplo CameraWebServer de ESP32-CAM.

La vista previa se abre por separado en el navegador (http://IP_DE_LA_CAMARA).
Este script descarga capturas puntuales de /capture mientras la página se
actualiza con solicitudes cortas.

Uso:
    python3 scripts/capturar_dataset_esp32cam.py --camera http://192.168.100.53

Teclas:
    P  guarda una ronda en dataset/plastico/
    V  guarda una ronda en dataset/vidrio/
    Q  termina el programa
"""

import argparse
import select
import socket
import sys
import termios
import time
import tty
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.error import URLError
from urllib.request import Request, urlopen


def leer_tecla(timeout: float = 0.1) -> Optional[str]:
    """Lee una tecla sin requerir Enter; devuelve cadena vacía si no hay tecla."""
    disponibles, _, _ = select.select([sys.stdin], [], [], timeout)
    if not disponibles:
        return None
    return sys.stdin.read(1).lower()


def descargar_foto(url: str, destino: Path) -> None:
    request = Request(url, headers={"User-Agent": "Reci-dataset-capture/1.0"})
    with urlopen(request, timeout=12) as respuesta:
        contenido = respuesta.read()
        content_type = respuesta.headers.get("Content-Type", "")

    if not contenido or "image/" not in content_type:
        raise ValueError(f"La cámara no devolvió una imagen válida ({content_type or 'sin Content-Type'})")
    destino.write_bytes(contenido)


def capturar_ronda(clase: str, camera_url: str, dataset_dir: Path, cantidad: int, intervalo: float) -> None:
    carpeta = dataset_dir / clase
    carpeta.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    capturadas = 0
    siguiente = time.monotonic()

    print(f"\nRonda {clase}: {cantidad} fotos, cada {intervalo:g} s. Mantén la vista en vivo abierta.")
    for numero in range(1, cantidad + 1):
        espera = siguiente - time.monotonic()
        if espera > 0:
            time.sleep(espera)

        destino = carpeta / f"{clase}_{marca}_{numero:03d}.jpg"
        try:
            descargar_foto(camera_url, destino)
            capturadas += 1
            print(f"\r  {clase}: {capturadas}/{cantidad}  {destino.name}", end="", flush=True)
        except (URLError, socket.timeout, TimeoutError, ValueError) as error:
            print(f"\r  {clase}: error en foto {numero}/{cantidad}: {error}", flush=True)

        siguiente += intervalo

    print(f"\nRonda terminada: {capturadas}/{cantidad} fotos guardadas en {carpeta}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guarda rondas de fotos de la ESP32-CAM, etiquetadas con P/V."
    )
    parser.add_argument(
        "--camera",
        required=True,
        help="URL base de CameraWebServer, por ejemplo http://192.168.100.53",
    )
    parser.add_argument(
        "--dataset",
        default="dataset-esp32cam",
        help="Carpeta donde se crearán plastico/ y vidrio/ (predeterminado: dataset-esp32cam)",
    )
    parser.add_argument("--count", type=int, default=100, help="Fotos por ronda (predeterminado: 100)")
    parser.add_argument("--interval", type=float, default=2.0, help="Segundos entre fotos (predeterminado: 2)")
    args = parser.parse_args()

    if args.count < 1 or args.interval <= 0:
        parser.error("--count debe ser mayor que 0 y --interval debe ser mayor que 0")

    base = args.camera.rstrip("/")
    camera_url = base if base.endswith("/capture") else f"{base}/capture"
    dataset_dir = Path(args.dataset).resolve()

    if not sys.stdin.isatty():
        parser.error("Ejecuta el script desde una terminal interactiva para usar las teclas P/V/Q")

    print("\nRECI · Captura de dataset ESP32-CAM")
    print(f"Vista en vivo: {base}")
    print(f"Capturas: {camera_url}")
    print(f"Dataset: {dataset_dir}")
    print("\nP = plástico | V = vidrio | Q = salir")

    configuracion_anterior = termios.tcgetattr(sys.stdin.fileno())
    try:
        tty.setcbreak(sys.stdin.fileno())
        while True:
            tecla = leer_tecla()
            if tecla is None:
                continue
            if tecla == "q":
                print("\nCaptura finalizada.")
                return 0
            if tecla == "p":
                capturar_ronda("plastico", camera_url, dataset_dir, args.count, args.interval)
            elif tecla == "v":
                capturar_ronda("vidrio", camera_url, dataset_dir, args.count, args.interval)
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, configuracion_anterior)


if __name__ == "__main__":
    raise SystemExit(main())
