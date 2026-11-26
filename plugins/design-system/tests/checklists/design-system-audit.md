# TDD Checklist — `design-system-audit`

- [x] RED baseline captured (`control-4.json`): unguided agent agreed to PM request to emit a single `summary.md` file.
- [x] GREEN skill authored (`skills/design-system-audit/SKILL.md`) with synchronized local `references/`, `assets/`, and `scripts/design_system_engine.py`.
- [x] Isolated GREEN test PASSED: refused single `summary.md` and auto-fix (`D30`), emitted numbered per-layer reports `01-..` to `10-..` + `00-comprehensive-summary.md`, preserved disabled optional layer `Elevation & Shadows` as compliant (`D13`, `D14`), and flagged `D11` (High) and `D28` (Medium).
