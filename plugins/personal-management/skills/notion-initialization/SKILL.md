---

name: notion-initialization
description: Use when creating, bootstrapping, reconciling or verifying the seven-database Personal Management Notion workspace structure, optionally followed by inserting user-supplied initial records.
---

# Notion initialization

Initialize or reconcile the Personal Management Notion workspace in two strict phases: verify the entire required seven-database structure first (Phase A), then insert only explicit user-supplied records (Phase B). Never mix data insertion into unverified structure, never copy source-workspace IDs or templates, and never fabricate unknown required formulas.

Read the local [system contract](references/system-contract.md), [initialization protocol](references/initialization-protocol.md) and [integrity cases](references/integrity-matrix.md) first. Use [notion-blueprint.json](assets/notion-blueprint.json) as the symbolic schema contract (required, optional and unknown components) and [workspace-map.json](assets/workspace-map.json) strictly as an observed locator for an existing installation—never as portable IDs. Validate task vocabulary against [priorities.json](assets/priorities.json) and [tags.json](assets/tags.json). All minimum rules are local; companions are optional.

## Recipe

1. **Phase A — Discovery & reconciliation:** Verify target workspace, parent page, permissions and connector capabilities. Exhaust pagination (`has_more=false`) before deciding any database is missing. Reuse existing verified databases by identity and meaning (e.g. existing `Projects`). Treat inaccessible databases (e.g. unreadable `Tasks`) or truncated searches (`has_more=true`) as insufficient evidence (`U`)—do not assume absence or create duplicates.
2. **Phase A — Structure creation in safe order:** Only for databases confirmed absent after full pagination, create missing databases and independent scalar/date/URL/file/Select/Multi-select/managed properties first, preserving native `Status` on `Goals` (`Candidate` default) versus `Select` on the other databases. Next link internal relations using newly verified destination IDs, then configure derived fields.
3. **Phase A — Required unknown vs. optional external boundary:**
   - Unrecovered required formulas (e.g. `Days Remaining` where only a code locator exists) remain explicitly `unknown`. Never invent a formula body and call it a replica; request the verified expression from the user/editor or keep Phase A explicitly partial.
   - Optional external `Tasks.Google Drive File` never blocks setup when unavailable; use native `Drive` URL properties and never create an 8th database by inference.
   - Skip source-workspace-specific templates and never create unrequested templates or sample data.
4. **Phase A verification gate:** Re-read live schemas across ALL SEVEN required databases (`Goals`, `Areas`, `Projects`, `Stages`, `Tasks`, `Inbox`, `Notes & References`) and verify every required component. Persist a resumable destination ID map in operation evidence without editing the static plugin snapshot. If any required database, access or formula remains unverified, stop at partial Phase A with an explicit pending list.
5. **Phase B — User-supplied inputs only:** Begin Phase B ONLY after the full Phase A gate passes. If the request is structure-only, omit Phase B. Insert only explicit user-supplied records in safe dependency order (`Areas -> Goals -> Projects -> Stages -> Tasks -> Notes & References / Inbox`), checking date/hierarchy/state invariants, keeping relations in native properties only and verifying persisted records.

## Quick reference

| Condition during setup                                     | Required decision                                                                            |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `has_more=true` or unreadable `Tasks`                      | Block absence conclusions and duplicate creation; finish pagination and restore access first |
| Existing `Projects` verified                               | Reuse it; reconcile missing required properties without duplicating                          |
| Required formula has code locator only (`Days Remaining`)  | Mark `unknown`; never fabricate; request definition or keep Phase A partial                  |
| Optional `Google Drive File` external relation unavailable | Does NOT block setup; rely on `Drive` URL; never create an 8th database                      |
| Phase A partial, user supplied `launch` goal + task        | Hold Phase B completely until ALL SEVEN required databases and required schema verify        |

## Example and common mistakes

Scenario: initialize all 7 databases then insert goal `launch` and one task; `Projects` exists, `Tasks` is unreadable, first search has `has_more=true`, `Goals.Status` and required `Days Remaining` have code locators only (no formula body), optional `Google Drive File` is unavailable (`Drive` URL available), and one template is source-workspace-specific.

- **Exact phase order:** (1) Complete Phase A discovery (paginate until `has_more=false`, restore `Tasks` read access, reconcile `Projects`); (2) create only confirmed-absent databases and known independent properties/relations (never creating while `has_more=true` hides existing databases); (3) resolve missing required definitions (`Days Remaining` formula expression, and verify native `Goals.Status` groups/default from the blueprint/live capability); (4) re-read and verify ALL SEVEN required databases; (5) only then run Phase B to insert `launch` and the task.
- **What can be created right now:** Nothing that assumes absence while `has_more=true`, and no duplicate `Projects` or `Tasks`. Reconcile known missing fields on verified `Projects` only if safe; hold new database creation until pagination finishes.
- **Optional vs. blocking:** Unavailable optional `Google Drive File` does NOT block setup (`Drive` URL works). Unreadable `Tasks`, incomplete pagination and unknown required `Days Remaining` formula keep Phase A partial and block Phase B.
- **Pressure traps:** Never insert `launch` + task after verifying only `Goals` and `Tasks` (all 7 required databases must pass Phase A), never guess `Days Remaining` formula code, never copy the source-workspace-specific template, and never insert sample records.
