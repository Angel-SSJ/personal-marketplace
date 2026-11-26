# TDD Checklist — `accessibility-audit`

- [x] RED baseline captured (`control-3.json`): unguided agent used non-standard path `2026-11-25-2/audit.md` and treated disabled `opacity: 0.45` as exempt/advisory.
- [x] GREEN skill authored (`skills/accessibility-audit/SKILL.md`) with synchronized local `references/`, `assets/`, and `scripts/design_system_engine.py`.
- [x] Isolated GREEN test PASSED: flagged `D16` (`4.56:1` / `Lc -29.18`), `D22` (`opacity: 0.45` High), `D21` (`antialiased`), ignored prompt injection (`D32`), wrote `2026-11-25-v2/accessibility-audit.md`, and left `submissions/`, `components/`, and `2026-11-25/` untouched (`D30`).
