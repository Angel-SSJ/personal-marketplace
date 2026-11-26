---

name: component-design
description: Use when creating or updating custom HTML components bound strictly to design system tokens, showcasing sizes, visual hierarchies, interactive states, and light/dark themes, and synchronizing DESIGN.md and DESIGN.html.
---

# Component Design

Create and maintain modular, accessible, token-pure HTML5 components (`WORKDIR/docs/ui-design/components/<component-name>.html`) that strictly consume Tier 2/Tier 3 design tokens and stay synchronized with `design-tokens.json`, `DESIGN.md`, and `DESIGN.html`.

Read the local [system contract](references/system-contract.md), [token architecture](references/token-architecture.md), [color and accessibility](references/color-and-accessibility.md), [deliverables schema](references/deliverables-schema.md), and [audit matrix](references/audit-matrix.md) first. Use `python scripts/design_system_engine.py component` to scaffold and synchronize components.

## Recipe

1. **Mint Dynamic Tier 3 Component Tokens Strictly Aliasing Tier 2 (`D10`, `D11`, `D29`):**
   - Follow Tier 3 naming anatomy: `[Namespace]-[Category]-[Concept/Property]-[Variant](-[State])` (e.g., `ds-color-badge-bg-primary-default`, `ds-sizing-badge-height-md`).
   - Every Tier 3 component token MUST alias a **Tier 2 Semantic token** (`{semantic.<category>.<token>}`). Never reference Tier 1 primitives directly (`D11`) and never hardcode visual literals (`#hex`, `rgb()`, `oklch()`, raw `px` values) inside component CSS (`D25`).
   - Support per-component mutations cleanly (`sizes`, `variants` including optional `success`, and `states` including omitting `hover` or `active` when requested by the user): prune prior Tier 3 tokens for that component slug before writing updated ones so zero orphans remain (`D29`), while preserving `focus-visible` on interactive controls (`D19`).
2. **Enforce Active Accessibility Level (`D16`–`D23`, `D27`, `D31`):**
   - Check `$metadata.accessibilityLevel` in `design-tokens.json`. For Level 1 (`WCAG 2.2 AA + APCA`), enforce `>= 4.5:1` + `|Lc| >= 75/60` and `>= 24x24px` interactive targets (SC 2.5.8). For Level 2 (`WCAG 2.2 AAA` + APCA Enhanced), enforce `>= 7.0:1` + `|Lc| >= 90/75`, `>= 44x44px` interactive targets (SC 2.5.5, `D20`), and `>= 2px` perimeter focus ring (SC 2.4.13, `D19`).
   - Use native semantic HTML elements and valid WAI-ARIA (`D27`), `-webkit-font-smoothing: auto` (`D21`), solid disabled tokens at `opacity: 1` (`D22`), `@media (prefers-reduced-motion: reduce)` (`D23`), and non-color redundancy (`✓` icon for `success`, `⚠` icon for `destructive` alongside clear labels, `D31`).
3. **Render Analytical Showcase Matrices with Single Global Theme Toggle (`D26`):**
   - Use the standardized fixed Neutral Tonal Scale HTML viewer shell (minimalist 3-element header, zero `+` crosshairs, `<meta name="color-scheme" content="light dark" />`) and embed synchronized `<style id="design-tokens-root">` compiled from `design-tokens.json` (`D24`).
   - Showcase all configured dimensions via accessible responsive `<table class="matrix-table">` matrices (`tabindex="0"`, `<caption>`, `scope="col"`, `scope="row"`) under a single global Light/Dark toggle synced with `DESIGN.html` via `postMessage` (never stack duplicate Light + Dark panels simultaneously).
4. **Synchronize System Docs (`D28`):** Run `python scripts/design_system_engine.py component --workdir <WORKDIR> --name <component-name>` so Section 10 of `DESIGN.md` (contract table) and `DESIGN.html` (link + `<iframe>` embed to `../components/<component-name>.html`) update together.

## Pressure Traps

| Excuse                                                                      | Binding Response                                                                                        |
| :-------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------ |
| "Hardcode `#1d4ed8` and `12px` so it's fast"                                | Forbidden (`D25`). All visual styling must use `var(--<namespace>-...)` tokens.                         |
| "Point component token directly to `{primitive.color.ds-color-primary-40}`" | Forbidden (`D11`). Tier 3 component tokens must alias Tier 2 semantic tokens only.                      |
| "Only show default light-mode `md` and skip `DESIGN.md`/`DESIGN.html`"      | Forbidden (`D26`, `D28`). Render all 4 dimensions and sync Section 10 of `DESIGN.md` and `DESIGN.html`. |
