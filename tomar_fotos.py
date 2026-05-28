# tomar_fotos.py
import cv2
import os
import sys
import time

if len(sys.argv) < 2:
    print("Uso: python3 tomar_fotos.py <clase>")
    print("Ejemplo: python3 tomar_fotos.py plastico")
    sys.exit(1)

CLASE   = sys.argv[1]
CARPETA = f"fotos_dataset/{CLASE}"
os.makedirs(CARPETA, exist_ok=True)

cap      = cv2.VideoCapture(0)
contador = len(os.listdir(CARPETA))
modo_rafaga   = False
ultima_foto   = 0
INTERVALO     = 0.2   # segundos entre fotos en modo ráfaga
DURACION      = 60    # segundos que dura la ráfaga
inicio_rafaga = 0

print(f"Tomando fotos para clase: {CLASE}")
print(f"Fotos existentes: {contador}")
print(f"Guardando en: {CARPETA}")
print()
print("CONTROLES:")
print("  ESPACIO → una foto")
print("  R       → ráfaga automática (1 foto cada 2 seg durante 60 seg)")
print("  Q       → salir")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    ahora = time.time()

    # Modo ráfaga automática
    if modo_rafaga:
        tiempo_restante = int(DURACION - (ahora - inicio_rafaga))

        if tiempo_restante <= 0:
            modo_rafaga = False
            print(f"\n  Ráfaga terminada — total: {contador} fotos")
        else:
            cv2.putText(frame, f"RAFAGA ACTIVA — {tiempo_restante}s restantes",
                        (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if ahora - ultima_foto >= INTERVALO:
                nombre = f"{CARPETA}/{CLASE}_{contador:04d}.jpg"
                cv2.imwrite(nombre, frame)
                ultima_foto = ahora
                contador += 1
                print(f"  Foto {contador} — {tiempo_restante}s restantes")

    # Info en pantalla
    cv2.putText(frame, f"Clase: {CLASE} | Fotos: {contador}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, "ESPACIO=1 foto | R=rafaga 60s | Q=salir",
                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

    cv2.imshow(f"RECI Dataset — {CLASE}", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord(' '):
        nombre = f"{CARPETA}/{CLASE}_{contador:04d}.jpg"
        cv2.imwrite(nombre, frame)
        contador += 1
        print(f"  Foto {contador} guardada")
    elif key == ord('r'):
        modo_rafaga   = True
        inicio_rafaga = time.time()
        ultima_foto   = 0
        print(f"\n  Ráfaga iniciada — 30 fotos en 60 segundos, mueve el objeto!")

cap.release()
cv2.destroyAllWindows()
print(f"\nListo — {contador} fotos en {CARPETA}/")
print(f"Sube la carpeta a Drive en:")
print(f"  Mi unidad/data set axel 1/separados/{CLASE}/")