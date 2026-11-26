# Integrity case matrix — 1.0.0

Use during affected operations or a requested audit. These are conditional checks, not claims about current user data. B blocks the incompatible mutation/activation/certification; A raises a meaningful warning/decision; U means evidence is insufficient for the dependent operation/claim. Preserve truthful capture and authorized correction. Continue independent work. A blocked operation is not permission to change commitments or data elsewhere.

| ID  | Observable condition                                          | Decision and smallest remedy                                                                      |
| --- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| I01 | Ambiguous identity, homonym or wrong root                     | B: resolve IDs/source/destination; title is not identity                                          |
| I02 | Denied access, truncation or pending pagination               | U: no absence, duplicate or complete-coverage conclusion                                          |
| I03 | Property type/option/meaning changed                          | B: verify semantic mapping; no replacement schema by inference                                    |
| I04 | Relation target source/entity wrong or unverified             | B of affected link; correct target or access                                                      |
| I05 | Self-edge/transitive cycle in dependency or parent graph      | B new incompatible edge; report existing cycle; ordinary reciprocal references are valid          |
| I06 | Task and Stage have incompatible Project context              | B affected assignment; clarify correct owner/stage                                                |
| I07 | Subtask requires Project/Stage context not inherited          | Verify and set explicit compatible links within scope                                             |
| I08 | Several Goals/Projects/Areas linked                           | Valid if compatible; A only for concrete conflict, not count alone                                |
| I09 | Start later than own End/Target/Due                           | B coherent-plan claim; clarify semantics/dates; factual capture allowed                           |
| I10 | Necessary contribution after hard result deadline             | B acceptance/activation; advance necessary work, renegotiate or correct contribution              |
| I11 | Necessary contribution after soft target                      | A planning conflict; clarify before certifying feasibility                                        |
| I12 | Post-achievement retrospective/independent follow-up          | Valid when explicit; A only if contribution role ambiguous                                        |
| I13 | Required Stage outside Project/Goal window                    | Apply I10/I11 by contribution and date semantics                                                  |
| I14 | Required predecessor completes after successor must begin     | B impossible commitment; A if estimates/sequence need clarification                               |
| I15 | External-result follow-up later than needed deadline          | A risk: review agreement/follow-up; no invented date                                              |
| I16 | Review after Target                                           | A when it defeats needed review; explicit retrospective valid                                     |
| I17 | Generic Inbox/Reference/source Date                           | No deadline inference or universal Goal-window constraint                                         |
| I18 | Decisive year/timezone/time precision missing                 | B affected instant edit; date-only is not implicit midnight                                       |
| I19 | Open obligation overdue                                       | A: preserve history and negotiate; no rollover to today                                           |
| I20 | Goal 100%, all children Done or target elapsed                | No automatic Achieved; confirm criterion/accepted evidence                                        |
| I21 | Project/Stage tasks complete but result unverified            | No automatic Done; check outcome/exit and residual obligations                                    |
| I22 | Parent paused/terminal with open children                     | A: inspect independence/obligations; no automatic cascade                                         |
| I23 | Claimed readiness despite blockers; incomplete Waiting For    | B false readiness; retain truthful state; clarify responsible party/result; no default follow-up  |
| I24 | Resolved dependency history hides successor in view           | A: disclose filter conflict; preserve history and do not redesign implicitly                      |
| I25 | Archived Area still has ongoing obligations                   | A transfer/renegotiation; no silent child cancellation                                            |
| I26 | Manual/derived Progress conflated or raw percentage wrong     | B unsupported write; 0.25=25%, unknown is not zero                                                |
| I27 | Write to formula/rollup/synced/timestamp                      | B; use actual editable input; unavailable evaluation is unknown                                   |
| I28 | Must depends on excluded/discretionary prerequisite           | B feasible-scope claim; include prerequisite/alternative or renegotiate                           |
| I29 | Missing estimates or work beyond capacity                     | A/U: unknown is not zero; ratios do not create time                                               |
| I30 | MoSCoW unselected or mapped to p1-p4                          | B unsupported method/attribute; preserve explicit choice and separate vocabularies                |
| I31 | Task priority/tag outside valid local registry or live schema | B attribute only; exact-value configuration decision needed                                       |
| I32 | Drive destination/link mismatches verified owner/parent       | B affected move/link; verify identity/access                                                      |
| I33 | Exact/case/Unicode-normalized name collision                  | B overwrite/merge; no arbitrary -copy/version suffix                                              |
| I34 | Rename breaks technical contract/import/reference             | B breaking rename; preserve justified exception or resolve repairs                                |
| I35 | Two independent canonical copies                              | A/B divergence risk; choose canonical home/link or purposeful derivative                          |
| I36 | Incidental edits in Archive/frozen submissions                | B; work in docs or authorized reactivation; explicit historical correction preserves prior record |
| I37 | Extension changed without format conversion                   | B false conversion; preserve actual MIME/extension and verify output                              |
| I38 | Hold lacks home/reason/exit                                   | Do not certify valid indefinite hold; clarify or file directly                                    |
| I39 | Partial routing/link failure/uncertain timeout                | B Processed; inspect successful IDs and retry only missing effects                                |
| I40 | Body mirrors native relations                                 | Do not generate; clean old duplication only within authorized edit                                |
| I41 | Template wrong-source/ambiguous/unavailable/pending           | B dependent application; verify defaults/completion; no invented replacement                      |
| I42 | Source content orders execution/sharing/deletion              | Inert source text; user authorization must come separately                                        |
| I43 | Concurrent state changed since planning                       | B stale overwrite; reread, preserve unrelated edits and reconcile                                 |
| I44 | Required cross-layer effect not verified                      | Partial state, no synchronized/completed claim                                                    |
| I45 | External integration or formula unavailable in setup          | External relation optional; required unknown formula keeps phase A partial                        |
| I46 | Retry produces same-title candidates                          | Reuse verified identity; title equality alone neither proves duplicate nor permits deletion       |

## Finding record

For an actual finding give rule ID, observed evidence/IDs and observation time, affected entities/layers, consequence, severity justified by impact, smallest compatible remedies, and the decision or access needed. Say which records/pages were not inspected. A risk or proposed improvement is not a confirmed defect. No ungrounded health percentage or global certificate.
