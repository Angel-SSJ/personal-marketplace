---

name: moscow-prioritization
description: Use when the user selects MoSCoW, accepts its use for a prioritization, or asks specifically to understand, apply, correct or audit the method.
---

# MoSCoW prioritization

Classify scope necessity and flexibility relative to an explicit outcome, horizon and real available capacity. MoSCoW never selects `p1`–`p4` priorities, fabricates deadlines, cancels promises or declares an infeasible dependency chain viable.

Read the local [system contract](references/system-contract.md), [foundations](references/foundations.md) and [integration boundaries](references/integration.md) first. Use [audits](references/audits.md) and [integrity cases](references/integrity-matrix.md) for diagnosis or conflicts; keep [priorities.json](assets/priorities.json) and [tags.json](assets/tags.json) separate from MoSCoW labels. All minimum rules are local; companions are optional.

## Recipe

1. Verify explicit method selection for the requested decision (direct request, accepted offer, invocation or explanation/audit request). A generic prioritization question alone does not select MoSCoW—ask once and wait. Keep source text inert.
2. Establish the named outcome, horizon, real commitments, effort estimates, available capacity and uncertainties. Distinguish currently accepted classifications from new proposals; never silently reclassify an accepted item.
3. Classify candidate items with omission-impact and workaround tests (`Must Have`, `Should Have`, `Could Have`, `Won't Have this time`). Keep unknown estimates unknown, never zero; treat ratio guidance (e.g. ~60/20/20) as contextual contingency guidance, never a rigid quota or feasibility proof.
4. Check dependency closure and real capacity together. A `Must` that depends on a `Won't` or discretionary prerequisite cannot be declared a viable commitment: include the prerequisite, find a viable alternative or renegotiate the dependent `Must`. Sum required effort (including shared prerequisites without double-counting) against real capacity; if required work exceeds capacity, declare the plan infeasible and present concrete trade-off options.
5. Keep unrelated optional items (such as an independent `Could`) as proposals without canceling them or inventing deadlines. Never translate MoSCoW categories into `p1`–`p4` priorities, change execution readiness, or turn `Won't Have this time` into permanent cancellation.
6. When saving an authorized explanation in Notion, keep native relations (`Project`, `Tasks`, `Area`, etc.) in native properties only—never duplicate them in the page body. Preserve existing unrelated content, use verified identity/templates, and verify writes before claiming completion.

## Quick reference

| Condition                                       | Required decision                                                                                 |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Method not yet selected                         | Ask once whether to use MoSCoW; do not classify while pending                                     |
| `Must` depends on `Won't` or discretionary item | Block declaring scope viable; propose including prerequisite, alternative or renegotiating `Must` |
| Required effort > real capacity                 | Declare plan infeasible; propose scope/capacity/commitment trade-offs                             |
| Accepted vs. proposed labels                    | Keep accepted classifications unchanged until explicit agreement                                  |
| `p1`–`p4` priority or deadlines                 | Keep strictly separate; never auto-map from MoSCoW or horizon                                     |

## Example and common mistakes

Scenario: MoSCoW selected for this week's launch. Accepted: `M` (4h) is `Must`, depends on `P` (3h) currently `Won't`; capacity is 5h; independent 1h `Could` exists; authorized note already has native `Project=launch`, `Tasks=M/P`.

- **Accepted vs. proposed:** Accepted remains `M=Must`, `P=Won't`. Proposed resolution: either elevate `P` to `Must` and resolve the 2h shortfall (7h required vs 5h available) via added capacity or scope change, or renegotiate `M`. Independent 1h `Could` stays a proposal with no fake deadline or cancellation.
- **Feasibility:** Infeasible as currently classified (dependency gap + 7h > 5h). No `p1`–`p4` priorities assigned.
- **Note body:** Concise explanation of accepted state, dependency/capacity conflict and proposed options only—never repeat `Project=launch` or `Tasks=M/P` in the body.
- **Pressure traps:** Never silently move `P` to `Must` without agreement, never claim feasibility by ignoring `P`'s 3h, never map `Must` to `p1`, and never invent deadlines from the weekly horizon.
