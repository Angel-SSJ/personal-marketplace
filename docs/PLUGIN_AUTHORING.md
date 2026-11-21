# Plugin Authoring & Data-Filling Checklist

## 1. Scaffold a New Plugin

Use the built-in CLI scaffolder so all 6 provider manifests, marketplace entries, starter logo, and catalog row stay consistent:

```powershell
pnpm run plugin:new -- `
  --id my-plugin `
  --name "My Plugin" `
  --category development `
  --description "One or two sentences describing what the plugin does and when to activate it."
```

Valid categories are defined in `schemas/enums/categories.json`.

## 2. Fill Initial Discovery Metadata

Review and refine the generated files under `plugins/<id>/`:

1. **Instructions (`skills/<id>/SKILL.md`)**: Write clear, harness-agnostic steps and verify frontmatter `name` matches the folder name and `description` is <=1024 characters.
2. **Logo (`assets/logo.svg`)**: Replace the starter SVG with a square icon (>=128x128 viewBox, transparent background, ~10% margin). Validated automatically for XML well-formedness.
3. **Antigravity Marketplace metadata (`.antigravity-plugin/plugin.json` & `.antigravity-plugin/README.md`)**: Keep `$schema` pointing to `https://antigravity.google/schemas/v1/plugin.json`, tailor the 3 `suggestedPrompts`, ensure `name`/`displayName` do not begin with provider names (`Antigravity`, `Gemini`, `Claude`, `Cursor`), and document prerequisites in `.antigravity-plugin/README.md` (rendered in the Antigravity Marketplace detail view). If adding Antigravity `mcp_config.json`, `hooks.json`, `rules/*.md`, or `agents/*.md`, follow [docs/README.antigravity.md](./README.antigravity.md).
4. **Entity registration files (`.toml` or `.yml`)**: If your plugin registers structured entities, follow `schemas/entity-entry.schema.json` (validated automatically by Taplo and `scripts/validate.ts`).
5. **Enum / config lists (`.json`)**: Place reusable option or event lists under `schemas/enums/` or inside your plugin folder.
6. **Scripts (`.ts` or `.js`)**: Use zero-build native Node 24/25 TypeScript (erasable syntax only, `import type`, explicit `.ts`/`.js` extensions) or ESM `.js`.
7. **HTML assets (`.html`)**: Place static previews or interactive assets under `plugins/<id>/assets/`; validated automatically by `html-validate` and Biome.

## 3. Run Local Verification Before Committing

```powershell
pnpm run format
pnpm run check
```

All commits must follow English Conventional Commits (`feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `build`, `style`, `perf`, `revert`) with optional kebab-case scopes, e.g.:

```text
feat(my-plugin): add initial multi-provider plugin bundle
```
