# Release Notes

## v0.1.0 (2026-11-21)

### Highlights

- Initialized `personal-marketplace` repository health checks, formatting, linting, and data validation across `.md`, `.json`, `.js`, `.ts`, `.toml`, `.yml`/`.yaml`, `.html`, and `.svg`.
- Configured native marketplace manifests for all 6 AI providers: GPT/Codex, Claude (Code & Cowork), Antigravity, Cursor, Kimi Code, and OpenCode.
- Added Superpowers-style lockstep version synchronization (`.version-bump.json` + `scripts/bump-version.ts`) and tag-triggered GitHub Release automation.
- Added plugin scaffolding (`scripts/new-plugin.ts`), multi-format validation (`scripts/validate.ts`), native `node:test` suites, GitHub Actions CI (`ci.yml`), and solo-friendly `main` branch ruleset template.
