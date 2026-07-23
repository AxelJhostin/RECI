# Estado de IA y Sistema Experto — Axel Hernández

**Fecha:** 22 de julio de 2026

**Responsable:** Axel Hernández — Lead IA + Sistema Experto
**Rama de trabajo:** `axel/ia-sistema-experto`

## Objetivo del módulo

Clasificar residuos de **vidrio** y **plástico** a partir de fotos de la
ESP32-CAM, de forma conservadora: si la evidencia no es suficiente, Reci no
abre una compuerta.

El flujo actual es:

```text
ESP32-CAM → API web de Reci → servicio de visión →
proveedor de visión + heurísticas OpenCV + sistema experto →
vidrio | plastico | desconocido → Arduino Mega
```

## Trabajo completado

### Sistema experto y regresiones de RECI2

- Se revisaron RECI2 (prototipo previo) y Reci (proyecto activo).
- Se portaron al proyecto activo correcciones para Gatorade, enjuague bucal,
  atomizadores y vasos de espuma/plástico.
- Se agregaron pruebas de regresión para evitar que esas correcciones se
  pierdan con cambios posteriores.
- Resultado actual: **117/117 pruebas formales aprobadas** y **3/3 pruebas
  de heurísticas OpenCV aprobadas**.

Commits relacionados:

- `0afe372` — correcciones de ambigüedad para Gatorade.
- `8f4e44a` — correcciones para envases y vasos plásticos.

### Servicio de visión

- El servicio privado FastAPI está integrado con la API web de Reci y se
  ejecutó localmente en la Mac para desarrollo.
- La clasificación actual usa un proveedor de visión para extraer atributos
  visuales, heurísticas OpenCV y el sistema experto de 193 reglas.
- Se añadió OpenAI como proveedor opcional, sin eliminar Claude ni Gemini.
  El proveedor se elige con variables de entorno y la respuesta se exige en
  JSON estructurado antes de pasar al sistema experto.
- La integración de OpenAI tiene **2/2 pruebas unitarias sin red**.

Commit relacionado:

- `ad11ee7` — proveedor OpenAI opcional para visión.

### Validación inicial con ESP32-CAM

- Se configuró y cargó el firmware de Reci en una AI Thinker ESP32-CAM.
- La cámara se conectó a Wi-Fi, alcanzó el servicio local y tomó tres fotos
  por clasificación con voto mayoritario.
- Se confirmaron clasificaciones correctas de botellas de plástico y de
  vidrio en pruebas controladas.
- Una captura de vidrio tuvo un fallo de comunicación en la tercera foto,
  pero las dos primeras coincidieron y el voto mayoritario clasificó
  correctamente. Se debe observar este comportamiento en la siguiente
  batería de pruebas, sin cambiar reglas todavía.

## Qué no se ha hecho deliberadamente

- No se ha portado el modelo MobileNet/TFLite de RECI2 tal cual.
- No se han modificado motores, servos, pantallas, navegación ni la app.
- No se han subido claves, credenciales, redes Wi-Fi ni secretos al
  repositorio.

El modelo de RECI2 no se descarta: se evaluará con fotos de la ESP32-CAM. Si
no conserva precisión con esa cámara, se reentrenará con un dataset propio.

## Pendiente de Axel

1. Capturar y etiquetar un dataset propio de la ESP32-CAM (meta inicial:
   mínimo 500 fotos por clase, con variedad de objetos, luz, ángulos y
   fondos).
2. Crear el flujo de captura con vista en vivo para supervisar cada ronda de
   fotos mientras se guardan por clase.
3. Evaluar el modelo de RECI2 frente al dataset de la ESP32-CAM.
4. Hacer transfer learning/reentrenamiento de MobileNetV2 si la evaluación
   muestra que el modelo previo no se adapta bien a la cámara real.
5. Integrar el modelo validado dentro de `ia/vision-service` como primer
   voto, conservando el sistema experto como decisión final y la API como
   respaldo para casos ambiguos.
6. Comparar proveedores de visión con fotos reales (precisión, latencia y
   costo) antes de activar uno en producción.

## Coordinación requerida con Paula

- Realizar la batería de pruebas de clasificación con objetos reales y
  registrar aciertos, errores, condiciones de luz y tiempo de respuesta.
- Ajustar los umbrales de confianza con datos reales si las pruebas lo
  requieren.
- Desplegar `ia/vision-service` en un host persistente y configurar, en el
  entorno de la app, `VISION_SERVICE_URL` y `VISION_SERVICE_API_KEY`.

Mientras se desarrolla localmente, el servicio corre en la Mac. Desplegarlo
significa que la app alojada pueda consultarlo sin depender de que esa Mac
esté encendida.

## Próxima sesión propuesta

1. Probar vidrio y plástico con cámara fija, luz estable y fondo simple.
2. Guardar los resultados de cada intento en una tabla de validación.
3. Habilitar la captura supervisada para comenzar el dataset.
4. Con las primeras fotos, comparar el proveedor actual con OpenAI y decidir
   con datos cuál se mantiene como principal.
