#include "Display.h"

// ------------------------------------------------------------
// Geometría de la cara (pantalla 128x64)
// ------------------------------------------------------------
// La cara está dibujada con primitivas, no con un bitmap. Un bitmap sería
// una foto muerta de 1KB; así Reci parpadea y cambia de humor, y ocupa
// prácticamente nada de flash.

static const int16_t SCREEN_W = 128;

static const int16_t EYE_W = 18;
static const int16_t EYE_H = 26;
static const int16_t EYE_TOP = 10;
static const int16_t EYE_L_X = 30;  // ojo izquierdo: x 30..47
static const int16_t EYE_R_X = 80;  // ojo derecho:   x 80..97
static const int16_t EYE_CY = EYE_TOP + EYE_H / 2;  // 23

static const int16_t MOUTH_CX = 64;

// Cuadrantes de drawCircleHelper (Adafruit_GFX)
static const uint8_t Q_TOP = 0x1 | 0x2;     // ∩
static const uint8_t Q_BOTTOM = 0x4 | 0x8;  // ∪

static const uint16_t BLINK_MS = 120;
static const uint16_t DOT_MS = 320;

static bool blinks(Face f) {
  return f == FACE_IDLE || f == FACE_MOVING || f == FACE_HAPPY;
}

// millis() da la vuelta a los ~49 días. Comparar la resta con signo aguanta
// el rollover; comparar `now >= deadline` directamente, no.
static bool due(uint32_t now, uint32_t deadline) {
  return (int32_t)(now - deadline) >= 0;
}

// ------------------------------------------------------------

bool ReciDisplay::begin() {
  Wire.begin();
  // 400kHz. A 100kHz cada refresco del OLED son ~90ms de bus bloqueado, y
  // con eso el robot deja de leer los ultrasonidos a tiempo. No lo bajes.
  Wire.setClock(400000);

  if (!_oled.begin(SSD1306_SWITCHCAPVCC, 0x3C)) return false;

  _oled.clearDisplay();
  _oled.display();
  scheduleBlink();
  _dirty = true;
  return true;
}

void ReciDisplay::setFace(Face face) {
  if (_face == face && !_showingMessage) return;
  _face = face;
  _showingMessage = false;
  _blinking = false;
  _dots = 0;
  scheduleBlink();
  _dirty = true;
}

void ReciDisplay::setMessage(const char* msg) {
  strncpy(_message, msg, sizeof(_message) - 1);
  _message[sizeof(_message) - 1] = '\0';
  _showingMessage = true;
  _dirty = true;
}

void ReciDisplay::scheduleBlink() {
  _nextBlinkAt = millis() + random(2500, 5200);
}

void ReciDisplay::tick() {
  const uint32_t now = millis();

  if (!_showingMessage && blinks(_face)) {
    if (!_blinking && due(now, _nextBlinkAt)) {
      _blinking = true;
      _blinkEndsAt = now + BLINK_MS;
      _dirty = true;
    } else if (_blinking && due(now, _blinkEndsAt)) {
      _blinking = false;
      scheduleBlink();
      _dirty = true;
    }
  }

  if (!_showingMessage && _face == FACE_THINKING && due(now, _nextDotAt)) {
    _dots = (_dots + 1) % 3;
    _nextDotAt = now + DOT_MS;
    _dirty = true;
  }

  // El OLED solo se toca cuando hay algo nuevo. Redibujar en cada loop()
  // serían ~25ms de I2C por vuelta y el robot se arrastraría.
  if (!_dirty) return;
  render();
  _dirty = false;
}

// ------------------------------------------------------------
// Dibujo
// ------------------------------------------------------------

// Varios arcos concéntricos = un arco con grosor. Adafruit_GFX no tiene
// arcos gruesos y un solo píxel se ve anémico en el OLED.
void ReciDisplay::drawArc(int16_t cx, int16_t cy, int16_t r, uint8_t quadrants, uint8_t thickness) {
  for (uint8_t i = 0; i < thickness; i++) {
    _oled.drawCircleHelper(cx, cy, r - i, quadrants, SSD1306_WHITE);
  }
}

void ReciDisplay::drawEyes() {
  // Parpadeo y sueño: el ojo colapsa a una rayita, igual que en la app.
  if (_blinking || _face == FACE_SLEEP) {
    _oled.fillRoundRect(EYE_L_X, EYE_CY - 2, EYE_W, 4, 2, SSD1306_WHITE);
    _oled.fillRoundRect(EYE_R_X, EYE_CY - 2, EYE_W, 4, 2, SSD1306_WHITE);
    return;
  }

  switch (_face) {
    case FACE_HAPPY:
      // Ojos ^^ — dos arcos hacia arriba.
      drawArc(EYE_L_X + EYE_W / 2, EYE_CY + 7, 10, Q_TOP, 3);
      drawArc(EYE_R_X + EYE_W / 2, EYE_CY + 7, 10, Q_TOP, 3);
      break;

    case FACE_MOVING:
      // Ojos entrecerrados: va concentrado en el camino.
      _oled.fillRoundRect(EYE_L_X, EYE_TOP + 6, EYE_W, 14, 6, SSD1306_WHITE);
      _oled.fillRoundRect(EYE_R_X, EYE_TOP + 6, EYE_W, 14, 6, SSD1306_WHITE);
      break;

    case FACE_THINKING:
      // Mirando hacia arriba, como quien piensa.
      _oled.fillRoundRect(EYE_L_X, EYE_TOP + 2, EYE_W, 12, 5, SSD1306_WHITE);
      _oled.fillRoundRect(EYE_R_X, EYE_TOP + 2, EYE_W, 12, 5, SSD1306_WHITE);
      break;

    case FACE_CONFUSED:
      // Ojos bien redondos, de "¿y esto qué es?".
      _oled.fillCircle(EYE_L_X + EYE_W / 2, EYE_CY, 9, SSD1306_WHITE);
      _oled.fillCircle(EYE_R_X + EYE_W / 2, EYE_CY, 9, SSD1306_WHITE);
      break;

    default:  // FACE_IDLE
      _oled.fillRoundRect(EYE_L_X, EYE_TOP, EYE_W, EYE_H, EYE_W / 2, SSD1306_WHITE);
      _oled.fillRoundRect(EYE_R_X, EYE_TOP, EYE_W, EYE_H, EYE_W / 2, SSD1306_WHITE);
      break;
  }
}

void ReciDisplay::drawMouth() {
  switch (_face) {
    case FACE_HAPPY:
      drawArc(MOUTH_CX, 38, 18, Q_BOTTOM, 3);  // sonrisota
      break;

    case FACE_MOVING:
      drawArc(MOUTH_CX, 42, 11, Q_BOTTOM, 3);  // sonrisa corta
      break;

    case FACE_CONFUSED:
      // Boca "o" de sorpresa.
      _oled.drawCircle(MOUTH_CX, 46, 6, SSD1306_WHITE);
      _oled.drawCircle(MOUTH_CX, 46, 5, SSD1306_WHITE);
      break;

    case FACE_SLEEP:
      _oled.fillRoundRect(MOUTH_CX - 6, 45, 12, 3, 1, SSD1306_WHITE);
      // zZz
      _oled.setTextColor(SSD1306_WHITE);
      _oled.setTextSize(1);
      _oled.setCursor(102, 14);
      _oled.print('z');
      _oled.setTextSize(2);
      _oled.setCursor(108, 2);
      _oled.print('Z');
      break;

    case FACE_THINKING: {
      // Tres puntitos; el activo, más gordo.
      for (uint8_t i = 0; i < 3; i++) {
        const int16_t x = MOUTH_CX - 12 + i * 12;
        if (i == _dots) _oled.fillCircle(x, 46, 3, SSD1306_WHITE);
        else _oled.drawCircle(x, 46, 2, SSD1306_WHITE);
      }
      break;
    }

    default:  // FACE_IDLE
      drawArc(MOUTH_CX, 40, 15, Q_BOTTOM, 3);
      break;
  }
}

void ReciDisplay::render() {
  _oled.clearDisplay();

  if (_showingMessage) {
    // Mensajes cortos en grande; los largos en chico y con salto de línea.
    const size_t len = strlen(_message);
    const uint8_t size = len <= 10 ? 2 : 1;
    const uint8_t charW = 6 * size;

    _oled.setTextSize(size);
    _oled.setTextColor(SSD1306_WHITE);
    _oled.setTextWrap(true);

    // Centrado horizontal solo si entra en una línea.
    const int16_t w = len * charW;
    const int16_t x = w < SCREEN_W ? (SCREEN_W - w) / 2 : 0;
    _oled.setCursor(x, len <= 21 ? 26 : 18);
    _oled.print(_message);
  } else {
    drawEyes();
    drawMouth();
  }

  _oled.display();
}
