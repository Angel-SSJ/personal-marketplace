# Provenance and Technical Sources

All operational rules, mathematical constants, lookup tables, and schemas are bundled locally inside each autonomous skill directory. No external network access or private documents are required at runtime.

## Normative & Technical Baselines (2026)

- **W3C WCAG 2.2** (ISO/IEC 40500:2025): 86 active Success Criteria across Levels A, AA, and AAA (relative luminance, no-rounding contrast thresholds, SC 2.4.11–2.4.13 focus visibility/appearance, SC 2.5.5/2.5.8 target size).
- **APCA-W3 `0.0.98G-4g` (`apca-w3` 0.1.9) & ARC (Bronze/Silver/Gold):** Polarity-aware perceptual lightness contrast (`Lc`), soft black clamp (`blkThrs=0.022`, `blkClmp=1.414`), and canonical font size/weight lookup tables.
- **W3C DTCG 2025.10 (Format, Color, Resolver Modules):** Structured `$value` color objects with 6-digit `hex` fallback, `$type` inheritance, `$description`, `$extensions`, and acyclic alias DAGs.
- **Three-Tier Token Architecture & Palette Philosophies:** Primitive $\leftarrow$ Semantic $\leftarrow$ Component unidirectional indirection; perceptual `OKLCH` color harmonies; Material 3 `Tonal Palette` (13-step), IBM `Carbon` (10-step + progressive layering `-01..03`), and `Radix Colors` (12-step Light/Dark).
