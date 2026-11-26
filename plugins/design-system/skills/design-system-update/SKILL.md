---

name: design-system-update
description: Use when updating an existing design system end-to-end or by selected layers, applying post-audit fixes, or propagating token changes in cascade across design-tokens.json, DESIGN.md, DESIGN.html, and components.
---

# Design System Update

Update an existing design system end-to-end or by selected layers with deterministic cascade propagation (`Tier 1 -> Tier 2 -> Tier 3 -> DESIGN.md -> DESIGN.html -> components/*.html`) and mandatory pre-persistence accessibility regression blocking.

Read the local [system contract](references/system-contract.md), [token architecture](references/token-architecture.md), [color and accessibility](references/color-and-accessibility.md), [deliverables schema](references/deliverables-schema.md), and [audit matrix](references/audit-matrix.md) first. Use `python scripts/design_system_engine.py update` for all mutations.

## Recipe

1. **Inspect Existing Contract:** Read `WORKDIR/docs/ui-design/submissions/design-tokens.json` (`$metadata` active `accessibilityLevel`, `colorPalettePhilosophy`, `colorHarmonyScheme`, `colorStandard`) before planning any change.
2. **Validate Cascade & Dual-Gate Accessibility Before Persistence (`D16`–`D20`, `D29`):**
   - Run `python scripts/design_system_engine.py update --workdir <WORKDIR> --changes <changes.json>`.
   - If any Light or Dark mode pairing fails the active dual-gate (`WCAG 2.2 AA + APCA` or `WCAG 2.2 AAA` + APCA Enhanced)—including dark-mode WCAG false-passes such as `#757575` on `#000000` (`4.56:1` WCAG AA, `Lc -29.18` APCA fail)—**block persistence immediately**, leave `submissions/` and `components/` untouched, report exact `CR` and signed `Lc`, and present the engine's nearest passing perceptual `OKLCH` tone proposal for user approval.
3. **Atomic Cascade Synchronization (`D24`, `D29`):** Never allow split updates (e.g., editing only `design-tokens.json` while deferring `DESIGN.md`, `DESIGN.html`, and `components/*.html`). Every authorized update recalculates dependent Tier 2/Tier 3 aliases and atomically updates `design-tokens.json`, `DESIGN.md`, `DESIGN.html`, and the embedded `<style id="design-tokens-root">` block in every `WORKDIR/docs/ui-design/components/*.html`.

## Pressure Traps

| Excuse                                                       | Binding Response                                                                                                      |
| :----------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------- |
| "WCAG says 4.56:1 passes AA, so ship `#757575` on `#000000`" | Dual-gate (`D16`). APCA `Lc -29.18` fails. Block persistence and propose nearest compliant `OKLCH` tone.              |
| "Only edit `design-tokens.json` now; update HTML later"      | Forbidden (`D24`, `D29`). Cascade all dependent tokens, `DESIGN.md`, `DESIGN.html`, and `components/*.html` together. |
