# Drift, bounded audits and scenarios

Compare live facts to the map only within requested scope. Categorize a difference as identity, type/option, relation, formula exposure, view function, presentation or semantic policy. A user's direct Notion edit may be intentional. Report evidence, effect and smallest proposed repair. Do not automatically restore the snapshot, redesign views or update this package.

## Observed differences to recheck

Earlier observations found that the source Tasks base lacked the dashboard Next Actions tab; the refreshed snapshot includes it. The dashboard exposes a table and calendar both named Scheduled & Tickler; the table filters Scheduled while the calendar is based on Start Date and includes other open statuses. The source calendar has an empty name in the observed snapshot. Deadline-only tasks with no Start Date are absent from that calendar. Preserve the precise source/dashboard view IDs and configurations from the snapshot, and re-fetch before reporting these as still current.

Current Next Actions uses an empty Blocked by relation rather than unresolved dependency status; retained resolved-history links keep tasks hidden. The user chose to retain history and propose release. This is a known unresolved implementation tradeoff, not permission to delete history or edit filters. Parent Stage/Project holds permit independent explicit actions. No automatic inherited-state restriction applies.

## Scenario expectations

| Input                                            | Expected handling                                                                               |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| User renames a property in Notion                | Fetch live schema, assess identity/meaning; map remains unchanged until synchronization request |
| User asks to add a task to a known project       | Read live schema/record, use accepted semantics, create within scope and verify                 |
| Unknown task tag appears                         | Ask for approval through vocabulary owner before registry extension/use                         |
| Task closes with two dependents                  | Inspect both, propose eligible releases, preserve history; explain current filter conflict      |
| Independent action in paused stage               | Permit explicitly accepted action after checking its own blockers                               |
| Inbox note creation succeeds but task link fails | Report partial state; reuse successful note on retry; keep Processed pending                    |
| Two Scheduled & Tickler labels                   | Identify view ID, source and predicate; do not silently unify them                              |
| User asks only to organize records               | Do not change schema/filter/layout implicitly                                                   |
| Method returns unsupported state                 | Ask equivalence; do not create option or repurpose generic Date                                 |
| No access to current Notion                      | Explain map is a snapshot, offer conditional reasoning and leave live-dependent writes pending  |
| User asks to sync map                            | Capture structural-only facts, validate and update this package/catalog, preserve peer skills   |

A schema check cannot simulate model behavior. Report actual executed checks and distinguish package validity, resolution, provider compatibility, installed state, activation and live outcomes. Do not certify all workspace records from a bounded sample.

## Goals checks

Check direct tasks and project contributions separately. Deduplicate task IDs when tracing both routes. Flag a target before its start, a declared Achieved goal without confirmed success, unsupported or unexplained progress, and incompatible links. A Review Date due or missing is a review prompt rather than evidence of failure. Completing all contributing work does not automatically achieve a goal. Pausing or dropping a goal never silently changes its tasks/projects. Check the exact status groups and view IDs from the snapshot because Goals uses a native Status property while several older bases use Select.
