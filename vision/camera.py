# vision/camera.py
# Módulo de captura de imagen en tiempo real
# Modo demo: ESPACIO activa cuenta regresiva → captura → clasifica
# En producción: sensor ultrasónico reemplaza el ESPACIO

import cv2
import os
import time
import numpy as np
from pathlib import Path
from datetime import datetime


class Camera:

    def __init__(self, camara_index=0, carpeta_capturas="images/capturas"):
        self.camara_index = camara_index
        self.carpeta      = Path(carpeta_capturas)
        self.carpeta.mkdir(parents=True, exist_ok=True)
        self.cap          = None

    def iniciar(self):
        self.cap = cv2.VideoCapture(self.camara_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"No se pudo abrir la cámara {self.camara_index}.")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        print("  📷 Cámara iniciada correctamente")

    def capturar_foto(self, nombre=None):
        if not self.cap or not self.cap.isOpened():
            self.iniciar()
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("No se pudo capturar imagen")
        if not nombre:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre = f"captura_{timestamp}.jpg"
        ruta = self.carpeta / nombre
        cv2.imwrite(str(ruta), frame)
        print(f"  📸 Foto guardada: {ruta}")
        return str(ruta)

    def modo_demo(self, extractor=None, cuenta_regresiva=3):
        """
        Modo demo para presentaciones y pruebas.
        ESPACIO → cuenta regresiva → captura → análisis → resultado
        En producción: sensor ultrasónico reemplaza el ESPACIO.
        """
        if not self.cap or not self.cap.isOpened():
            self.iniciar()

        print("\n  📷 MODO DEMO ACTIVO")
        print("  ─────────────────────────────────────────")
        print("  1. Coloca el objeto frente a la cámara")
        print("  2. Presiona ESPACIO para clasificar")
        print("  3. Espera el resultado")
        print("  ─────────────────────────────────────────")
        print("  Q → Salir\n")

        PREVIEW   = "preview"
        COUNTDOWN = "countdown"
        ANALIZANDO = "analizando"
        RESULTADO  = "resultado"

        estado           = PREVIEW
        tiempo_countdown = None
        ultimo_resultado = None
        tiempo_resultado = None
        frame_capturado  = None
        progreso_texto   = ["Analizando imagen   ",
                            "Analizando imagen.  ",
                            "Analizando imagen.. ",
                            "Analizando imagen..."]
        progreso_idx     = 0
        tiempo_progreso  = time.time()

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            h, w = frame.shape[:2]
            ahora = time.time()

            # ── PREVIEW ──────────────────────────────────────────
            if estado == PREVIEW:
                self._barra_inferior(frame, h, w)
                cv2.putText(frame,
                           "Coloca el objeto y presiona ESPACIO",
                           (w//2 - 290, h//2),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.85,
                           (255, 255, 255), 2)
                cv2.putText(frame,
                           "ESPACIO: Clasificar  |  Q: Salir",
                           (10, h - 18),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                           (180, 180, 180), 1)

            # ── COUNTDOWN ────────────────────────────────────────
            elif estado == COUNTDOWN:
                transcurrido  = ahora - tiempo_countdown
                cuenta_actual = cuenta_regresiva - int(transcurrido)

                self._barra_inferior(frame, h, w)

                if cuenta_actual > 0:
                    # Número grande centrado
                    cv2.putText(frame, str(cuenta_actual),
                               (w//2 - 45, h//2 + 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 6,
                               (0, 255, 255), 10)
                    cv2.putText(frame,
                               "Mantén el objeto quieto...",
                               (w//2 - 210, h//2 - 80),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.85,
                               (255, 255, 0), 2)
                else:
                    # Capturar sin flash
                    frame_capturado = frame.copy()
                    ruta = self.capturar_foto()
                    estado = ANALIZANDO
                    progreso_idx   = 0
                    tiempo_progreso = ahora

                    # Analizar en segundo plano
                    if extractor:
                        print("\n  🔍 Analizando objeto...")
                        ultimo_resultado = self._analizar(extractor, ruta)

                    estado         = RESULTADO
                    tiempo_resultado = time.time()

            # ── ANALIZANDO ────────────────────────────────────────
            elif estado == ANALIZANDO:
                # Mostrar frame congelado con indicador de progreso
                if frame_capturado is not None:
                    frame = frame_capturado.copy()

                # Overlay oscuro
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)

                # Texto animado de progreso
                if ahora - tiempo_progreso > 0.4:
                    progreso_idx   = (progreso_idx + 1) % 4
                    tiempo_progreso = ahora

                cv2.putText(frame,
                           progreso_texto[progreso_idx],
                           (w//2 - 190, h//2),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                           (0, 255, 255), 3)

                # Barra de progreso animada
                barra_total = w - 200
                barra_fill  = int((ahora % 2) / 2 * barra_total)
                cv2.rectangle(frame, (100, h//2 + 40),
                             (100 + barra_total, h//2 + 60),
                             (50, 50, 50), -1)
                cv2.rectangle(frame, (100, h//2 + 40),
                             (100 + barra_fill, h//2 + 60),
                             (0, 255, 255), -1)

            # ── RESULTADO ─────────────────────────────────────────
            elif estado == RESULTADO:
                # Mostrar frame congelado de fondo
                if frame_capturado is not None:
                    frame = frame_capturado.copy()

                self._dibujar_resultado(frame, h, w, ultimo_resultado)

                # Countdown para volver a preview
                restante = max(0, 5.0 - (ahora - tiempo_resultado))
                cv2.putText(frame,
                           f"Siguiente en {restante:.0f}s  |  ESPACIO: nuevo",
                           (10, h - 18),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                           (180, 180, 180), 1)

                if ahora - tiempo_resultado > 5.0:
                    estado = PREVIEW
                    print("\n  🔄 Listo para siguiente objeto")
                    print("  Presiona ESPACIO para clasificar\n")

            cv2.imshow("RECI — Sistema de Reciclaje Inteligente", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("  👋 Saliendo...")
                break
            elif key == ord(' '):
                if estado == PREVIEW:
                    estado           = COUNTDOWN
                    tiempo_countdown = time.time()
                    print("\n  ⏳ Iniciando cuenta regresiva...")
                elif estado == RESULTADO:
                    # Permitir nueva captura antes de los 5 segundos
                    estado           = COUNTDOWN
                    tiempo_countdown = time.time()
                    print("\n  ⏳ Iniciando cuenta regresiva...")

        self.detener()

    def _barra_inferior(self, frame, h, w):
        """Fondo semitransparente en la parte inferior."""
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - 50), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    def _dibujar_resultado(self, frame, h, w, resultado):
        """Dibuja el resultado grande y claro sobre el frame."""

        # Overlay oscuro
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

        if not resultado:
            cv2.putText(frame, "ERROR — Intenta de nuevo",
                       (w//2 - 220, h//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                       (0, 0, 255), 3)
            return

        conclusion = resultado["conclusion"]
        confianza  = resultado["confianza"]
        compuerta  = resultado["hardware"]["compuerta"]
        mensaje    = resultado["hardware"]["mensaje"]

        colores = {
            "VIDRIO":      (255, 150,   0),
            "PLASTICO":    (  0, 220,   0),
            "ORGANICO":    (  0, 220, 220),
            "LATA":        (  0,  80, 255),
            "DESCONOCIDO": (150, 150, 150)
        }
        color = colores.get(conclusion, (150, 150, 150))

        # Categoría — texto grande centrado
        tam = cv2.getTextSize(conclusion,
                              cv2.FONT_HERSHEY_SIMPLEX, 3.5, 8)[0]
        x   = (w - tam[0]) // 2
        cv2.putText(frame, conclusion,
                   (x, h//2 - 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 3.5,
                   color, 8)

        # Confianza
        texto_conf = f"Confianza: {confianza*100:.1f}%"
        tam2 = cv2.getTextSize(texto_conf,
                               cv2.FONT_HERSHEY_SIMPLEX, 1.1, 2)[0]
        x2   = (w - tam2[0]) // 2
        cv2.putText(frame, texto_conf,
                   (x2, h//2 + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.1,
                   (255, 255, 255), 2)

        # Compuerta o mensaje
        if compuerta != "ninguna":
            texto_comp = f"Compuerta: {compuerta.upper()}"
            tam3 = cv2.getTextSize(texto_comp,
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            x3   = (w - tam3[0]) // 2
            cv2.putText(frame, texto_comp,
                       (x3, h//2 + 75),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                       color, 2)
        else:
            tam4 = cv2.getTextSize(mensaje,
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)[0]
            x4   = (w - tam4[0]) // 2
            cv2.putText(frame, mensaje,
                       (x4, h//2 + 75),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                       (0, 100, 255), 2)

        # Barra de confianza
        barra_w = int((w - 200) * confianza)
        cv2.rectangle(frame, (100, h - 45),
                     (w - 100, h - 25),
                     (50, 50, 50), -1)
        cv2.rectangle(frame, (100, h - 45),
                     (100 + barra_w, h - 25),
                     color, -1)

    def _analizar(self, extractor, ruta):
        """Analiza una imagen con el sistema experto."""
        try:
            resultado = extractor.analizar_y_clasificar(ruta)
            print(f"\n  {'═'*50}")
            print(f"  RESULTADO: {resultado['conclusion']}")
            print(f"  CONFIANZA: {resultado['confianza']*100:.1f}%")
            print(f"  COMPUERTA: {resultado['hardware']['compuerta']}")
            print(f"  MENSAJE  : {resultado['hardware']['mensaje']}")
            print(f"  {'═'*50}\n")
            return resultado
        except Exception as e:
            if "429" in str(e):
                print("  ⚠ Rate limit — espera unos segundos e intenta de nuevo")
            else:
                print(f"  ❌ Error al analizar: {e}")
            return None

    def capturar_y_clasificar(self, extractor, delay=2):
        """Para integración con Raspberry Pi y sensor ultrasónico."""
        if not self.cap or not self.cap.isOpened():
            self.iniciar()
        print(f"  ⏳ Capturando en {delay} segundos...")
        time.sleep(delay)
        ruta = self.capturar_foto()
        return self._analizar(extractor, ruta)

    def detener(self):
        """Libera la cámara."""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("  📷 Cámara liberada")

    def __repr__(self):
        return f"Camera(index={self.camara_index})"


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from vision.attribute_extractor import AttributeExtractor

    print("\n" + "█"*50)
    print("  RECI — SISTEMA DE RECICLAJE INTELIGENTE")
    print("█"*50)

    extractor = AttributeExtractor()
    camara    = Camera()

    try:
        camara.modo_demo(extractor=extractor, cuenta_regresiva=3)
    except KeyboardInterrupt:
        print("\n  Interrumpido por el usuario")
    finally:
        camara.detener()