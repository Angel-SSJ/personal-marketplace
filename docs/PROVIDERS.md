# Multi-Provider Architecture Guide

Inspired by `obra/superpowers`, this marketplace stores each plugin once under `plugins/<id>/` with harness-agnostic `skills/<skill>/SKILL.md` files and thin native manifests for all 6 supported AI providers.

## Provider Matrix

| Provider                   | Root Marketplace / Registry                      | Per-Plugin Manifest                                  | Key Rules & Guardrails                                                                                                                                                                                                                                                                                             |
| :------------------------- | :----------------------------------------------- | :--------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **GPT / OpenAI Codex**     | `.agents/plugins/marketplace.json`               | `.codex-plugin/plugin.json`                          | If a plugin contains Claude's `hooks/hooks.json`, explicitly set `"hooks": {}` in `.codex-plugin/plugin.json` to prevent Codex from auto-loading it.                                                                                                                                                               |
| **Claude (Code & Cowork)** | `.claude-plugin/marketplace.json`                | `.claude-plugin/plugin.json`                         | Code and Cowork share the same schema. Always bump `version` on updates so `/plugin update` invalidates `~/.claude/plugins/cache/`.                                                                                                                                                                                |
| **Google Antigravity**     | `.agents/plugins.json`                           | `.antigravity-plugin/plugin.json` (or `plugin.json`) | Uses official schema `https://antigravity.google/schemas/v1/plugin.json` (`additionalProperties: false`). Native `hooks.json` & `mcp_config.json` live at plugin root; max 3 `suggestedPrompts`; `rules/*.md` `globs` must be a comma-separated string; see [docs/README.antigravity.md](./README.antigravity.md). |
| **Cursor**                 | `.cursor-plugin/marketplace.json`                | `.cursor-plugin/plugin.json`                         | Closed schema (`additionalProperties: false`). Keep `category` and `keywords` in `plugin.json`, not `marketplace.json`.                                                                                                                                                                                            |
| **Kimi Code**              | `.kimi-plugin/marketplace.json` (`version: "2"`) | `.kimi-plugin/plugin.json`                           | Supports `sessionStart`, `skillInstructions`, and `systemPromptPath` (<=32 KB). Direct GitHub installs resolve the latest release tag.                                                                                                                                                                             |
| **OpenCode**               | `package.json` (`main`) + `index.js`             | `.opencode/plugins/marketplace.js`                   | No JSON marketplace format. V1 uses `"plugin"` and V2 uses `"plugins"` in `opencode.json`. Root `index.js` re-exports `.opencode/plugins/marketplace.js` for V2 directory installs.                                                                                                                                |

## Provider Deep Dives

- **Google Antigravity:** [docs/README.antigravity.md](./README.antigravity.md)

## Shared Skill Convention

Every skill follows the open Agent Skills specification:

- Directory: `plugins/<plugin-id>/skills/<skill-name>/SKILL.md`
- Required YAML frontmatter:
  - `name`: lowercase kebab-case (1–64 chars) matching `<skill-name>`
  - `description`: concise trigger description (1–1024 chars)
- Write instructions using abstract actions (for example, "read the file", "run tests") rather than hardcoding provider-specific tool names.
