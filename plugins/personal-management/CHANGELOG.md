# Changelog

## 0.2.0 (2026-11-24)

### Added

- `notion-initialization`: New autonomous skill implementing strict two-phase Notion workspace initialization (`Phase A` full seven-database structure creation/reconciliation and live verification gate before `Phase B` user-supplied data insertion), with explicit `required`/`optional`/`unknown` handling for unrecovered formulas and optional external `Google Drive File`.
- `system-integrity-audit`: New autonomous read-only skill for cross-layer integrity auditing across Notion and Google Drive, with mandatory coverage/pagination reporting, no ungrounded health percentages, and preservation of valid local patterns (`04-archives/01-projects/`, retrospective follow-ups, meaningful Area subfolders).
- `assets/notion-blueprint.json`: Portable symbolic contract for the seven Notion databases (`Goals`, `Areas`, `Projects`, `Stages`, `Tasks`, `Inbox`, `Notes & References`) containing zero source workspace IDs, explicit reciprocal relation and rollup mappings, and all 11 required formula expressions user-verified (`definition_status: "known"`, including the enhanced `Inbox.Needs Clarification` formula).
- `scripts/validate-package.py`: Self-contained Python standard-library package validator with `--self-test` negative test suite.
- Root Agent Plugins 1.0 portable `plugin.json` and `mcp.json` alongside preserved provider overlay manifests.
- Consolidated behavioral test suite (`tests/behavior/`, `tests/checklists/`, `tests/TEST-REPORT.md`).

### Changed

- Rewrote all eight original skills (`file-naming`, `para-workflow`, `code-knowledge-workflow`, `gtd-workflow`, `inbox-workflow`, `task-writing`, `moscow-prioritization`, `notion-workflow`) for full standalone autonomy, synchronized local contracts (`system-contract.md`, `integrity-matrix.md`, `naming-policy.md`, `storage-architecture.md`, `intake-policy.md`), and cross-layer integrity guardrails (`I01`–`I46`).
- Aligned Drive storage roots to the observed kebab-case hierarchy (`01-projects`, `02-areas`, `03-resources`, `04-archives/01-projects/`, `05-intake`).
- Separated observed installation locators (`assets/workspace-map.json`) from portable symbolic schema definitions (`assets/notion-blueprint.json`).
- Removed external repository/catalog maintenance dependencies (`manager-repository`, `content_refs`, external catalog refresh instructions) in favor of verifiable local validation.
- Bumped all provider manifests coherently from `0.1.0` to `0.2.0` while preserving package identity and the official Notion MCP endpoint (`https://mcp.notion.com/mcp`).

## 0.1.0

- Initial eight-skill Personal Management plugin release.
