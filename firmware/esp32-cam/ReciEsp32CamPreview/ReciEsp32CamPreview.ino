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
#include "../ReciEsp32Cam/ReciEsp32Cam.ino"
#undef setup
#undef loop

namespace {

httpd_handle_t previewServer = nullptr;

constexpr char kIndexHtml[] = R"HTML(
<!doctype html>
<html lang="es"><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reci ESP32-CAM</title>
<style>body{margin:0;background:#111;color:#eee;font:16px system-ui;text-align:center}main{max-width:900px;margin:24px auto;padding:0 16px}img{width:100%;max-width:800px;border-radius:12px;background:#222}code{background:#222;padding:3px 6px;border-radius:4px}</style>
</head><body><main><h1>Reci · Vista de diagnóstico</h1>
<p>Deja esta página abierta y envía <code>C</code> por el Monitor Serial para clasificar.</p>
<img src="/stream" alt="Stream de la ESP32-CAM">
<p>Captura puntual: <code>/capture</code></p></main></body></html>
)HTML";

esp_err_t indexHandler(httpd_req_t* request) {
  httpd_resp_set_type(request, "text/html");
  return httpd_resp_send(request, kIndexHtml, HTTPD_RESP_USE_STRLEN);
}

esp_err_t captureHandler(httpd_req_t* request) {
  camera_fb_t* frame = esp_camera_fb_get();
  if (frame == nullptr) {
    httpd_resp_send_err(request, HTTPD_503_SERVICE_UNAVAILABLE, "No se pudo capturar la foto");
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

esp_err_t streamHandler(httpd_req_t* request) {
  static constexpr char kStreamContentType[] = "multipart/x-mixed-replace;boundary=reci-frame";
  static constexpr char kBoundary[] = "\r\n--reci-frame\r\n";
  static constexpr char kPartHeader[] = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

  httpd_resp_set_type(request, kStreamContentType);
  char header[80];

  while (true) {
    camera_fb_t* frame = esp_camera_fb_get();
    if (frame == nullptr) return ESP_FAIL;

    const int headerLength = snprintf(header, sizeof(header), kPartHeader,
                                      static_cast<unsigned>(frame->len));
    esp_err_t result = httpd_resp_send_chunk(request, kBoundary, strlen(kBoundary));
    if (result == ESP_OK) result = httpd_resp_send_chunk(request, header, headerLength);
    if (result == ESP_OK) {
      result = httpd_resp_send_chunk(request,
                                     reinterpret_cast<const char*>(frame->buf), frame->len);
    }
    esp_camera_fb_return(frame);
    if (result != ESP_OK) return result;  // el navegador cerró el stream
    delay(35);
  }
}

void startPreviewServer() {
  if (previewServer != nullptr) return;

  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;
  config.ctrl_port = 32769;
  config.max_uri_handlers = 3;
  config.stack_size = 8192;

  if (httpd_start(&previewServer, &config) != ESP_OK) {
    Serial.println(F("ERROR: no se pudo iniciar el servidor de vista previa"));
    return;
  }

  httpd_uri_t indexUri = {.uri = "/", .method = HTTP_GET, .handler = indexHandler, .user_ctx = nullptr};
  httpd_uri_t captureUri = {.uri = "/capture", .method = HTTP_GET, .handler = captureHandler, .user_ctx = nullptr};
  httpd_uri_t streamUri = {.uri = "/stream", .method = HTTP_GET, .handler = streamHandler, .user_ctx = nullptr};
  httpd_register_uri_handler(previewServer, &indexUri);
  httpd_register_uri_handler(previewServer, &captureUri);
  httpd_register_uri_handler(previewServer, &streamUri);

  Serial.print(F("Vista previa lista: http://"));
  Serial.println(WiFi.localIP());
}

}  // namespace

void setup() {
  reciClassificationSetup();
  if (WiFi.status() == WL_CONNECTED) startPreviewServer();
}

void loop() {
  reciClassificationLoop();
}
