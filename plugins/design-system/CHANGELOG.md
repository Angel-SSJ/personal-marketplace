# Changelog

## 0.1.0 (2026-11-25)

### Added

- Five autonomous skills: `design-system-create`, `design-system-update`, `accessibility-audit`, `design-system-audit`, and `component-design`.
- Zero-dependency Python 3 deterministic engine (`scripts/design_system_engine.py`) implementing `OKLCH <-> sRGB` binary-search gamut mapping, 6 color harmony schemes, 3 color palette philosophies (`Tonal Palette`, `Carbon (IBM)`, `Radix Colors`), W3C DTCG 2025.10 generation with `$metadata` + `$extensions` mirroring, WCAG 2.2 AA/AAA + APCA `0.0.98G-4g` dual-gate contrast evaluation, cascade updates, component HTML generation, and read-only versioned auditing.
- Synchronized local contracts (`system-contract.md`, `token-architecture.md`, `color-and-accessibility.md`, `deliverables-schema.md`, `audit-matrix.md` covering `D01`–`D32`) and JSON registries (`apca-lookup-table.json`, `design-system-schema.json`).
- Multi-provider plugin manifests (`plugin.json`, `.antigravity-plugin/`, `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.kimi-plugin/`) and static validator (`scripts/validate-package.py --self-test`).
