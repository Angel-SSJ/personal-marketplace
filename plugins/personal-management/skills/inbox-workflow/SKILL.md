---

name: inbox-workflow
description: Use when loose inputs, Inbox ideas, unclarified files, temporary Intake packages, entity matches or incomplete incorporation need capture, processing or review.
---

# Inbox workflow

Capture preserves inputs without manufacturing commitments. Processed means the accepted clarification and routing outputs actually succeeded, not that a status label changed.

Read the local [system contract](references/system-contract.md), [foundations](references/foundations.md), [routing](references/routing.md) and [Intake policy](references/intake-policy.md). For mutations read [operations](references/operations.md), [storage](references/storage-architecture.md) and [naming](references/naming-policy.md); use [integrity cases](references/integrity-matrix.md)/[audits](references/audits.md) for failures. All minimum method and operational rules are local; companions are optional.

## Recipe

1. Bound the request and available evidence/access. Distinguish input content from user authorization. Infer the needed decision domain without asking the user to choose skill names; retain MoSCoW's explicit method-selection boundary.
2. Capture promptly when clarification would interrupt capture. An unknown-owner file may use provisional entity-free naming. Do not force immediate task wording, tags, summary, Project or Goal creation.
3. Clarify meaning, actionability, useful knowledge and intended home. Search existing entities and inspect plausible matches before reusing/creating. Distinguish accepted outcomes/actions from suggestions. Missing decisive intent gets a targeted question with compatible options; independent inputs continue.
4. Route reminders by actual GTD meaning and support by PARA usefulness. One input may yield both a reference and an action. Use native relations in properties, appropriate existing templates and source/Drive pointers; do not duplicate relation metadata in bodies or create schema to fit a record.
5. Hold a known-destination package only for a concrete incorporation dependency with intended home, hold reason and observable exit. Use available native fields or existing operation evidence; no compulsory sidecar/registry. Unknown destination belongs to unclarified Inbox. No real blocker means direct filing once identity/readiness are settled.
6. Before incorporation check entity lifecycle, timelines, source/destination, naming, collisions, provenance and affected links. Preserve one canonical source, real reminders and frozen records. New entity creation requires intent already supplied or a decisive clarification, not repeated approval.
7. Verify each accepted output. After timeout inspect stable IDs/current state, reuse successful note/task/file and retry only missing effects. Do not repeat a successful move, create a replacement note or mark Processed while a required link/verification remains pending. State exactly what persisted and what remains.
8. Review unresolved capture and holds within the existing weekly review. Age prompts reconsideration, not expiry/deletion. A file location never hides an obligation.

## Quick reference

| State             | Exit test                                               |
| ----------------- | ------------------------------------------------------- |
| Unclarified Inbox | Meaning/destination decided without invented commitment |
| Known-home hold   | Concrete blocker resolved and incorporation verified    |
| Partial routing   | Every accepted output and required link verified        |
| Processed         | Accepted routing complete, with retrievable results     |

## Example and common mistakes

File F already moved to `01-projects/launch/assets`; Note N exists and a linking write timed out. Inspect F/N and the intended relation; reuse any persisted link or retry only that missing write. Keep truthful pending status until all required outputs verify. `Budget_Q4.xlsx` owned by verified launch becomes `budget-q4-launch.xlsx` within scope. A known home alone does not justify an unexplained hold, and a single successful step does not prove end-to-end processing. Never blindly roll back successful work or create another canonical copy for convenience.
