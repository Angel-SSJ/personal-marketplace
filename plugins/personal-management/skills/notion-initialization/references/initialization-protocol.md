# Two-phase Notion initialization protocol

## Portable blueprint versus observed snapshot

- Read [notion-blueprint.json](../assets/notion-blueprint.json) as the normative symbolic contract for the seven required databases: `Goals`, `Areas`, `Projects`, `Stages`, `Tasks`, `Inbox` and `Notes & References`.
- Treat [workspace-map.json](../assets/workspace-map.json) strictly as an observed locator for an existing installation. Never copy observed source IDs, collection URLs, property URLs or source-workspace-specific templates into a new workspace.
- Record newly created or reconciled destination IDs in operation evidence so interrupted runs can resume safely without mutating the static plugin snapshot.

## Phase A: Structure creation, reconciliation and verification gate

1. **Discover before creating:** Confirm the target workspace, parent page, connector capabilities and permissions. Search and list existing databases to full pagination (`has_more=false`).
   - Truncated results (`has_more=true`) or denied access (e.g. unreadable `Tasks`) yield insufficient evidence (`U`). Never treat an unreadable or unpaginated database as absent, and never create a duplicate database.
   - Reconcile existing databases by identity and meaning, not title alone (reuse existing `Projects`; never create an 8th database by inference).
2. **Create confirmed missing required databases and independent fields:** Only after pagination is complete and absence is confirmed, create missing databases in safe order (`Areas`, `Goals`, `Projects`, `Stages`, `Tasks`, `Inbox`, `Notes & References`) with their independent scalar, date, URL, file, number-percent, `Select`, `Multi-select` and managed timestamp properties.
   - Preserve native `Status` on `Goals` (default `Candidate`; groups `to_do`: `Candidate`; `in_progress`: `Active`, `On hold`; `complete`: `Achieved`, `Dropped`) versus `Select` `Status` on `Projects`, `Stages`, `Tasks`, `Inbox` and `Notes & References`.
3. **Link internal relations:** Configure all required bidirectional and unidirectional relations using newly verified destination database IDs. Set bidirectional relations cleanly without duplicate competing definitions.
4. **Derived fields (formulas and rollups):**
   - Required formulas whose expressions are `unknown` in the blueprint (where only a formula code locator was observed, e.g. `Days Remaining`, `Calculated Progress`, `Available`, `Done Count`, `Eligible Count`, `Is blocked`, `Is blocking`, `Needs Clarification`) CANNOT be fabricated or certified as exact replicas.
   - Obtain verified formula expressions via a capable API or directly from the user's Notion formula editor. A proposed functional alternative is a separate user-approved design, never a verified replica.
   - Rollups (`Completed Tasks`, `Eligible Tasks` on `Projects` and `Stages`) depend on verified `Tasks` relations and `Tasks.Done Count` / `Tasks.Eligible Count` formulas.
   - While any required formula or database remains unknown, inaccessible or unverified, **Phase A remains explicitly partial** with a concrete list of pending items.
5. **Optional components and templates:**
   - `Tasks.Google Drive File` is an **optional** external synced relation. Its unavailability does NOT block Phase A or setup; the native `Drive` URL property supports Drive links without it. Link it only if a verified external target exists; never create an 8th database.
   - Do not create new templates or copy source-workspace-specific templates unless explicitly requested. Preserve existing views; additional views are optional for database initialization.
6. **Strict Phase A gate:** Re-read live schemas for ALL SEVEN required databases and verify every required property, option, relation and derived field. A connector success response alone does not prove schema correctness. **Do NOT enter Phase B until the full seven-database required structure is verified**—even if the user's supplied inputs only reference a subset of databases (such as `Goals` and `Tasks`).

## Phase B: User-supplied data insertion (only after Phase A passes)

- Omit Phase B completely if the user only requested structure creation.
- Never insert sample data, demo records or unrequested templates.
- Clarify decisive ambiguities, search existing records to avoid duplicates, check date/hierarchy/state invariants and insert ONLY user-supplied records in safe dependency order: `Areas` -> `Goals` -> `Projects` -> `Stages` -> `Tasks` -> `Notes & References` / `Inbox`.
- Apply appropriate verified existing templates if present on the target database, set relations in native properties only (never duplicated in bodies), and verify persisted records and links before reporting completion.
