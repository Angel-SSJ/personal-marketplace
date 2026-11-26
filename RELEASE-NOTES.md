# Release Notes

## v0.2.0 (2026-11-26)

### Highlights

- **Autonomous ten-skill `personal-management` suite:** Rewrote all eight original skills (`code-knowledge-workflow`, `file-naming`, `gtd-workflow`, `inbox-workflow`, `moscow-prioritization`, `notion-workflow`, `para-workflow`, `task-writing`) to operate independently with synchronized local contracts (`system-contract.md`, `integrity-matrix.md`, `naming-policy.md`, `storage-architecture.md`, `intake-policy.md`) and JSON-backed task vocabularies (`p1`–`p4`, empty initial `tags`).
- **Added `notion-initialization` and `system-integrity-audit`:** Implemented strict two-phase Notion initialization (`Phase A` full seven-database verification gate before `Phase B` user-supplied inputs) and read-only cross-layer integrity auditing with explicit coverage/pagination reporting (`I01`–`I46`).
- **Portable Notion symbolic blueprint:** Added `assets/notion-blueprint.json` with zero leaked source workspace IDs, explicit reciprocal relation and rollup mappings, optional `Tasks.Google Drive File`, and all 11 user-verified Notion formula expressions (including the enhanced `Inbox.Needs Clarification` formula), cleanly separated from `assets/workspace-map.json`.
- **Self-contained package validation & behavioral evidence:** Added `scripts/validate-package.py` (with `--self-test` negative checks), portable root `plugin.json` / `mcp.json`, updated `GUIDE.md` / `CHANGELOG.md` / `SOURCES.md`, and consolidated behavioral test fixtures and checklists covering all 46 integrity rules (`I01`–`I46`) in `tests/`.
- **Marketplace lockstep sync:** Updated `package.json`, `.claude-plugin/marketplace.json`, `.cursor-plugin/marketplace.json`, `docs/CATALOG.md`, and all six `personal-management` provider manifests to `0.2.0`.

## v0.1.0 (2026-11-21)

### Highlights

- Initialized `personal-marketplace` repository health checks, formatting, linting, and data validation across `.md`, `.json`, `.js`, `.ts`, `.toml`, `.yml`/`.yaml`, `.html`, and `.svg`.
- Configured native marketplace manifests for all 6 AI providers: GPT/Codex, Claude (Code & Cowork), Antigravity, Cursor, Kimi Code, and OpenCode.
- Added Superpowers-style lockstep version synchronization (`.version-bump.json` + `scripts/bump-version.ts`) and tag-triggered GitHub Release automation.
- Added plugin scaffolding (`scripts/new-plugin.ts`), multi-format validation (`scripts/validate.ts`), native `node:test` suites, GitHub Actions CI (`ci.yml`), and solo-friendly `main` branch ruleset template.
