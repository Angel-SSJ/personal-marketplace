# Google Antigravity Integration & Marketplace Guide

This document describes how `personal-marketplace` packages, validates, installs, and publishes plugins for **Google Antigravity** (Antigravity App, Antigravity CLI `agy`, Antigravity IDE, and IDE extensions).

- Official Plugins Guide: <https://antigravity.google/docs/plugins>
- Official Marketplace Guide: <https://antigravity.google/docs/marketplace>
- Official Build Plugins Guide: <https://antigravity.google/docs/build-plugins>
- Official JSON Schema (v1): <https://antigravity.google/schemas/v1/plugin.json>

## 1. How Antigravity Discovery & Marketplace Work

Unlike Claude Code or Cursor, Antigravity's `/plugin install <name>@<marketplace>` syntax only resolves the curated official marketplace (`antigravity-plugins-official`). Personal and multi-plugin repositories integrate with Antigravity through three native paths:

1. **Direct GitHub Subfolder Installation (no clone needed)**:
   - Shell CLI: `agy plugin install https://github.com/Angel-SSJ/personal-marketplace/tree/main/plugins/<id>`
2. **Workspace & Global Discovery Registry (`.agents/plugins.json` / `~/.gemini/config/plugins.json`)**:
   - Workspace discovery is already configured at `.agents/plugins.json` (`entries: [{ "path": "plugins" }]`), scanning one level deep inside the repo root.
   - To share a local clone across _all_ workspaces, reference its absolute path in `~/.gemini/config/plugins.json` (`~` is not expanded inside `plugins.json`, and workspace `.agents/plugins.json` restricts paths to the repo root for security).
3. **Local CLI / App Installation**:
   - Shell CLI: `agy plugin install ./plugins/<id>`
   - Interactive CLI: `/plugin` -> **Discover** -> **Install from local directory** -> select `./plugins/<id>`
   - List installed plugins: `agy plugin list --json`
4. **Antigravity Marketplace Publishing**: Once a plugin passes `agy plugin validate` with zero errors and includes complete metadata (`name`, `displayName`, `description`, `version`, `logo`, `suggestedPrompts`, `author`, `license`, `keywords`) plus `.antigravity-plugin/README.md`, it can be submitted via the official partner intake form documented at <https://antigravity.google/docs/build-plugins>.

## 2. Native Plugin Layout for Antigravity

Inside a multi-provider plugin directory (`plugins/<id>/`), Antigravity gives precedence to `.antigravity-plugin/plugin.json` over a root `plugin.json`:

```text
plugins/<id>/
├── .antigravity-plugin/
│   ├── plugin.json        # Required manifest ($schema: https://antigravity.google/schemas/v1/plugin.json)
│   └── README.md          # Pre-install detail view rendered in Antigravity Marketplace UI
├── assets/
│   └── logo.svg           # Square >=128x128 logo (~10% transparent padding, readable on Light & Dark themes)
├── scripts/               # Optional helper scripts (0755 executable in Marketplace bundles)
├── mcp_config.json        # Optional MCP servers (namespaced as <plugin-name>_<server-name>)
├── hooks.json             # Optional lifecycle hooks (must live at plugin root, not hooks/hooks.json)
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md       # YAML frontmatter: name (1-64 chars matching dir), description (1-1024 chars)
│       ├── scripts/
│       └── references/
├── agents/
│   └── <agent-name>.md    # Optional custom agents / subagents (name, description, model, tools)
└── rules/
    ├── AGENTS.md          # Optional always-on plugin rule (no frontmatter needed)
    └── <rule-name>.md     # Optional triggered rule (trigger: always_on | model_decision | glob | manual)
```

## 3. Automated Validation Rules Enforced in This Repo

Our local validator (`pnpm run validate:data` / `scripts/validate.ts`) enforces Antigravity's official pre-publish rules in addition to JSON Schema checks:

- **Manifest (`schemas/plugin-manifest.schema.json` -> `antigravity`):** Matches `https://antigravity.google/schemas/v1/plugin.json` with `additionalProperties: false`, strict kebab-case `name`, valid `logo` path, max 3 `suggestedPrompts`, and rejects reserved leading provider prefixes (`Antigravity`, `Gemini`, `Claude`, `Cursor`).
- **MCP (`schemas/antigravity-mcp-config.schema.json`):** Validates `mcpServers` structure, ensures `variables` live inside `mcpServers.<server>.variables` (never at root), and forbids redeclaring built-in `PLUGIN_ROOT` or `PLUGIN_DATA` in `env`.
- **Hooks (`schemas/antigravity-hooks.schema.json`):** Validates named hook groups at `<plugin-root>/hooks.json` (grouped `{ matcher, hooks }` for `PreToolUse`/`PostToolUse`, flat handler arrays for `SessionStart`/`PreInvocation`/`PostInvocation`/`Stop`) and rejects `${PLUGIN_ROOT}` in hook commands (use relative `./scripts/...`).
- **Rules (`rules/*.md`):** Enforces valid `trigger` values and requires `globs` to be a **comma-separated string** (never a YAML array).
- **Agents (`agents/*.md`):** Enforces kebab-case `name`, non-empty `description`, valid `model` (`inherit`, `flash_lite`, `flash`, `pro`), and valid `commandExecutionPolicy` (`off`, `auto`, `eager`, `sandbox`).

## 4. Validating with `agy` CLI in Multi-Tool Repositories

Because plugins in this repository also ship manifests for Claude, Cursor, Codex, and Kimi, `agy plugin validate --strict` may emit expected warnings for other-tool files (`.mcp.json`, `mcp.json`, `AGENTS.md` at plugin root, or `hooks/hooks.json`). Run without `--strict` or filter known multi-tool files with `--json`:

```bash
agy plugin validate ./plugins/<id>
```
