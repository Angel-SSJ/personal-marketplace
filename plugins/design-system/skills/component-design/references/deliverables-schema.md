# Standardized Deliverables & Directory Schema

All outputs live strictly under `WORKDIR/docs/ui-design/`:

- `WORKDIR/docs/ui-design/submissions/design-tokens.json`: W3C DTCG 2025.10 single source of truth (explicit or inherited `$type` on every token; never raw Python dict strings in compiled CSS).
- `WORKDIR/docs/ui-design/submissions/DESIGN.md`: Lossless, reconstructible contract with full YAML frontmatter (metadata, semantic Light/Dark hex & alias refs, typography, spacing/z-index, shape/stroke, elevation, motion, opacity, sizing, per-component specs), 10 fixed H2 sections (`## 1. Identity and Philosophy` through `## 10. Components`), and a live-computed Dual-Gate Contrast Verification table.
- `WORKDIR/docs/ui-design/submissions/DESIGN.html`: Standardized editorial visual showcase:
  - **Fixed Viewer Shell Palette:** Chrome uses the fixed 13-step **Neutral Tonal Scale (Brand-Tinted)** (`--shell-0` `#000000` .. `--shell-100` `#ffffff`), decoupled from `--<namespace>-*` so every design system renders in a consistent neutral Light/Dark frame without altering its own tokens.
  - **Clean Hairline Architecture:** Full-bleed horizontal bands and `1px` vertical guide rails with **zero artificial `+` crosshairs**, natural full-width text wrapping (no premature narrow line breaks), and single-quoted `font-family` inline styles so all typography specimens render accurately.
  - **Minimalist 3-Element Header:** Contains **ONLY** (1) Design System title, (2) section navigation links, and (3) single global theme toggle (`<meta name="color-scheme" content="light dark" />`, `:root { color-scheme: light dark; }`, `localStorage`, and `postMessage` sync to embedded component iframes).
  - **10 Visual Sections:** Editorial Identity intro + 6-cell metadata strip; categorized Color Palette sub-bands (`Brand & Accent`, `Surface`, `Text`, `Feedback & Status`, `Disabled`, `Primitive Scales`) with live theme-aware `#hex` labels; Typography specimen rows; split hairline panels + softly-bordered boxes + proportional bars for Layers 4–9; and synced component `<iframe>` embeds in Section 10.
- `WORKDIR/docs/ui-design/components/<component-name>.html`: Standalone accessible HTML5 component showcase using the same fixed Neutral Tonal Scale viewer shell, minimalist 3-element header, embedded `<style id="design-tokens-root">`, and single global Light/Dark toggle (never stacked duplicate Light + Dark views). Renders accessible responsive analytical matrix tables (`tabindex="0"`, `role="region"`, `<caption>`, `scope="col"`, `scope="row"`) strictly for the component's configured `sizes`, `variants` (including optional `success` paired with `✓` and `destructive` paired with `⚠` per WCAG SC 1.4.1), and `states` (mutable per component without leaving orphaned Tier 3 tokens).
- `WORKDIR/docs/ui-design/audits/<yyyy-mm-dd>[-v2|-v3...]/`:
  - `00-comprehensive-summary.md` (and optional `.html`)
  - `01-identity-and-philosophy.md` .. `09-sizing.md`
  - `10-components.md`
  - `accessibility-audit.md` (standalone or alongside full audit)

Optional layers (`Elevation & Shadows`, `Motion & Animation`): when disabled in `$metadata.optionalLayers`, reserve their section in `DESIGN.md` and `DESIGN.html` with `"Status: Omitted (Optional Layer)"` and keep `@media (prefers-reduced-motion: reduce)` active in CSS.
