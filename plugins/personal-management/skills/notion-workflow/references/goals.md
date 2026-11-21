# Goals contract

## Scope and identity

Goals tracks a desired result with a success criterion and a chosen review horizon. Two-day, ten-week and other durations are valid; elapsed time does not determine entity type. A task expresses an action, a project organizes finite deliverable work, an Area maintains an ongoing standard, and a Goal records the desired result whose achievement is reviewed. This is the user's local operational adaptation, not a fixed GTD horizon rule.

Use the live-verified source IDs and property schema in assets/workspace-map.json. The initial Goals collection is collection://41fa6b72-a529-8186-9a0a-000b39d4c045. Identify the database and linked dashboard separately. The snapshot preserves actual structural definitions, not goal records. No parent-goal hierarchy or separate metrics database is currently mapped.

## Properties and meanings

| Property                        | Handling                                                                                                                                         |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name                            | Desired result, preserving the user's intent                                                                                                     |
| Success Criteria                | Observable evidence or agreed condition of achievement; ask if unclear                                                                           |
| Status                          | Native Status with Candidate, Active, On hold, Achieved, Dropped; use exact live options                                                         |
| Start Date                      | Actual planned start of the goal period, not automatic task scheduling                                                                           |
| Target Date                     | Desired achievement horizon; distinguish planning intent from an explicitly agreed hard deadline                                                 |
| Review Date                     | Next evidence/decision review; may be earlier than Target Date                                                                                   |
| Progress                        | Number formatted as percentage; manual user-supplied judgment with its stated basis; write 0.25 for 25 percent when using raw numeric properties |
| Days Remaining                  | Derived from Target Date; read-only; unknown formula execution is not an observed value                                                          |
| Area                            | Responsibility context through reciprocal Areas Goals                                                                                            |
| Projects                        | Contributing projects through reciprocal Projects Goals                                                                                          |
| Direct Tasks                    | Independent contributing actions through reciprocal Tasks Goals                                                                                  |
| Evidence                        | Notes and references supporting assessment through reciprocal Notes & References Goals                                                           |
| Created Time / Last Edited Time | System-maintained; never fabricate historical timestamps                                                                                         |

Do not force a numeric metric onto a qualitative goal or invent intermediate progress. Progress reaching 100 percent does not by itself authorize Achieved. Missing manual progress remains unknown, not zero. The field is Number/percent; a ring is not assumed unless the live schema or UI confirms that setting.

## Relationship routes

Use Goal -> Direct Tasks for a few independent actions. Use Goal -> Projects -> Tasks for organized project work. Both routes may contribute to one goal when distinct actions warrant them. Reuse existing relevant records before creating more. A Project is optional for a goal and a Goal is optional for ordinary projects/actions.

Prefer direct links for tasks outside contributing projects rather than redundantly maintaining the same task through both routes. Do not erase a user-maintained redundant link automatically. Deduplicate by task identity when producing a combined action view or summary. Direct Tasks does not itself enforce that a task has no Project. Multiple linked goals are technically possible; avoid assuming a mandatory single-goal cardinality not enforced by the live schema.

An Area link establishes context, never a commitment. Evidence links to actual notes or references and their Drive sources. Do not create placeholder evidence or fake Drive URLs. Projects and Tasks expose Goals as reciprocal properties; set one side and verify both rather than issue redundant competing writes. Stages contribute through their Projects and do not need an invented Goals property.

## Lifecycle

Candidate -> Active when the user accepts pursuit of the result. Establish the criterion, horizon if supplied and an actual route forward through direct actions or projects; expose missing information without inventing commitments. Candidate can remain undated until intent is clear.

Active -> On hold when deliberately paused, recording the known reason and reconsideration trigger in existing support. Inspect linked commitments and ask which remain independent or require renegotiation. A hold never silently cascades into cancellation or suspension of tasks/projects.

Active or On hold -> Achieved after reviewing Success Criteria and actual evidence with accepted user intent. Completing linked projects, reaching a target date or closing every task is insufficient by itself. An accepted authoritative user completion statement can supply the decision; do not demand a new evidence document.

Candidate, Active or On hold -> Dropped only for an accepted decision to stop pursuing the result. Preserve evidence/history and inspect residual obligations. Linked tasks/projects retain their actual state until separately authorized decisions cover them. Reopen a terminal goal only within a user request, then verify its current criterion, context and route forward.

Review Date identifies when to reassess rather than when to perform all work. A two-day goal may benefit from a next-day review and a ten-week goal from the existing weekly review; suggest these proportionately and obtain the real date from user intent rather than impose defaults. Target Date alone does not create Due Date on child tasks, calendar appointments, or timeboxes. Preserve overdue history instead of silently extending targets to today.

## Inbox and method handoff

An ambiguous aspiration is clarified in Inbox before activation. If it is retained as a Candidate goal, the existing Inbox Decision can explain the destination and an authorized page-body mention can link the Goal. Inbox has no Goals relation in the current schema. Ask before a structural addition; do not write a Goal into the Project field. Mark Processed only after the accepted routing is actually complete. A vague someday wish can remain Someday/Maybe without a forced Goal record.

Use GTD for accepted commitments, next-action discovery and review, PARA for real support location, CODE for selecting and interpreting evidence, and task-writing for action expression and vocabulary. Goals does not automatically select MoSCoW or map p1-p4 from method categories.

## Views and dashboard

The source Goals base currently provides Full Details, Active Goals, Candidates, Review Due, Timeline, By Area and Achieved & Dropped. Active Goals filters Active, Candidates filters Candidate, and Review Due selects Active/On hold with Review Date on or before today or empty. Timeline uses Start Date to Target Date. By Area groups by Area while excluding terminal states. Achieved & Dropped shows both terminal decisions and evidence. Check stored IDs/configuration and actual provider responses before modifying any view.

The linked Goals dashboard initially exposes Active Goals. Source views and dashboard tabs remain distinct surfaces. Do not promise that source tabs appear everywhere automatically. Absence of a source view on the dashboard is not automatically a defect.

## Behavioral cases for review

- A two-day decision goal uses direct tasks, with no automatically created project.
- A ten-week validation goal links multiple projects and independent recruiting actions when accepted.
- A task linked through both routes appears once in a combined report.
- All tasks Done, but success not observed: retain actual goal state and review the missing evidence.
- Goal is paused or dropped: propose handling of genuine remaining commitments without silent cascades.
- Target changed: preserve child due dates unless the actual agreements change within scope.
- A live option, relation or date field differs: re-fetch and ask for missing semantic equivalence rather than create a replacement.
