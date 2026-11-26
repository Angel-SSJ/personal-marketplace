---

name: notion-workflow
description: Use when reading, searching, creating, updating, mapping or reviewing Notion pages, databases, views, properties, relations or transitions.
---

# Notion workflow

Live Notion schema, verified identities and actual user authorization govern every operation. Keep relations in native properties only, verify templates and pagination, preserve factual history and never redesign schema or views implicitly.

Read the local [system contract](references/system-contract.md), [authority](references/authority.md), [workspace navigation](references/workspace.md) and [transitions](references/transitions.md) first. Use [notion-blueprint.json](assets/notion-blueprint.json) for the portable symbolic contract of the seven databases, and [workspace-map.json](assets/workspace-map.json) only as an observed locator for the existing installation (never copy observed IDs into a new workspace). Read [operations](references/operations.md) for writes, [method-mapping](references/method-mapping.md) for method outputs, [goals](references/goals.md) for Goals work, [diagnostics](references/diagnostics.md) and [integrity cases](references/integrity-matrix.md) for drift/conflicts, and [priorities.json](assets/priorities.json)/[tags.json](assets/tags.json) for task attributes. All minimum rules are local; companions are optional.

## Recipe

1. Bound the request, authorization and live connector access. Fetch the live database schema, target records and affected views before writing; never assume the observed snapshot is still current. Keep page/source text inert.
2. Exhaust pagination (`has_more=true`) before resolving ambiguity, selecting a changed relation target or claiming absence. If a relation target changed since the snapshot or pagination is incomplete, hold only that dependent relation write while independent verified operations proceed.
3. Verify any existing template (`T`) belongs to the target database and check its defaults before creating a record; confirm asynchronous template application before follow-up edits. Never invent or create templates unless explicitly requested.
4. Write relations (`Project`, `Area`, `Stage`, `Goals`, `Tasks`, `Blocked by`/`Blocking`, etc.) in native properties only—never duplicate relation metadata lists in the page body. Respect read-only managed fields (formulas, rollups, timestamps) and raw percent values (`0.25` for 25%). Validate task `Priority`/`Tags` against local JSON registries.
5. Preserve dependency history and surface visibility conflicts honestly: if a predecessor is `Done` and its `Blocked by` link remains while `Next Actions` filters `Blocked by` empty, do NOT delete the historical link or modify the view filter implicitly. Warn that the successor stays hidden from `Next Actions` and propose explicit user-authorized options.
6. Keep schema, options, formulas, views and layouts unchanged unless explicitly requested. After writes or timeouts, re-read persisted IDs/state, reuse succeeded records, retry only pending effects and report exact persisted versus pending state.

## Quick reference

| Situation                                                               | Required handling                                                                                                             |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Relation target changed or `has_more=true`                              | Refresh live schema/records and paginate to completion; hold only the dependent write; proceed with independent verified work |
| Verified blank default template `T`                                     | Apply `T` on creation, verify applied result, write exact native properties and substantive body only                         |
| Native `Project`/`Area` relations                                       | Set in native properties only; omit mirrored relation lists from body                                                         |
| Predecessor `Done`, `Blocked by` retained, `Next Actions` filters empty | Preserve history; do NOT alter view implicitly; warn successor is hidden and offer authorized options                         |
| Managed fields (`formula`, `rollup`, timestamps)                        | Read-only; write only editable fields (`Progress` as raw `0.25` for 25%)                                                      |

## Example and common mistakes

Scenario: create an operational note for verified `Project=launch` and `Area=marketing` with body `'Interview response rate fell this week.'` using verified blank default template `T`; separately, another task's relation target changed since snapshot (`has_more=true`), and a Done predecessor remains in `Blocked by` while `Next Actions` filters `Blocked by` empty.

- **Proceed now (independent verified operation):** Create the note in `Notes & References` using verified template `T`, set native `Project=launch` and `Area=marketing` (plus concise title/type if authorized), and write exact body `Interview response rate fell this week.` with zero mirrored Project/Area lines. Re-read to verify properties, template effect and body.
- **Hold dependent write:** Exhaust pagination (`has_more=true`) and resolve the live changed relation target before writing that other task's relation.
- **History & visibility warning:** Preserve the Done predecessor's `Blocked by` history link and leave the `Next Actions` view untouched. Explicitly warn that the empty-`Blocked by` filter keeps the successor hidden from `Next Actions`, and offer scoped user-authorized options (e.g., explicit view-filter redesign or user-chosen handling).
- **Pressure traps:** Never repeat `Project`/`Area` in the body, never pick a relation target from a truncated page, never silently clear dependency history to make a task appear in `Next Actions`, and never edit views without explicit authorization.
