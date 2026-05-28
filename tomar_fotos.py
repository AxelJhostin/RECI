# tomar_fotos.py
# Toma fotos rápidas con la cámara para el dataset de RECI
# Uso: python3 tomar_fotos.py plastico
#      python3 tomar_fotos.py vidrio

import cv2
import os
import sys
from datetime import datetime

if len(sys.argv) < 2:
    print("Uso: python3 tomar_fotos.py <clase>")
    print("Ejemplo: python3 tomar_fotos.py plastico")
    sys.exit(1)

CLASE     = sys.argv[1]
CARPETA   = f"fotos_dataset/{CLASE}"
os.makedirs(CARPETA, exist_ok=True)

cap     = cv2.VideoCapture(0)
contador = len(os.listdir(CARPETA))

print(f"Tomando fotos para clase: {CLASE}")
print(f"Fotos existentes: {contador}")
print(f"Guardando en: {CARPETA}")
print()
print("CONTROLES:")
print("  ESPACIO  → tomar foto")
print("  H        → tomar 10 fotos rápidas seguidas")
print("  Q        → salir")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Mostrar contador en pantalla
    cv2.putText(frame, f"Clase: {CLASE} | Fotos: {contador}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, "ESPACIO=foto | H=10 rapidas | Q=salir",
                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
    cv2.imshow(f"RECI Dataset — {CLASE}", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    elif key == ord(' '):
        # Una foto
        nombre = f"{CARPETA}/{CLASE}_{contador:04d}.jpg"
        cv2.imwrite(nombre, frame)
        contador += 1
        print(f"  Foto {contador} guardada")

    elif key == ord('h'):
        # 10 fotos rápidas
        print(f"  Tomando 10 fotos rápidas...")
        for i in range(10):
            ret, frame2 = cap.read()
            nombre = f"{CARPETA}/{CLASE}_{contador:04d}.jpg"
            cv2.imwrite(nombre, frame2)
            contador += 1
        print(f"  10 fotos guardadas — total: {contador}")

cap.release()
cv2.destroyAllWindows()
print(f"\nListo — {contador} fotos en {CARPETA}/")
print(f"Sube la carpeta {CARPETA}/ a Drive en:")
print(f"  Mi unidad/data set axel 1/separados/{CLASE}/")# tomar_fotos.py
# Toma fotos rápidas con la cámara para el dataset de RECI
# Uso: python3 tomar_fotos.py plastico
#      python3 tomar_fotos.py vidrio

import cv2
import os
import sys
from datetime import datetime

if len(sys.argv) < 2:
    print("Uso: python3 tomar_fotos.py <clase>")
    print("Ejemplo: python3 tomar_fotos.py plastico")
    sys.exit(1)

CLASE     = sys.argv[1]
CARPETA   = f"fotos_dataset/{CLASE}"
os.makedirs(CARPETA, exist_ok=True)

cap     = cv2.VideoCapture(0)
contador = len(os.listdir(CARPETA))

print(f"Tomando fotos para clase: {CLASE}")
print(f"Fotos existentes: {contador}")
print(f"Guardando en: {CARPETA}")
print()
print("CONTROLES:")
print("  ESPACIO  → tomar foto")
print("  H        → tomar 10 fotos rápidas seguidas")
print("  Q        → salir")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Mostrar contador en pantalla
    cv2.putText(frame, f"Clase: {CLASE} | Fotos: {contador}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, "ESPACIO=foto | H=10 rapidas | Q=salir",
                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
    cv2.imshow(f"RECI Dataset — {CLASE}", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    elif key == ord(' '):
        # Una foto
        nombre = f"{CARPETA}/{CLASE}_{contador:04d}.jpg"
        cv2.imwrite(nombre, frame)
        contador += 1
        print(f"  Foto {contador} guardada")

    elif key == ord('h'):
        # 10 fotos rápidas
        print(f"  Tomando 10 fotos rápidas...")
        for i in range(10):
            ret, frame2 = cap.read()
            nombre = f"{CARPETA}/{CLASE}_{contador:04d}.jpg"
            cv2.imwrite(nombre, frame2)
            contador += 1
        print(f"  10 fotos guardadas — total: {contador}")

cap.release()
cv2.destroyAllWindows()
print(f"\nListo — {contador} fotos en {CARPETA}/")
print(f"Sube la carpeta {CARPETA}/ a Drive en:")
print(f"  Mi unidad/data set axel 1/separados/{CLASE}/")