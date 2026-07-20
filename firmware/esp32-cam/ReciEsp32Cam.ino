// ============================================================
// Reci · ESP32-CAM AI Thinker
//
// Captura una foto, consulta /api/face/recognize y ordena al Arduino Mega
// mostrar el saludo en LCD/OLED. La ESP32 nunca accede a Supabase.
//
// Requiere: ArduinoJson (Library Manager) y la placa ESP32 de Espressif.
// Antes de compilar, copia ReciEsp32CamSecrets.h.example como
// ReciEsp32CamSecrets.h y configura Wi-Fi, URL de la web y ROBOT_API_KEY.
// ============================================================

#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include "esp_camera.h"

#include "ReciEsp32CamSecrets.h"

namespace {

// Pines de cámara para el módulo AI Thinker ESP32-CAM.
constexpr int kCameraPwdn = 32;
constexpr int kCameraReset = -1;
constexpr int kCameraXclk = 0;
constexpr int kCameraSiod = 26;
constexpr int kCameraSioc = 27;
constexpr int kCameraY9 = 35;
constexpr int kCameraY8 = 34;
constexpr int kCameraY7 = 39;
constexpr int kCameraY6 = 36;
constexpr int kCameraY5 = 21;
constexpr int kCameraY4 = 19;
constexpr int kCameraY3 = 18;
constexpr int kCameraY2 = 5;
constexpr int kCameraVsync = 25;
constexpr int kCameraHref = 23;
constexpr int kCameraPclk = 22;

// UART dedicado hacia Arduino Mega: ESP RX=GPIO13, TX=GPIO14.
// Serial (USB) queda libre para mensajes de depuración y programación.
constexpr int kMegaRxPin = 13;
constexpr int kMegaTxPin = 14;
constexpr unsigned long kMegaBaud = 9600;
constexpr unsigned long kRecognizeEveryMs = 10'000UL;
// ── BLOQUE DE PRUEBA — quitar cuando se decida la integración final ──────
// Clasifica cada 15s, además del reconocimiento facial cada 10s, solo para
// validar la cadena ESP32-CAM -> Next.js -> vision-service -> Claude con la
// cámara física. No manda nada al Mega todavía (eso es la Fase 4 real, con
// Bluetooth de por medio).
constexpr unsigned long kClassifyEveryMs = 15'000UL;
unsigned long nextClassifyAt = 0;
// ── FIN BLOQUE DE PRUEBA ───────────────────────────────────────────────
constexpr char kMultipartBoundary[] = "ReciFaceBoundary2026";

HardwareSerial mega(1);
unsigned long nextRecognitionAt = 0;

class MultipartCameraStream final : public Stream {
 public:
  MultipartCameraStream(const String& prefix, const uint8_t* image, size_t imageLength, const String& suffix)
      : _prefix(prefix), _image(image), _imageLength(imageLength), _suffix(suffix) {}

  size_t totalLength() const { return _prefix.length() + _imageLength + _suffix.length(); }
  int available() override { return static_cast<int>(totalLength() - _position); }
  int peek() override { return -1; }
  void flush() override {}
  size_t write(uint8_t) override { return 0; }

  int read() override {
    if (_position >= totalLength()) return -1;
    const size_t prefixLength = _prefix.length();
    const size_t imageEnd = prefixLength + _imageLength;
    int value;

    if (_position < prefixLength) value = static_cast<uint8_t>(_prefix[_position]);
    else if (_position < imageEnd) value = _image[_position - prefixLength];
    else value = static_cast<uint8_t>(_suffix[_position - imageEnd]);

    ++_position;
    return value;
  }

 private:
  const String& _prefix;
  const uint8_t* _image;
  size_t _imageLength;
  const String& _suffix;
  size_t _position = 0;
};

void sendMega(const String& command) {
  mega.print(command);
  mega.print('\n');
  Serial.print(F("MEGA <- "));
  Serial.println(command);
}

String cleanLine(String line) {
  line.replace("\r", " ");
  line.replace("\n", " ");
  line.replace("|", " ");
  line.trim();
  return line;
}

void showOnLcd(const String& firstLine, const String& secondLine) {
  sendMega("CMD:LCD:" + cleanLine(firstLine) + "|" + cleanLine(secondLine));
}

bool connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print(F("Conectando al Wi-Fi"));

  const unsigned long deadline = millis() + 20'000UL;
  while (WiFi.status() != WL_CONNECTED && static_cast<long>(millis() - deadline) < 0) {
    delay(300);
    Serial.print('.');
  }
  Serial.println();

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println(F("ERROR: no se pudo conectar al Wi-Fi"));
    showOnLcd("Error de WiFi", "Revisa Reci");
    return false;
  }

  Serial.print(F("Wi-Fi listo: "));
  Serial.println(WiFi.localIP());
  return true;
}

bool startCamera() {
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
  config.frame_size = psramFound() ? FRAMESIZE_QVGA : FRAMESIZE_QQVGA;
  config.jpeg_quality = 12;
  config.fb_count = psramFound() ? 2 : 1;
  config.grab_mode = CAMERA_GRAB_LATEST;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println(F("ERROR: no se pudo iniciar la cámara"));
    showOnLcd("Error de camara", "Revisa Reci");
    return false;
  }
  return true;
}

String postRecognition(camera_fb_t* frame, int& statusCode) {
  WiFiClient client;
  HTTPClient http;
  const String url = String(RECI_API_BASE_URL) + "/api/face/recognize";
  const String prefix = String("--") + kMultipartBoundary + "\r\n"
      "Content-Disposition: form-data; name=\"image\"; filename=\"face.jpg\"\r\n"
      "Content-Type: image/jpeg\r\n\r\n";
  const String suffix = String("\r\n--") + kMultipartBoundary + "--\r\n";
  MultipartCameraStream payload(prefix, frame->buf, frame->len, suffix);

  if (!http.begin(client, url)) {
    statusCode = -1;
    return "";
  }
  http.addHeader("Authorization", String("Bearer ") + RECI_ROBOT_API_KEY);
  http.addHeader("Content-Type", String("multipart/form-data; boundary=") + kMultipartBoundary);
  statusCode = http.sendRequest("POST", &payload, payload.totalLength());
  const String body = statusCode > 0 ? http.getString() : "";
  http.end();
  return body;
}

bool fetchGreeting(const String& profileId) {
  WiFiClient client;
  HTTPClient http;
  const String url = String(RECI_API_BASE_URL) + "/api/robot/display?profile_id=" + profileId;
  if (!http.begin(client, url)) return false;

  http.addHeader("Authorization", String("Bearer ") + RECI_ROBOT_API_KEY);
  const int statusCode = http.GET();
  const String body = statusCode == HTTP_CODE_OK ? http.getString() : "";
  http.end();
  if (statusCode != HTTP_CODE_OK) return false;

  JsonDocument document;
  if (deserializeJson(document, body)) return false;
  JsonArray lines = document["lines"].as<JsonArray>();
  if (lines.size() != 2) return false;

  showOnLcd(lines[0].as<String>(), lines[1].as<String>());
  return true;
}

void recognizePerson() {
  if (WiFi.status() != WL_CONNECTED && !connectWiFi()) return;

  sendMega("CMD:FACE:thinking");
  camera_fb_t* frame = esp_camera_fb_get();
  if (frame == nullptr) {
    Serial.println(F("ERROR: no se pudo capturar foto"));
    sendMega("CMD:FACE:confused");
    return;
  }

  int statusCode = 0;
  const String body = postRecognition(frame, statusCode);
  esp_camera_fb_return(frame);
  if (statusCode != HTTP_CODE_OK) {
    Serial.printf("ERROR: /recognize respondió %d\n", statusCode);
    sendMega("CMD:FACE:confused");
    showOnLcd("No pude verte", "Intenta de nuevo");
    return;
  }

  JsonDocument document;
  if (deserializeJson(document, body)) {
    Serial.println(F("ERROR: JSON de reconocimiento inválido"));
    sendMega("CMD:FACE:confused");
    return;
  }

  const bool matched = document["matched"] | false;
  if (!matched) {
    Serial.println(F("Sin coincidencia facial"));
    sendMega("CMD:FACE:idle");
    showOnLcd("Hola, soy Reci", "Recicla y gana");
    return;
  }

  const String profileId = document["profile_id"].as<String>();
  if (!fetchGreeting(profileId)) {
    Serial.println(F("ERROR: no se pudo obtener saludo"));
    sendMega("CMD:FACE:confused");
    return;
  }

  sendMega("CMD:FACE:happy");
  Serial.print(F("Reconocido: "));
  Serial.println(document["display_name"].as<String>());
}

// ── BLOQUE DE PRUEBA — quitar cuando se decida la integración final ──────
// Mismo patrón que postRecognition()/recognizePerson(), pero contra
// /api/vision/classify. Solo imprime el resultado por Serial — no mueve
// servos ni le habla al Mega, es solo para validar la cámara + la cadena.
String postClassify(camera_fb_t* frame, int& statusCode) {
  WiFiClient client;
  HTTPClient http;
  const String url = String(RECI_API_BASE_URL) + "/api/vision/classify";
  const String prefix = String("--") + kMultipartBoundary + "\r\n"
      "Content-Disposition: form-data; name=\"image\"; filename=\"residuo.jpg\"\r\n"
      "Content-Type: image/jpeg\r\n\r\n";
  const String suffix = String("\r\n--") + kMultipartBoundary + "--\r\n";
  MultipartCameraStream payload(prefix, frame->buf, frame->len, suffix);

  if (!http.begin(client, url)) {
    statusCode = -1;
    return "";
  }
  http.addHeader("Authorization", String("Bearer ") + RECI_ROBOT_API_KEY);
  http.addHeader("Content-Type", String("multipart/form-data; boundary=") + kMultipartBoundary);
  statusCode = http.sendRequest("POST", &payload, payload.totalLength());
  const String body = statusCode > 0 ? http.getString() : "";
  http.end();
  return body;
}

void classifyResiduoDePrueba() {
  if (WiFi.status() != WL_CONNECTED && !connectWiFi()) return;

  Serial.println(F("--- PRUEBA vision/classify ---"));
  camera_fb_t* frame = esp_camera_fb_get();
  if (frame == nullptr) {
    Serial.println(F("ERROR: no se pudo capturar foto"));
    return;
  }

  int statusCode = 0;
  const String body = postClassify(frame, statusCode);
  esp_camera_fb_return(frame);

  if (statusCode != HTTP_CODE_OK) {
    Serial.printf("ERROR: /vision/classify respondio %d\n", statusCode);
    Serial.println(body);
    return;
  }

  JsonDocument document;
  if (deserializeJson(document, body)) {
    Serial.println(F("ERROR: JSON de clasificacion invalido"));
    return;
  }

  Serial.print(F("material="));
  Serial.print(document["material"].as<String>());
  Serial.print(F(" confianza="));
  Serial.print(document["confidence"].as<float>());
  Serial.print(F(" regla="));
  Serial.println(document["rule_applied"].as<String>());
}
// ── FIN BLOQUE DE PRUEBA ───────────────────────────────────────────────

}  // namespace

void setup() {
  Serial.begin(115200);
  mega.begin(kMegaBaud, SERIAL_8N1, kMegaRxPin, kMegaTxPin);
  delay(500);

  showOnLcd("Hola, soy Reci", "Preparando camara");
  if (!startCamera()) return;
  if (!connectWiFi()) return;

  showOnLcd("Hola, soy Reci", "Mira a camara");
  sendMega("CMD:FACE:idle");
  nextRecognitionAt = millis() + 3'000UL;
  nextClassifyAt = millis() + 8'000UL;  // BLOQUE DE PRUEBA — quitar después
}

void loop() {
  const unsigned long ahora = millis();

  if (static_cast<long>(ahora - nextRecognitionAt) >= 0) {
    recognizePerson();
    nextRecognitionAt = millis() + kRecognizeEveryMs;
  }

  // BLOQUE DE PRUEBA — quitar este if cuando termines de validar la cámara
  if (static_cast<long>(ahora - nextClassifyAt) >= 0) {
    classifyResiduoDePrueba();
    nextClassifyAt = millis() + kClassifyEveryMs;
  }
}
