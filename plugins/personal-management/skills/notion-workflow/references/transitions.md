# Workflow transitions

## Inbox

Capture unclear input as Inbox, or clarify a blank-status capture before processing. For a clarified idea/file, inspect existing entities before proposing reuse or creation. One input may yield an existing/new action, an existing/new note, or both. Use Inbox Tasks and Notes relations to preserve the result. Processed requires the intended clarification and routing actually completed. Do not mark Processed merely after changing a label. Failures leave the transition pending and expose partial created records for reuse on retry.

On hold is justified for a known-destination package with a concrete incorporation dependency. Preserve Intended Home, Hold Reason and Exit Condition using the existing support. The fields are available aids, not mandatory contents for every captured item. Keep a real action/Waiting For reminder visible separately. Release after the condition is met and incorporation verified. Someday/Maybe belongs to an incubated reminder, with useful support in its proper home rather than indefinite Intake.

## Tasks

Next Action denotes a selected executable action. In progress denotes started work. Waiting For requires the expected external result and responsible party, with a real follow-up if known. Scheduled uses a genuine future start/reconsideration trigger. Due Date is a real deadline, never a preferred work date. In review is a genuine approval/review step. Someday/Maybe is an uncommitted possibility. Done requires evidence appropriate to the user's requested completion; Cancelled requires the accepted cancellation of work and preservation/renegotiation of any genuine promise.

Blocked by is an independent dependency relation; an item can have Next Action state yet be withheld from the current Next Actions view. A parent with Subtasks is withheld by that view. Project or Stage On hold does not automatically prohibit independent explicitly executable tasks. Check independence and actual blockers rather than enforce a blanket inherited status rule.

On task closure, inspect directly dependent tasks and propose which can be released, retaining dependency history. Do not automatically delete relations or promote dependent work. Current Next Actions filters require an empty Blocked by field; preserving the historical link can therefore keep a task hidden after resolution. Disclose this conflict and offer a scoped, explicitly authorized filter redesign or another user-selected handling. Do not claim release succeeded from the predecessor's closure alone.

## Projects and Stages

Planned is accepted planned work; Active is underway, On hold is deliberately paused, Done means the actual outcome/stage exit verified, and Cancelled is a decided cancellation. Task completion percentage alone does not establish project completion. Confirm residual obligations and delivery before closure. Start/End dates are planning horizons unless the user explicitly supplies a hard deadline. Milestone Date and Milestone Criterion describe a simple checkpoint; Deliverable links its actual output. Goals can coordinate results across projects or direct actions using the local [Goals contract](goals.md). No separate milestone entity is assumed.

Stage tasks should reference that stage's project. Subtasks must preserve the correct Project/Stage linkage explicitly if live relations do not inherit. Inspect self-dependencies, cycles, contradictory identities and cross-project stage assignments before adding links. Flag existing conflicts, and ask where intent is unclear. Multi-project relation capability is not evidence that every task should belong to multiple projects.

## Notes and Areas

In review -> Saved after the relevant review decision; Saved -> Archived when deliberately inactive; reopening depends on the user's intent. Pinned is an independent checkbox. Type identifies Idea, Meeting, Note, Reference or Resource. A note can generate a linked task without becoming an executable task itself. Resources is a view of notes, not a separate database. Areas maintain ongoing standards, have no finite completion requirement, and may own routine actions directly. Archived area means the responsibility has ended. Preserve Drive provenance and access.
