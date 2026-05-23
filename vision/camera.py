# vision/camera.py
# Módulo de captura de imagen en tiempo real
# Usa la cámara de la laptop/Raspberry Pi para capturar frames
# y los pasa al extractor de atributos

import cv2
import os
import time
from pathlib import Path
from datetime import datetime


class Camera:
    """
    Maneja la captura de imágenes desde la cámara.
    Compatible con laptop (Mac/Windows) y Raspberry Pi.
    """

    def __init__(self, camara_index=0, carpeta_capturas="images/capturas"):
        """
        camara_index     : índice de la cámara (0 = cámara principal)
        carpeta_capturas : donde se guardan las fotos capturadas
        """
        self.camara_index    = camara_index
        self.carpeta         = Path(carpeta_capturas)
        self.carpeta.mkdir(parents=True, exist_ok=True)
        self.cap             = None

    def iniciar(self):
        """Inicia la cámara."""
        self.cap = cv2.VideoCapture(self.camara_index)
        if not self.cap.isOpened():
            raise RuntimeError(
                f"No se pudo abrir la cámara {self.camara_index}. "
                "Verifica que esté conectada y no esté en uso."
            )
        # Configurar resolución
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        print(f"  📷 Cámara iniciada correctamente")

    def capturar_foto(self, nombre=None):
        """
        Captura una foto y la guarda.
        Retorna la ruta del archivo guardado.
        """
        if not self.cap or not self.cap.isOpened():
            self.iniciar()

        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("No se pudo capturar imagen de la cámara")

        # Nombre del archivo
        if not nombre:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre = f"captura_{timestamp}.jpg"

        ruta = self.carpeta / nombre
        cv2.imwrite(str(ruta), frame)
        print(f"  📸 Foto guardada: {ruta}")
        return str(ruta)

    def modo_preview(self, extractor=None):
        """
        Muestra preview en tiempo real de la cámara.
        Presiona ESPACIO para capturar y clasificar.
        Presiona Q para salir.
        """
        if not self.cap or not self.cap.isOpened():
            self.iniciar()

        print("\n  📷 MODO PREVIEW ACTIVO")
        print("  ─────────────────────────────────")
        print("  ESPACIO → Capturar y clasificar")
        print("  Q       → Salir")
        print("  ─────────────────────────────────\n")

        ultimo_resultado = None

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Overlay de instrucciones en el frame
            h, w = frame.shape[:2]
            overlay = frame.copy()

            # Fondo semitransparente para texto
            cv2.rectangle(overlay, (0, h-80), (w, h), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

            cv2.putText(frame, "ESPACIO: Capturar | Q: Salir",
                       (10, h-50), cv2.FONT_HERSHEY_SIMPLEX,
                       0.7, (255, 255, 255), 2)

            # Mostrar último resultado si existe
            if ultimo_resultado:
                conclusion = ultimo_resultado["conclusion"]
                confianza  = ultimo_resultado["confianza"]
                colores = {
                    "VIDRIO":      (255, 100,   0),
                    "PLASTICO":    (  0, 200,   0),
                    "ORGANICO":    (  0, 200, 200),
                    "LATA":        (  0,   0, 255),
                    "DESCONOCIDO": (150, 150, 150)
                }
                color = colores.get(conclusion, (150, 150, 150))
                texto = f"{conclusion} ({confianza*100:.1f}%)"
                cv2.putText(frame, texto,
                           (10, h-15), cv2.FONT_HERSHEY_SIMPLEX,
                           0.8, color, 2)

            cv2.imshow("RECI — Sistema de Reciclaje Inteligente", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or key == ord('Q'):
                print("  👋 Saliendo del modo preview...")
                break

            elif key == ord(' '):
                print("\n  📸 Capturando imagen...")
                ruta = self.capturar_foto()

                if extractor:
                    print("  🔍 Analizando con sistema experto...")
                    try:
                        resultado = extractor.analizar_y_clasificar(ruta)
                        ultimo_resultado = resultado
                        print(f"\n  {'═'*50}")
                        print(f"  RESULTADO: {resultado['conclusion']}")
                        print(f"  CONFIANZA: {resultado['confianza']*100:.1f}%")
                        print(f"  COMPUERTA: {resultado['hardware']['compuerta']}")
                        print(f"  {'═'*50}\n")
                    except Exception as e:
                        print(f"  ❌ Error al analizar: {e}")
                else:
                    print(f"  ✅ Foto guardada en: {ruta}")

        self.detener()

    def capturar_y_clasificar(self, extractor, delay=2):
        """
        Captura automáticamente después de un delay y clasifica.
        Útil para modo automático sin intervención del usuario.
        """
        if not self.cap or not self.cap.isOpened():
            self.iniciar()

        print(f"  ⏳ Capturando en {delay} segundos...")
        time.sleep(delay)

        ruta = self.capturar_foto()
        resultado = extractor.analizar_y_clasificar(ruta)
        return resultado

    def detener(self):
        """Libera la cámara."""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("  📷 Cámara liberada")

    def __repr__(self):
        return f"Camera(index={self.camara_index}, carpeta={self.carpeta})"


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from vision.attribute_extractor import AttributeExtractor

    print("\n" + "█"*50)
    print("  RECI — MODO CÁMARA EN TIEMPO REAL")
    print("█"*50)

    extractor = AttributeExtractor()
    camara    = Camera()

    try:
        camara.modo_preview(extractor=extractor)
    except KeyboardInterrupt:
        print("\n  Interrumpido por el usuario")
    finally:
        camara.detener()