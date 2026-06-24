# vision/camera.py
# Módulo de captura de imagen en tiempo real
# Modo demo: ESPACIO activa cuenta regresiva → captura → clasifica
# Flujo: TM (contexto) → Gemini (análisis) → SE (decisión) · fallback TM+OpenCV
# En producción: sensor ultrasónico reemplaza el ESPACIO

import cv2
import os
import time
import threading
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

        # En macOS, isOpened() puede ser True aunque el SO bloquee el acceso
        # por permisos: el primer read() devuelve ret=False. Detectarlo aquí
        # evita que el bucle de modo_demo termine en silencio.
        ret, _ = self.cap.read()
        if not ret:
            self.cap.release()
            self.cap = None
            raise RuntimeError(
                "La cámara se abrió pero no entrega imágenes (ret=False).\n"
                "  → En macOS, ve a Ajustes del Sistema → Privacidad y Seguridad → Cámara\n"
                "    y habilita el permiso para tu Terminal/IDE. Luego reinicia la Terminal."
            )

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

    def modo_demo(self, extractor=None, tm_classifier=None, cuenta_regresiva=1):
        """
        Modo demo para presentaciones y pruebas.
        ESPACIO → cuenta regresiva → captura → análisis → resultado

        Tres destinos posibles:
        - VIDRIO    → compuerta izquierda
        - PLASTICO  → compuerta derecha
        - Resto     → tacho general (con botones P/V para corregir si hay error)

        Corrección manual en pantalla de resultado:
        - P → corregir a PLÁSTICO
        - V → corregir a VIDRIO

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
        if tm_classifier:
            print("  🤖 Flujo híbrido: TM (contexto) → Gemini (análisis) → SE (decisión)")
        else:
            print("  🔮 Modo Gemini puro — sin modelo TM disponible")
        print("  P/V: Corregir resultado  |  Q: Salir\n")

        PREVIEW    = "preview"
        COUNTDOWN  = "countdown"
        ANALIZANDO = "analizando"
        RESULTADO  = "resultado"

        estado           = PREVIEW
        tiempo_countdown = None
        ultimo_resultado = None
        tiempo_resultado = None
        frame_capturado  = None
        ruta_analisis    = None
        hilo_analisis    = None
        resultado_hilo   = [None]
        progreso_texto   = ["Analizando imagen   ",
                            "Analizando imagen.  ",
                            "Analizando imagen.. ",
                            "Analizando imagen..."]
        progreso_idx    = 0
        tiempo_progreso = time.time()

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
                           "ESPACIO: Clasificar  |  P/V: Corregir  |  Q: Salir",
                           (10, h - 18),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                           (180, 180, 180), 1)

            # ── COUNTDOWN ────────────────────────────────────────
            elif estado == COUNTDOWN:
                transcurrido  = ahora - tiempo_countdown
                cuenta_actual = cuenta_regresiva - int(transcurrido)

                self._barra_inferior(frame, h, w)

                if cuenta_actual > 0:
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
                    frame_capturado = frame.copy()
                    ruta_analisis   = self.capturar_foto()
                    estado          = ANALIZANDO
                    progreso_idx    = 0
                    tiempo_progreso = ahora
                    # Lanzar el análisis en un hilo separado para que la
                    # barra de progreso animada no se congele mientras
                    # Gemini / TM responden.
                    if extractor:
                        resultado_hilo = [None]
                        def _run_analisis(ruta=ruta_analisis):
                            resultado_hilo[0] = self._analizar(
                                extractor, ruta, tm_classifier=tm_classifier)
                        hilo_analisis = threading.Thread(
                            target=_run_analisis, daemon=True)
                        hilo_analisis.start()
                    else:
                        hilo_analisis = None

            # ── ANALIZANDO ────────────────────────────────────────
            elif estado == ANALIZANDO:
                if frame_capturado is not None:
                    frame = frame_capturado.copy()

                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)

                if ahora - tiempo_progreso > 0.4:
                    progreso_idx    = (progreso_idx + 1) % 4
                    tiempo_progreso = ahora

                cv2.putText(frame,
                           progreso_texto[progreso_idx],
                           (w//2 - 190, h//2),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                           (0, 255, 255), 3)

                barra_total = w - 200
                barra_fill  = int((ahora % 2) / 2 * barra_total)
                cv2.rectangle(frame, (100, h//2 + 40),
                             (100 + barra_total, h//2 + 60),
                             (50, 50, 50), -1)
                cv2.rectangle(frame, (100, h//2 + 40),
                             (100 + barra_fill, h//2 + 60),
                             (0, 255, 255), -1)

                # Transición a RESULTADO cuando el hilo termine
                if hilo_analisis is not None and not hilo_analisis.is_alive():
                    ultimo_resultado = resultado_hilo[0]
                    estado           = RESULTADO
                    tiempo_resultado = time.time()
                    hilo_analisis    = None
                elif hilo_analisis is None:
                    # Sin extractor — pasar directamente
                    estado           = RESULTADO
                    tiempo_resultado = time.time()

            # ── RESULTADO ─────────────────────────────────────────
            elif estado == RESULTADO:
                if frame_capturado is not None:
                    frame = frame_capturado.copy()

                self._dibujar_resultado(frame, h, w, ultimo_resultado)

                restante = max(0, 5.0 - (ahora - tiempo_resultado))
                cv2.putText(frame,
                           f"Siguiente en {restante:.0f}s  |  ESPACIO: nuevo  |  P/V: corregir",
                           (10, h - 18),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5,
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
                    estado           = COUNTDOWN
                    tiempo_countdown = time.time()
                    print("\n  ⏳ Iniciando cuenta regresiva...")

            elif key == ord('p') or key == ord('P'):
                if estado == RESULTADO and ultimo_resultado:
                    ultimo_resultado["conclusion"]               = "PLASTICO"
                    ultimo_resultado["hardware"]["compuerta"]    = "derecha"
                    ultimo_resultado["hardware"]["led"]          = "verde"
                    ultimo_resultado["hardware"]["angulo_servo"] = 135
                    ultimo_resultado["hardware"]["mensaje"]      = "PLÁSTICO — corregido manualmente"
                    tiempo_resultado = time.time()
                    print("  ✏️  Corregido manualmente → PLASTICO")

            elif key == ord('v') or key == ord('V'):
                if estado == RESULTADO and ultimo_resultado:
                    ultimo_resultado["conclusion"]               = "VIDRIO"
                    ultimo_resultado["hardware"]["compuerta"]    = "izquierda"
                    ultimo_resultado["hardware"]["led"]          = "azul"
                    ultimo_resultado["hardware"]["angulo_servo"] = 45
                    ultimo_resultado["hardware"]["mensaje"]      = "VIDRIO — corregido manualmente"
                    tiempo_resultado = time.time()
                    print("  ✏️  Corregido manualmente → VIDRIO")

        self.detener()

    def _barra_inferior(self, frame, h, w):
        """Fondo semitransparente en la parte inferior."""
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - 50), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    def _dibujar_resultado(self, frame, h, w, resultado):
        """
        Dibuja el resultado sobre el frame.

        VIDRIO   → texto naranja, compuerta izquierda
        PLASTICO → texto verde, compuerta derecha
        Resto    → texto rojo, tacho general + botones P/V para corregir
        """
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
            "ORGANICO":    (  0,   0, 255),
            "LATA":        (  0,   0, 255),
            "DESCONOCIDO": (  0,   0, 255)
        }
        color = colores.get(conclusion, (0, 0, 255))

        # ── Categoría — texto grande centrado ────────────────────
        tam = cv2.getTextSize(conclusion,
                              cv2.FONT_HERSHEY_SIMPLEX, 3.5, 8)[0]
        x   = (w - tam[0]) // 2
        cv2.putText(frame, conclusion,
                   (x, h//2 - 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 3.5,
                   color, 8)

        # ── Confianza ─────────────────────────────────────────────
        texto_conf = f"Confianza: {confianza*100:.1f}%"
        tam2 = cv2.getTextSize(texto_conf,
                               cv2.FONT_HERSHEY_SIMPLEX, 1.1, 2)[0]
        x2   = (w - tam2[0]) // 2
        cv2.putText(frame, texto_conf,
                   (x2, h//2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.1,
                   (255, 255, 255), 2)

        # ── Destino del objeto ────────────────────────────────────
        if compuerta != "ninguna":
            # VIDRIO o PLASTICO — mostrar compuerta
            texto_comp = f"Compuerta: {compuerta.upper()}"
            tam3 = cv2.getTextSize(texto_comp,
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            x3   = (w - tam3[0]) // 2
            cv2.putText(frame, texto_comp,
                       (x3, h//2 + 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                       color, 2)
        else:
            # Tacho general — mostrar destino claramente
            texto_tg = "DEPOSITAR EN TACHO GENERAL"
            tam4 = cv2.getTextSize(texto_tg,
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
            x4   = (w - tam4[0]) // 2
            cv2.putText(frame, texto_tg,
                       (x4, h//2 + 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                       (0, 0, 255), 2)

            # Submensaje más pequeño
            tam5 = cv2.getTextSize(mensaje,
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
            x5   = (w - tam5[0]) // 2
            cv2.putText(frame, mensaje,
                       (x5, h//2 + 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                       (180, 180, 180), 1)

        # ── Hint de corrección — SIEMPRE visible ─────────────────
        # Permite corregir tanto si fue a compuerta como a tacho general
        hint = "Incorrecto?  P = Plastico  |  V = Vidrio"
        tam_h = cv2.getTextSize(hint, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)[0]
        x_h   = (w - tam_h[0]) // 2
        cv2.putText(frame, hint,
                   (x_h, h//2 + 125),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                   (150, 150, 150), 1)

        # ── Barra de confianza ────────────────────────────────────
        barra_w = int((w - 200) * confianza)
        cv2.rectangle(frame, (100, h - 45),
                     (w - 100, h - 25),
                     (50, 50, 50), -1)
        cv2.rectangle(frame, (100, h - 45),
                     (100 + barra_w, h - 25),
                     color, -1)

    def _analizar(self, extractor, ruta, tm_classifier=None):
        """
        Flujo híbrido TM + Gemini + Sistema Experto:
        - TM corre siempre como contexto inicial
        - Gemini analiza siempre la imagen visualmente
        - El sistema experto toma la decisión final

        Si Gemini falla (sin internet, rate limit), se usa TM solo como fallback.
        """
        try:
            resultado = extractor.analizar_y_clasificar_hibrido(
                ruta, clf=tm_classifier)

            conclusion = resultado["conclusion"]
            hardware   = resultado["hardware"]

            print(f"\n  {'═'*50}")
            print(f"  RESULTADO : {conclusion}")
            print(f"  DESTINO   : {hardware['compuerta'] if hardware['compuerta'] != 'ninguna' else 'tacho general'}")
            print(f"  MENSAJE   : {hardware['mensaje']}")
            print(f"  {'═'*50}\n")
            return resultado

        except Exception as e:
            err = str(e).lower()
            if "429" in err or "quota" in err or "rate" in err:
                print("  ⚠ Rate limit Gemini — usando TM como fallback")
            elif "503" in err or "500" in err or "unavailable" in err or "timeout" in err:
                print("  ⚠ Gemini no disponible — usando TM como fallback")
            else:
                print(f"  ⚠ Error en análisis ({e.__class__.__name__}: {e}) — usando TM como fallback")
            try:
                resultado = extractor.analizar_y_clasificar_tm(
                    ruta, clf=tm_classifier)
                return resultado
            except Exception as e2:
                print(f"  ❌ Fallback TM también falló: {e2}")
            return None

    def capturar_y_clasificar(self, extractor, tm_classifier=None, delay=2):
        """Para Raspberry Pi + sensor ultrasónico."""
        if not self.cap or not self.cap.isOpened():
            self.iniciar()
        print(f"  ⏳ Capturando en {delay} segundos...")
        time.sleep(delay)
        ruta = self.capturar_foto()
        return self._analizar(extractor, ruta, tm_classifier=tm_classifier)

    def detener(self):
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
    from vision.tm_classifier import TeachableMachineClassifier

    print("\n" + "█"*50)
    print("  RECI — SISTEMA DE RECICLAJE INTELIGENTE")
    print("█"*50)

    extractor = AttributeExtractor()

    tm_classifier = None
    try:
        tm_classifier = TeachableMachineClassifier()
        print("  🤖 Modo: TM (contexto) → Gemini (análisis) → SE (decisión)")
    except FileNotFoundError:
        print("  🔮 Modo: Solo Gemini")

    camara = Camera()

    try:
        camara.modo_demo(
            extractor=extractor,
            tm_classifier=tm_classifier,
            cuenta_regresiva=1
        )
    except KeyboardInterrupt:
        print("\n  Interrumpido por el usuario")
    except RuntimeError as e:
        print(f"\n  ❌ {e}")
    finally:
        camara.detener()