---

name: design-system-create
description: Use when creating a new end-to-end design system from scratch, defining foundation parameters, generating W3C DTCG 2025.10 tokens, or producing DESIGN.md and DESIGN.html deliverables.
---

# Design System Create

Create a complete, accessible, three-tier W3C DTCG 2025.10 design system across all 9 layers with zero silent defaults and deterministic perceptual color math.

Read the local [system contract](references/system-contract.md), [token architecture](references/token-architecture.md), [color and accessibility](references/color-and-accessibility.md), [deliverables schema](references/deliverables-schema.md), and [audit matrix](references/audit-matrix.md) first. Use [design-system-schema.json](assets/design-system-schema.json), [apca-lookup-table.json](assets/apca-lookup-table.json), and `python scripts/design_system_engine.py create` for all calculations and file generation.

## Mandatory Foundation Gate (Hard Stop)

Never proceed to scale generation or file creation—even under urgent deadlines or demo pressure—until the user explicitly establishes all four constrained parameters:

1. **Accessibility Standard (`D01`):** `WCAG 2.2 AA + APCA` (Level 1) or `WCAG 2.2 AAA` (Level 2: WCAG 2.2 AAA + APCA Enhanced).
2. **Color Palette Philosophy (`D02`):** `Tonal Palette` (13-step M3), `Carbon (IBM)` (10-step + layering), or `Radix Colors` (12-step Light/Dark).
3. **Color Harmony Scheme (`D03`):** `Monochromatic`, `Analogous`, `Complementary`, `Split-Complementary`, `Triadic`, or `Tetradic`.
4. **Primary Color Standard (`D04`):** `OKLCH`, `HEX`, or `RGB` (`OKLCH` automatically emits 6-digit `HEX`/`sRGB` fallbacks for Figma/Penpot).

Also confirm `name`, `namespace`, `seedColor`, and whether optional layers (`Elevation & Shadows`, `Motion & Animation`) are enabled.

## Recipe

1. **Enforce Gate (`D01`–`D04`):** If any of the 4 foundation parameters is missing, stop immediately and ask the user explicitly. Do not guess or invent defaults.
2. **Keep Layer 1 (`Identity and Philosophy`) Out of Tokens (`D05`):** Store Layer 1 exclusively in root `$metadata` (mirrored in `$extensions["com.design-system.metadata"]`) and Section 1 of `DESIGN.md` / `DESIGN.html`. Never generate design tokens for Layer 1.
3. **Run Deterministic Engine:** Execute `python scripts/design_system_engine.py create --workdir <WORKDIR> --config <config.json>` to compute `OKLCH` harmony seeds, gamut-mapped scales, dual-gate verified Light/Dark semantic tokens, and all 7 mandatory layers (+ optional layers if enabled).
4. **Verify Deliverables (`WORKDIR/docs/ui-design/submissions/`):** Confirm `design-tokens.json`, lossless reconstructible `DESIGN.md` (YAML frontmatter + 10 fixed sections + dual-gate contrast table), and `DESIGN.html` (fixed Neutral Tonal Scale viewer shell with zero `+` crosshairs, minimalist 3-element header, single global Light/Dark toggle, categorized color sub-bands, live typography specimens, and Layers 4–9 visual showcases) exist with zero dual-gate contrast violations.

## Pressure Traps

| Excuse                                           | Binding Response                                                                                                    |
| :----------------------------------------------- | :------------------------------------------------------------------------------------------------------------------ |
| "Demo in 10 minutes; pick sensible defaults now" | Hard stop (`D01`–`D04`). Ask for the 4 missing parameters before generating anything.                               |
| "Include Identity & Philosophy as design tokens" | Forbidden (`D05`). Store in `$metadata` + `$extensions` and Section 1 of `DESIGN.md`/`DESIGN.html` only.            |
| "Skip optional layer sections when disabled"     | Keep Sections 6/7 reserved with `"Status: Omitted (Optional Layer)"` (`D14`) and preserve `prefers-reduced-motion`. |
