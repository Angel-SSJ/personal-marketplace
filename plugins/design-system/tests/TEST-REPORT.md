# Design System v0.1.0 — Test & Validation Report

Date: 2026-11-25

## 1. Deterministic Engine Unit & Lifecycle Tests (`temp/work/test_engine.py`)

- **Result:** `7/7` tests PASSED (`0` failures, `0` errors).
- **Verified invariants:**
  - Canonical APCA-W3 `0.0.98G-4g` polarity calculations (`#111111/#e8e6dd = +90.48`, `#00bbff/#000000 = -59.66`, `#000000/#ffffff = +106.04`, `#ffffff/#000000 = -107.88`, `#767676/#ffffff = +71.57`, `#ffffff/#767676 = -77.16`, `#ffffff/#d95f02 = -69.80`).
  - Dark-mode WCAG 2.2 AA false-pass caught by dual-gate (`#757575` on `#000000`: WCAG `4.56:1` pass, APCA `Lc -29.18` fail -> rejected).
  - WCAG no-rounding boundary (`#777777` on `#ffffff` `< 4.5` fails; `#767676` `>= 4.5` passes AA; `#595959` `>= 7.0` passes AAA).
  - Out-of-gamut `OKLCH` binary-search chroma reduction (`oklch(0.70, 0.25, 29°)` mapped cleanly into sRGB `[0, 1]` with valid 6-digit `hex`).
  - All 6 harmony schemes and 3 palette philosophies (`13`-step Tonal Palette, `10`-step Carbon + white/black, `12`-step Radix Light/Dark).
  - End-to-end `create_design_system` gate enforcement (`D01`–`D04`), `create_or_update_component` + `DESIGN.html` linkage, `update_design_system` pre-persistence accessibility regression blocking (`D16`/`D29`), and read-only same-day audit versioning (`2026-11-25` -> `2026-11-25-v2`, `D30`).

## 2. Isolated TDD Behavioral Evaluations (`RED -> GREEN`)

| Skill                  | Unguided RED Control                                     | Isolated GREEN Test                                                                                            | Result |
| :--------------------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------- | :----- |
| `design-system-create` | Skipped `D01`–`D04` under 10-min demo pressure           | Hard-stopped on `D01`–`D04`, rejected Layer 1 tokens (`D05`)                                                   | PASS   |
| `design-system-update` | Approximated APCA, made cascade conditional              | Blocked `D16` (`4.56:1` / `Lc -29.18`), refused split update (`D24`, `D29`)                                    | PASS   |
| `accessibility-audit`  | Used `2026-11-25-2/audit.md`, downgraded `opacity: 0.45` | Flagged `D16`, `D22` (High), `D21`, ignored injection (`D32`), wrote `2026-11-25-v2/accessibility-audit.md`    | PASS   |
| `design-system-audit`  | Agreed to single `summary.md`                            | Refused `summary.md` & auto-fix (`D30`), emitted `00-..` to `10-..`, preserved disabled optional layer (`D14`) | PASS   |
| `component-design`     | Omitted APCA Gold, `44x44px` AAA target, Tier 3 anatomy  | Enforced `D10`, `D11`, `D20`, `D25`, `D26`, `D28` + `<style id="design-tokens-root">`                          | PASS   |

## 3. Static Package Validation & Negative Self-Tests (`scripts/validate-package.py --self-test`)

- Verified all 6 provider manifests, 3 MCP configs, 5 skills, YAML frontmatter, local-only markdown links, byte-identical synchronized references/assets/engine, and all 6 negative self-test cases (`corrupted_frontmatter`, `nonlocal_cross_skill_link`, `reference_contract_drift`, `engine_script_drift`, `manifest_version_mismatch`, `leaked_machine_path`).
