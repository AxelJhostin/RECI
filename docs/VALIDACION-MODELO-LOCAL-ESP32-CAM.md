# Validación y relevo — MobileNetV2 local con ESP32-CAM

**Fecha de actualización:** 23 de julio de 2026  
**Responsable:** Axel Hernández  
**Rama:** `axel/ia-sistema-experto`

Este documento reúne la evidencia disponible del modelo local para que la
persona que continúe el trabajo pueda evaluar, ajustar o reentrenar sin
perder el contexto ni contaminar los conjuntos de prueba.

## 1. Artefacto integrado

El servicio usa el MobileNetV2/TensorFlow Lite producido por el run
`RECI2/runs/run_20260721_2129`.

Archivos versionados:

- `ia/vision-service/model/model.tflite`
- `ia/vision-service/model/labels.txt`
- `ia/vision-service/model/entrenamiento_manifest.json`

Datos registrados por el entrenamiento:

| Partición | Plástico | Vidrio |
| --- | ---: | ---: |
| Entrenamiento | 13,258 | 13,043 |
| Validación | 2,343 | 2,304 |

La exactitud de validación reportada fue **98.43 %**. Esta cifra corresponde a
la distribución anterior y no representa automáticamente el rendimiento con
la ESP32-CAM.

## 2. Arquitectura híbrida actual

La ESP32-CAM toma tres fotos por residuo. Cada foto se analiza con:

1. OpenAI + heurísticas OpenCV + sistema experto.
2. MobileNetV2 local.
3. Dos votos independientes, sin ponderarlos dentro de la foto.

Esto produce seis predicciones observables sobre tres imágenes iguales. El
firmware conserva una mayoría simple de los hasta seis votos. `desconocido`
es abstención; con empate o menos de dos votos válidos, responde
`desconocido`.

El modelo local solo conoce `plastico` y `vidrio`; no puede reconocer latas,
cartón u orgánicos. Por seguridad:

- se prueba únicamente con plástico y vidrio, las clases que el TFLite conoce;
- si el TFLite no carga, continúa el flujo anterior de OpenAI;
- la decisión final requiere una mayoría y al menos dos votos válidos;
- se debe mantener una matriz de confusión con imágenes nuevas de la
  ESP32-CAM.

## 3. Resultados obtenidos

### 3.1 Dataset local anterior

Se ejecutó el TFLite sobre 4,010 imágenes locales etiquetadas:

| Material real | Correctas | Incorrectas | Exactitud |
| --- | ---: | ---: | ---: |
| Plástico | 2,008/2,010 | 2 | 99.90 % |
| Vidrio | 1,996/2,000 | 4 | 99.80 % |
| **Total** | **4,004/4,010** | **6** | **99.85 %** |

Estas fotos probablemente participaron en el entrenamiento. El resultado
confirma que el artefacto fue portado correctamente, pero no demuestra
generalización.

### 3.2 Imágenes independientes de RECI2

Sobre 15 imágenes reales etiquetadas de `RECI2/images/`, el modelo acertó
**13/15 (86.67 %)**.

Errores conocidos:

- `prueba10.jpeg`: Gatorade de vidrio clasificado como plástico con 0.930.
- `prueba12.jpeg`: Gatorade plástico clasificado como vidrio con 0.765.

El problema no es una sola dirección: la marca, la forma y la etiqueta son
parecidas mientras cambia el material. No se añadió una regla exclusiva para
Gatorade. La decisión ahora se valida con seis votos independientes: los
resultados del modelo se observan y cuentan, pero la matriz de pruebas debe
confirmar su comportamiento antes de usar el sistema con objetos fuera de
plástico y vidrio.

### 3.3 Matriz manual de seis votos

En una prueba manual de **14 objetos** etiquetados como plástico o vidrio,
se anotaron los tres resultados de OpenAI+sistema experto y los tres del
modelo local por objeto. Al contar los seis resultados sin ponderación y
tratar `desconocido` como abstención, la mayoría coincidió con la etiqueta en
**13/14 casos (92.9 %)**.

El único desacuerdo fue un objeto etiquetado como plástico cuyos cinco votos
válidos fueron vidrio. Se debe revisar visualmente esa etiqueta en la próxima
sesión antes de usarla como evidencia para entrenar. Esta matriz es pequeña y
controlada: justifica probar la política de voto, pero no sustituye una
evaluación independiente con muchas capturas ESP32-CAM.

### 3.4 Capturas reales de la ESP32-CAM

Se encontraron **201 JPEG válidos QVGA (320×240)** en la carpeta local:

```text
ia/vision-service/dataset-esp32cam/vidrio/
```

La carpeta está ignorada por Git y las fotografías **no se suben al
repositorio**. Quien trabaje en otra computadora deberá recibirlas por un
medio autorizado o repetir la captura.

Resultados del MobileNetV2:

| Ronda | Vidrio correcto | Predijo plástico | Exactitud |
| --- | ---: | ---: | ---: |
| `20260723_091721` | 1/1 | 0 | 100.0 % |
| `20260723_091754` | 77/100 | 23 | 77.0 % |
| `20260723_092325` | 63/100 | 37 | 63.0 % |
| **Total** | **141/201** | **60** | **70.15 %** |

Algunos errores tuvieron confianza alta, incluso cercana a 1.0. Por tanto,
el TFLite actual no está calibrado para decidir solo con la resolución, luz y
encuadre de la ESP32-CAM.

Todavía no existen capturas ESP32-CAM guardadas en la clase `plastico`, así
que no se puede calcular una matriz binaria completa ni concluir que el
problema afecte igual a ambas clases.

## 4. Interpretación

La diferencia entre 99.85 % en el dataset anterior y 70.15 % en vidrio
ESP32-CAM evidencia un cambio de dominio:

- cámara y óptica distintas;
- resolución QVGA;
- compresión JPEG;
- iluminación y fondos reales;
- encuadres parciales o rotados;
- pocos objetos físicos repetidos.

El modelo está integrado y ejecuta correctamente, pero necesita evaluación
balanceada y posiblemente fine-tuning. No se debe presentar 98.43 % como
precisión esperada del robot físico.

## 5. Orden recomendado para continuar

1. Conservar al menos una ronda completa de vidrio como prueba final sin
   usarla para entrenamiento.
2. Capturar plástico con la misma ESP32-CAM y condiciones comparables.
3. Agregar más objetos físicos por clase; la variedad de objetos importa más
   que miles de fotogramas casi iguales.
4. Dividir por objeto o sesión completa, no repartir aleatoriamente fotos
   consecutivas entre entrenamiento y prueba.
5. Medir por separado MobileNetV2, OpenAI y la mayoría de seis votos sobre el
   mismo conjunto.
6. Calcular matriz de confusión, precisión y recall por clase.
7. Hacer fine-tuning con las sesiones de entrenamiento, manteniendo intacto
   el conjunto reservado.
8. Repetir la evaluación reservada y comparar antes/después.
9. Ajustar abstenciones o mínimo de votos solo con evidencia y aprobación de
   Paula.

Meta sugerida para revisión con Paula: al menos 90 % por clase en un conjunto
independiente de la ESP32-CAM. La votación actual debe validarse solo con
plástico y vidrio hasta añadir una política específica para otros materiales.

## 6. Pruebas de software vigentes

- Servicio de visión híbrido: **13/13 pruebas aprobadas**.
- Sistema experto: **118/118 pruebas aprobadas**.
- Comprobación TypeScript: sin errores.

Estas pruebas protegen la integración y las reglas, pero no sustituyen la
validación con objetos y capturas nuevas.
