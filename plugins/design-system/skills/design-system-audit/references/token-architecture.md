# Three-Tier Token Architecture & W3C DTCG 2025.10 Contract

## Three-Tier Unidirectional Hierarchy

Dependencies point strictly downward (`Component -> Semantic -> Primitive`). Updates cascade monotonically upward (`Primitive -> Semantic -> Component`).

1. **Tier 1 — Base / Primitive (`primitive.<category>.<token>`):**
   - **Anatomy:** `[Namespace]-[Category]-[Scale/Token]` (e.g., `ds-color-primary-40`, `ds-spacing-4`, `ds-sizing-target-min`).
   - **Rule:** Stores concrete raw W3C DTCG 2025.10 `$value` objects/literals only. Never contains `{...}` aliases (`D11`).
2. **Tier 2 — Semantic / System (`semantic.<category>.<token>`):**
   - **Anatomy:** `[Namespace]-[Category]-[Concept/Property]-[Variant](-[State])` (`[State]` optional when not applicable; e.g., `ds-color-bg-canvas-default`, `ds-color-action-primary-hover`).
   - **Rule:** Aliases Tier 1 primitives (`"{primitive.<category>.<token>}"`). Mode-aware tokens store Light in `$value` and both modes in `$extensions["com.design-system.modes"] = { "light": "{...}", "dark": "{...}" }`.
3. **Tier 3 — Component (`component.<category>.<token>`):**
   - **Anatomy:** `[Namespace]-[Category]-[Concept/Property]-[Variant](-[State])` (e.g., `ds-color-button-bg-primary-default`, `ds-sizing-button-height-md`).
   - **Rule:** Aliases **Tier 2 semantic tokens only** (`"{semantic.<category>.<token>}"`). Skipping Tier 2 to reference Tier 1 or raw literals is a High defect (`D11`).

## W3C DTCG 2025.10 Format & Color Module Rules

- Every token carries `$value`, `$type` (direct or inherited from parent group), and `$description` (`D07`).
- No token or group key may start with `$` or contain `{`, `}`, or `.`; no object may have both `$value` and child tokens (`D06`).
- Alias graph must be a Directed Acyclic Graph (DAG) with zero cycles or dangling pointers (`D12`).
- **Layer 1 (`Identity and Philosophy`):** Stored exclusively in root `"$metadata"` and mirrored in `"$extensions": { "com.design-system.metadata": { ... } }`. Zero design tokens are generated for Layer 1 (`D05`).
- **Color `$value` & Figma/Penpot Interoperability:** Uses DTCG 2025.10 structured color object (`{ "colorSpace": "oklch"|"srgb", "components": [...], "alpha": 1, "hex": "#rrggbb" }`) plus `$extensions["com.design-system.color"]` containing `primaryStandard`, `css`, `oklch`, `srgbHex`, `srgbRgb`, and `srgbComponents` (`D08`).
