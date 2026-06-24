# vision/visual_heuristics.py
# Análisis visual con OpenCV para refinar atributos cuando Gemini no está disponible.
# Complementa al clasificador TM (solo 2 clases: plastico/vidrio) con señales reales
# de la imagen: brillo, color, forma, textura.

import cv2
import numpy as np


def _roi_centro(img: np.ndarray, fraccion: float = 0.6) -> np.ndarray:
    """Recorta la región central donde suele estar el objeto."""
    h, w = img.shape[:2]
    mh, mw = int(h * fraccion), int(w * fraccion)
    y0, x0 = (h - mh) // 2, (w - mw) // 2
    return img[y0:y0 + mh, x0:x0 + mw]


def extraer_senales_visuales(img_bgr: np.ndarray) -> dict:
    """
    Extrae métricas visuales de la imagen para refinar atributos del TM.
    No depende de red externa — solo OpenCV + NumPy.
    """
    if img_bgr is None or img_bgr.size == 0:
        return {}

    roi = _roi_centro(img_bgr)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    h_ch, s_ch, v_ch = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    white_mask    = (s_ch < 35) & (v_ch > 175)
    green_mask    = (h_ch >= 35) & (h_ch <= 85) & (s_ch > 40) & (v_ch > 40)
    amber_mask    = (h_ch >= 10) & (h_ch <= 30) & (s_ch > 50) & (v_ch > 50)
    specular_mask = gray > 215

    white_ratio    = float(np.mean(white_mask))
    green_ratio    = float(np.mean(green_mask))
    amber_ratio    = float(np.mean(amber_mask))
    specular_ratio = float(np.mean(specular_mask))
    mean_sat       = float(np.mean(s_ch))
    val_std        = float(np.std(v_ch))
    transparency_score = val_std if mean_sat < 80 else val_std * 0.5

    blur  = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 40, 120)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    aspect_ratio     = 1.0
    is_elongated     = False
    is_flat          = False
    contour_area_pct = 0.0

    if contours:
        main = max(contours, key=cv2.contourArea)
        contour_area_pct = cv2.contourArea(main) / (roi.shape[0] * roi.shape[1])
        _, _, bw, bh = cv2.boundingRect(main)
        if bw > 0:
            aspect_ratio = bh / bw
            is_elongated = aspect_ratio > 1.25
            is_flat      = aspect_ratio < 0.75 or (aspect_ratio < 1.0 and contour_area_pct > 0.35)

    lap = cv2.Laplacian(gray, cv2.CV_64F)
    textura_var = float(np.var(lap))

    return {
        "white_ratio":        white_ratio,
        "green_ratio":        green_ratio,
        "amber_ratio":        amber_ratio,
        "specular_ratio":     specular_ratio,
        "mean_saturation":    mean_sat,
        "transparency_score": transparency_score,
        "aspect_ratio":       aspect_ratio,
        "is_elongated":       is_elongated,
        "is_flat":            is_flat,
        "contour_area_pct":   contour_area_pct,
        "textura_var":        textura_var,
    }


def refinar_atributos(atributos: dict, img_bgr: np.ndarray,
                      clase_tm: str = None, prob_tm: float = None) -> dict:
    """
    Refina los atributos genéricos del TM usando señales visuales reales.
    Se usa cuando Gemini no está disponible (429, 503, sin internet).

    Prioridad: señales visuales fuertes > voto del TM de 2 clases.
    """
    senales = extraer_senales_visuales(img_bgr)
    if not senales:
        return atributos

    out   = dict(atributos)
    wr    = senales["white_ratio"]
    sr    = senales["specular_ratio"]
    sat   = senales["mean_saturation"]
    ts    = senales["transparency_score"]
    flat  = senales["is_flat"]
    elong = senales["is_elongated"]
    gr    = senales["green_ratio"]
    ar    = senales["amber_ratio"]
    tex   = senales["textura_var"]
    cap   = senales["contour_area_pct"]

    brillo_vidrio   = sr > 0.035
    brillo_mate     = sr <= 0.025

    aspect = senales["aspect_ratio"]

    # ── 1. PAPEL / OBJETO NO BOTELLA ──────────────────────────────────
    # Papel blanco plano: mucho blanco, mate, forma plana, no alargado
    parece_papel = (
        not elong
        and flat
        and wr > 0.30
        and brillo_mate
        and sat < 55
    )
    if parece_papel:
        out.update({
            "objeto_reconocido": "papel_servilleta",
            "transparencia":     "ninguna",
            "color":             "blanco_opaco",
            "forma":             "rectangular_plana",
            "brillo":            "bajo",
            "tapa":              "sin_tapa",
            "textura":           "lisa_sin_brillo",
            "rigidez":           "flexible",
            "confianza_ml":      "baja",
        })
        return out

    # ── 2. VASO PLÁSTICO (TM dice vidrio pero no brilla como vidrio) ──
    # Cubre vasos blancos de café y vasos de chocolate/chocolate mate
    parece_vaso_plastico = (
        clase_tm == "vidrio"
        and sr < 0.015
        and (flat or aspect < 1.0 or wr > 0.15)
    )
    if parece_vaso_plastico:
        es_blanco = wr > 0.15
        out.update({
            "objeto_reconocido": "vaso_plastico_blanco" if es_blanco else "vaso_plastico",
            "transparencia":     "ninguna",
            "color":             "blanco_opaco" if es_blanco else ("ambar" if ar > 0.15 else "marron_tierra"),
            "forma":             "conica" if flat or aspect < 0.9 else "cilindrica_ancha",
            "brillo":            "bajo" if sr < 0.005 else "medio_difuso",
            "tapa":              "sin_tapa",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
            "confianza_ml":      "alta",
        })
        return out

    # ── 3. VIDRIO cuando TM dice plástico ─────────────────────────────
    # Solo aplica con señales MUY específicas de vidrio ámbar/verde oscuro.
    # Evita falsos positivos en PET colorido (Colgate, Powerade) que también brillan.
    parece_vidrio = (
        clase_tm == "plastico"
        and brillo_vidrio
        and ar > 0.10
        and sat < 55
    )
    if parece_vidrio:
        if gr > ar and gr > 0.08:
            color_vidrio = "verde_oscuro"
        elif ar > 0.10:
            color_vidrio = "ambar"
        elif ts > 40:
            color_vidrio = "transparente"
        else:
            color_vidrio = "variado_vivo"

        out.update({
            "objeto_reconocido": "botella_cerveza_vidrio" if ar > 0.08 else "botella_jugo_vidrio",
            "transparencia":     "alta" if ts > 40 else ("ninguna" if color_vidrio != "transparente" else "media"),
            "color":             color_vidrio,
            "forma":             "cilindrica_estandar",
            "brillo":            "alto_nitido",
            "tapa":              "twist_off_metalica",
            "textura":           "lisa_brillante",
            "rigidez":           "rigido",
            "confianza_ml":      "media",
        })
        return out

    # ── 4. Refinamiento parcial (sin cambiar objeto_reconocido) ───────
    if brillo_vidrio:
        out["brillo"] = "alto_nitido"
    elif sr > 0.012:
        out["brillo"] = "medio_difuso"
    else:
        out["brillo"] = "bajo"

    if wr > 0.35 and sat < 45:
        out["color"] = "blanco_opaco"
        out["transparencia"] = "ninguna"
    elif ts > 45 and sat < 60:
        out["transparencia"] = "alta"
        out["color"] = "transparente"

    if flat and wr > 0.20:
        out["forma"] = "rectangular_plana"
    elif not elong and wr > 0.25:
        out["forma"] = "conica"

    # Si TM está muy seguro pero señales visuales son ambiguas, bajar confianza
    if prob_tm and prob_tm > 0.95 and sat < 30 and sr < 0.02:
        out["confianza_ml"] = "media"

    return out
