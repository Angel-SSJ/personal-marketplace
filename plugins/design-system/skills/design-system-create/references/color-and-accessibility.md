# Perceptual Color (`OKLCH`), Palette Philosophies, and Dual-Gate Accessibility

## Perceptual `OKLCH` Core & Color Harmony Schemes

All hue rotations, chroma harmonization, and lightness stepping execute internally in perceptual `OKLCH` (`L in [0, 1]`, `C >= 0`, `H in [0, 360)`) with 32-iteration binary-search chroma reduction into sRGB `[0, 1]` before emitting 6-digit `hex` fallbacks.

- `Monochromatic`: single hue $H_0$ across chroma/lightness variations.
- `Analogous`: $H_0$, $(H_0 + 30^\circ) \bmod 360^\circ$, $(H_0 + 330^\circ) \bmod 360^\circ$.
- `Complementary`: $H_0$, $(H_0 + 180^\circ) \bmod 360^\circ$.
- `Split-Complementary`: $H_0$, $(H_0 + 150^\circ) \bmod 360^\circ$, $(H_0 + 210^\circ) \bmod 360^\circ$.
- `Triadic`: $H_0$, $(H_0 + 120^\circ) \bmod 360^\circ$, $(H_0 + 240^\circ) \bmod 360^\circ$.
- `Tetradic`: $H_0$, $(H_0 + 60^\circ) \bmod 360^\circ$, $(H_0 + 180^\circ) \bmod 360^\circ$, $(H_0 + 240^\circ) \bmod 360^\circ$.
- Dedicated chroma-harmonized functional seeds are always generated: `neutral` ($H_0$, low chroma), `success` ($145^\circ$), `warning` ($75^\circ$), `danger` ($25^\circ$), `info` ($250^\circ$).

## Color Palette Philosophies

1. **Tonal Palette (Material 3):** 13 discrete tonal steps (`0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100`) with parabolic chroma tapering at extremes.
2. **Carbon (IBM):** 10-step ramp (`10, 20, 30, 40, 50, 60, 70, 80, 90, 100`) + `white`/`black` + progressive surface layering (`background`, `layer-01..03`, `field-01..03`, `border-subtle-01..03`).
3. **Radix Colors:** 12-step functional scale (`1..12` Light and `dark-1..dark-12` Dark): `1–2` backgrounds, `3–5` UI surfaces default/hover/active, `6–8` borders/focus, `9–10` solid fills, `11–12` low/high-contrast text.

## Dual-Gate Accessibility (`WCAG 2.2` + `APCA 0.0.98G-4g`)

Never round up failing contrast ratios (`4.499:1` fails `4.5:1`). Always evaluate polarity-aware APCA (`text` vs `bg` never swapped) via `scripts/design_system_engine.py` and `assets/apca-lookup-table.json`.

| Role                | Level 1 (`WCAG 2.2 AA + APCA` Silver)                                                                  | Level 2 (`WCAG 2.2 AAA` + APCA Gold)                              |
| :------------------ | :----------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------- |
| Body text           | `CR >= 4.5:1` AND `\|Lc\| >= 75` (min `14px`)                                                          | `CR >= 7.0:1` AND `\|Lc\| >= 90` (min `16px`)                     |
| Fluent content      | `CR >= 4.5:1` AND `\|Lc\| >= 60`                                                                       | `CR >= 7.0:1` AND `\|Lc\| >= 75`                                  |
| Large / display     | `CR >= 3.0:1` AND `\|Lc\| >= 45` (`<= 90` glare cap `>36px bold`)                                      | `CR >= 4.5:1` AND `\|Lc\| >= 60` (`<= 90` glare cap `>36px bold`) |
| UI controls & focus | `CR >= 3.0:1` AND `\|Lc\| >= 30`                                                                       | `CR >= 3.0:1` AND `\|Lc\| >= 45`, `>= 2px` perimeter (SC 2.4.13)  |
| Hit target size     | `>= 24x24 CSS px` (SC 2.5.8)                                                                           | `>= 44x44 CSS px` (SC 2.5.5)                                      |
| Rendering & motion  | `-webkit-font-smoothing: auto`; `prefers-reduced-motion: reduce`; solid disabled tokens (`opacity: 1`) | Same + SC 2.3.3 animation from interactions                       |

## Semantic Status Actions (`success` & `destructive`)

- Semantic `action-success-*` and `feedback-{success,warning,danger,info}-default` roles are derived dynamically from the active palette philosophy (`Tonal Palette`, `Carbon (IBM)`, or `Radix Colors`) and validated through the active dual-gate (`WCAG 2.2` + `APCA`) in both Light and Dark modes.
- Because green contributes ~71.5% of sRGB relative luminance, bright saturated green with white text fails contrast; darkened perceptual `OKLCH` green in Light mode and high-lightness green with dark text in Dark mode satisfy both Level 1 and Level 2.
- Per **WCAG SC 1.4.1 (Use of Color / `D31`)**, `success` and `destructive` actions must never rely on green vs. red alone (red-green CVD safety): always pair semantic color with clear action text and distinct iconography (`✓` for `success`, `⚠` for `destructive`).
