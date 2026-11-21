# Plugin Catalog

Discover and install personal plugins across all 6 supported AI providers.

## Marketplace Install Commands

| Provider                   | How to Add / Install Plugins from This Marketplace                                                                                                                                                           |
| :------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Claude (Code & Cowork)** | `claude plugin marketplace add Angel-SSJ/personal-marketplace`                                                                                                                                               |
| **GPT / OpenAI Codex**     | `codex plugin marketplace add Angel-SSJ/personal-marketplace`                                                                                                                                                |
| **Cursor**                 | Add `https://github.com/Angel-SSJ/personal-marketplace` in Cursor Settings -> Plugins                                                                                                                        |
| **Google Antigravity**     | `agy plugin install https://github.com/Angel-SSJ/personal-marketplace/tree/main/plugins/<id>` (or workspace discovery via `.agents/plugins.json`; see [docs/README.antigravity.md](./README.antigravity.md)) |
| **Kimi Code**              | `/plugins marketplace https://raw.githubusercontent.com/Angel-SSJ/personal-marketplace/main/.kimi-plugin/marketplace.json`                                                                                   |
| **OpenCode**               | Add `"personal-marketplace@git+https://github.com/Angel-SSJ/personal-marketplace.git"` to `opencode.json` (`plugins` in V2, `plugin` in V1)                                                                  |

## Available Plugins

| ID                    | Display Name        | Category       | Providers | Description                                                                                                                                                                                       |
| :-------------------- | :------------------ | :------------- | :-------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `personal-management` | Personal Management | `productivity` | All 6     | Personal productivity and knowledge management suite integrating GTD, PARA, CODE, Inbox/Intake processing, MoSCoW prioritization, task writing, file naming, and Notion + Google Drive workflows. |
