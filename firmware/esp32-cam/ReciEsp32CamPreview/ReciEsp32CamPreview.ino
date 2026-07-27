// Reci · ESP32-CAM AI Thinker · diagnóstico con vista previa
//
// Sketch separado para pruebas. Reutiliza el firmware de clasificación de
// Reci y añade una página local para ver la cámara mientras se envía C por el
// Monitor Serial. No modifica ReciEsp32Cam.ino ni CameraWebServer.
//
// Safari: http://IP_DE_LA_ESP32/
// Foto puntual para scripts: http://IP_DE_LA_ESP32/capture

#include <esp_http_server.h>

// Incluimos el sketch de producción bajo otros nombres de setup/loop. Así
// esta prueba conserva exactamente la misma cámara, Wi-Fi, endpoint y voto
// mayoritario que ReciEsp32Cam, sin copiar ni divergir su lógica.
#define setup reciClassificationSetup
#define loop reciClassificationLoop
#define classifyResidue reciClassificationResidue
#define readClassificationRequest reciClassificationReadRequest
#include "../ReciEsp32Cam/ReciEsp32Cam.ino"
#undef readClassificationRequest
#undef classifyResidue
#undef setup
#undef loop

namespace {

httpd_handle_t previewServer = nullptr;
// Safari y la clasificación compiten por los framebuffers de la cámara. La
// página usa capturas cortas (en vez de un stream HTTP permanente), así que
// /capture queda disponible para el script y para las tres fotos de C.
volatile bool classificationInProgress = false;

// El firmware normal usa un solo framebuffer porque solo toma una foto cada
// vez. La vista de Safari mantiene una captura activa, por lo que esta prueba
// necesita dos buffers en la AI Thinker con PSRAM: uno para el stream y otro
// para las tres fotos de C.
bool restartCameraForPreview() {
  esp_camera_deinit();

  camera_config_t config{};
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = kCameraY2;
  config.pin_d1 = kCameraY3;
  config.pin_d2 = kCameraY4;
  config.pin_d3 = kCameraY5;
  config.pin_d4 = kCameraY6;
  config.pin_d5 = kCameraY7;
  config.pin_d6 = kCameraY8;
  config.pin_d7 = kCameraY9;
  config.pin_xclk = kCameraXclk;
  config.pin_pclk = kCameraPclk;
  config.pin_vsync = kCameraVsync;
  config.pin_href = kCameraHref;
  config.pin_sccb_sda = kCameraSiod;
  config.pin_sccb_scl = kCameraSioc;
  config.pin_pwdn = kCameraPwdn;
  config.pin_reset = kCameraReset;
  config.xclk_freq_hz = 20'000'000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 12;
  config.fb_count = psramFound() ? 2 : 1;
  config.grab_mode = psramFound() ? CAMERA_GRAB_LATEST : CAMERA_GRAB_WHEN_EMPTY;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println(F("ERROR: no se pudo reiniciar la camara para la vista previa"));
    showOnLcd("Error de camara", "Revisa Reci");
    return false;
  }
  Serial.println(psramFound() ? F("Vista previa: 2 buffers QVGA")
                               : F("AVISO: sin PSRAM, stream y C no son simultaneos"));
  return true;
}

constexpr char kIndexHtml[] = R"HTML(
<!doctype html>
<html lang="es"><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reci ESP32-CAM</title>
<style>body{margin:0;background:#111;color:#eee;font:16px system-ui;text-align:center}main{max-width:900px;margin:24px auto;padding:0 16px}img{width:100%;max-width:800px;border-radius:12px;background:#222}code{background:#222;padding:3px 6px;border-radius:4px}</style>
</head><body><main><h1>Reci · Vista de diagnóstico</h1>
<p>Deja esta página abierta y envía <code>C</code> por el Monitor Serial para clasificar.</p>
<img id="preview" src="/capture" alt="Vista de la ESP32-CAM">
<script>
const preview = document.getElementById('preview');
let busy = false;
async function refreshPreview() {
  if (busy) return;
  busy = true;
  try {
    const response = await fetch('/capture?ts=' + Date.now(), {cache:'no-store'});
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const blob = await response.blob();
    const nextUrl = URL.createObjectURL(blob);
    const oldUrl = preview.dataset.objectUrl;
    preview.src = nextUrl;
    preview.dataset.objectUrl = nextUrl;
    if (oldUrl) URL.revokeObjectURL(oldUrl);
  } catch (error) {
    console.warn('No se pudo actualizar la vista', error);
  } finally {
    busy = false;
  }
}
setInterval(refreshPreview, 500);
refreshPreview();
</script>
<p>Captura puntual: <code>/capture</code></p></main></body></html>
)HTML";

esp_err_t indexHandler(httpd_req_t* request) {
  httpd_resp_set_type(request, "text/html");
  return httpd_resp_send(request, kIndexHtml, HTTPD_RESP_USE_STRLEN);
}

esp_err_t captureHandler(httpd_req_t* request) {
  camera_fb_t* frame = esp_camera_fb_get();
  if (frame == nullptr) {
    httpd_resp_set_status(request, "503 Service Unavailable");
    httpd_resp_set_type(request, "text/plain");
    httpd_resp_sendstr(request, "No se pudo capturar la foto");
    return ESP_FAIL;
  }

  httpd_resp_set_type(request, "image/jpeg");
  httpd_resp_set_hdr(request, "Content-Disposition", "inline; filename=reci-preview.jpg");
  const esp_err_t result = httpd_resp_send(request,
                                            reinterpret_cast<const char*>(frame->buf),
                                            frame->len);
  esp_camera_fb_return(frame);
  return result;
}

void startPreviewServer() {
  if (previewServer != nullptr) return;

  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;
  config.ctrl_port = 32769;
  config.max_uri_handlers = 2;
  config.stack_size = 8192;

  if (httpd_start(&previewServer, &config) != ESP_OK) {
    Serial.println(F("ERROR: no se pudo iniciar el servidor de vista previa"));
    return;
  }

  httpd_uri_t indexUri = {.uri = "/", .method = HTTP_GET, .handler = indexHandler, .user_ctx = nullptr};
  httpd_uri_t captureUri = {.uri = "/capture", .method = HTTP_GET, .handler = captureHandler, .user_ctx = nullptr};
  httpd_register_uri_handler(previewServer, &indexUri);
  httpd_register_uri_handler(previewServer, &captureUri);

  Serial.print(F("Vista previa lista: http://"));
  Serial.println(WiFi.localIP());
}

}  // namespace

void setup() {
  reciClassificationSetup();
  if (WiFi.status() == WL_CONNECTED && restartCameraForPreview()) startPreviewServer();
}

void loop() {
  while (Serial.available() > 0) {
    const char command = static_cast<char>(Serial.read());
    if (command == 'c' || command == 'C') {
      classificationInProgress = true;
      reciClassificationResidue();
      classificationInProgress = false;
    }
  }
}
