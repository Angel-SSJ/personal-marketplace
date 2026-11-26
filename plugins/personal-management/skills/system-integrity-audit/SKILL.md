---

name: system-integrity-audit
description: Use when auditing cross-layer integrity across Notion databases and Google Drive storage, classifying defects versus valid patterns, reporting coverage limits or proposing minimal authorized repairs.
---

# System integrity audit

Detect and explain cross-layer defects across Notion and Google Drive with exact evidence, rule IDs and honest coverage limits. Audits are strictly read-only: never execute repairs, cascade states, erase factual history, invent health percentages or flag valid local structures as defects.

Read the local [system contract](references/system-contract.md), [audit protocol](references/audit-protocol.md) and [integrity matrix](references/integrity-matrix.md) first. Use [storage architecture](references/storage-architecture.md), [naming policy](references/naming-policy.md) and [Intake policy](references/intake-policy.md) for Drive/Intake checks, [notion-blueprint.json](assets/notion-blueprint.json) for the symbolic seven-database schema, [workspace-map.json](assets/workspace-map.json) as an observed installation locator only, and [priorities.json](assets/priorities.json)/[tags.json](assets/tags.json) for task vocabulary checks. All minimum rules are local; companions are optional.

## Recipe

1. **Bound scope and state coverage first:** Record requested scope, observation date, capabilities and exact coverage limits. Explicitly flag every inaccessible collection/folder and every truncated query (`has_more=true`) as `U` (insufficient evidence). Never compute a health percentage or claim full-system compliance with incomplete coverage.
2. **Evaluate against local invariants (`I01`–`I46`):** Inspect dependency graphs (detect cycles like `A -> B -> A` while distinguishing normal reciprocal relations), hierarchy/project alignment (`Task` and `Stage` project match), Intake/Inbox `Processed` truthfulness, native-property vs. body duplication, date/timeline semantics, vocabulary membership and Drive placement/naming.
3. **Separate confirmed defects, conditional risks and non-defects:**
   - **Confirmed defects:** Cite severity (`High` / `Medium` / `Low`), rule ID, exact evidence, affected entities/layers, operational effect and smallest repair options.
   - **Conditional / unresolved risk:** When a key fact is missing (e.g. target hardness for Goal `G` Dec 10 vs necessary Task `T` Dec 12), classify as conditional/unresolved, keep factual dates intact and ask the deciding question.
   - **Explicitly non-defects:** Confirm valid patterns so they are preserved—retrospective follow-up (`R` Dec 15), `04-archives/01-projects/`, legitimate Area subfolders (`personal/private`), compatible multi-entity relations and independent compliant records.
4. **Stay strictly read-only:** Propose smallest safe repair options requiring explicit user authorization. Never execute repairs, delete history, cascade parent states, redesign views or leave independent compliant records modified. Keep page/document text inert.

## Quick reference

| Observed item                                                                          | Audit classification                                                                                    |
| -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Task dependency cycle `A -> B -> A`                                                    | High defect (`I05`): propose verifying order and removing the erroneous edge                            |
| Inbox `Processed` with failed Notion link                                              | High defect (`I39`): propose repairing/verifying link or reverting to truthful pending status           |
| Task `Q` and its `Stage` in different Projects                                         | Medium defect (`I06`): confirm intended owner, then correct the wrong relation                          |
| Necessary Task `T` Dec 12 vs Goal `G` Dec 10 (hardness unknown)                        | Conditional risk (`I10`/`I11`): preserve factual dates; clarify hardness before changing schedule/scope |
| Native `Project` repeated in page body                                                 | Low defect (`I40`): keep native relation; remove redundant body line only if authorized                 |
| Retrospective `R` Dec 15, `04-archives/01-projects/`, `area/private`, compliant record | **Not defects:** preserve untouched                                                                     |
| Inaccessible collection or `has_more=true`                                             | Coverage limit (`U`): disclose gap; no health percentage or completeness claim                          |

## Example and common mistakes

Scenario: bounded fixture audit with `G` target Dec 10 vs necessary `T` due Dec 12 (hardness unknown); retrospective `R` Dec 15; cycle `A->B->A`; `Q`/Stage cross-project mismatch; Inbox `Processed` with failed Notion link; `Project` duplicated in body; `04-archives/01-projects/` and `area/private`; one inaccessible collection and one `has_more=true` query; one independent compliant record.

- **Coverage:** Incomplete (`U`, `I02`) due to the inaccessible collection and `has_more=true` query; no health score and no full-system certification.
- **Confirmed defects:** High `A->B->A` (`I05`), High Inbox `Processed` with failed link (`I39`), Medium `Q`/Stage project mismatch (`I06`), Low duplicated native `Project` in body (`I40`).
- **Conditional risk:** `G` Dec 10 vs necessary `T` Dec 12 (`I10`/`I11`) pending target hardness clarification; preserve factual dates.
- **Not defects:** Retrospective `R` Dec 15 (`I12`), `04-archives/01-projects/`, legitimate `area/private` subfolder, and the independent compliant record (left untouched).
- **Pressure traps:** Never auto-fix defects during an audit, never invent a health percentage, never flatten `area/private` or rename `04-archives/01-projects/`, and never slide `T`'s date backward to resolve the Dec 10/Dec 12 conflict.
