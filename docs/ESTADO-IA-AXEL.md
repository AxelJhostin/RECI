# Estado de IA y Sistema Experto — Axel Hernández

**Fecha de actualización:** 23 de julio de 2026

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
- Resultado actual: **118/118 pruebas formales aprobadas (100 %)**. Estas
  pruebas cubren vidrio, plástico, casos ambiguos, casos extremos, objetos
  del campus, orgánicos y latas.

Commits relacionados:

- `0afe372` — correcciones de ambigüedad para Gatorade.
- `8f4e44a` — correcciones para envases y vasos plásticos.

### Servicio de visión

- El servicio privado FastAPI está integrado con la API web de Reci y se
  ejecutó localmente en la Mac para desarrollo.
- La clasificación actual usa un proveedor de visión para extraer atributos
  visuales, heurísticas OpenCV y el sistema experto de 193 reglas.
- Se configuró OpenAI como proveedor principal local para las pruebas; Claude
  y Gemini quedan disponibles como alternativas, sin eliminarse.
- OpenAI responde mediante Responses API y la respuesta se exige en JSON
  estructurado antes de pasar al sistema experto.
- La integración de OpenAI tiene pruebas unitarias sin red y una prueba real
  completada contra el endpoint local.

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
- La vista previa de la cámara se verificó desde Safari y la cámara entregó
  imágenes correctamente. La IP de la ESP32-CAM es dinámica y puede cambiar
  al reconectarla; por eso no se fija como configuración del proyecto.
- En esta sesión no se ejecutaron nuevas pruebas físicas porque la cámara no
  está conectada. Las próximas pruebas deben hacerse únicamente con la
  ESP32-CAM que se usará en el sistema final.

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
6. Validar OpenAI con fotos reales (precisión, latencia y costo); usar Claude
   o Gemini solo como comparación cuando aparezca un caso ambiguo.

### Alcance de las pruebas

- La botella de chocolatada Toni de formato marrón/estrecho se considera un
  caso atípico y queda fuera del conjunto de aceptación actual. No se añadió
  una regla especial para ella, para evitar alterar el comportamiento de los
  envases plásticos generales.
- Las pruebas de aceptación se concentrarán en botellas y recipientes de
  plástico y vidrio representativos del sistema.

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

## Próxima sesión propuesta (cuando vuelva a estar disponible la cámara)

1. Probar vidrio y plástico con cámara fija, luz estable y fondo simple.
2. Guardar los resultados de cada intento en una tabla de validación.
3. Habilitar la captura supervisada para comenzar el dataset.
4. Validar OpenAI, ya seleccionado como proveedor principal local, con las
   primeras fotos. Usar Claude solo como comparación si aparece un caso
   ambiguo o un error repetible.
