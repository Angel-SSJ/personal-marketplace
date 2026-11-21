# Personal storage architecture and lifecycle

This is the user's confirmed local profile, shared by the three methodology skills. It adds exact directory roles to the general methods. It prescribes no project-name format, filename convention, mandatory root file, README, or contents/sections of documents. The directory names below are structure, not document naming rules.

## Parent paths and structural layout

Paths are relative to the person's chosen storage root, not to this skill package or an automatically selected workspace. Maintain the same four PARA parents and category meaning across relevant storage surfaces. Respect ownership/access; aligning existing storage requires an authorized migration, not blind mirroring or copying all contents.

```text
01_projects/
  <project>/
    docs/
    drafts/
    submissions/
    assets/
02_areas/
  <area>/
03_resources/
  <topic-or-utility>/
04_archives/
  Projects/
  Areas/
  Resources/
```

Angle-bracket entries illustrate containers whose names the person chooses freely. They do not impose a naming pattern. For a newly established supported project, the four sibling directories define its internal layout. When auditing existing projects, inspect their role coverage and propose missing structure; do not create empty trees in unrelated storage, duplicate active commitments, or claim a migration was executed.

Keep nesting shallow: project directories are siblings under 01_projects, their four role directories are direct children, and Areas/Resources use flat direct containers. Further nesting requires a concrete retrieval/ownership need rather than a speculative taxonomy. Standard Archive category children are part of the profile, not a reason for arbitrary extra levels.

## Directory responsibilities

| Destination                        | Holds                                                                                                                  | Boundary                                                                                                                                                   |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01_projects/<project>/docs/        | Current working documents, living drafts, editable intermediate packets                                                | Superseded iterations and temporary scratches move to drafts; finalized frozen exports live in submissions                                                 |
| 01_projects/<project>/drafts/      | Scratches, temporary working notes, discarded iterations, superseded versions                                          | Despite the name, the current living draft belongs in docs; retain history without cluttering the active version                                           |
| 01_projects/<project>/submissions/ | Finalized, frozen, export-ready deliverables and delivered snapshots                                                   | Never overwrite the frozen record during iteration; edit working material in docs and produce a distinct final snapshot                                    |
| 01_projects/<project>/assets/      | Project-exclusive sources, raw data, media, references, and external materials                                         | Shared/reusable canonical references may stay in Resources or Areas with links; do not force divergent copies                                              |
| 02_areas/<area>/                   | Ongoing standards, policies, long-term logs, current contracts, recurring procedures                                   | Finite-project drafts and deliverables do not live directly here; use narrowly justified records/receipts subdirectories only for real recordkeeping needs |
| 03_resources/<topic-or-utility>/   | Reusable templates, knowledge, summaries, snippets, research, and source assets without a current performance standard | A potential project reminder belongs in Someday/Maybe; its background material can remain here                                                             |
| 04_archives/Projects/              | Whole inactive project containers with their internal layout preserved                                                 | No live working edits; preserve frozen deliverables and provenance                                                                                         |
| 04_archives/Areas/                 | Retired responsibility containers                                                                                      | An Area is retired when the role ends, not “completed” like a finite project                                                                               |
| 04_archives/Resources/             | Obsolete/inactive topic containers retained for history                                                                | Retain and retrieve according to actual usefulness and retention needs                                                                                     |

## Active project and Area boundaries

A supported active project is a real finite multi-action commitment with an identifiable finish and a genuine agreed target horizon/date. Each active project container needs a corresponding visible Next Action or Waiting For reminder in the action system. A folder is not itself an action list. A GTD project with no support need does not require a folder.

If a target date is unknown, surface the gap and clarify the real agreement or planning horizon; never manufacture a hard task deadline, cancel a genuine promise, or hide it in Resources merely to satisfy the profile. An estimated planning target is not a hard deadline or an arbitrary task due date. Typical sub-year scope is guidance; larger ambitions can yield nearer finite outcomes without a universal twelve-month cutoff.

Future-trigger-only or deliberately paused work is not an actively supported container under this stricter profile. Preserve its reminder and useful support in the appropriate nonactive category, and reactivate when a genuine next action/waiting relationship exists. If active work has no route forward, expose the gap before moving anything; do not invent an action or silently reclassify accepted work.

An Area maintains a standard indefinitely. When fulfilling that standard requires a finite multi-step outcome or project deliverable, create/link a Project and keep its active drafts there. A single routine call, inspection, or habit can remain an Area-related action in the task system without creating a fake multi-step project or storing the to-do in the Area folder. Standards and persistent records stay in the Area.

## Work and delivery pipeline

Initiate real commitment and action/waiting linkage → establish project support layout → gather/link relevant assets → edit current work in docs → move superseded/scratch iterations to drafts → export a finalized snapshot into submissions → verify outcome and remaining obligations → harvest reusable knowledge → archive intact when inactive.

These steps do not require any particular file or its contents. A finalized export alone does not close the project. Check sign-off, residual follow-ups, and the actual outcome. If a frozen submission needs correction while the project is active, revise working material in docs and create a separate finalized artifact; preserve the prior delivered record. No filename/version syntax is imposed.

## Harvest, archive, and reactivate

Promote genuinely reusable templates or knowledge from project docs/assets into 03_resources, or retain responsibility-specific standards in 02_areas. Preserve source provenance and access; a copy or link is often safer than removing evidence needed by a delivered record. Not every raw source becomes a Resource.

Before archiving, complete, transfer, or explicitly renegotiate remaining obligations in the action system. Move the entire inactive project to 04_archives/Projects without reorganizing its internal layout. Retired Areas go to 04_archives/Areas; inactive Resources go to 04_archives/Resources. Temporary waiting is not completion; a waiting active project normally stays in Projects.

Archive is behaviorally read-only cold storage: do not author or revise working material there. Read-only historical lookup is allowed and does not by itself reactivate a project. If actual work resumes, restore the whole relevant project to 01_projects, establish its current action/waiting state, and edit working material in docs while preserving submissions. Reusable reference reactivation can return a topic to 03_resources; renewed responsibility belongs in 02_areas. Do not overwrite an active destination; resolve identity/collision and preserve records first.

Immutability here is workflow policy, not a claim of filesystem permissions, automatic versioning, or tamper-proof storage. All moves, edits, exports, link repairs, and deletions require actual authorization/access and verification. Updating this skill does not execute any of them.

## Review and retrieval

- Weekly: synchronize supported Projects with current Next Actions/Waiting For, lifecycle changes, and support retrieval in the existing Weekly Review.
- Monthly: check Area standards and active responsibilities; a quarterly broader check can supplement this when useful. Spawn real finite outcomes rather than leaving active deliverable drafts in Areas.
- On reuse/as needed: check Resources relevance, provenance, and retrieval. Optional quarterly hygiene handles recurring clutter. Distill incrementally at useful encounters; do not summarize every reference on arrival.
- Annually: review archive retention and retrieval needs. Identify purge/export candidates subject to actual obligations and authorization; never automatically delete historical records.

The intake's sixty-second retrieval goal is a local usability target, not a universal theorem or a mandate for alphabetical filenames. Assess a representative retrieval task and fix actual friction. Keep reviews proportionate; a failed folder check is not a reason to repeat a full-system audit every day.

## Temporary Intake extension

The four PARA categories remain the support homes. The additional 05_intake staging parent is governed by [Inbox and Intake policy](intake-policy.md), including projects/areas/resources containers, unknown-destination inbox, justified holds and verified exits. It is temporary, not another permanent support category.
