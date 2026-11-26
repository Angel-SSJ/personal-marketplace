# Personal Management

Self-contained ten-skill personal productivity and knowledge management suite integrating GTD, PARA, CODE, Inbox/Intake processing, MoSCoW prioritization, task writing, global file and folder naming, Notion workflow, two-phase Notion initialization, and read-only cross-layer system integrity auditing.

## Included Skills

- **`/code-knowledge-workflow`** (`skills/code-knowledge-workflow/SKILL.md`): Capture, Organize, Distill, and Express (CODE) knowledge workflows and work packets.
- **`/file-naming`** (`skills/file-naming/SKILL.md`): Global file and folder naming policy across ordinary files, technical exceptions, numbering, and provisional capture.
- **`/gtd-workflow`** (`skills/gtd-workflow/SKILL.md`): Getting Things Done (GTD) commitment clarification, next actions, waiting items, timeline semantics, weekly reviews, and engagement.
- **`/inbox-workflow`** (`skills/inbox-workflow/SKILL.md`): Inbox capture, clarification, `05-intake` staging, entity matching, and idempotent package incorporation.
- **`/moscow-prioritization`** (`skills/moscow-prioritization/SKILL.md`): Explicit-selection MoSCoW scope prioritization, dependency closure, and capacity feasibility reviews.
- **`/notion-initialization`** (`skills/notion-initialization/SKILL.md`): Two-phase Notion workspace initialization (`Phase A` full seven-database structure gate before `Phase B` user-supplied records).
- **`/notion-workflow`** (`skills/notion-workflow/SKILL.md`): Live-schema Notion workspace reading, updating, templates, views, goal tracking, and structural drift checks.
- **`/para-workflow`** (`skills/para-workflow/SKILL.md`): PARA (Projects, Areas, Resources, Archives) information architecture and storage lifecycle management, preserving `04-archives/01-projects/`.
- **`/system-integrity-audit`** (`skills/system-integrity-audit/SKILL.md`): Read-only cross-layer integrity auditing across Notion and Google Drive with explicit coverage limits and non-defect preservation.
- **`/task-writing`** (`skills/task-writing/SKILL.md`): Actionable task titles, descriptions, JSON-validated priority (`p1`–`p4`) and lowercase tag vocabularies, dates, timeboxes, and waiting reminders.

## Required Apps & Integrations

This plugin is designed to operate with **Notion** (action, goals, and workspace records) and **Google Drive** (permanent PARA file storage):

- **Notion**: Configured out of the box via the official hosted Notion remote MCP server (`mcp_config.json` -> `https://mcp.notion.com/mcp`, OAuth). If you already use the official Antigravity Notion plugin, you can keep using its existing account connection.
- **Google Drive**: Connect Google Drive using the official Antigravity Google Drive plugin (`gdrive`) or your workspace's synced Google Drive root so file-naming, PARA, CODE, and Intake workflows can inspect and organize files.

## Installation in Antigravity

```bash
agy plugin validate ./personal-management
agy plugin install ./personal-management
```
