# Personal Management

Personal productivity and knowledge management suite integrating GTD, PARA, CODE, Inbox/Intake processing, MoSCoW prioritization, task writing, file naming, and Notion + Google Drive workflows.

## Included Skills

- **`/code-knowledge-workflow`** (`skills/code-knowledge-workflow/SKILL.md`): Capture, Organize, Distill, and Express (CODE) knowledge workflows and work packets.
- **`/file-naming`** (`skills/file-naming/SKILL.md`): Consistent naming policy for documents, media, data, scripts, and source files across origins.
- **`/gtd-workflow`** (`skills/gtd-workflow/SKILL.md`): Getting Things Done (GTD) commitment clarification, next actions, waiting items, weekly reviews, and engagement.
- **`/inbox-workflow`** (`skills/inbox-workflow/SKILL.md`): Inbox capture, clarification, `05_intake` staging, entity matching, and pending package incorporation.
- **`/moscow-prioritization`** (`skills/moscow-prioritization/SKILL.md`): Explicit MoSCoW scope prioritization, dependency checks, and capacity feasibility reviews.
- **`/notion-workflow`** (`skills/notion-workflow/SKILL.md`): Live Notion workspace reading, updating, mapping, goal tracking, and structural drift checks.
- **`/para-workflow`** (`skills/para-workflow/SKILL.md`): PARA (Projects, Areas, Resources, Archives) information architecture and storage lifecycle management.
- **`/task-writing`** (`skills/task-writing/SKILL.md`): Actionable task titles, descriptions, validated priority/tag vocabularies, dates, timeboxes, and waiting reminders.

## Required Apps & Integrations

This plugin is designed to operate with **Notion** (action, goals, and workspace records) and **Google Drive** (permanent PARA file storage):

- **Notion**: Configured out of the box via the official hosted Notion remote MCP server (`mcp_config.json` -> `https://mcp.notion.com/mcp`, OAuth). If you already use the official Antigravity Notion plugin, you can keep using its existing account connection.
- **Google Drive**: Connect Google Drive using the official Antigravity Google Drive plugin (`gdrive`) or your workspace's synced Google Drive root so file-naming, PARA, CODE, and Intake workflows can inspect and organize files.

## Installation in Antigravity

```bash
agy plugin validate ./plugins/personal-management
agy plugin install ./plugins/personal-management
```
