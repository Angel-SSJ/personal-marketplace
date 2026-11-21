# Optional prioritization-method handoff

This reference handles method selection only. MoSCoW rules, categories, calculations, and audits belong exclusively to the separate self-contained **moscow-prioritization** skill; this package does not load or reproduce them.

## When to offer

Offer when the user explicitly asks to prioritize, rank, compare importance, or choose which competing work to retain, or when their stated goal reasonably implies that decision. Examples include “What should I focus on this week?” or “Which tasks should stay when there is not enough time?” Do not infer a request to prioritize merely from a long list or from ordinary task wording, capture, filing, pausing, blocker tracking, or a check of existing labels.

When that prioritization intent is present and no method choice is already established for it, ask once in the conversation's language: **“Would you like to use MoSCoW for this prioritization?”** Wait for the answer before handing off or applying that method. Do not classify, map labels, perform its method-specific tests, or assume consent while the question is pending. Independent authorized wording edits can continue.

## Decision branches

| User decision                                                           | Task-writing action                                                                                                   |
| ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Yes, use MoSCoW                                                         | Hand off to moscow-prioritization for the agreed prioritization; read that skill before method work                   |
| Explicit request already says to use MoSCoW, or user invokes that skill | The method choice is already supplied for this scope; hand off without asking redundantly                             |
| No                                                                      | Do not invoke or simulate it; continue requested writing work, or hand off another method the user explicitly selects |
| No answer or ambiguous answer                                           | Keep the method choice pending; do not treat silence, urgency, or an unrelated reply as acceptance                    |
| Prior choice/preference already covers this same decision               | Respect it without repeated prompts; a new use outside its stated scope needs its own choice                          |
| Dedicated skill unavailable                                             | Explain the unavailable handoff; continue independent writing edits without reconstructing the method logic           |

Existing user-supplied prioritization results may be preserved as supplied data without interpreting or recomputing them. New classification or auditing under a named method needs the corresponding choice. Asking to detect an invalid date or missing waiting owner is task maintenance, not automatic permission to choose a prioritization method.

## Handoff and return

Pass the user's stated goal, actual competing work, real constraints, current commitments, known capacity, and uncertainties. Supply existing task context only when relevant; do not invent a result while delegating. Informational entity relations do not install, preload, or invoke the skill automatically.

On return, distinguish proposed versus accepted decisions and preserve the actual commitments and task readiness. Express the accepted result; do not select, automatically map, or overwrite priority identifiers from external method output. Any accepted priority/tag attribute must still belong to its current bundled JSON registry; method results do not extend those lists. A prioritization decision does not itself execute work, cancel a promise, authorize messages, or modify storage. Reflect accepted representation changes only within the user's authorization and verify actual writes.
