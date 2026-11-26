# Personal Management

Self-contained ten-skill personal productivity and knowledge management suite integrating GTD, PARA, CODE, Inbox/Intake processing, MoSCoW prioritization, task writing, global file and folder naming, Notion workflow, two-phase Notion initialization, and read-only cross-layer system integrity auditing.

## Metadata

- **ID:** `personal-management`
- **Category:** `productivity`
- **Version:** `0.2.0`
- **License:** `MIT`
- **Providers:** Agent Plugins 1.0 (`plugin.json`, `mcp.json`), Antigravity, Claude (Code & Cowork), Codex, Cursor, Kimi Code, OpenCode

## Bundled Skills (Autonomous)

Each skill operates independently with synchronized local contracts, integrity rules, naming/storage policies, and JSON registries inside its own directory. Removing any other skill directory does not break the remaining skills.

| Skill                     | Purpose                                                                                                                                     |
| :------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------ |
| `code-knowledge-workflow` | Knowledge capture, provenance, distillation, work packets, and expressive outputs (CODE).                                                   |
| `file-naming`             | Global file and folder naming policy across ordinary files, technical exceptions, numbering, and provisional capture.                       |
| `gtd-workflow`            | Commitment clarification, next actions, waiting items, timeline semantics, weekly reviews, and overload recovery (GTD).                     |
| `inbox-workflow`          | Loose-input capture, clarification, `05-intake` holds, entity matching, and idempotent partial-write recovery.                              |
| `moscow-prioritization`   | Explicit-selection MoSCoW scope classification, dependency closure, and real-capacity feasibility checks.                                   |
| `notion-initialization`   | Two-phase initialization and reconciliation of the seven-database Notion workspace (`Phase A` structure gate before `Phase B` user inputs). |
| `notion-workflow`         | Live-schema Notion database, page, template, view, relation, and Goal operations.                                                           |
| `para-workflow`           | Projects, Areas, Resources, and Archives storage placement and lifecycle transitions (PARA).                                                |
| `system-integrity-audit`  | Read-only cross-layer integrity auditing across Notion and Google Drive with explicit coverage limits and non-defect preservation.          |
| `task-writing`            | Task title/description expression and JSON-validated priority (`p1`–`p4`) and lowercase tag vocabularies.                                   |

## Storage Architecture & Notion Model

- **Notion (7 databases):** `Goals`, `Areas`, `Projects`, `Stages`, `Tasks`, `Inbox`, and `Notes & References`. Relations live in native properties only (never duplicated as metadata inventories in page bodies). `Goals.Status` uses native Notion `Status`; other databases use `Select`. `Tasks.Google Drive File` is an optional external integration; native `Drive` URL properties work without it.
- **Google Drive roots:** `01-projects/<project>/{docs,drafts,submissions,assets}/`, `02-areas/<area>/` (preserving meaningful subdivisions such as `personal/private` and `software-development/certifications`), `03-resources/<resource>/`, `04-archives/01-projects/<project>/`, and demand-driven `05-intake/`.
- **Portable blueprint vs. observed snapshot:** `notion-workflow`, `notion-initialization`, and `system-integrity-audit` bundle `assets/notion-blueprint.json` (symbolic portable contract with zero source workspace IDs and all 11 required Notion formula expressions user-verified as `known`) separately from `assets/workspace-map.json` (observed installation locator only). Any future unrecovered required formula remains explicitly `unknown` until verified.

## Required Apps Setup (`Notion` & `Google Drive`)

### Notion

- **Pre-configured MCP:** Ships with the official hosted Notion remote MCP server (`https://mcp.notion.com/mcp`) in `mcp.json`, `.mcp.json`, and `mcp_config.json`.
- **Authentication:** Sign in with OAuth on first use. No live workspace writes occur automatically on installation.

### Google Drive

Connect Google Drive using your active provider's native integration or synced local Drive folder. No external Drive MCP endpoint is invented by this package.

## Package Validation

Run the self-contained Python standard-library validator from the package root:

```bash
python scripts/validate-package.py
python scripts/validate-package.py --self-test
node skills/task-writing/scripts/vocabulary.mjs
```

Static validation verifies manifests, YAML frontmatter, JSON schemas, local link autonomy, synchronized contract equality, symbolic blueprint integrity, and vocabulary validity. It does not simulate live Notion/Drive API runtime execution.
