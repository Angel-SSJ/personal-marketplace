# Design System Plugin (`design-system`)

Self-contained five-skill design system engineering suite covering end-to-end W3C DTCG 2025.10 creation, cascade updates, perceptual `OKLCH` harmonies and palette philosophies (`Tonal Palette`, `Carbon (IBM)`, `Radix Colors`), dual-gate accessibility auditing (`WCAG 2.2 AA + APCA` / `WCAG 2.2 AAA + APCA Enhanced`), layer-by-layer structural auditing, and modular token-pure HTML component showcases.

## Metadata

- **ID:** `design-system`
- **Category:** `design`
- **Version:** `0.1.0`
- **License:** `MIT`
- **Providers:** Agent Plugins 1.0 (`plugin.json`, `mcp.json`), Antigravity, Claude (Code & Cowork), Codex, Cursor, Kimi Code

## Bundled Skills (100% Autonomous)

Each skill bundles byte-identical copies of all 5 normative references (`references/`), 2 JSON registries (`assets/`), and the zero-dependency Python 3 standard-library engine (`scripts/design_system_engine.py`).

| Skill                  | Purpose                                                                                                                                                  |
| :--------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `design-system-create` | End-to-end creation across all 9 layers with mandatory foundation gates (`D01`–`D04`) and `design-tokens.json`, `DESIGN.md`, `DESIGN.html` deliverables. |
| `design-system-update` | End-to-end or selective layer updates with cascade propagation and pre-persistence accessibility regression blocking (`D16`–`D20`, `D24`, `D29`).        |
| `accessibility-audit`  | Strictly read-only dual-gate WCAG 2.2 AA/AAA + APCA `0.0.98G-4g` auditing (`audits/<yyyy-mm-dd>[-vN]/accessibility-audit.md`).                           |
| `design-system-audit`  | Strictly read-only layer-by-layer and cross-layer integrity auditing (`00-comprehensive-summary.md`, `01-..` to `10-..`).                                |
| `component-design`     | Modular, accessible, token-pure HTML5 component showcases (`components/<component-name>.html`) across sizes, variants, states, and Light/Dark themes.    |

## Package Validation

```bash
python scripts/validate-package.py
python scripts/validate-package.py --self-test
```
