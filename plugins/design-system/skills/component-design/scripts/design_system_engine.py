#!/usr/bin/env python3
"""Deterministic Design System Engine (Python 3 standard library only).

Implements:
- Exact sRGB <-> Linear sRGB <-> Oklab <-> OKLCH color conversions with binary-search sRGB gamut mapping.
- Six perceptual OKLCH Color Harmony Schemes and three Color Palette Philosophies:
  Tonal Palette (13-step M3), Carbon (IBM) (10-step + layering), Radix Colors (12-step Light/Dark).
- Dual-gate accessibility evaluation: WCAG 2.2 AA/AAA + APCA-W3 0.0.98G-4g (apca-w3 0.1.9).
- W3C DTCG 2025.10 design-tokens.json generation, cascade updates, component HTML authoring,
  and strictly read-only layer/accessibility auditing.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

ACCEPTED_ACCESSIBILITY_LEVELS = ("WCAG 2.2 AA + APCA", "WCAG 2.2 AAA")
ACCEPTED_COLOR_STANDARDS = ("OKLCH", "HEX", "RGB")
ACCEPTED_HARMONY_SCHEMES = (
    "Monochromatic",
    "Analogous",
    "Complementary",
    "Split-Complementary",
    "Triadic",
    "Tetradic",
)
ACCEPTED_PALETTE_PHILOSOPHIES = ("Tonal Palette", "Carbon (IBM)", "Radix Colors")

# APCA-W3 0.0.98G-4g / apca-w3 0.1.9 official constants
APCA_MAIN_TRC = 2.4
APCA_SRCO = 0.2126729
APCA_SGCO = 0.7151522
APCA_SBCO = 0.0721750
APCA_BLK_THRS = 0.022
APCA_BLK_CLMP = 1.414
APCA_DELTA_Y_MIN = 0.0005
APCA_NORM_BG = 0.56
APCA_NORM_TXT = 0.57
APCA_REV_BG = 0.65
APCA_REV_TXT = 0.62
APCA_SCALE = 1.14
APCA_LO_CLIP = 0.1
APCA_LO_OFFSET = 0.027


def _load_asset(name: str) -> dict[str, Any]:
    return json.loads((ASSETS_DIR / name).read_text(encoding="utf-8"))


def _cbrt(x: float) -> float:
    return math.copysign(abs(x) ** (1.0 / 3.0), x)


def _srgb_channel_to_linear(c: float) -> float:
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb_channel(c: float) -> float:
    if c <= 0.0031308:
        return 12.92 * c
    return 1.055 * (c ** (1.0 / 2.4)) - 0.055


def hex_to_srgb(hex_str: str) -> list[float]:
    h = hex_str.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    if len(h) != 6 or not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"Invalid 6-digit hex color: {hex_str}")
    return [int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0]


def srgb_to_hex(rgb: list[float]) -> str:
    r, g, b = (max(0, min(255, round(ch * 255.0))) for ch in rgb)
    return f"#{r:02x}{g:02x}{b:02x}"


def srgb_to_oklch(rgb: list[float]) -> list[float]:
    r, g, b = (_srgb_channel_to_linear(ch) for ch in rgb)
    l_ = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m_ = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s_ = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

    l_c = _cbrt(l_)
    m_c = _cbrt(m_)
    s_c = _cbrt(s_)

    L = 0.2104542553 * l_c + 0.7936177850 * m_c - 0.0040720468 * s_c
    a = 1.9779984951 * l_c - 2.4285922050 * m_c + 0.4505937099 * s_c
    b_ok = 0.0259040371 * l_c + 0.7827717662 * m_c - 0.8086757660 * s_c

    C = math.hypot(a, b_ok)
    H = (math.degrees(math.atan2(b_ok, a)) + 360.0) % 360.0 if C > 1e-7 else 0.0
    return [round(max(0.0, min(1.0, L)), 4), round(C, 4), round(H, 2)]


def oklch_to_linear_srgb(l: float, c: float, h: float) -> list[float]:
    h_rad = math.radians(h)
    a = c * math.cos(h_rad)
    b = c * math.sin(h_rad)

    l_ = l + 0.3963377774 * a + 0.2158037573 * b
    m_ = l - 0.1055613458 * a - 0.0638541728 * b
    s_ = l - 0.0894841775 * a - 1.2914855480 * b

    l3 = l_ * l_ * l_
    m3 = m_ * m_ * m_
    s3 = s_ * s_ * s_

    r = +4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3
    g = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3
    b_lin = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3
    return [r, g, b_lin]


def _in_srgb_gamut(lin_rgb: list[float], eps: float = 1e-6) -> bool:
    return all(-eps <= ch <= 1.0 + eps for ch in lin_rgb)


def gamut_map_oklch_to_srgb(
    l: float, c: float, h: float
) -> tuple[float, float, float, list[float], str]:
    """Map OKLCH into sRGB gamut via 32-iteration binary-search chroma reduction at fixed L and H."""
    l_clamped = max(0.0, min(1.0, float(l)))
    h_norm = float(h) % 360.0
    c_val = max(0.0, float(c))

    if l_clamped <= 0.0001:
        return (0.0, 0.0, h_norm, [0.0, 0.0, 0.0], "#000000")
    if l_clamped >= 0.9999:
        return (1.0, 0.0, h_norm, [1.0, 1.0, 1.0], "#ffffff")

    lin = oklch_to_linear_srgb(l_clamped, c_val, h_norm)
    if not _in_srgb_gamut(lin):
        lo, hi = 0.0, c_val
        for _ in range(32):
            mid = (lo + hi) * 0.5
            if _in_srgb_gamut(oklch_to_linear_srgb(l_clamped, mid, h_norm)):
                lo = mid
            else:
                hi = mid
        c_val = lo
        lin = oklch_to_linear_srgb(l_clamped, c_val, h_norm)

    srgb = [round(max(0.0, min(1.0, _linear_to_srgb_channel(max(0.0, min(1.0, ch))))), 4) for ch in lin]
    hex_val = srgb_to_hex(srgb)
    return (round(l_clamped, 4), round(c_val, 4), round(h_norm, 2), srgb, hex_val)


def parse_color(value: str | dict[str, Any]) -> dict[str, Any]:
    """Parse hex, rgb(...), oklch(...), or DTCG 2025.10 color object into canonical representations."""
    alpha = 1.0
    if isinstance(value, dict):
        cs = value.get("colorSpace", "srgb")
        comps = value.get("components", [0, 0, 0])
        alpha = float(value.get("alpha", 1.0))
        if cs == "oklch":
            l_v, c_v, h_v = (0.0 if x == "none" else float(x) for x in comps[:3])
            l_m, c_m, h_m, srgb, hex_val = gamut_map_oklch_to_srgb(l_v, c_v, h_v)
            oklch = [l_m, c_m, h_m]
        elif cs == "srgb":
            srgb = [round(max(0.0, min(1.0, 0.0 if x == "none" else float(x))), 4) for x in comps[:3]]
            hex_val = value.get("hex") or srgb_to_hex(srgb)
            oklch = srgb_to_oklch(srgb)
        elif "hex" in value:
            srgb = hex_to_srgb(str(value["hex"]))
            hex_val = srgb_to_hex(srgb)
            oklch = srgb_to_oklch(srgb)
        else:
            raise ValueError(f"Unsupported DTCG color object: {value}")
    elif isinstance(value, str):
        s = value.strip()
        if s.startswith("#"):
            srgb = [round(ch, 4) for ch in hex_to_srgb(s)]
            hex_val = srgb_to_hex(srgb)
            oklch = srgb_to_oklch(srgb)
        elif s.lower().startswith("rgb"):
            nums = [float(x) for x in re.findall(r"[\d.]+", s)]
            if len(nums) < 3:
                raise ValueError(f"Invalid rgb() string: {value}")
            srgb = [round(max(0.0, min(1.0, n / 255.0)), 4) for n in nums[:3]]
            if len(nums) >= 4:
                alpha = max(0.0, min(1.0, nums[3]))
            hex_val = srgb_to_hex(srgb)
            oklch = srgb_to_oklch(srgb)
        elif s.lower().startswith("oklch"):
            nums = [float(x) for x in re.findall(r"[-+]?[\d.]+", s)]
            if len(nums) < 3:
                raise ValueError(f"Invalid oklch() string: {value}")
            l_in = nums[0] / 100.0 if "%" in s.split()[0] else nums[0]
            l_m, c_m, h_m, srgb, hex_val = gamut_map_oklch_to_srgb(l_in, nums[1], nums[2])
            if len(nums) >= 4:
                alpha = max(0.0, min(1.0, nums[3]))
            oklch = [l_m, c_m, h_m]
        else:
            raise ValueError(f"Unsupported color string: {value}")
    else:
        raise ValueError(f"Unsupported color value type: {type(value)}")

    r8, g8, b8 = (max(0, min(255, round(ch * 255.0))) for ch in srgb)
    return {
        "oklch": oklch,
        "srgb": srgb,
        "hex": hex_val,
        "rgb_css": f"rgb({r8}, {g8}, {b8})",
        "oklch_css": f"oklch({oklch[0]:.4f} {oklch[1]:.4f} {oklch[2]:.2f})",
        "alpha": round(alpha, 4),
    }


def wcag_relative_luminance(hex_str: str) -> float:
    r, g, b = (_srgb_channel_to_linear(ch) for ch in hex_to_srgb(hex_str))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def wcag_contrast_ratio(hex1: str, hex2: str) -> float:
    y1 = wcag_relative_luminance(hex1)
    y2 = wcag_relative_luminance(hex2)
    lighter = max(y1, y2)
    darker = min(y1, y2)
    return (lighter + 0.05) / (darker + 0.05)


def _apca_screen_luminance(hex_str: str) -> float:
    r, g, b = hex_to_srgb(hex_str)
    ys = (
        APCA_SRCO * (r ** APCA_MAIN_TRC)
        + APCA_SGCO * (g ** APCA_MAIN_TRC)
        + APCA_SBCO * (b ** APCA_MAIN_TRC)
    )
    if ys < 0.0:
        return 0.0
    if ys <= APCA_BLK_THRS:
        return ys + ((APCA_BLK_THRS - ys) ** APCA_BLK_CLMP)
    return ys


def apca_contrast_lc(text_hex: str, bg_hex: str) -> float:
    """Compute signed APCA-W3 0.0.98G-4g Lightness Contrast (Lc)."""
    y_txt = _apca_screen_luminance(text_hex)
    y_bg = _apca_screen_luminance(bg_hex)

    if abs(y_bg - y_txt) < APCA_DELTA_Y_MIN:
        return 0.0

    if y_bg > y_txt:
        sapc = ((y_bg ** APCA_NORM_BG) - (y_txt ** APCA_NORM_TXT)) * APCA_SCALE
        if sapc < APCA_LO_CLIP:
            return 0.0
        return round((sapc - APCA_LO_OFFSET) * 100.0, 2)

    sapc = ((y_bg ** APCA_REV_BG) - (y_txt ** APCA_REV_TXT)) * APCA_SCALE
    if sapc > -APCA_LO_CLIP:
        return 0.0
    return round((sapc + APCA_LO_OFFSET) * 100.0, 2)


def evaluate_contrast_pair(
    text_hex: str,
    bg_hex: str,
    role: str = "body",
    level: str = "WCAG 2.2 AA + APCA",
    font_px: float = 16.0,
    font_weight: int = 400,
) -> dict[str, Any]:
    """Dual-gate contrast evaluation (WCAG 2.2 + APCA 0.0.98G-4g) without rounding up."""
    if level not in ACCEPTED_ACCESSIBILITY_LEVELS:
        raise ValueError(f"Unsupported accessibility level: {level}")
    table = _load_asset("apca-lookup-table.json")
    thresholds = table["dual_gate_thresholds"][level].get(
        role, table["dual_gate_thresholds"][level]["body"]
    )
    cr = wcag_contrast_ratio(text_hex, bg_hex)
    lc = apca_contrast_lc(text_hex, bg_hex)

    wcag_min = float(thresholds["wcag_min"])
    apca_min = float(thresholds["apca_min"])
    wcag_passed = cr >= wcag_min
    apca_passed = abs(lc) >= apca_min
    glare_warning = (
        role == "large"
        and font_px > 36.0
        and font_weight >= 700
        and abs(lc) > float(thresholds.get("apca_max_glare", 90.0))
    )
    return {
        "textHex": text_hex,
        "bgHex": bg_hex,
        "role": role,
        "level": level,
        "wcagRatio": round(cr, 3),
        "wcagMin": wcag_min,
        "wcag_passed": wcag_passed,
        "apcaLc": lc,
        "apcaMin": apca_min,
        "apca_passed": apca_passed,
        "glare_warning": glare_warning,
        "passed": wcag_passed and apca_passed and not glare_warning,
    }


def suggest_accessible_tone(
    text_oklch: list[float],
    bg_hex: str,
    role: str = "body",
    level: str = "WCAG 2.2 AA + APCA",
) -> dict[str, Any]:
    """Find nearest perceptual OKLCH lightness adjustment that passes dual-gate contrast."""
    bg_l = parse_color(bg_hex)["oklch"][0]
    base_l, base_c, base_h = text_oklch
    prefer_dark = bg_l >= 0.55

    candidates = []
    for step in range(0, 101):
        cand_l = step / 100.0
        l_m, c_m, h_m, _, cand_hex = gamut_map_oklch_to_srgb(cand_l, base_c, base_h)
        ev = evaluate_contrast_pair(cand_hex, bg_hex, role=role, level=level)
        if ev["passed"]:
            dist = abs(cand_l - base_l) + (0.05 if (prefer_dark and cand_l > bg_l) or (not prefer_dark and cand_l < bg_l) else 0.0)
            candidates.append((dist, cand_hex, [l_m, c_m, h_m], ev))

    if candidates:
        candidates.sort(key=lambda item: item[0])
        _, best_hex, best_oklch, best_ev = candidates[0]
        return {"hex": best_hex, "oklch": best_oklch, "evaluation": best_ev}

    fallback_hex = "#000000" if prefer_dark else "#ffffff"
    return {
        "hex": fallback_hex,
        "oklch": parse_color(fallback_hex)["oklch"],
        "evaluation": evaluate_contrast_pair(fallback_hex, bg_hex, role=role, level=level),
    }


def generate_harmony_seeds(seed_color: str, scheme: str) -> dict[str, list[float]]:
    """Derive brand/accent seeds in perceptual OKLCH + chroma-harmonized functional status seeds."""
    if scheme not in ACCEPTED_HARMONY_SCHEMES:
        raise ValueError(f"Unsupported color harmony scheme: {scheme}")
    parsed = parse_color(seed_color)
    l0, c0, h0 = parsed["oklch"]
    c_brand = max(0.08, min(0.22, c0 if c0 > 0.04 else 0.14))

    if scheme == "Monochromatic":
        seeds = {
            "primary": [l0, c_brand, h0],
            "secondary": [l0, round(c_brand * 0.55, 4), h0],
            "accent": [l0, round(min(0.24, c_brand * 0.85), 4), h0],
        }
    elif scheme == "Analogous":
        seeds = {
            "primary": [l0, c_brand, h0],
            "secondary": [l0, c_brand, round((h0 + 30.0) % 360.0, 2)],
            "accent": [l0, c_brand, round((h0 + 330.0) % 360.0, 2)],
        }
    elif scheme == "Complementary":
        comp = round((h0 + 180.0) % 360.0, 2)
        seeds = {
            "primary": [l0, c_brand, h0],
            "secondary": [l0, round(c_brand * 0.85, 4), comp],
            "accent": [l0, round(min(0.24, c_brand * 1.1), 4), comp],
        }
    elif scheme == "Split-Complementary":
        seeds = {
            "primary": [l0, c_brand, h0],
            "secondary": [l0, c_brand, round((h0 + 150.0) % 360.0, 2)],
            "accent": [l0, c_brand, round((h0 + 210.0) % 360.0, 2)],
        }
    elif scheme == "Triadic":
        seeds = {
            "primary": [l0, c_brand, h0],
            "secondary": [l0, c_brand, round((h0 + 120.0) % 360.0, 2)],
            "accent": [l0, c_brand, round((h0 + 240.0) % 360.0, 2)],
        }
    else:  # Tetradic
        seeds = {
            "primary": [l0, c_brand, h0],
            "secondary": [l0, c_brand, round((h0 + 60.0) % 360.0, 2)],
            "accent": [l0, c_brand, round((h0 + 180.0) % 360.0, 2)],
            "quaternary": [l0, c_brand, round((h0 + 240.0) % 360.0, 2)],
        }

    # Dedicated chroma-harmonized functional status & brand-tinted neutral seeds
    seeds["neutral"] = [0.55, round(min(0.015, c_brand * 0.12), 4), h0]
    seeds["success"] = [0.60, round(max(0.12, min(0.18, c_brand)), 4), 145.0]
    seeds["warning"] = [0.72, round(max(0.13, min(0.18, c_brand)), 4), 75.0]
    seeds["danger"] = [0.56, round(max(0.15, min(0.21, c_brand)), 4), 25.0]
    seeds["info"] = [0.58, round(max(0.12, min(0.18, c_brand)), 4), 250.0]
    return seeds


def make_dtcg_color_token(
    l: float, c: float, h: float, color_standard: str, description: str
) -> dict[str, Any]:
    """Build a W3C DTCG 2025.10 compliant color token with automatic HEX/sRGB fallback."""
    if color_standard not in ACCEPTED_COLOR_STANDARDS:
        raise ValueError(f"Unsupported color standard: {color_standard}")
    l_m, c_m, h_m, srgb, hex_val = gamut_map_oklch_to_srgb(l, c, h)
    r8, g8, b8 = (max(0, min(255, round(ch * 255.0))) for ch in srgb)
    rgb_css = f"rgb({r8}, {g8}, {b8})"
    oklch_css = f"oklch({l_m:.4f} {c_m:.4f} {h_m:.2f})"

    if color_standard == "OKLCH":
        val_obj = {
            "colorSpace": "oklch",
            "components": [l_m, c_m, h_m],
            "alpha": 1,
            "hex": hex_val,
        }
        primary_css = oklch_css
    else:
        val_obj = {
            "colorSpace": "srgb",
            "components": srgb,
            "alpha": 1,
            "hex": hex_val,
        }
        primary_css = hex_val if color_standard == "HEX" else rgb_css

    return {
        "$type": "color",
        "$value": val_obj,
        "$description": description,
        "$extensions": {
            "com.design-system.color": {
                "primaryStandard": color_standard,
                "css": primary_css,
                "oklch": [l_m, c_m, h_m],
                "srgbHex": hex_val,
                "srgbRgb": rgb_css,
                "srgbComponents": srgb,
            }
        },
    }


def generate_palette_scales(
    seeds: dict[str, list[float]], philosophy: str, color_standard: str
) -> dict[str, dict[str, dict[str, Any]]]:
    """Generate primitive color scales under Tonal Palette, Carbon (IBM), or Radix Colors."""
    if philosophy not in ACCEPTED_PALETTE_PHILOSOPHIES:
        raise ValueError(f"Unsupported color palette philosophy: {philosophy}")

    scales: dict[str, dict[str, dict[str, Any]]] = {}

    if philosophy == "Tonal Palette":
        # Material 3 13-step tonal scale (0..100)
        steps = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100]
        for role_name, (_, base_c, base_h) in seeds.items():
            scales[role_name] = {}
            for step in steps:
                target_l = step / 100.0
                # Parabolic chroma taper toward pure black/white
                taper = math.sin(math.pi * target_l) ** 0.75 if 0 < step < 100 else 0.0
                c_step = base_c * taper
                scales[role_name][str(step)] = make_dtcg_color_token(
                    target_l,
                    c_step,
                    base_h,
                    color_standard,
                    f"{role_name.title()} tonal palette step {step}",
                )

    elif philosophy == "Carbon (IBM)":
        # IBM Carbon 10-step scale (10..100) + white/black
        carbon_lightness = {
            "10": 0.96,
            "20": 0.89,
            "30": 0.80,
            "40": 0.70,
            "50": 0.60,
            "60": 0.50,
            "70": 0.41,
            "80": 0.32,
            "90": 0.23,
            "100": 0.14,
        }
        for role_name, (_, base_c, base_h) in seeds.items():
            scales[role_name] = {}
            for step, target_l in carbon_lightness.items():
                taper = math.sin(math.pi * target_l) ** 0.65
                c_step = base_c * taper
                scales[role_name][step] = make_dtcg_color_token(
                    target_l,
                    c_step,
                    base_h,
                    color_standard,
                    f"{role_name.title()} Carbon scale step {step}",
                )
        scales["neutral"]["white"] = make_dtcg_color_token(
            1.0, 0.0, 0.0, color_standard, "Carbon pure white"
        )
        scales["neutral"]["black"] = make_dtcg_color_token(
            0.0, 0.0, 0.0, color_standard, "Carbon pure black"
        )

    else:  # Radix Colors (12-step functional scale 1..12 for light + dark-1..dark-12 for dark)
        radix_light = [
            (1, 0.99, 0.08),
            (2, 0.97, 0.14),
            (3, 0.94, 0.25),
            (4, 0.90, 0.36),
            (5, 0.85, 0.48),
            (6, 0.80, 0.58),
            (7, 0.73, 0.70),
            (8, 0.64, 0.85),
            (9, 0.54, 1.00),
            (10, 0.48, 0.96),
            (11, 0.42, 0.82),
            (12, 0.22, 0.55),
        ]
        radix_dark = [
            (1, 0.14, 0.12),
            (2, 0.17, 0.18),
            (3, 0.21, 0.30),
            (4, 0.25, 0.42),
            (5, 0.30, 0.52),
            (6, 0.36, 0.62),
            (7, 0.44, 0.74),
            (8, 0.54, 0.86),
            (9, 0.62, 1.00),
            (10, 0.68, 0.95),
            (11, 0.82, 0.78),
            (12, 0.95, 0.35),
        ]
        for role_name, (_, base_c, base_h) in seeds.items():
            scales[role_name] = {}
            for step, target_l, c_mult in radix_light:
                scales[role_name][str(step)] = make_dtcg_color_token(
                    target_l,
                    base_c * c_mult,
                    base_h,
                    color_standard,
                    f"{role_name.title()} Radix light functional step {step}",
                )
            for step, target_l, c_mult in radix_dark:
                scales[role_name][f"dark-{step}"] = make_dtcg_color_token(
                    target_l,
                    base_c * c_mult,
                    base_h,
                    color_standard,
                    f"{role_name.title()} Radix dark functional step {step}",
                )

    return scales


# ---------------------------------------------------------------------------
# W3C DTCG 2025.10 Generator, Cascade Updater, Component Builder & Auditor
# ---------------------------------------------------------------------------

import argparse
import datetime as _dt
import html as _html
import sys

DTCG_SCHEMA_URL = "https://www.designtokens.org/schemas/2025.10/format.json"
ALIAS_RE = re.compile(r"^\{([^{}]+)\}$")
PRIMITIVE_NAME_RE = re.compile(
    r"^[a-z0-9]+-(color|typography|spacing|shape|elevation|motion|opacity|sizing)-[a-z0-9]+(-[a-z0-9]+)*$"
)
SEMANTIC_NAME_RE = re.compile(
    r"^[a-z0-9]+-(color|typography|spacing|shape|elevation|motion|opacity|sizing)-[a-z0-9]+-[a-z0-9]+(-[a-z0-9]+)*$"
)


def _validate_foundation_config(config: dict[str, Any]) -> None:
    missing = []
    if config.get("accessibilityLevel") not in ACCEPTED_ACCESSIBILITY_LEVELS:
        missing.append(f"accessibilityLevel (must be one of {ACCEPTED_ACCESSIBILITY_LEVELS})")
    if config.get("colorPalettePhilosophy") not in ACCEPTED_PALETTE_PHILOSOPHIES:
        missing.append(f"colorPalettePhilosophy (must be one of {ACCEPTED_PALETTE_PHILOSOPHIES})")
    if config.get("colorHarmonyScheme") not in ACCEPTED_HARMONY_SCHEMES:
        missing.append(f"colorHarmonyScheme (must be one of {ACCEPTED_HARMONY_SCHEMES})")
    if config.get("colorStandard") not in ACCEPTED_COLOR_STANDARDS:
        missing.append(f"colorStandard (must be one of {ACCEPTED_COLOR_STANDARDS})")
    if missing:
        raise ValueError("Missing or invalid mandatory foundation parameters: " + "; ".join(missing))


def _resolve_alias(tokens: dict[str, Any], value: Any, mode: str = "light", stack: tuple[str, ...] = ()) -> Any:
    if isinstance(value, str):
        m = ALIAS_RE.match(value.strip())
        if not m:
            return value
        path = m.group(1)
        if path in stack:
            raise ValueError(f"Circular alias detected: {' -> '.join(stack + (path,))}")
        node: Any = tokens
        for seg in path.split("."):
            if not isinstance(node, dict) or seg not in node:
                raise ValueError(f"Unresolvable alias target: {value}")
            node = node[seg]
        if not isinstance(node, dict) or "$value" not in node:
            raise ValueError(f"Alias points to non-token group: {value}")
        modes_ext = node.get("$extensions", {}).get("com.design-system.modes", {})
        target_val = modes_ext.get(mode, node["$value"]) if isinstance(modes_ext, dict) else node["$value"]
        return _resolve_alias(tokens, target_val, mode=mode, stack=stack + (path,))
    if isinstance(value, dict):
        return {k: _resolve_alias(tokens, v, mode=mode, stack=stack) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_alias(tokens, item, mode=mode, stack=stack) for item in value]
    return value


def safe_font_family_css(font_family_val: Any) -> str:
    """Format font-family with single quotes so it never breaks double-quoted HTML style attributes."""
    if isinstance(font_family_val, list):
        parts = []
        for item in font_family_val:
            s = str(item).strip().strip('"').strip("'")
            parts.append(f"'{s}'" if " " in s else s)
        return ", ".join(parts)
    return str(font_family_val).replace('"', "'")


def _infer_token_type(val: Any, category: str) -> str:
    """Infer W3C DTCG 2025.10 $type when an override inserts a new token without explicit $type."""
    if category == "color":
        return "color"
    if isinstance(val, dict):
        if "colorSpace" in val or "hex" in val:
            return "color"
        if "value" in val and "unit" in val:
            return "duration" if val["unit"] in ("ms", "s") else "dimension"
        if "offsetX" in val and "blur" in val:
            return "shadow"
        if "fontSize" in val and "fontFamily" in val:
            return "typography"
        if "timingFunction" in val and "duration" in val:
            return "transition"
        if "width" in val and "style" in val and "color" in val:
            return "border"
    if isinstance(val, list):
        if len(val) == 4 and all(isinstance(x, (int, float)) for x in val):
            return "cubicBezier"
        if all(isinstance(x, str) for x in val):
            return "fontFamily"
    if isinstance(val, (int, float)):
        return "fontWeight" if category == "typography" else "number"
    return "string"


def _token_to_css_value(token_type: str, resolved_val: Any, color_standard: str) -> str:
    if token_type == "color" and isinstance(resolved_val, dict):
        parsed = parse_color(resolved_val)
        if color_standard == "OKLCH":
            return parsed["oklch_css"]
        if color_standard == "RGB":
            return parsed["rgb_css"]
        return parsed["hex"]
    if token_type == "dimension" and isinstance(resolved_val, dict):
        return f"{resolved_val['value']}{resolved_val['unit']}"
    if token_type == "duration" and isinstance(resolved_val, dict):
        return f"{resolved_val['value']}{resolved_val['unit']}"
    if token_type == "cubicBezier" and isinstance(resolved_val, list):
        return f"cubic-bezier({', '.join(str(x) for x in resolved_val)})"
    if token_type == "fontFamily":
        if isinstance(resolved_val, list):
            return ", ".join(f'"{f}"' if " " in f else f for f in resolved_val)
        return str(resolved_val)
    if token_type == "shadow":
        items = resolved_val if isinstance(resolved_val, list) else [resolved_val]
        parts = []
        for s in items:
            inset = "inset " if s.get("inset") else ""
            ox = f"{s['offsetX']['value']}{s['offsetX']['unit']}"
            oy = f"{s['offsetY']['value']}{s['offsetY']['unit']}"
            bl = f"{s['blur']['value']}{s['blur']['unit']}"
            sp = f"{s['spread']['value']}{s['spread']['unit']}"
            col = _token_to_css_value("color", s["color"], color_standard)
            parts.append(f"{inset}{ox} {oy} {bl} {sp} {col}")
        return ", ".join(parts)
    if token_type == "border" and isinstance(resolved_val, dict):
        w = _token_to_css_value("dimension", resolved_val["width"], color_standard)
        st = resolved_val["style"] if isinstance(resolved_val["style"], str) else "solid"
        col = _token_to_css_value("color", resolved_val["color"], color_standard)
        return f"{w} {st} {col}"
    if token_type == "transition" and isinstance(resolved_val, dict):
        dur = _token_to_css_value("duration", resolved_val["duration"], color_standard)
        dly = _token_to_css_value("duration", resolved_val["delay"], color_standard)
        tf = _token_to_css_value("cubicBezier", resolved_val["timingFunction"], color_standard)
        return f"all {dur} {tf} {dly}"
    if token_type == "typography" and isinstance(resolved_val, dict):
        fw = resolved_val.get("fontWeight", 400)
        fs = _token_to_css_value("dimension", resolved_val["fontSize"], color_standard)
        lh = resolved_val.get("lineHeight", 1.5)
        ff = _token_to_css_value("fontFamily", resolved_val["fontFamily"], color_standard)
        return f"{fw} {fs}/{lh} {ff}"
    # Fallback safeguard if a dimension/duration dict arrives without explicit $type
    if isinstance(resolved_val, dict) and "value" in resolved_val and "unit" in resolved_val:
        return f"{resolved_val['value']}{resolved_val['unit']}"
    return str(resolved_val)


def _pick_step_for_philosophy(philosophy: str, role: str, mode: str) -> str:
    if philosophy == "Tonal Palette":
        mapping = {
            ("canvas", "light"): "99", ("canvas", "dark"): "10",
            ("surface", "light"): "95", ("surface", "dark"): "20",
            ("surface_elevated", "light"): "90", ("surface_elevated", "dark"): "30",
            ("text_primary", "light"): "10", ("text_primary", "dark"): "95",
            ("text_muted", "light"): "30", ("text_muted", "dark"): "80",
            ("action_default", "light"): "40", ("action_default", "dark"): "80",
            ("action_hover", "light"): "30", ("action_hover", "dark"): "90",
            ("action_active", "light"): "20", ("action_active", "dark"): "70",
            ("on_action", "light"): "100", ("on_action", "dark"): "10",
            ("border_subtle", "light"): "70", ("border_subtle", "dark"): "40",
            ("border_focus", "light"): "30", ("border_focus", "dark"): "80",
            ("disabled_bg", "light"): "90", ("disabled_bg", "dark"): "20",
            ("disabled_fg", "light"): "40", ("disabled_fg", "dark"): "70",
        }
        return mapping[(role, mode)]
    if philosophy == "Carbon (IBM)":
        mapping = {
            ("canvas", "light"): "white", ("canvas", "dark"): "100",
            ("surface", "light"): "10", ("surface", "dark"): "90",
            ("surface_elevated", "light"): "20", ("surface_elevated", "dark"): "80",
            ("text_primary", "light"): "100", ("text_primary", "dark"): "10",
            ("text_muted", "light"): "80", ("text_muted", "dark"): "30",
            ("action_default", "light"): "70", ("action_default", "dark"): "30",
            ("action_hover", "light"): "80", ("action_hover", "dark"): "20",
            ("action_active", "light"): "90", ("action_active", "dark"): "40",
            ("on_action", "light"): "white", ("on_action", "dark"): "100",
            ("border_subtle", "light"): "40", ("border_subtle", "dark"): "70",
            ("border_focus", "light"): "80", ("border_focus", "dark"): "30",
            ("disabled_bg", "light"): "20", ("disabled_bg", "dark"): "90",
            ("disabled_fg", "light"): "70", ("disabled_fg", "dark"): "40",
        }
        return mapping[(role, mode)]
    # Radix Colors
    mapping = {
        ("canvas", "light"): "1", ("canvas", "dark"): "dark-1",
        ("surface", "light"): "2", ("surface", "dark"): "dark-2",
        ("surface_elevated", "light"): "3", ("surface_elevated", "dark"): "dark-3",
        ("text_primary", "light"): "12", ("text_primary", "dark"): "dark-12",
        ("text_muted", "light"): "11", ("text_muted", "dark"): "dark-11",
        ("action_default", "light"): "11", ("action_default", "dark"): "dark-11",
        ("action_hover", "light"): "12", ("action_hover", "dark"): "dark-12",
        ("action_active", "light"): "10", ("action_active", "dark"): "dark-10",
        ("on_action", "light"): "1", ("on_action", "dark"): "dark-1",
        ("border_subtle", "light"): "6", ("border_subtle", "dark"): "dark-6",
        ("border_focus", "light"): "8", ("border_focus", "dark"): "dark-9",
        ("disabled_bg", "light"): "3", ("disabled_bg", "dark"): "dark-3",
        ("disabled_fg", "light"): "11", ("disabled_fg", "dark"): "dark-11",
    }
    return mapping[(role, mode)]


def _evaluate_system_contrast_rows(tokens: dict[str, Any]) -> list[dict[str, Any]]:
    meta = tokens.get("$metadata", {})
    ns = meta.get("namespace", "ds")
    level = meta.get("accessibilityLevel", "WCAG 2.2 AA + APCA")
    sem_colors = tokens.get("semantic", {}).get("color", {})

    pairs = [
        ("Primary Text on Canvas", f"{ns}-color-text-primary-default", f"{ns}-color-bg-canvas-default", "body"),
        ("Muted Text on Canvas", f"{ns}-color-text-muted-default", f"{ns}-color-bg-canvas-default", "content"),
        ("On-Action on Primary CTA", f"{ns}-color-text-on-action-default", f"{ns}-color-action-primary-default", "content"),
        ("On-Action on Success CTA", f"{ns}-color-text-on-action-default", f"{ns}-color-action-success-default", "content"),
        ("On-Action on Destructive CTA", f"{ns}-color-text-on-action-default", f"{ns}-color-action-danger-default", "content"),
        ("Success Feedback on Canvas", f"{ns}-color-feedback-success-default", f"{ns}-color-bg-canvas-default", "content"),
        ("Warning Feedback on Canvas", f"{ns}-color-feedback-warning-default", f"{ns}-color-bg-canvas-default", "content"),
        ("Danger Feedback on Canvas", f"{ns}-color-feedback-danger-default", f"{ns}-color-bg-canvas-default", "content"),
        ("Info Feedback on Canvas", f"{ns}-color-feedback-info-default", f"{ns}-color-bg-canvas-default", "content"),
        ("Focus Ring on Canvas", f"{ns}-color-border-focus-default", f"{ns}-color-bg-canvas-default", "focus"),
    ]
    rows: list[dict[str, Any]] = []
    for label, fg_key, bg_key, role in pairs:
        if fg_key not in sem_colors or bg_key not in sem_colors:
            continue
        for mode in ("light", "dark"):
            fg_raw = sem_colors[fg_key].get("$extensions", {}).get("com.design-system.modes", {}).get(mode, sem_colors[fg_key]["$value"])
            bg_raw = sem_colors[bg_key].get("$extensions", {}).get("com.design-system.modes", {}).get(mode, sem_colors[bg_key]["$value"])
            fg_hex = parse_color(_resolve_alias(tokens, fg_raw, mode=mode))["hex"]
            bg_hex = parse_color(_resolve_alias(tokens, bg_raw, mode=mode))["hex"]
            ev = evaluate_contrast_pair(fg_hex, bg_hex, role=role, level=level)
            rows.append({
                "label": label,
                "mode": mode,
                "role": role,
                "fgToken": fg_key,
                "bgToken": bg_key,
                "fgHex": fg_hex,
                "bgHex": bg_hex,
                **ev,
            })
    return rows


def _check_system_accessibility(tokens: dict[str, Any]) -> list[dict[str, Any]]:
    meta = tokens.get("$metadata", {})
    level = meta.get("accessibilityLevel", "WCAG 2.2 AA + APCA")
    violations = []
    for row in _evaluate_system_contrast_rows(tokens):
        if not row["passed"]:
            proposal = suggest_accessible_tone(parse_color(row["fgHex"])["oklch"], row["bgHex"], role=row["role"], level=level)
            violations.append({
                "ruleId": "D16" if row["role"] in ("body", "content") else "D18",
                "mode": row["mode"],
                "fgToken": row["fgToken"],
                "bgToken": row["bgToken"],
                "evaluation": {
                    "passed": row["passed"],
                    "wcagRatio": row["wcagRatio"],
                    "wcagMin": row["wcagMin"],
                    "apcaLc": row["apcaLc"],
                    "apcaMin": row["apcaMin"],
                },
                "proposedNearestTone": proposal,
            })
    return violations


def compile_css_variables(tokens: dict[str, Any]) -> str:
    """Compile all Tier 1, Tier 2, and Tier 3 tokens into :root (light) and [data-theme='dark'] CSS."""
    meta = tokens["$metadata"]
    cs = meta["colorStandard"]
    light_lines: list[str] = []
    dark_lines: list[str] = []

    for tier in ("primitive", "semantic", "component"):
        tier_obj = tokens.get(tier, {})
        for cat_name, cat_obj in tier_obj.items():
            if not isinstance(cat_obj, dict):
                continue
            inherited_type = cat_obj.get("$type", "string")
            for tok_name, tok_def in cat_obj.items():
                if tok_name.startswith("$") or not isinstance(tok_def, dict) or "$value" not in tok_def:
                    continue
                t_type = tok_def.get("$type", inherited_type)
                modes = tok_def.get("$extensions", {}).get("com.design-system.modes", {})
                l_val = _resolve_alias(tokens, modes.get("light", tok_def["$value"]), mode="light")
                d_val = _resolve_alias(tokens, modes.get("dark", tok_def["$value"]), mode="dark")
                l_css = _token_to_css_value(t_type, l_val, cs)
                d_css = _token_to_css_value(t_type, d_val, cs)
                light_lines.append(f"  --{tok_name}: {l_css};")
                if d_css != l_css:
                    dark_lines.append(f"  --{tok_name}: {d_css};")

    return (
        ":root {\n"
        + "\n".join(light_lines)
        + "\n}\n\n[data-theme=\"dark\"] {\n"
        + "\n".join(dark_lines)
        + "\n}\n\n@media (prefers-reduced-motion: reduce) {\n"
        "  *, *::before, *::after {\n"
        "    animation-duration: 0.01ms !important;\n"
        "    animation-iteration-count: 1 !important;\n"
        "    transition-duration: 0.01ms !important;\n"
        "    scroll-behavior: auto !important;\n"
        "  }\n"
        "}\n"
    )


_THEME_HEAD_JS = """  <meta name="color-scheme" content="light dark" />
  <script>
    (function () {
      try {
        var saved = localStorage.getItem('ds-color-scheme');
        var meta = document.querySelector('meta[name="color-scheme"]');
        if (saved === 'light' || saved === 'dark') {
          if (meta) meta.content = saved;
          document.documentElement.dataset.theme = saved;
        } else {
          var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
          document.documentElement.dataset.theme = prefersDark ? 'dark' : 'light';
        }
      } catch (e) {}
    })();
  </script>"""

_THEME_TOGGLE_JS = """  <script>
    (function () {
      const root = document.documentElement;
      const meta = document.querySelector('meta[name="color-scheme"]');
      const btn = document.getElementById('global-theme-toggle');
      const label = document.getElementById('global-theme-label');

      function getSystemTheme() {
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }

      function applyTheme(theme, broadcast) {
        root.dataset.theme = theme;
        if (label) label.textContent = theme === 'dark' ? 'Dark' : 'Light';
        if (btn) btn.setAttribute('aria-pressed', String(theme === 'dark'));
        if (broadcast) {
          document.querySelectorAll('iframe[data-ds-component-frame]').forEach((frame) => {
            try { frame.contentWindow.postMessage({ type: 'ds-theme', theme: theme }, '*'); } catch (e) {}
          });
        }
      }

      if (btn) {
        btn.addEventListener('click', () => {
          const current = root.dataset.theme === 'dark' ? 'dark' : 'light';
          const target = current === 'dark' ? 'light' : 'dark';
          const sys = getSystemTheme();
          try {
            if (target === sys) {
              localStorage.removeItem('ds-color-scheme');
              if (meta) meta.content = 'light dark';
            } else {
              localStorage.setItem('ds-color-scheme', target);
              if (meta) meta.content = target;
            }
          } catch (e) {}
          applyTheme(target, true);
        });
      }

      window.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'ds-theme' && (event.data.theme === 'light' || event.data.theme === 'dark')) {
          if (meta) meta.content = event.data.theme;
          applyTheme(event.data.theme, false);
        }
      });

      window.addEventListener('storage', (event) => {
        if (event.key === 'ds-color-scheme') {
          const next = (event.newValue === 'light' || event.newValue === 'dark') ? event.newValue : getSystemTheme();
          if (meta) meta.content = event.newValue || 'light dark';
          applyTheme(next, true);
        }
      });

      applyTheme(root.dataset.theme === 'dark' ? 'dark' : 'light', false);
    })();
  </script>"""


def _shared_editorial_css(ns: str) -> str:
    """Standardized HTML viewer shell using fixed Neutral Tonal Scale (Brand-Tinted).
    Decoupled from --{ns}-* tokens so every design system presents consistently without altering its tokens."""
    return f"""    /* === STANDARDIZED HTML VIEWER SHELL (FIXED NEUTRAL TONAL SCALE · BRAND-TINTED) === */
    :root {{
      color-scheme: light dark;
      --shell-0: #000000;
      --shell-10: #030304;
      --shell-20: #16151a;
      --shell-30: #2e2d33;
      --shell-40: #48464e;
      --shell-50: #64626a;
      --shell-60: #807f87;
      --shell-70: #9f9da5;
      --shell-80: #bebdc3;
      --shell-90: #dedde1;
      --shell-95: #eeeef0;
      --shell-99: #fcfcfc;
      --shell-100: #ffffff;

      --shell-canvas: var(--shell-99);
      --shell-surface: var(--shell-95);
      --shell-surface-hover: var(--shell-90);
      --shell-hairline: var(--shell-90);
      --shell-hairline-strong: var(--shell-80);
      --shell-ink: var(--shell-10);
      --shell-ink-secondary: var(--shell-30);
      --shell-muted: var(--shell-40);
      --shell-faint: var(--shell-50);
      --shell-bar: var(--shell-30);

      --shell-font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
      --shell-font-mono: ui-monospace, "SFMono-Regular", "Cascadia Mono", Consolas, monospace;
      --shell-max-width: 1180px;
    }}
    :root[data-theme="dark"] {{
      --shell-canvas: var(--shell-10);
      --shell-surface: var(--shell-20);
      --shell-surface-hover: var(--shell-30);
      --shell-hairline: var(--shell-30);
      --shell-hairline-strong: var(--shell-40);
      --shell-ink: var(--shell-100);
      --shell-ink-secondary: var(--shell-80);
      --shell-muted: var(--shell-70);
      --shell-faint: var(--shell-60);
      --shell-bar: var(--shell-80);
    }}
    :root:has(> head > meta[name="color-scheme"][content="dark"]) {{ color-scheme: dark; }}
    :root:has(> head > meta[name="color-scheme"][content="light"]) {{ color-scheme: light; }}

    *, *::before, *::after {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      font-family: var(--shell-font-sans);
      font-size: 15px;
      line-height: 1.55;
      background: var(--shell-canvas);
      color: var(--shell-ink);
      -webkit-font-smoothing: auto;
      font-variant-numeric: tabular-nums;
    }}

    .visually-hidden:where(:not(:focus-within, :active)) {{
      position: absolute !important;
      clip-path: inset(50%) !important;
      overflow: hidden !important;
      width: 1px !important;
      height: 1px !important;
      margin: -1px !important;
      padding: 0 !important;
      border: 0 !important;
      white-space: nowrap !important;
    }}
    .skip-link:focus {{
      position: fixed; top: 12px; left: 12px; z-index: 1200;
      background: var(--shell-ink); color: var(--shell-canvas);
      padding: 8px 16px; border-radius: 9999px;
      text-decoration: none; font-weight: 600; font-size: 13px;
    }}

    .band-wrap {{ width: 100%; border-bottom: 1px solid var(--shell-hairline); }}
    .band-inner {{ max-width: var(--shell-max-width); margin-inline: auto; border-inline: 1px solid var(--shell-hairline); }}

    .topbar-wrap {{ position: sticky; top: 0; z-index: 300; background: var(--shell-canvas); border-bottom: 1px solid var(--shell-hairline); }}
    .topbar {{
      max-width: var(--shell-max-width); margin-inline: auto; border-inline: 1px solid var(--shell-hairline);
      display: flex; align-items: center; justify-content: space-between; gap: 20px; min-height: 60px; padding: 10px 36px;
    }}
    .topbar__title {{ font-size: 15px; font-weight: 600; letter-spacing: -0.02em; color: var(--shell-ink); text-decoration: none; white-space: nowrap; flex: 0 0 auto; }}
    .topbar__nav {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 16px; }}
    .topbar__nav a {{ font-size: 13px; font-weight: 500; color: var(--shell-muted); text-decoration: none; white-space: nowrap; transition: color 140ms ease; }}
    .topbar__nav a:hover, .topbar__nav a:focus-visible {{ color: var(--shell-ink); }}
    .topbar__nav a:focus-visible {{ outline: 2px solid var(--shell-ink); outline-offset: 4px; border-radius: 4px; }}
    .theme-toggle-btn {{
      display: inline-flex; align-items: center; gap: 8px; min-height: 36px; padding: 6px 14px; border-radius: 9999px;
      border: 1px solid var(--shell-hairline-strong); background: transparent; color: var(--shell-ink);
      font-family: var(--shell-font-sans); font-size: 13px; font-weight: 500; cursor: pointer; white-space: nowrap; flex: 0 0 auto;
      transition: background 140ms ease, border-color 140ms ease;
    }}
    .theme-toggle-btn:hover {{ background: var(--shell-surface); }}
    .theme-toggle-btn:focus-visible {{ outline: 2px solid var(--shell-ink); outline-offset: 2px; }}

    .section-intro {{ padding: 52px 40px 40px; }}
    .section-title {{ margin: 0 0 16px 0; font-size: clamp(28px, 3.6vw, 38px); font-weight: 700; line-height: 1.12; letter-spacing: -0.03em; color: var(--shell-ink); }}
    .section-lead {{ margin: 0; width: 100%; font-size: 16px; line-height: 1.58; color: var(--shell-muted); }}
    .section-lead strong {{ color: var(--shell-ink); font-weight: 600; }}
    .section-body-copy {{ margin: 16px 0 0 0; width: 100%; font-size: 15px; line-height: 1.65; color: var(--shell-muted); }}

    .subband {{ border-top: 1px solid var(--shell-hairline); }}
    .subband__head {{ display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding: 20px 40px; }}
    .subband__title {{ margin: 0; font-size: 16px; font-weight: 600; letter-spacing: -0.015em; color: var(--shell-ink); white-space: nowrap; }}
    .subband__meta {{ font-size: 13px; color: var(--shell-muted); white-space: nowrap; }}

    .swatch-grid {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); border-top: 1px solid var(--shell-hairline); }}
    @media (max-width: 980px) {{ .swatch-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }} }}
    @media (max-width: 600px) {{ .swatch-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    .swatch-cell {{ padding: 20px; border-right: 1px solid var(--shell-hairline); border-bottom: 1px solid var(--shell-hairline); display: flex; flex-direction: column; gap: 12px; min-width: 0; }}
    .swatch-chip {{ width: 100%; height: 74px; border-radius: 8px; border: 1px solid var(--shell-hairline-strong); }}
    .swatch-info {{ display: flex; flex-direction: column; gap: 2px; min-width: 0; }}
    .swatch-name {{ font-size: 13px; font-weight: 600; color: var(--shell-ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .swatch-value {{ font-family: var(--shell-font-mono); font-size: 12px; color: var(--shell-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}

    .scale-row {{ display: grid; grid-template-columns: 180px minmax(0, 1fr); border-top: 1px solid var(--shell-hairline); }}
    @media (max-width: 780px) {{ .scale-row {{ grid-template-columns: 1fr; }} }}
    .scale-row__label {{ padding: 16px 24px 16px 40px; border-right: 1px solid var(--shell-hairline); display: flex; flex-direction: column; justify-content: center; gap: 2px; }}
    .scale-row__steps {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(40px, 1fr)); padding: 14px 28px; gap: 6px; align-items: center; }}
    @media (max-width: 780px) {{ .scale-row__label {{ border-right: none; border-bottom: 1px solid var(--shell-hairline); padding: 14px 20px; }} .scale-row__steps {{ padding: 14px 20px; }} }}
    .scale-step {{ display: flex; flex-direction: column; gap: 5px; min-width: 0; }}
    .scale-step__chip {{ height: 34px; border-radius: 5px; border: 1px solid var(--shell-hairline-strong); }}
    .scale-step__num {{ font-family: var(--shell-font-mono); font-size: 10px; color: var(--shell-muted); text-align: center; white-space: nowrap; }}

    .type-list {{ border-top: 1px solid var(--shell-hairline); }}
    .type-row {{ display: grid; grid-template-columns: 310px minmax(0, 1fr); align-items: end; gap: 32px; padding: 30px 40px; border-bottom: 1px solid var(--shell-hairline); }}
    .type-row:last-child {{ border-bottom: none; }}
    @media (max-width: 760px) {{ .type-row {{ grid-template-columns: 1fr; gap: 12px; padding: 24px 20px; }} }}
    .type-row__meta {{ display: flex; flex-direction: column; gap: 4px; min-width: 0; }}
    .type-row__name {{ font-size: 13px; font-weight: 600; color: var(--shell-ink); white-space: nowrap; }}
    .type-row__specs {{ font-size: 12px; color: var(--shell-muted); white-space: nowrap; }}
    .type-row__sample {{ margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--shell-ink); }}

    .split-band {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); border-top: 1px solid var(--shell-hairline); }}
    @media (max-width: 820px) {{ .split-band {{ grid-template-columns: 1fr; }} }}
    .split-col {{ padding: 32px 40px 40px; border-right: 1px solid var(--shell-hairline); }}
    .split-col:last-child {{ border-right: none; }}
    @media (max-width: 820px) {{ .split-col {{ border-right: none; border-bottom: 1px solid var(--shell-hairline); padding: 28px 20px; }} .split-col:last-child {{ border-bottom: none; }} }}
    .split-col__head {{ display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 24px; }}
    .split-col__head h3 {{ margin: 0; font-size: 16px; font-weight: 600; color: var(--shell-ink); white-space: nowrap; }}
    .split-col__count {{ font-size: 13px; color: var(--shell-muted); white-space: nowrap; }}

    .token-box-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 12px; }}
    .token-box {{ padding: 16px; border: 1px solid var(--shell-hairline); border-radius: 8px; background: var(--shell-surface); display: flex; flex-direction: column; gap: 6px; min-width: 0; }}
    .token-box__name {{ font-size: 13px; font-weight: 600; color: var(--shell-ink); white-space: nowrap; }}
    .token-box__meta {{ font-family: var(--shell-font-mono); font-size: 12px; color: var(--shell-muted); }}
    .token-box__desc {{ font-size: 12px; color: var(--shell-faint); }}

    .radii-row {{ display: flex; flex-wrap: wrap; gap: 20px; }}
    .radii-item {{ display: flex; flex-direction: column; gap: 10px; }}
    .radii-box {{ width: 82px; height: 82px; border: 1px solid var(--shell-hairline-strong); background: var(--shell-surface); }}

    .bar-row {{ display: grid; grid-template-columns: 140px minmax(0, 1fr); align-items: center; gap: 20px; padding: 14px 0; border-top: 1px solid var(--shell-hairline); }}
    .bar-track {{ display: flex; align-items: center; gap: 14px; min-width: 0; }}
    .bar-fill {{ height: 11px; border-radius: 3px; background: var(--shell-bar); min-width: 4px; flex: 0 0 auto; }}

    .table-wrapper {{ overflow: auto; max-inline-size: 100%; border-top: 1px solid var(--shell-hairline); background: var(--shell-canvas); container-type: inline-size; }}
    .table-wrapper:focus-visible {{ outline: 2px solid var(--shell-ink); outline-offset: -2px; }}
    table.matrix-table {{ width: 100%; border-collapse: separate; border-spacing: 0; text-align: left; }}
    table.matrix-table caption {{ padding: 18px 40px; text-align: left; font-size: 15px; font-weight: 600; color: var(--shell-ink); border-bottom: 1px solid var(--shell-hairline); background: var(--shell-canvas); }}
    table.matrix-table th, table.matrix-table td {{ padding: 18px 20px; border-bottom: 1px solid var(--shell-hairline); border-right: 1px solid var(--shell-hairline); vertical-align: middle; }}
    table.matrix-table th:first-child, table.matrix-table td:first-child {{ padding-left: 40px; }}
    table.matrix-table th:last-child, table.matrix-table td:last-child {{ border-right: none; padding-right: 40px; }}
    table.matrix-table tbody tr:last-child th, table.matrix-table tbody tr:last-child td {{ border-bottom: none; }}
    table.matrix-table thead th {{ position: sticky; top: 0; z-index: 1; background: var(--shell-surface); font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--shell-muted); white-space: nowrap; }}
    table.matrix-table tbody th {{ position: sticky; left: 0; background: var(--shell-canvas); font-size: 13px; font-weight: 600; color: var(--shell-ink); white-space: nowrap; }}

    @media (max-width: 720px) {{
      .topbar {{ padding: 10px 20px; gap: 12px; }}
      .section-intro {{ padding: 40px 20px 32px; }}
      .subband__head {{ padding: 16px 20px; }}
      table.matrix-table caption {{ padding: 16px 20px; }}
      table.matrix-table th:first-child, table.matrix-table td:first-child {{ padding-left: 20px; }}
      table.matrix-table th:last-child, table.matrix-table td:last-child {{ padding-right: 20px; }}
    }}

    @media (forced-colors: active) {{
      .band-wrap, .band-inner, .subband, .swatch-cell, .swatch-chip, .token-box, .theme-toggle-btn, table.matrix-table th, table.matrix-table td {{ border-color: CanvasText; }}
      :focus-visible {{ outline: 2px solid Highlight !important; }}
    }}
"""


def _render_design_md(tokens: dict[str, Any]) -> str:
    meta = tokens["$metadata"]
    ns = meta["namespace"]
    opt = meta.get("optionalLayers", {})
    elev_enabled = opt.get("elevationAndShadows", True)
    motion_enabled = opt.get("motionAndAnimation", True)
    components = meta.get("components", [])
    comp_specs = meta.get("componentSpecs", {})
    cs = meta.get("colorStandard", "OKLCH")

    sem_c_yaml = []
    for k, v in tokens.get("semantic", {}).get("color", {}).items():
        if k.startswith("$") or not isinstance(v, dict):
            continue
        modes = v.get("$extensions", {}).get("com.design-system.modes", {})
        l_ref = modes.get("light", v["$value"])
        d_ref = modes.get("dark", v["$value"])
        l_hex = parse_color(_resolve_alias(tokens, l_ref, mode="light"))["hex"]
        d_hex = parse_color(_resolve_alias(tokens, d_ref, mode="dark"))["hex"]
        sem_c_yaml.append(f'  {k}: {{ light: "{l_hex}", dark: "{d_hex}", lightRef: "{l_ref}", darkRef: "{d_ref}" }}')

    typo_yaml = []
    typo_md_rows = []
    for k, v in tokens.get("semantic", {}).get("typography", {}).items():
        if k.startswith("$") or not isinstance(v, dict):
            continue
        val = _resolve_alias(tokens, v["$value"])
        ff = safe_font_family_css(val["fontFamily"])
        fs = _token_to_css_value("dimension", val["fontSize"], cs)
        fw = val["fontWeight"]
        lh = val["lineHeight"]
        ls = _token_to_css_value("dimension", val.get("letterSpacing", {"value": 0, "unit": "px"}), cs)
        typo_yaml.append(f'  {k}: {{ fontFamily: "{ff}", fontSize: "{fs}", fontWeight: {fw}, lineHeight: {lh}, letterSpacing: "{ls}" }}')
        typo_md_rows.append(f"| `--{k}` | `{fs}` | `{fw}` | `{lh}` | `{ls}` | {v.get('$description', '')} |")

    def _yaml_dim_or_val(cat_dict: dict[str, Any]) -> list[str]:
        out = []
        for k, v in cat_dict.items():
            if k.startswith("$") or not isinstance(v, dict) or "$value" not in v:
                continue
            val = v["$value"]
            if isinstance(val, dict) and "value" in val and "unit" in val:
                out.append(f'  {k}: "{val["value"]}{val["unit"]}"')
            elif v.get("$type") == "shadow":
                out.append(f'  {k}: "{_token_to_css_value("shadow", val, cs)}"')
            else:
                out.append(f"  {k}: {json.dumps(val)}")
        return out

    spacing_yaml = _yaml_dim_or_val(tokens.get("primitive", {}).get("spacing", {}))
    shape_yaml = _yaml_dim_or_val(tokens.get("primitive", {}).get("shape", {}))
    elev_yaml = _yaml_dim_or_val(tokens.get("primitive", {}).get("elevation", {})) if elev_enabled else []
    motion_yaml = _yaml_dim_or_val(tokens.get("primitive", {}).get("motion", {})) if motion_enabled else []
    opacity_yaml = _yaml_dim_or_val(tokens.get("primitive", {}).get("opacity", {}))
    sizing_yaml = _yaml_dim_or_val(tokens.get("primitive", {}).get("sizing", {}))

    comp_yaml_lines = []
    comp_rows_list = []
    for c in components:
        sp = comp_specs.get(c, {})
        c_sizes = sp.get("sizes", ["sm", "md", "lg"])
        c_vars = sp.get("variants", ["primary", "secondary", "ghost", "destructive"])
        c_states = sp.get("states", ["default", "hover", "active", "focus-visible", "disabled"])
        comp_yaml_lines.append(
            f'  {c}:\n    sizes: {json.dumps(c_sizes)}\n    variants: {json.dumps(c_vars)}\n'
            f'    states: {json.dumps(c_states)}\n    deliverable: "../components/{c}.html"'
        )
        comp_rows_list.append(
            f"| `{c}` | {', '.join(f'`{x}`' for x in c_sizes)} | {', '.join(f'`{x}`' for x in c_vars)} | "
            f"{', '.join(f'`{x}`' for x in c_states)} | `light`, `dark` | [components/{c}.html](../components/{c}.html) |"
        )
    comp_rows = "\n".join(comp_rows_list) or "| *(none yet)* | — | — | — | — | — |"

    a11y_rows = _evaluate_system_contrast_rows(tokens)
    a11y_table_rows = "\n".join(
        f"| {r['label']} | `{r['mode']}` | `{r['fgHex']}` on `{r['bgHex']}` | **{r['wcagRatio']}:1** (≥{r['wcagMin']}) | **Lc {r['apcaLc']}** (≥{r['apcaMin']}) | {'PASS' if r['passed'] else 'FAIL'} |"
        for r in a11y_rows
    )

    desc_escaped = str(meta.get("description", "")).replace('"', '\\"')
    traits = meta.get("definingTraits", [])
    traits_block = ("\n**Defining Traits:**\n" + "\n".join(f"- {t}" for t in traits) + "\n") if traits else ""

    return f"""---
version: "{meta['version']}"
name: "{meta['name']}"
namespace: "{ns}"
description: "{desc_escaped}"
accessibilityLevel: "{meta['accessibilityLevel']}"
colorStandard: "{meta['colorStandard']}"
colorHarmonyScheme: "{meta['colorHarmonyScheme']}"
colorPalettePhilosophy: "{meta['colorPalettePhilosophy']}"
seedColor: "{meta['seedColor']}"
seedOklch: {json.dumps(meta['seedOklch'])}
themes: {json.dumps(meta['themes'])}
optionalLayers: {json.dumps(meta['optionalLayers'])}

semanticColors:
{chr(10).join(sem_c_yaml)}

typography:
{chr(10).join(typo_yaml)}

spacingAndZIndex:
{chr(10).join(spacing_yaml)}

shapeAndStroke:
{chr(10).join(shape_yaml)}

elevation:
{chr(10).join(elev_yaml) or "  status: Omitted (Optional Layer)"}

motion:
{chr(10).join(motion_yaml) or "  status: Omitted (Optional Layer)"}

opacity:
{chr(10).join(opacity_yaml)}

sizing:
{chr(10).join(sizing_yaml)}

components:
{chr(10).join(comp_yaml_lines) or "  {}"}
---

# {meta['name']} — Design System Contract (`DESIGN.md`)

> **Lossless Single-Contract Guarantee:** This document contains the complete YAML token registry, Light/Dark mode mappings, dual-gate accessibility proofs, and per-component contracts required to reconstruct `design-tokens.json`, `DESIGN.html`, and `components/*.html` from `DESIGN.md` alone.  
> Single source of truth: [`design-tokens.json`](./design-tokens.json) (W3C DTCG 2025.10) · Visual showcase: [`DESIGN.html`](./DESIGN.html)

## 1. Identity and Philosophy

{meta.get('description', f"{meta['name']} accessible design system.")}
{traits_block}
- **System Name:** {meta['name']}
- **Token Namespace:** `{ns}`
- **Version:** `{meta['version']}`
- **Accessibility Standard:** `{meta['accessibilityLevel']}`
- **Primary Color Standard:** `{meta['colorStandard']}` (internal perceptual math in `OKLCH`; automatic `HEX`/`sRGB` fallback included)
- **Color Harmony Scheme:** `{meta['colorHarmonyScheme']}`
- **Color Palette Philosophy:** `{meta['colorPalettePhilosophy']}`
- **Primary Seed Color:** `{meta['seedColor']}` (`oklch({meta['seedOklch'][0]} {meta['seedOklch'][1]} {meta['seedOklch'][2]})`)
- **Supported Themes / Modes:** `{', '.join(meta['themes'])}`
- **Optional Layers:** `Elevation & Shadows`: `{'Enabled' if elev_enabled else 'Omitted (Optional Layer)'}`, `Motion & Animation`: `{'Enabled' if motion_enabled else 'Omitted (Optional Layer)'}`

## 2. Color Palette

- **Tier 1 Primitives:** `{len([k for k in tokens['primitive']['color'] if not k.startswith('$')])}` color tokens generated under `{meta['colorPalettePhilosophy']}` from `{meta['colorHarmonyScheme']}` seeds.
- **Tier 2 Semantic Roles:** `{len([k for k in tokens['semantic']['color'] if not k.startswith('$')])}` dual-mode (`light` / `dark`) tokens verified against `{meta['accessibilityLevel']}`.

### Dual-Gate Contrast Verification (`{meta['accessibilityLevel']}`)

| Role Pair | Mode | Pair (HEX) | WCAG 2.2 Ratio | APCA `0.0.98G-4g` | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
{a11y_table_rows}

## 3. Typography

| Semantic Token | Size | Weight | Line Height | Letter Spacing | Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
{chr(10).join(typo_md_rows)}

## 4. Spacing, Layout & Z-Index

- **Tokens:** `{len([k for k in tokens['primitive']['spacing'] if not k.startswith('$')])}` primitive tokens and `{len([k for k in tokens['semantic']['spacing'] if not k.startswith('$')])}` semantic tokens covering geometric spacing steps, container widths, and Z-Index strata.

## 5. Shape, Radius & Stroke

- **Tokens:** `{len([k for k in tokens['primitive']['shape'] if not k.startswith('$')])}` primitive tokens and `{len([k for k in tokens['semantic']['shape'] if not k.startswith('$')])}` semantic tokens covering corner radii, hairline strokes, and accessible focus rings.

## 6. Elevation & Shadows

{'- **Status:** Enabled — layered DTCG `shadow` composite tokens configured for Light and Dark elevation.' if elev_enabled else '- **Status:** Omitted (Optional Layer) — no shadow tokens required by system contract.'}

## 7. Motion & Animation

{'- **Status:** Enabled — durations capped at `<= 500ms` with `cubicBezier` easing curves and mandatory `@media (prefers-reduced-motion: reduce)`.' if motion_enabled else '- **Status:** Omitted (Optional Layer) — `@media (prefers-reduced-motion: reduce)` safeguard remains active in compiled CSS.'}

## 8. Opacity & Interaction State

- **Policy:** Disabled controls use dedicated solid/explicit disabled color tokens at `opacity: 1` (never CSS `opacity` dimming on interactive controls). Opacity scale is reserved for backdrops and frosted overlays.

## 9. Sizing

- **Target Size Guarantee:** Minimum interactive hit target set to `{'44px' if meta['accessibilityLevel'] == 'WCAG 2.2 AAA' else '24px'}` (`--{ns}-sizing-target-min`) per WCAG 2.2 {'SC 2.5.5 (AAA)' if meta['accessibilityLevel'] == 'WCAG 2.2 AAA' else 'SC 2.5.8 (AA)'}.

## 10. Components

| Component | Sizes | Visual Variants | Interactive States | Themes | Deliverable |
| :--- | :--- | :--- | :--- | :--- | :--- |
{comp_rows}
"""


def _render_design_html(tokens: dict[str, Any]) -> str:
    meta = tokens["$metadata"]
    ns = meta["namespace"]
    css_vars = compile_css_variables(tokens)
    base_css = _shared_editorial_css(ns)
    opt = meta.get("optionalLayers", {})
    elev_enabled = opt.get("elevationAndShadows", True)
    motion_enabled = opt.get("motionAndAnimation", True)
    components = meta.get("components", [])
    sem_c = tokens.get("semantic", {}).get("color", {})
    prim_c = tokens.get("primitive", {}).get("color", {})

    def swatch_cell(tok_name: str, short_name: str) -> str:
        if tok_name in sem_c:
            modes = sem_c[tok_name].get("$extensions", {}).get("com.design-system.modes", {})
            l_hex = parse_color(_resolve_alias(tokens, modes.get("light", sem_c[tok_name]["$value"]), mode="light"))["hex"]
            d_hex = parse_color(_resolve_alias(tokens, modes.get("dark", sem_c[tok_name]["$value"]), mode="dark"))["hex"]
            val_attr = f'data-hex-light="{l_hex}" data-hex-dark="{d_hex}"'
            init_val = l_hex
        elif tok_name in prim_c:
            hx = prim_c[tok_name]["$value"]["hex"]
            val_attr = f'data-hex-light="{hx}" data-hex-dark="{hx}"'
            init_val = hx
        else:
            return ""
        return (
            f'<div class="swatch-cell" title="--{_html.escape(tok_name)}">'
            f'<div class="swatch-chip" style="background:var(--{tok_name});"></div>'
            f'<div class="swatch-info">'
            f'<span class="swatch-name">{_html.escape(short_name)}</span>'
            f'<span class="swatch-value" {val_attr}>{_html.escape(init_val)}</span>'
            f'</div></div>'
        )

    def color_subband(title: str, subtitle: str, items: list[tuple[str, str]]) -> str:
        cells = [swatch_cell(tk, lbl) for tk, lbl in items if tk in sem_c or tk in prim_c]
        if not cells:
            return ""
        return (
            f'<div class="subband">'
            f'<div class="subband__head"><h3 class="subband__title">{_html.escape(title)}</h3>'
            f'<span class="subband__meta">{_html.escape(subtitle)} · {len(cells)}</span></div>'
            f'<div class="swatch-grid">{"".join(cells)}</div></div>'
        )

    def scale_rows_html() -> str:
        groups = [
            ("primary", "Primary"), ("secondary", "Secondary"), ("accent", "Accent"),
            ("neutral", "Neutral"), ("success", "Success"), ("warning", "Warning"),
            ("danger", "Danger"), ("info", "Info"),
        ]
        rows = []
        for gkey, gtitle in groups:
            prefix = f"{ns}-color-{gkey}-"
            matched = [(k[len(prefix):], k, v) for k, v in prim_c.items() if k.startswith(prefix) and isinstance(v, dict) and "$value" in v]
            if not matched:
                continue
            cells = []
            for step_lbl, tname, tdef in matched[:13]:
                hx = tdef["$value"].get("hex", "")
                cells.append(
                    f'<div class="scale-step" title="--{tname} · {hx}">'
                    f'<div class="scale-step__chip" style="background:var(--{tname});"></div>'
                    f'<span class="scale-step__num">{_html.escape(step_lbl)}</span></div>'
                )
            rows.append(
                f'<div class="scale-row">'
                f'<div class="scale-row__label"><span class="swatch-name">{_html.escape(gtitle)}</span>'
                f'<span class="swatch-value">{len(matched)} steps</span></div>'
                f'<div class="scale-row__steps">{"".join(cells)}</div></div>'
            )
        if not rows:
            return ""
        return (
            f'<div class="subband">'
            f'<div class="subband__head"><h3 class="subband__title">Primitive Scales</h3>'
            f'<span class="subband__meta">{_html.escape(meta["colorPalettePhilosophy"])} · {len(rows)} ramps</span></div>'
            f'{"".join(rows)}</div>'
        )

    # Layer 3: Typography specimens (single-quoted font-family to avoid breaking style="...")
    type_rows_html = []
    for tname, tdef in tokens.get("semantic", {}).get("typography", {}).items():
        if tname.startswith("$") or not isinstance(tdef, dict):
            continue
        short = tname.replace(f"{ns}-typography-", "")
        val = _resolve_alias(tokens, tdef["$value"])
        fs = _token_to_css_value("dimension", val["fontSize"], meta["colorStandard"])
        fw = val["fontWeight"]
        lh = val["lineHeight"]
        ls = _token_to_css_value("dimension", val.get("letterSpacing", {"value": 0, "unit": "px"}), meta["colorStandard"])
        ff = safe_font_family_css(val["fontFamily"])
        style_str = f"font-family:{ff};font-size:{fs};font-weight:{fw};line-height:{lh};letter-spacing:{ls};"
        type_rows_html.append(
            f'<div class="type-row">'
            f'<div class="type-row__meta"><span class="type-row__name">{_html.escape(short)}</span>'
            f'<span class="type-row__specs">{fs} · weight {fw} · lh {lh} · tracking {ls}</span></div>'
            f'<p class="type-row__sample" style="{_html.escape(style_str, quote=True)}">The quick brown fox jumps over the lazy dog</p>'
            f'</div>'
        )

    # Layer 4: Spacing, Layout & Z-Index
    spacing_bars, layout_cards, zindex_cards = [], [], []
    for tname, tdef in tokens.get("primitive", {}).get("spacing", {}).items():
        if tname.startswith("$") or not isinstance(tdef, dict):
            continue
        short = tname.replace(f"{ns}-spacing-", "")
        if short.startswith("zindex-"):
            zindex_cards.append(
                f'<div class="token-box"><span class="token-box__name">{_html.escape(short.replace("zindex-", ""))}</span>'
                f'<span class="token-box__meta">z-index: {tdef["$value"]}</span>'
                f'<span class="token-box__desc">{_html.escape(tdef.get("$description", ""))}</span></div>'
            )
        elif short.startswith("container-"):
            v = tdef["$value"]
            layout_cards.append(
                f'<div class="token-box"><span class="token-box__name">{_html.escape(short.replace("container-", ""))}</span>'
                f'<span class="token-box__meta">{v["value"]}{v["unit"]}</span>'
                f'<span class="token-box__desc">{_html.escape(tdef.get("$description", ""))}</span></div>'
            )
        elif isinstance(tdef["$value"], dict) and "value" in tdef["$value"]:
            v = tdef["$value"]
            px = float(v["value"])
            spacing_bars.append(
                f'<div class="bar-row">'
                f'<div><div class="token-box__name">{_html.escape(short)}</div><div class="token-box__meta">{v["value"]}{v["unit"]}</div></div>'
                f'<div class="bar-track"><div class="bar-fill" style="width:{min(px * 2.2, 240):.0f}px;"></div></div></div>'
            )

    # Layer 5: Shape, Radius & Stroke
    radii_tiles, stroke_cards = [], []
    for tname, tdef in tokens.get("primitive", {}).get("shape", {}).items():
        if tname.startswith("$") or not isinstance(tdef, dict):
            continue
        short = tname.replace(f"{ns}-shape-", "")
        v = tdef["$value"]
        v_txt = f"{v['value']}{v['unit']}" if isinstance(v, dict) and "value" in v else str(v)
        if short.startswith("radius-"):
            radii_tiles.append(
                f'<div class="radii-item">'
                f'<div class="radii-box" style="border-radius:var(--{tname});"></div>'
                f'<span class="token-box__name">{_html.escape(short.replace("radius-", ""))}</span>'
                f'<span class="token-box__meta">{_html.escape(v_txt)}</span></div>'
            )
        else:
            stroke_cards.append(
                f'<div class="token-box">'
                f'<div style="height:40px;border-radius:6px;border:{_html.escape(v_txt)} solid var(--shell-ink);background:var(--shell-canvas);"></div>'
                f'<span class="token-box__name">{_html.escape(short)}</span>'
                f'<span class="token-box__meta">{_html.escape(v_txt)}</span>'
                f'<span class="token-box__desc">{_html.escape(tdef.get("$description", ""))}</span></div>'
            )

    # Layer 6: Elevation & Shadows
    elev_cards = []
    if elev_enabled:
        for tname, tdef in tokens.get("primitive", {}).get("elevation", {}).items():
            if tname.startswith("$") or not isinstance(tdef, dict):
                continue
            short = tname.replace(f"{ns}-elevation-", "")
            elev_cards.append(
                f'<div class="token-box" style="background:var(--shell-canvas);">'
                f'<div style="height:64px;border-radius:8px;background:var(--shell-surface);box-shadow:var(--{tname});border:1px solid var(--shell-hairline);"></div>'
                f'<span class="token-box__name">{_html.escape(short)}</span>'
                f'<span class="token-box__meta">--{_html.escape(tname)}</span>'
                f'<span class="token-box__desc">{_html.escape(tdef.get("$description", ""))}</span></div>'
            )

    # Layer 7: Motion & Animation
    dur_bars, ease_cards = [], []
    if motion_enabled:
        for tname, tdef in tokens.get("primitive", {}).get("motion", {}).items():
            if tname.startswith("$") or not isinstance(tdef, dict):
                continue
            short = tname.replace(f"{ns}-motion-", "")
            if tdef.get("$type") == "duration" and isinstance(tdef["$value"], dict):
                ms = float(tdef["$value"]["value"])
                dur_bars.append(
                    f'<div class="bar-row">'
                    f'<div><div class="token-box__name">{_html.escape(short.replace("duration-", ""))}</div><div class="token-box__meta">{tdef["$value"]["value"]}{tdef["$value"]["unit"]}</div></div>'
                    f'<div class="bar-track"><div class="bar-fill" style="width:{min(ms * 0.65, 220):.0f}px;"></div></div></div>'
                )
            elif isinstance(tdef["$value"], list):
                ease_cards.append(
                    f'<div class="token-box">'
                    f'<span class="token-box__name">{_html.escape(short.replace("easing-", ""))}</span>'
                    f'<span class="token-box__meta">cubic-bezier({", ".join(str(x) for x in tdef["$value"])})</span>'
                    f'<span class="token-box__desc">{_html.escape(tdef.get("$description", ""))}</span></div>'
                )

    # Layer 8: Opacity & Interaction State
    op_cards = []
    for tname, tdef in tokens.get("primitive", {}).get("opacity", {}).items():
        if tname.startswith("$") or not isinstance(tdef, dict):
            continue
        short = tname.replace(f"{ns}-opacity-", "")
        op_cards.append(
            f'<div class="token-box">'
            f'<div style="height:44px;border-radius:6px;border:1px solid var(--shell-hairline-strong);background:repeating-conic-gradient(var(--shell-hairline) 0% 25%, transparent 0% 50%) 50% / 12px 12px;overflow:hidden;">'
            f'<div style="width:100%;height:100%;background:var(--shell-ink);opacity:var(--{tname});"></div></div>'
            f'<span class="token-box__name">{_html.escape(short)}</span>'
            f'<span class="token-box__meta">opacity: {tdef["$value"]}</span>'
            f'<span class="token-box__desc">{_html.escape(tdef.get("$description", ""))}</span></div>'
        )

    # Layer 9: Sizing
    sizing_bars = []
    for tname, tdef in tokens.get("primitive", {}).get("sizing", {}).items():
        if tname.startswith("$") or not isinstance(tdef, dict):
            continue
        short = tname.replace(f"{ns}-sizing-", "")
        v = tdef["$value"]
        px = float(v["value"]) if isinstance(v, dict) and "value" in v else 24.0
        v_txt = f"{v['value']}{v['unit']}" if isinstance(v, dict) and "value" in v else str(v)
        sizing_bars.append(
            f'<div class="bar-row">'
            f'<div><div class="token-box__name">{_html.escape(short)}</div><div class="token-box__meta">{_html.escape(v_txt)}</div></div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{min(px * 2.8, 220):.0f}px;"></div><span class="token-box__desc">{_html.escape(tdef.get("$description", ""))}</span></div></div>'
        )

    # Layer 10: Components
    comp_embeds = []
    for c in components:
        comp_embeds.append(
            f'<div class="comp-embed">'
            f'<div class="comp-embed__head"><span class="subband__title">{_html.escape(c)}</span>'
            f'<a href="../components/{_html.escape(c)}.html">Open standalone →</a></div>'
            f'<iframe data-ds-component-frame src="../components/{_html.escape(c)}.html" title="{_html.escape(c)} component matrix showcase" loading="lazy"></iframe></div>'
        )
    comp_html = "".join(comp_embeds) or '<div class="subband" style="padding:28px 40px;"><p class="section-body-copy" style="margin:0;">No components generated yet. Use <code>component-design</code> to add components.</p></div>'

    sem_color_count = sum(1 for k in sem_c if not k.startswith("$"))
    type_count = len(type_rows_html)
    elev_body = (
        f'<div class="subband" style="padding:32px 40px 40px;"><div class="token-box-grid">{"".join(elev_cards)}</div></div>'
        if elev_enabled else
        '<div class="subband" style="padding:28px 40px;"><p class="section-body-copy" style="margin:0;">Status: Omitted (Optional Layer).</p></div>'
    )
    motion_body = (
        f'<div class="split-band">'
        f'<div class="split-col"><div class="split-col__head"><h3>Durations</h3><span class="split-col__count">{len(dur_bars)}</span></div>{"".join(dur_bars)}</div>'
        f'<div class="split-col"><div class="split-col__head"><h3>Easing</h3><span class="split-col__count">{len(ease_cards)}</span></div><div class="token-box-grid">{"".join(ease_cards)}</div></div>'
        f'</div>'
        if motion_enabled else
        '<div class="subband" style="padding:28px 40px;"><p class="section-body-copy" style="margin:0;">Status: Omitted (Optional Layer). <code>prefers-reduced-motion: reduce</code> remains active in CSS.</p></div>'
    )

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
{_THEME_HEAD_JS}
  <title>{_html.escape(meta['name'])}</title>
  <style id="design-tokens-root">
{css_vars}
  </style>
  <style>
{base_css}
    .comp-embed {{ border-top: 1px solid var(--shell-hairline); }}
    .comp-embed__head {{ display: flex; justify-content: space-between; align-items: center; padding: 18px 40px; border-bottom: 1px solid var(--shell-hairline); }}
    .comp-embed__head a {{ color: var(--shell-muted); font-size: 13px; text-decoration: none; white-space: nowrap; }}
    .comp-embed__head a:hover {{ color: var(--shell-ink); }}
    .comp-embed iframe {{ width: 100%; height: 660px; border: 0; display: block; background: var(--shell-canvas); }}
  </style>
</head>
<body>
  <a href="#main-content" class="skip-link visually-hidden">Skip to content</a>

  <header class="topbar-wrap">
    <div class="topbar">
      <a href="#layer-1-identity" class="topbar__title">{_html.escape(meta['name'])}</a>
      <nav class="topbar__nav" aria-label="Design System Sections">
        <a href="#layer-1-identity">About</a>
        <a href="#layer-2-color">Colors</a>
        <a href="#layer-3-typography">Typography</a>
        <a href="#layer-4-spacing">Spacing</a>
        <a href="#layer-5-shape">Shape</a>
        <a href="#layer-6-elevation">Elevation</a>
        <a href="#layer-7-motion">Motion</a>
        <a href="#layer-8-opacity">Opacity</a>
        <a href="#layer-9-sizing">Sizing</a>
        <a href="#layer-10-components">Components</a>
      </nav>
      <button type="button" id="global-theme-toggle" class="theme-toggle-btn" aria-pressed="false">
        <span aria-hidden="true">◐</span>
        <span id="global-theme-label">Theme</span>
      </button>
    </div>
  </header>

  <main id="main-content">
    <section id="layer-1-identity" class="band-wrap">
      <div class="band-inner">
        <div class="section-intro">
          <h1 class="section-title">About {_html.escape(meta['name'])}</h1>
          <p class="section-lead"><strong>{_html.escape(meta['name'])} v{_html.escape(meta['version'])}.</strong> {_html.escape(meta.get('description', ''))}</p>
          <p class="section-body-copy">Built with a {_html.escape(meta['colorHarmonyScheme'])} harmony under the {_html.escape(meta['colorPalettePhilosophy'])} philosophy in {_html.escape(meta['colorStandard'])} (with automatic HEX/sRGB fallbacks), verified end-to-end against {_html.escape(meta['accessibilityLevel'])} across Light and Dark modes.</p>
        </div>
        <div class="subband">
          <div class="swatch-grid">
            <div class="swatch-cell"><span class="swatch-name">Accessibility</span><span class="swatch-value">{_html.escape(meta['accessibilityLevel'])}</span></div>
            <div class="swatch-cell"><span class="swatch-name">Philosophy</span><span class="swatch-value">{_html.escape(meta['colorPalettePhilosophy'])}</span></div>
            <div class="swatch-cell"><span class="swatch-name">Harmony</span><span class="swatch-value">{_html.escape(meta['colorHarmonyScheme'])}</span></div>
            <div class="swatch-cell"><span class="swatch-name">Standard</span><span class="swatch-value">{_html.escape(meta['colorStandard'])}</span></div>
            <div class="swatch-cell"><span class="swatch-name">Seed</span><span class="swatch-value">{_html.escape(meta['seedColor'])}</span></div>
            <div class="swatch-cell"><span class="swatch-name">Namespace</span><span class="swatch-value">--{_html.escape(ns)}-*</span></div>
          </div>
        </div>
      </div>
    </section>

    <section id="layer-2-color" class="band-wrap">
      <div class="band-inner">
        <div class="section-intro">
          <h2 class="section-title">{sem_color_count} semantic colors</h2>
          <p class="section-lead"><strong>{_html.escape(meta['name'])} anchors on {_html.escape(meta['seedColor'])} as its primary seed.</strong> Generated as a {_html.escape(meta['colorHarmonyScheme'])} {_html.escape(meta['colorPalettePhilosophy'])} in {_html.escape(meta['colorStandard'])}; all values below resolve live for the active theme.</p>
        </div>
        {color_subband("Brand & Accent", f"{meta['colorHarmonyScheme']} CTA & focus", [
            (f"{ns}-color-action-primary-default", "action-primary"),
            (f"{ns}-color-action-primary-hover", "action-primary-hover"),
            (f"{ns}-color-action-primary-active", "action-primary-active"),
            (f"{ns}-color-border-focus-default", "border-focus"),
        ])}
        {color_subband("Surface", "Page, card and hairline backgrounds", [
            (f"{ns}-color-bg-canvas-default", "bg-canvas"),
            (f"{ns}-color-bg-surface-default", "bg-surface"),
            (f"{ns}-color-bg-surface-elevated", "bg-elevated"),
            (f"{ns}-color-border-subtle-default", "border-subtle"),
        ])}
        {color_subband("Text", "Typography contrast ladder", [
            (f"{ns}-color-text-primary-default", "text-primary"),
            (f"{ns}-color-text-muted-default", "text-muted"),
            (f"{ns}-color-text-on-action-default", "text-on-action"),
        ])}
        {color_subband("Feedback & Status", "Semantic actions & validation", [
            (f"{ns}-color-action-success-default", "action-success"),
            (f"{ns}-color-action-success-hover", "action-success-hover"),
            (f"{ns}-color-action-danger-default", "action-danger"),
            (f"{ns}-color-action-danger-hover", "action-danger-hover"),
            (f"{ns}-color-feedback-warning-default", "feedback-warning"),
            (f"{ns}-color-feedback-info-default", "feedback-info"),
        ])}
        {color_subband("Disabled", "Solid tokens at opacity 1", [
            (f"{ns}-color-disabled-bg-default", "disabled-bg"),
            (f"{ns}-color-disabled-fg-default", "disabled-fg"),
        ])}
        {scale_rows_html()}
      </div>
    </section>

    <section id="layer-3-typography" class="band-wrap">
      <div class="band-inner">
        <div class="section-intro">
          <h2 class="section-title">{type_count} type tokens</h2>
          <p class="section-lead"><strong>Rendered live across {type_count} semantic typography roles.</strong> Native font smoothing (<code>auto</code>) preserved for APCA stroke integrity.</p>
        </div>
        <div class="type-list">{"".join(type_rows_html)}</div>
      </div>
    </section>

    <section id="layer-4-spacing" class="band-wrap">
      <div class="band-inner">
        <div class="section-intro">
          <h2 class="section-title">Spacing, layout &amp; z-index</h2>
          <p class="section-lead"><strong>{len(spacing_bars)} spacing values, {len(layout_cards)} container widths, and {len(zindex_cards)} z-index strata.</strong> Geometric structural rhythm paired with explicit elevation stacking layers.</p>
        </div>
        <div class="split-band">
          <div class="split-col"><div class="split-col__head"><h3>Spacing</h3><span class="split-col__count">{len(spacing_bars)}</span></div>{"".join(spacing_bars)}</div>
          <div class="split-col"><div class="split-col__head"><h3>Layout &amp; Z-Index</h3><span class="split-col__count">{len(layout_cards) + len(zindex_cards)}</span></div><div class="token-box-grid" style="margin-bottom:14px;">{"".join(layout_cards)}</div><div class="token-box-grid">{"".join(zindex_cards)}</div></div>
        </div>
      </div>
    </section>

    <section id="layer-5-shape" class="band-wrap">
      <div class="band-inner">
        <div class="section-intro">
          <h2 class="section-title">Shape, radius &amp; stroke</h2>
          <p class="section-lead"><strong>{len(radii_tiles)} corner radii and {len(stroke_cards)} stroke widths.</strong> Geometric corner radii paired with hairline borders and high-contrast focus rings.</p>
        </div>
        <div class="split-band">
          <div class="split-col"><div class="split-col__head"><h3>Radii</h3><span class="split-col__count">{len(radii_tiles)}</span></div><div class="radii-row">{"".join(radii_tiles)}</div></div>
          <div class="split-col"><div class="split-col__head"><h3>Strokes</h3><span class="split-col__count">{len(stroke_cards)}</span></div><div class="token-box-grid">{"".join(stroke_cards)}</div></div>
        </div>
      </div>
    </section>

    <section id="layer-6-elevation" class="band-wrap">
      <div class="band-inner">
        <div class="section-intro">
          <h2 class="section-title">Elevation &amp; shadows</h2>
          <p class="section-lead"><strong>{'%d shadow levels configured.' % len(elev_cards) if elev_enabled else 'Omitted (Optional Layer).'}</strong></p>
        </div>
        {elev_body}
      </div>
    </section>

    <section id="layer-7-motion" class="band-wrap">
      <div class="band-inner">
        <div class="section-intro">
          <h2 class="section-title">Motion &amp; animation</h2>
          <p class="section-lead"><strong>{'%d durations and %d easing curves.' % (len(dur_bars), len(ease_cards)) if motion_enabled else 'Omitted (Optional Layer).'}</strong> Reduced-motion safeguards remain active in compiled CSS.</p>
        </div>
        {motion_body}
      </div>
    </section>

    <section id="layer-8-opacity" class="band-wrap">
      <div class="band-inner">
        <div class="section-intro">
          <h2 class="section-title">Opacity &amp; interaction state</h2>
          <p class="section-lead"><strong>{len(op_cards)} opacity tokens and solid disabled contract.</strong> Disabled interactive controls always render at opacity 1 using dedicated color tokens.</p>
        </div>
        <div class="split-band">
          <div class="split-col"><div class="split-col__head"><h3>Opacity</h3><span class="split-col__count">{len(op_cards)}</span></div><div class="token-box-grid">{"".join(op_cards)}</div></div>
          <div class="split-col">
            <div class="split-col__head"><h3>Interaction States</h3><span class="split-col__count">5</span></div>
            <div class="token-box-grid">
              <div class="token-box"><span class="token-box__name">default</span><span class="token-box__desc">Resting semantic role</span></div>
              <div class="token-box"><span class="token-box__name">hover</span><span class="token-box__desc">Optional pointer tonal shift</span></div>
              <div class="token-box"><span class="token-box__name">active</span><span class="token-box__desc">Pressed state feedback</span></div>
              <div class="token-box"><span class="token-box__name">focus-visible</span><span class="token-box__desc">Keyboard focus ring (SC 2.4.7 / 2.4.13)</span></div>
              <div class="token-box"><span class="token-box__name">disabled</span><span class="token-box__desc">Solid tokens, opacity: 1</span></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="layer-9-sizing" class="band-wrap">
      <div class="band-inner">
        <div class="section-intro">
          <h2 class="section-title">Sizing &amp; touch targets</h2>
          <p class="section-lead"><strong>{len(sizing_bars)} sizing tokens enforcing the active WCAG 2.2 minimum interactive hit target.</strong></p>
        </div>
        <div class="subband" style="padding:24px 40px 36px;">{"".join(sizing_bars)}</div>
      </div>
    </section>

    <section id="layer-10-components" class="band-wrap">
      <div class="band-inner">
        <div class="section-intro">
          <h2 class="section-title">Components</h2>
          <p class="section-lead"><strong>Token-pure HTML5 components synced to the global theme toggle.</strong> Each component renders analytical variant × state × size matrices.</p>
        </div>
        {comp_html}
      </div>
    </section>
  </main>

  <script>
    (function () {{
      function syncHexLabels() {{
        const theme = document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light';
        document.querySelectorAll('[data-hex-light]').forEach((el) => {{
          el.textContent = theme === 'dark' ? el.dataset.hexDark : el.dataset.hexLight;
        }});
      }}
      new MutationObserver(syncHexLabels).observe(document.documentElement, {{ attributes: true, attributeFilter: ['data-theme'] }});
      window.addEventListener('DOMContentLoaded', syncHexLabels);
      syncHexLabels();
    }})();
  </script>
{_THEME_TOGGLE_JS}
</body>
</html>
"""


def _render_component_html(tokens: dict[str, Any], name: str, spec: dict[str, Any]) -> str:
    meta = tokens["$metadata"]
    ns = meta["namespace"]
    css_vars = compile_css_variables(tokens)
    base_css = _shared_editorial_css(ns)
    sizes = list(spec.get("sizes", ["sm", "md", "lg"]))
    variants = list(spec.get("variants", ["primary", "secondary", "ghost", "destructive"]))
    states = list(spec.get("states", ["default", "hover", "active", "focus-visible", "disabled"]))
    title = name.replace("-", " ").title()

    variant_icons = {
        "success": '<svg class="comp-icon" viewBox="0 0 24 24" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>',
        "destructive": '<svg class="comp-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    }
    state_labels = {
        "default": "Default", "hover": "Hover", "active": "Active",
        "focus-visible": "Focus-Visible", "disabled": "Disabled",
    }

    def build_size_table(sz: str) -> str:
        header_cols = "".join(f'<th scope="col">{_html.escape(state_labels.get(st, st.title()))}</th>' for st in states)
        rows = []
        for var_name in variants:
            icon_svg = variant_icons.get(var_name, "")
            tds = []
            for st in states:
                disabled_attr = ' disabled aria-disabled="true"' if st == "disabled" else ""
                state_cls = f" is-{st}" if st not in ("default", "disabled") else ""
                cls = f"ds-comp ds-comp--{var_name} ds-comp--{sz}{state_cls}"
                tds.append(f'<td><button type="button" class="{cls}"{disabled_attr}>{icon_svg}<span>{_html.escape(var_name.title())}</span></button></td>')
            rows.append(f'<tr><th scope="row">{_html.escape(var_name.title())}</th>{"".join(tds)}</tr>')
        return f"""
        <div id="matrix-{sz}" class="table-wrapper" tabindex="0" role="region" aria-labelledby="cap-{name}-{sz}">
          <table class="matrix-table">
            <caption id="cap-{name}-{sz}">Size: {_html.escape(sz)} — Variants × States</caption>
            <thead><tr><th scope="col">Variant</th>{header_cols}</tr></thead>
            <tbody>{"".join(rows)}</tbody>
          </table>
        </div>"""

    size_tables_html = "".join(build_size_table(sz) for sz in sizes)

    size_header_cols = "".join(f'<th scope="col">{_html.escape(sz)}</th>' for sz in sizes)
    size_rows = []
    for var_name in variants:
        icon_svg = variant_icons.get(var_name, "")
        cells = [
            f'<td><button type="button" class="ds-comp ds-comp--{var_name} ds-comp--{sz}">{icon_svg}<span>{_html.escape(var_name.title())} ({_html.escape(sz)})</span></button></td>'
            for sz in sizes
        ]
        size_rows.append(f'<tr><th scope="row">{_html.escape(var_name.title())}</th>{"".join(cells)}</tr>')

    nav_size_links = "".join(f'<a href="#matrix-{_html.escape(sz)}">{_html.escape(sz)}</a>' for sz in sizes)

    # Emit variant CSS strictly for configured variants & states
    var_css_blocks = []
    if "primary" in variants:
        var_css_blocks.append(f".ds-comp--primary {{ background: var(--{ns}-color-{name}-bg-primary-default); color: var(--{ns}-color-{name}-text-primary-default); }}")
        if "hover" in states:
            var_css_blocks.append(f".ds-comp--primary:hover, .ds-comp--primary.is-hover {{ background: var(--{ns}-color-{name}-bg-primary-hover); }}")
        if "active" in states:
            var_css_blocks.append(f".ds-comp--primary:active, .ds-comp--primary.is-active {{ background: var(--{ns}-color-{name}-bg-primary-active); }}")
    if "secondary" in variants:
        var_css_blocks.append(f".ds-comp--secondary {{ background: var(--{ns}-color-{name}-bg-secondary-default); color: var(--{ns}-color-{name}-text-secondary-default); border-color: var(--{ns}-color-border-subtle-default); }}")
        if "hover" in states:
            var_css_blocks.append(f".ds-comp--secondary:hover, .ds-comp--secondary.is-hover {{ background: var(--{ns}-color-{name}-bg-secondary-hover); }}")
    if "ghost" in variants:
        var_css_blocks.append(f".ds-comp--ghost {{ background: transparent; color: var(--{ns}-color-{name}-text-ghost-default); }}")
        if "hover" in states:
            var_css_blocks.append(f".ds-comp--ghost:hover, .ds-comp--ghost.is-hover {{ background: var(--{ns}-color-{name}-bg-ghost-hover); }}")
    if "success" in variants:
        var_css_blocks.append(f".ds-comp--success {{ background: var(--{ns}-color-{name}-bg-success-default); color: var(--{ns}-color-{name}-text-success-default); }}")
        if "hover" in states:
            var_css_blocks.append(f".ds-comp--success:hover, .ds-comp--success.is-hover {{ background: var(--{ns}-color-{name}-bg-success-hover); }}")
        if "active" in states:
            var_css_blocks.append(f".ds-comp--success:active, .ds-comp--success.is-active {{ background: var(--{ns}-color-{name}-bg-success-active); }}")
    if "destructive" in variants:
        var_css_blocks.append(f".ds-comp--destructive {{ background: var(--{ns}-color-{name}-bg-destructive-default); color: var(--{ns}-color-{name}-text-destructive-default); }}")
        if "hover" in states:
            var_css_blocks.append(f".ds-comp--destructive:hover, .ds-comp--destructive.is-hover {{ background: var(--{ns}-color-{name}-bg-destructive-hover); }}")
        if "active" in states:
            var_css_blocks.append(f".ds-comp--destructive:active, .ds-comp--destructive.is-active {{ background: var(--{ns}-color-{name}-bg-destructive-active); }}")

    size_css_blocks = []
    size_pad = {"sm": ("1", "3", "sm"), "md": ("2", "4", "md"), "lg": ("3", "5", "lg")}
    for sz in sizes:
        pv, ph, fs_k = size_pad.get(sz, ("2", "4", "md"))
        size_css_blocks.append(
            f".ds-comp--{sz} {{ min-height: var(--{ns}-sizing-{name}-height-{sz}); padding: var(--{ns}-spacing-{pv}) var(--{ns}-spacing-{ph}); font-size: var(--{ns}-typography-size-{fs_k}); }}"
        )

    disabled_css = (
        f".ds-comp:disabled {{ background: var(--{ns}-color-{name}-bg-disabled-default); color: var(--{ns}-color-{name}-text-disabled-default); border-color: transparent; opacity: var(--{ns}-opacity-solid-100); cursor: not-allowed; }}"
        if "disabled" in states else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
{_THEME_HEAD_JS}
  <title>{_html.escape(title)} — {_html.escape(meta['name'])}</title>
  <style id="design-tokens-root">
{css_vars}
  </style>
  <style>
{base_css}
    .ds-comp {{
      font-family: var(--{ns}-typography-family-sans);
      font-weight: var(--{ns}-typography-weight-semibold);
      border-radius: var(--{ns}-shape-{name}-radius-default);
      border: var(--{ns}-shape-stroke-thin) solid transparent;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: var(--{ns}-spacing-2);
      min-width: var(--{ns}-sizing-target-min);
      white-space: nowrap;
    }}
    {chr(10).join("    " + b for b in size_css_blocks)}
    {chr(10).join("    " + b for b in var_css_blocks)}
    .ds-comp:focus-visible, .ds-comp.is-focus-visible {{ outline: var(--{ns}-shape-stroke-focus) solid var(--{ns}-color-border-focus-default); outline-offset: 2px; }}
    {disabled_css}
    .comp-icon {{ width: 16px; height: 16px; stroke: currentColor; fill: none; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round; flex: 0 0 auto; }}
  </style>
</head>
<body>
  <a href="#main-content" class="skip-link visually-hidden">Skip to content</a>
  <header class="topbar-wrap">
    <div class="topbar">
      <a href="../submissions/DESIGN.html" class="topbar__title">{_html.escape(title)}</a>
      <nav class="topbar__nav" aria-label="{_html.escape(title)} Sections">
        <a href="../submissions/DESIGN.html">← {_html.escape(meta['name'])}</a>
        {nav_size_links}
        <a href="#matrix-sizes">Sizes</a>
      </nav>
      <button type="button" id="global-theme-toggle" class="theme-toggle-btn" aria-pressed="false">
        <span aria-hidden="true">◐</span>
        <span id="global-theme-label">Theme</span>
      </button>
    </div>
  </header>

  <main id="main-content">
    <section class="band-wrap">
      <div class="band-inner">
        <div class="section-intro">
          <h1 class="section-title">{_html.escape(title)} matrix</h1>
          <p class="section-lead"><strong>{len(variants)} hierarchies × {len(states)} states × {len(sizes)} sizes.</strong> Rendered strictly from Tier 3 component tokens synced to the single global theme toggle.</p>
        </div>
        {size_tables_html}
        <div id="matrix-sizes" class="table-wrapper" tabindex="0" role="region" aria-labelledby="cap-{name}-sizes">
          <table class="matrix-table">
            <caption id="cap-{name}-sizes">Size Comparison — Variants × {' / '.join(sizes)}</caption>
            <thead><tr><th scope="col">Variant</th>{size_header_cols}</tr></thead>
            <tbody>{"".join(size_rows)}</tbody>
          </table>
        </div>
      </div>
    </section>
  </main>
{_THEME_TOGGLE_JS}
</body>
</html>
"""


def _write_submissions(workdir: Path, tokens: dict[str, Any]) -> None:
    sub_dir = workdir / "docs" / "ui-design" / "submissions"
    sub_dir.mkdir(parents=True, exist_ok=True)
    tokens["$extensions"]["com.design-system.metadata"] = json.loads(json.dumps(tokens["$metadata"]))
    (sub_dir / "design-tokens.json").write_text(json.dumps(tokens, indent=2) + "\n", encoding="utf-8")
    (sub_dir / "DESIGN.md").write_text(_render_design_md(tokens), encoding="utf-8")
    (sub_dir / "DESIGN.html").write_text(_render_design_html(tokens), encoding="utf-8")


def create_design_system(workdir: Path, config: dict[str, Any]) -> dict[str, Any]:
    """Create a complete W3C DTCG 2025.10 design system across all 9 layers."""
    _validate_foundation_config(config)
    workdir = Path(workdir)
    name = str(config.get("name", "Design System"))
    ns = str(config.get("namespace", "ds")).strip().lower()
    level = config["accessibilityLevel"]
    philosophy = config["colorPalettePhilosophy"]
    harmony = config["colorHarmonyScheme"]
    color_std = config["colorStandard"]
    seed_color = str(config.get("seedColor", "#4393e1"))
    opt_layers = config.get("optionalLayers", {"elevationAndShadows": True, "motionAndAnimation": True})
    elev_enabled = bool(opt_layers.get("elevationAndShadows", True))
    motion_enabled = bool(opt_layers.get("motionAndAnimation", True))

    seeds = generate_harmony_seeds(seed_color, harmony)
    scales = generate_palette_scales(seeds, philosophy, color_std)

    prim_colors: dict[str, Any] = {"$type": "color"}
    for role_name, steps in scales.items():
        for step_key, tok_obj in steps.items():
            prim_colors[f"{ns}-color-{role_name}-{step_key}"] = tok_obj

    def _sem_color(role_group: str, role_key: str, desc: str) -> dict[str, Any]:
        l_step = _pick_step_for_philosophy(philosophy, role_key, "light")
        d_step = _pick_step_for_philosophy(philosophy, role_key, "dark")
        l_ref = f"{{primitive.color.{ns}-color-{role_group}-{l_step}}}"
        d_ref = f"{{primitive.color.{ns}-color-{role_group}-{d_step}}}"
        return {
            "$value": l_ref,
            "$description": desc,
            "$extensions": {"com.design-system.modes": {"light": l_ref, "dark": d_ref}},
        }

    sem_colors: dict[str, Any] = {
        "$type": "color",
        f"{ns}-color-bg-canvas-default": _sem_color("neutral", "canvas", "Default page canvas background"),
        f"{ns}-color-bg-surface-default": _sem_color("neutral", "surface", "Default elevated surface"),
        f"{ns}-color-bg-surface-elevated": _sem_color("neutral", "surface_elevated", "Elevated interactive surface step"),
        f"{ns}-color-text-primary-default": _sem_color("neutral", "text_primary", "Primary high-contrast text"),
        f"{ns}-color-text-muted-default": _sem_color("neutral", "text_muted", "Secondary/muted readable text"),
        f"{ns}-color-text-on-action-default": _sem_color("neutral", "on_action", "Foreground text on solid action fills"),
        f"{ns}-color-action-primary-default": _sem_color("primary", "action_default", "Primary interactive fill"),
        f"{ns}-color-action-primary-hover": _sem_color("primary", "action_hover", "Primary interactive hover fill"),
        f"{ns}-color-action-primary-active": _sem_color("primary", "action_active", "Primary interactive active fill"),
        f"{ns}-color-action-success-default": _sem_color("success", "action_default", "Success interactive fill (dual-gate verified)"),
        f"{ns}-color-action-success-hover": _sem_color("success", "action_hover", "Success interactive hover fill"),
        f"{ns}-color-action-success-active": _sem_color("success", "action_active", "Success interactive active fill"),
        f"{ns}-color-action-danger-default": _sem_color("danger", "action_default", "Destructive action fill"),
        f"{ns}-color-action-danger-hover": _sem_color("danger", "action_hover", "Destructive interactive hover fill"),
        f"{ns}-color-action-danger-active": _sem_color("danger", "action_active", "Destructive interactive active fill"),
        f"{ns}-color-feedback-success-default": _sem_color("success", "action_default", "Success semantic feedback color"),
        f"{ns}-color-feedback-warning-default": _sem_color("warning", "action_default", "Warning semantic feedback color"),
        f"{ns}-color-feedback-danger-default": _sem_color("danger", "action_default", "Error/danger semantic feedback color"),
        f"{ns}-color-feedback-info-default": _sem_color("info", "action_default", "Informational semantic feedback color"),
        f"{ns}-color-border-subtle-default": _sem_color("neutral", "border_subtle", "Subtle container border"),
        f"{ns}-color-border-focus-default": _sem_color("primary", "border_focus", "Keyboard focus ring color"),
        f"{ns}-color-disabled-bg-default": _sem_color("neutral", "disabled_bg", "Solid disabled background (opacity 1)"),
        f"{ns}-color-disabled-fg-default": _sem_color("neutral", "disabled_fg", "Solid disabled foreground (opacity 1)"),
    }

    target_min = 44 if level == "WCAG 2.2 AAA" else 24
    metadata = {
        "name": name,
        "namespace": ns,
        "version": str(config.get("version", "1.0.0")),
        "description": str(config.get("description", f"{name} accessible design system")),
        "accessibilityLevel": level,
        "colorStandard": color_std,
        "colorHarmonyScheme": harmony,
        "colorPalettePhilosophy": philosophy,
        "seedColor": parse_color(seed_color)["hex"],
        "seedOklch": parse_color(seed_color)["oklch"],
        "themes": ["light", "dark"],
        "optionalLayers": {"elevationAndShadows": elev_enabled, "motionAndAnimation": motion_enabled},
        "components": [],
        "componentSpecs": {},
    }

    tokens: dict[str, Any] = {
        "$schema": DTCG_SCHEMA_URL,
        "$metadata": metadata,
        "$extensions": {"com.design-system.metadata": json.loads(json.dumps(metadata))},
        "primitive": {
            "color": prim_colors,
            "typography": {
                f"{ns}-typography-family-sans": {"$type": "fontFamily", "$value": ["Inter", "system-ui", "sans-serif"], "$description": "Primary sans-serif typeface"},
                f"{ns}-typography-size-sm": {"$type": "dimension", "$value": {"value": 14, "unit": "px"}, "$description": "Small font size"},
                f"{ns}-typography-size-md": {"$type": "dimension", "$value": {"value": 16, "unit": "px"}, "$description": "Base body font size"},
                f"{ns}-typography-size-lg": {"$type": "dimension", "$value": {"value": 20, "unit": "px"}, "$description": "Large font size"},
                f"{ns}-typography-weight-regular": {"$type": "fontWeight", "$value": 400, "$description": "Regular weight"},
                f"{ns}-typography-weight-semibold": {"$type": "fontWeight", "$value": 600, "$description": "Semibold weight"},
                f"{ns}-typography-lineheight-base": {"$type": "number", "$value": 1.5, "$description": "Base line-height ratio"},
            },
            "spacing": {
                f"{ns}-spacing-1": {"$type": "dimension", "$value": {"value": 4, "unit": "px"}, "$description": "4px spacing step"},
                f"{ns}-spacing-2": {"$type": "dimension", "$value": {"value": 8, "unit": "px"}, "$description": "8px spacing step"},
                f"{ns}-spacing-3": {"$type": "dimension", "$value": {"value": 12, "unit": "px"}, "$description": "12px spacing step"},
                f"{ns}-spacing-4": {"$type": "dimension", "$value": {"value": 16, "unit": "px"}, "$description": "16px spacing step"},
                f"{ns}-spacing-5": {"$type": "dimension", "$value": {"value": 24, "unit": "px"}, "$description": "24px spacing step"},
                f"{ns}-spacing-6": {"$type": "dimension", "$value": {"value": 32, "unit": "px"}, "$description": "32px spacing step"},
                f"{ns}-spacing-8": {"$type": "dimension", "$value": {"value": 48, "unit": "px"}, "$description": "48px spacing step"},
                f"{ns}-spacing-zindex-base": {"$type": "number", "$value": 0, "$description": "Base z-index"},
                f"{ns}-spacing-zindex-modal": {"$type": "number", "$value": 1000, "$description": "Modal z-index"},
            },
            "shape": {
                f"{ns}-shape-radius-sm": {"$type": "dimension", "$value": {"value": 4, "unit": "px"}, "$description": "Small radius"},
                f"{ns}-shape-radius-md": {"$type": "dimension", "$value": {"value": 8, "unit": "px"}, "$description": "Medium radius"},
                f"{ns}-shape-radius-full": {"$type": "dimension", "$value": {"value": 9999, "unit": "px"}, "$description": "Pill radius"},
                f"{ns}-shape-stroke-thin": {"$type": "dimension", "$value": {"value": 1, "unit": "px"}, "$description": "Thin stroke width"},
                f"{ns}-shape-stroke-focus": {"$type": "dimension", "$value": {"value": 2, "unit": "px"}, "$description": "Focus ring width"},
            },
            "opacity": {
                f"{ns}-opacity-backdrop-50": {"$type": "number", "$value": 0.5, "$description": "Modal backdrop opacity"},
                f"{ns}-opacity-solid-100": {"$type": "number", "$value": 1.0, "$description": "Full opacity for solid disabled controls"},
            },
            "sizing": {
                f"{ns}-sizing-target-min": {"$type": "dimension", "$value": {"value": target_min, "unit": "px"}, "$description": "WCAG 2.2 minimum interactive target size"},
                f"{ns}-sizing-control-sm": {"$type": "dimension", "$value": {"value": max(target_min, 32), "unit": "px"}, "$description": "Small control height"},
                f"{ns}-sizing-control-md": {"$type": "dimension", "$value": {"value": max(target_min, 40), "unit": "px"}, "$description": "Medium control height"},
                f"{ns}-sizing-control-lg": {"$type": "dimension", "$value": {"value": max(target_min, 48), "unit": "px"}, "$description": "Large control height"},
            },
        },
        "semantic": {
            "color": sem_colors,
            "typography": {
                f"{ns}-typography-body-md": {
                    "$type": "typography",
                    "$value": {
                        "fontFamily": f"{{primitive.typography.{ns}-typography-family-sans}}",
                        "fontSize": f"{{primitive.typography.{ns}-typography-size-md}}",
                        "fontWeight": f"{{primitive.typography.{ns}-typography-weight-regular}}",
                        "letterSpacing": {"value": 0, "unit": "px"},
                        "lineHeight": f"{{primitive.typography.{ns}-typography-lineheight-base}}",
                    },
                    "$description": "Default body typography role",
                }
            },
            "spacing": {
                f"{ns}-spacing-layout-gutter": {"$type": "dimension", "$value": f"{{primitive.spacing.{ns}-spacing-4}}", "$description": "Standard layout gutter"}
            },
            "shape": {
                f"{ns}-shape-control-radius-default": {"$type": "dimension", "$value": f"{{primitive.shape.{ns}-shape-radius-md}}", "$description": "Default control corner radius"}
            },
            "opacity": {
                f"{ns}-opacity-overlay-default": {"$type": "number", "$value": f"{{primitive.opacity.{ns}-opacity-backdrop-50}}", "$description": "Default overlay backdrop opacity"}
            },
            "sizing": {
                f"{ns}-sizing-control-height-sm": {"$type": "dimension", "$value": f"{{primitive.sizing.{ns}-sizing-control-sm}}", "$description": "Small interactive control height"},
                f"{ns}-sizing-control-height-md": {"$type": "dimension", "$value": f"{{primitive.sizing.{ns}-sizing-control-md}}", "$description": "Medium interactive control height"},
                f"{ns}-sizing-control-height-lg": {"$type": "dimension", "$value": f"{{primitive.sizing.{ns}-sizing-control-lg}}", "$description": "Large interactive control height"},
            },
        },
        "component": {"color": {"$type": "color"}, "typography": {}, "spacing": {}, "shape": {}, "opacity": {}, "sizing": {}},
    }

    if elev_enabled:
        tokens["primitive"]["elevation"] = {
            f"{ns}-elevation-shadow-sm": {
                "$type": "shadow",
                "$value": {"color": {"colorSpace": "srgb", "components": [0, 0, 0], "alpha": 0.12, "hex": "#000000"}, "offsetX": {"value": 0, "unit": "px"}, "offsetY": {"value": 2, "unit": "px"}, "blur": {"value": 6, "unit": "px"}, "spread": {"value": 0, "unit": "px"}, "inset": False},
                "$description": "Subtle elevation shadow",
            }
        }
        tokens["semantic"]["elevation"] = {
            f"{ns}-elevation-surface-raised": {"$type": "shadow", "$value": f"{{primitive.elevation.{ns}-elevation-shadow-sm}}", "$description": "Raised surface elevation"}
        }
        tokens["component"]["elevation"] = {}

    if motion_enabled:
        tokens["primitive"]["motion"] = {
            f"{ns}-motion-duration-fast": {"$type": "duration", "$value": {"value": 150, "unit": "ms"}, "$description": "Fast micro-interaction duration"},
            f"{ns}-motion-easing-standard": {"$type": "cubicBezier", "$value": [0.2, 0.0, 0.0, 1.0], "$description": "Standard easing curve"},
        }
        tokens["semantic"]["motion"] = {
            f"{ns}-motion-transition-interactive": {
                "$type": "transition",
                "$value": {"duration": f"{{primitive.motion.{ns}-motion-duration-fast}}", "delay": {"value": 0, "unit": "ms"}, "timingFunction": f"{{primitive.motion.{ns}-motion-easing-standard}}"},
                "$description": "Default interactive state transition",
            }
        }
        tokens["component"]["motion"] = {}

    _write_submissions(workdir, tokens)
    violations = _check_system_accessibility(tokens)
    return {
        "valid": True,
        "submissionsDir": str(workdir / "docs" / "ui-design" / "submissions"),
        "accessibilityViolations": violations,
    }


def create_or_update_component(workdir: Path, name: str, spec: dict[str, Any]) -> dict[str, Any]:
    """Mint Tier 3 component tokens dynamically from spec (aliasing Tier 2 only, pruning removed variants/states),
    write <name>.html, and sync DESIGN.md/DESIGN.html."""
    workdir = Path(workdir)
    tok_path = workdir / "docs" / "ui-design" / "submissions" / "design-tokens.json"
    tokens = json.loads(tok_path.read_text(encoding="utf-8"))
    ns = tokens["$metadata"]["namespace"]
    comp_slug = re.sub(r"[^a-z0-9-]+", "-", name.strip().lower()).strip("-")

    sizes = list(spec.get("sizes", ["sm", "md", "lg"]))
    variants = list(spec.get("variants", ["primary", "secondary", "ghost", "destructive"]))
    states = list(spec.get("states", ["default", "hover", "active", "focus-visible", "disabled"]))
    if spec.get("interactive", True) and "focus-visible" not in states:
        states.append("focus-visible")
    norm_spec = {**spec, "sizes": sizes, "variants": variants, "states": states}

    # Prune prior Tier 3 tokens for this component slug so removed variants/states leave zero orphans (D29)
    for cat in ("color", "shape", "sizing"):
        cat_dict = tokens.setdefault("component", {}).setdefault(cat, {})
        prefix = f"{ns}-{cat}-{comp_slug}-"
        for k in [k for k in cat_dict if k.startswith(prefix)]:
            del cat_dict[k]

    comp_color = tokens["component"]["color"]
    comp_color.setdefault("$type", "color")

    if "primary" in variants:
        comp_color[f"{ns}-color-{comp_slug}-bg-primary-default"] = {"$value": f"{{semantic.color.{ns}-color-action-primary-default}}", "$description": f"{comp_slug} primary default bg"}
        comp_color[f"{ns}-color-{comp_slug}-text-primary-default"] = {"$value": f"{{semantic.color.{ns}-color-text-on-action-default}}", "$description": f"{comp_slug} primary text"}
        if "hover" in states:
            comp_color[f"{ns}-color-{comp_slug}-bg-primary-hover"] = {"$value": f"{{semantic.color.{ns}-color-action-primary-hover}}", "$description": f"{comp_slug} primary hover bg"}
        if "active" in states:
            comp_color[f"{ns}-color-{comp_slug}-bg-primary-active"] = {"$value": f"{{semantic.color.{ns}-color-action-primary-active}}", "$description": f"{comp_slug} primary active bg"}

    if "secondary" in variants:
        comp_color[f"{ns}-color-{comp_slug}-bg-secondary-default"] = {"$value": f"{{semantic.color.{ns}-color-bg-surface-default}}", "$description": f"{comp_slug} secondary bg"}
        comp_color[f"{ns}-color-{comp_slug}-text-secondary-default"] = {"$value": f"{{semantic.color.{ns}-color-text-primary-default}}", "$description": f"{comp_slug} secondary text"}
        if "hover" in states:
            elev_key = f"{ns}-color-bg-surface-elevated" if f"{ns}-color-bg-surface-elevated" in tokens["semantic"]["color"] else f"{ns}-color-bg-surface-default"
            comp_color[f"{ns}-color-{comp_slug}-bg-secondary-hover"] = {"$value": f"{{semantic.color.{elev_key}}}", "$description": f"{comp_slug} secondary hover bg"}

    if "ghost" in variants:
        comp_color[f"{ns}-color-{comp_slug}-text-ghost-default"] = {"$value": f"{{semantic.color.{ns}-color-text-primary-default}}", "$description": f"{comp_slug} ghost text"}
        if "hover" in states:
            comp_color[f"{ns}-color-{comp_slug}-bg-ghost-hover"] = {"$value": f"{{semantic.color.{ns}-color-bg-surface-default}}", "$description": f"{comp_slug} ghost hover bg"}

    if "success" in variants:
        comp_color[f"{ns}-color-{comp_slug}-bg-success-default"] = {"$value": f"{{semantic.color.{ns}-color-action-success-default}}", "$description": f"{comp_slug} success default bg"}
        comp_color[f"{ns}-color-{comp_slug}-text-success-default"] = {"$value": f"{{semantic.color.{ns}-color-text-on-action-default}}", "$description": f"{comp_slug} success text"}
        if "hover" in states:
            comp_color[f"{ns}-color-{comp_slug}-bg-success-hover"] = {"$value": f"{{semantic.color.{ns}-color-action-success-hover}}", "$description": f"{comp_slug} success hover bg"}
        if "active" in states:
            comp_color[f"{ns}-color-{comp_slug}-bg-success-active"] = {"$value": f"{{semantic.color.{ns}-color-action-success-active}}", "$description": f"{comp_slug} success active bg"}

    if "destructive" in variants:
        comp_color[f"{ns}-color-{comp_slug}-bg-destructive-default"] = {"$value": f"{{semantic.color.{ns}-color-action-danger-default}}", "$description": f"{comp_slug} destructive default bg"}
        comp_color[f"{ns}-color-{comp_slug}-text-destructive-default"] = {"$value": f"{{semantic.color.{ns}-color-text-on-action-default}}", "$description": f"{comp_slug} destructive text"}
        if "hover" in states:
            hover_key = f"{ns}-color-action-danger-hover" if f"{ns}-color-action-danger-hover" in tokens["semantic"]["color"] else f"{ns}-color-action-danger-default"
            comp_color[f"{ns}-color-{comp_slug}-bg-destructive-hover"] = {"$value": f"{{semantic.color.{hover_key}}}", "$description": f"{comp_slug} destructive hover bg"}
        if "active" in states:
            active_key = f"{ns}-color-action-danger-active" if f"{ns}-color-action-danger-active" in tokens["semantic"]["color"] else f"{ns}-color-action-danger-default"
            comp_color[f"{ns}-color-{comp_slug}-bg-destructive-active"] = {"$value": f"{{semantic.color.{active_key}}}", "$description": f"{comp_slug} destructive active bg"}

    if "disabled" in states:
        comp_color[f"{ns}-color-{comp_slug}-bg-disabled-default"] = {"$value": f"{{semantic.color.{ns}-color-disabled-bg-default}}", "$description": f"{comp_slug} disabled bg (opacity 1)"}
        comp_color[f"{ns}-color-{comp_slug}-text-disabled-default"] = {"$value": f"{{semantic.color.{ns}-color-disabled-fg-default}}", "$description": f"{comp_slug} disabled text (opacity 1)"}

    tokens["component"]["shape"][f"{ns}-shape-{comp_slug}-radius-default"] = {
        "$type": "dimension",
        "$value": f"{{semantic.shape.{ns}-shape-control-radius-default}}",
        "$description": f"{comp_slug} corner radius",
    }
    for sz in sizes:
        sem_sz = sz if f"{ns}-sizing-control-height-{sz}" in tokens["semantic"]["sizing"] else "md"
        tokens["component"]["sizing"][f"{ns}-sizing-{comp_slug}-height-{sz}"] = {
            "$type": "dimension",
            "$value": f"{{semantic.sizing.{ns}-sizing-control-height-{sem_sz}}}",
            "$description": f"{comp_slug} {sz} height",
        }

    if comp_slug not in tokens["$metadata"]["components"]:
        tokens["$metadata"]["components"].append(comp_slug)
    tokens["$metadata"].setdefault("componentSpecs", {})[comp_slug] = {
        "sizes": sizes,
        "variants": variants,
        "states": states,
        "element": spec.get("element", "button"),
    }

    _write_submissions(workdir, tokens)
    comp_dir = workdir / "docs" / "ui-design" / "components"
    comp_dir.mkdir(parents=True, exist_ok=True)
    comp_path = comp_dir / f"{comp_slug}.html"
    comp_path.write_text(_render_component_html(tokens, comp_slug, norm_spec), encoding="utf-8")
    return {"component": comp_slug, "path": str(comp_path), "synced": True, "spec": norm_spec}


def update_design_system(workdir: Path, changes: dict[str, Any]) -> dict[str, Any]:
    """Apply selective or full layer updates in cascade; infer missing $type; block persistence on accessibility regression."""
    workdir = Path(workdir)
    tok_path = workdir / "docs" / "ui-design" / "submissions" / "design-tokens.json"
    tokens = json.loads(tok_path.read_text(encoding="utf-8"))
    candidate = json.loads(json.dumps(tokens))

    if "metadata" in changes and isinstance(changes["metadata"], dict):
        candidate["$metadata"].update(changes["metadata"])

    for tier, cats in changes.get("tokenOverrides", {}).items():
        if tier not in ("primitive", "semantic", "component"):
            continue
        for cat, entries in cats.items():
            candidate.setdefault(tier, {}).setdefault(cat, {})
            for tok_name, new_val in entries.items():
                if tok_name in candidate[tier][cat] and isinstance(candidate[tier][cat][tok_name], dict):
                    candidate[tier][cat][tok_name]["$value"] = new_val
                    if "$type" not in candidate[tier][cat][tok_name] and "$type" not in candidate[tier][cat]:
                        candidate[tier][cat][tok_name]["$type"] = _infer_token_type(new_val, cat)
                    if "com.design-system.modes" in candidate[tier][cat][tok_name].get("$extensions", {}):
                        candidate[tier][cat][tok_name]["$extensions"]["com.design-system.modes"]["light"] = new_val
                        candidate[tier][cat][tok_name]["$extensions"]["com.design-system.modes"]["dark"] = new_val
                else:
                    candidate[tier][cat][tok_name] = {
                        "$type": _infer_token_type(new_val, cat),
                        "$value": new_val,
                        "$description": f"Updated {tok_name}",
                    }

    violations = _check_system_accessibility(candidate)
    if violations:
        return {
            "applied": False,
            "reason": "Blocked due to accessibility contrast regression (D16/D18).",
            "accessibilityViolations": violations,
        }

    _write_submissions(workdir, candidate)

    css_vars = compile_css_variables(candidate)
    comp_dir = workdir / "docs" / "ui-design" / "components"
    updated_components = []
    if comp_dir.is_dir():
        for html_file in sorted(comp_dir.glob("*.html")):
            txt = html_file.read_text(encoding="utf-8")
            updated_txt = re.sub(
                r'(<style id="design-tokens-root">)(.*?)(</style>)',
                lambda m: f"{m.group(1)}\n{css_vars}\n  {m.group(3)}",
                txt,
                flags=re.DOTALL,
            )
            html_file.write_text(updated_txt, encoding="utf-8")
            updated_components.append(html_file.name)

    return {"applied": True, "updatedComponents": updated_components, "accessibilityViolations": []}


def _next_audit_dir(workdir: Path, date_str: str) -> Path:
    base = workdir / "docs" / "ui-design" / "audits"
    candidate = base / date_str
    if not candidate.exists() or not any(candidate.iterdir()):
        candidate.mkdir(parents=True, exist_ok=True)
        return candidate
    v = 2
    while True:
        cand = base / f"{date_str}-v{v}"
        if not cand.exists() or not any(cand.iterdir()):
            cand.mkdir(parents=True, exist_ok=True)
            return cand
        v += 1


def audit_design_system(
    workdir: Path,
    mode: str = "full",
    layer: str | None = None,
    fmt: str = "md",
    date_str: str | None = None,
) -> dict[str, Any]:
    """Strictly read-only audit of submissions/ and components/; writes reports to audits/<yyyy-mm-dd>[-vN]/."""
    workdir = Path(workdir)
    today = date_str or _dt.date.today().isoformat()
    audit_dir = _next_audit_dir(workdir, today)

    tok_path = workdir / "docs" / "ui-design" / "submissions" / "design-tokens.json"
    tokens = json.loads(tok_path.read_text(encoding="utf-8"))
    meta = tokens.get("$metadata", {})
    schema = _load_asset("design-system-schema.json")
    a11y_violations = _check_system_accessibility(tokens)

    findings: list[dict[str, Any]] = []
    for v in a11y_violations:
        findings.append({
            "ruleId": v["ruleId"],
            "severity": "High",
            "layer": "color-palette",
            "detail": f"{v['mode']} mode {v['fgToken']} on {v['bgToken']}: WCAG {v['evaluation']['wcagRatio']}:1, APCA Lc {v['evaluation']['apcaLc']}",
        })

    # Check Tier 3 -> Tier 1 skip (D11)
    for cat, entries in tokens.get("component", {}).items():
        if not isinstance(entries, dict):
            continue
        for k, v in entries.items():
            if k.startswith("$") or not isinstance(v, dict):
                continue
            val = v.get("$value")
            if isinstance(val, str) and val.startswith("{primitive."):
                findings.append({"ruleId": "D11", "severity": "High", "layer": "components", "detail": f"Tier 3 token {k} bypasses Tier 2 and references {val}"})

    written_files: list[str] = []
    if mode in ("accessibility", "full"):
        a11y_md = (
            f"# Accessibility Audit Report\n\n"
            f"- **Date:** {today}\n"
            f"- **Standard:** `{meta.get('accessibilityLevel')}`\n"
            f"- **Read-Only Scope:** `submissions/` and `components/` (unmodified)\n"
            f"- **Defects Found:** {len(a11y_violations)}\n"
        )
        p = audit_dir / "accessibility-audit.md"
        p.write_text(a11y_md, encoding="utf-8")
        written_files.append(p.name)

    if mode == "full":
        for l_info in schema["layers"]:
            slug = l_info["slug"]
            l_findings = [f for f in findings if f["layer"] == slug]
            md = f"# Layer {l_info['index']} Audit — {l_info['title']}\n\n- **Findings:** {len(l_findings)}\n"
            p = audit_dir / f"{l_info['audit_file']}.md"
            p.write_text(md, encoding="utf-8")
            written_files.append(p.name)
        comp_p = audit_dir / "10-components.md"
        comp_p.write_text(f"# Layer 10 Audit — Components\n\n- **Registered Components:** {len(meta.get('components', []))}\n", encoding="utf-8")
        written_files.append(comp_p.name)
        sum_p = audit_dir / "00-comprehensive-summary.md"
        sum_p.write_text(
            f"# Comprehensive Design System Audit Summary\n\n"
            f"- **Date:** {today}\n- **System:** {meta.get('name')}\n- **Total Findings:** {len(findings)}\n",
            encoding="utf-8",
        )
        written_files.append(sum_p.name)

    return {"auditDir": str(audit_dir), "mode": mode, "findingsCount": len(findings), "writtenFiles": written_files}


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic Design System Engine")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create")
    p_create.add_argument("--workdir", type=Path, required=True)
    p_create.add_argument("--config", type=Path, required=True)

    p_update = sub.add_parser("update")
    p_update.add_argument("--workdir", type=Path, required=True)
    p_update.add_argument("--changes", type=Path, required=True)

    p_comp = sub.add_parser("component")
    p_comp.add_argument("--workdir", type=Path, required=True)
    p_comp.add_argument("--name", required=True)
    p_comp.add_argument("--spec", type=Path, default=None)

    p_audit = sub.add_parser("audit")
    p_audit.add_argument("--workdir", type=Path, required=True)
    p_audit.add_argument("--mode", choices=["full", "accessibility"], default="full")
    p_audit.add_argument("--format", choices=["md", "html", "both"], default="md")
    p_audit.add_argument("--date", default=None)

    args = parser.parse_args()
    if args.cmd == "create":
        res = create_design_system(args.workdir, json.loads(args.config.read_text(encoding="utf-8")))
    elif args.cmd == "update":
        res = update_design_system(args.workdir, json.loads(args.changes.read_text(encoding="utf-8")))
    elif args.cmd == "component":
        spec = json.loads(args.spec.read_text(encoding="utf-8")) if args.spec else {}
        res = create_or_update_component(args.workdir, args.name, spec)
    else:
        res = audit_design_system(args.workdir, mode=args.mode, fmt=args.format, date_str=args.date)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
