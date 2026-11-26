---

name: design-system-audit
description: Use when auditing a design system layer by layer and across layers for W3C DTCG 2025.10 conformance, three-tier token integrity, naming anatomy, deliverable sync, and component coherence.
---

# Design System Audit

Run a strictly read-only, layer-by-layer and cross-layer integrity audit across all 9 design system layers and all registered components, producing fixed numbered per-layer reports plus a comprehensive summary report.

Read the local [system contract](references/system-contract.md), [token architecture](references/token-architecture.md), [color and accessibility](references/color-and-accessibility.md), [deliverables schema](references/deliverables-schema.md), and [audit matrix](references/audit-matrix.md) first. Use `python scripts/design_system_engine.py audit --mode full` for deterministic validation.

## Recipe

1. **Stay Strictly Read-Only (`D30`, `D32`):** Never modify `WORKDIR/docs/ui-design/submissions/` or `WORKDIR/docs/ui-design/components/`. Refuse any request to "auto-fix during the audit"; propose minimal safe repairs for `design-system-update` instead.
2. **Enforce Fixed Numbered Per-Layer Report Convention (`D30`):**
   - Never collapse a full audit into a single `summary.md` file.
   - Write to `WORKDIR/docs/ui-design/audits/<yyyy-mm-dd>/` (incrementing `-v2`, `-v3` if already present on the same day) in `.md` format by default (plus `.html` when requested):
     - `00-comprehensive-summary.md`
     - `01-identity-and-philosophy.md` .. `09-sizing.md`
     - `10-components.md`
     - `accessibility-audit.md` (when dual-gate accessibility is audited alongside)
3. **Classify Confirmed Defects vs. Valid Non-Defects (`D01`–`D32`):**
   - **Confirmed Defects (`High`/`Medium`/`Low`):** Cite Rule ID, exact token/file evidence, affected layers, and smallest repair option (e.g., `D11` Tier 3 -> Tier 1 skip, `D28` unregistered `components/<name>.html` missing from `DESIGN.md`/`DESIGN.html` Section 10, `D24` cross-file drift, `D05` Layer 1 tokens).
   - **Valid Non-Defects (Preserve):** Intentionally disabled optional layers (`Elevation & Shadows`, `Motion & Animation`) marked `enabled: false` in `$metadata.optionalLayers` and documented as `"Status: Omitted (Optional Layer)"` in `DESIGN.md`/`DESIGN.html` (`D14`) are **compliant**, not defects.

## Pressure Traps

| Excuse                                              | Binding Response                                                                                                       |
| :-------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| "Just put everything in one `summary.md` file"      | Forbidden (`D30`). Always emit fixed numbered per-layer reports `01-..` to `10-..` plus `00-comprehensive-summary.md`. |
| "Auto-fix the broken card token while auditing"     | Forbidden (`D30`). Audits are strictly read-only; hand off repairs to `design-system-update`.                          |
| "Flag disabled `Elevation & Shadows` as incomplete" | Non-defect (`D13`, `D14`). Optional layers explicitly omitted in `$metadata` and docs are compliant.                   |
