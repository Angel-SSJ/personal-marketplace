# Personal Management

Personal productivity and knowledge management suite integrating GTD, PARA, CODE, Inbox/Intake processing, MoSCoW prioritization, task writing, file naming, and Notion + Google Drive workflows.

## Metadata

- **ID:** `personal-management`
- **Category:** `productivity`
- **Version:** `0.1.0`
- **License:** `MIT`
- **Providers:** Codex, Claude (Code & Cowork), Antigravity, Cursor, Kimi Code, OpenCode

## Bundled Skills

| Skill                     | Purpose                                                                                             |
| :------------------------ | :-------------------------------------------------------------------------------------------------- |
| `code-knowledge-workflow` | Knowledge capture, distillation, work packets, and expressive outputs (CODE).                       |
| `file-naming`             | Cross-origin filename policy for support documents, media, data, and source files.                  |
| `gtd-workflow`            | Commitment clarification, next actions, waiting items, weekly reviews, and overload recovery (GTD). |
| `inbox-workflow`          | Loose-input triage, `05_intake` staging, entity matching, and pending package incorporation.        |
| `moscow-prioritization`   | Explicit MoSCoW scope prioritization, omission tests, and capacity checks.                          |
| `notion-workflow`         | Notion database, page, view, and goal operations anchored to the workspace map.                     |
| `para-workflow`           | Projects, Areas, Resources, and Archives storage organization and lifecycle transitions (PARA).     |
| `task-writing`            | Task title/description expression and JSON-validated priority and tag vocabularies.                 |

## Required Apps Setup (`Notion` & `Google Drive`)

### Notion

- **Pre-configured MCP**: Ships with the official hosted Notion remote MCP server (`https://mcp.notion.com/mcp`) in `mcp_config.json` (Antigravity) and `.mcp.json` (Claude, Cursor, Codex, Kimi Code).
- **Authentication**: Sign in with OAuth on first use (Codex marketplace policy is set to `authentication: "ON_USE"`).
- **OpenCode**: Configure the Notion remote MCP server (`https://mcp.notion.com/mcp`) in your `opencode.json` if you want live Notion access alongside the auto-discovered skills.

### Google Drive

Permanent PARA files (`01_projects`, `02_areas`, `03_resources`, `04_archives`, `05_intake`) live in Google Drive. Connect Google Drive using your active provider's native integration or synced local Drive folder:

- **Google Antigravity**: Install and sign in to the official Google Drive (`gdrive`) plugin.
- **Claude (Code & Cowork)**: Enable the native Google Drive connector or mount your Google Drive folder locally.
- **Cursor / OpenAI Codex / Kimi Code / OpenCode**: Enable your provider's Google Drive connector/MCP server or work against your local Google Drive for Desktop sync root.
