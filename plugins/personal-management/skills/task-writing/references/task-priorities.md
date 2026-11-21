# Registry-backed priority representation

## Allowed values come from JSON only

Read the current [priority registry](../assets/priorities.json) and [vocabulary policy](vocabulary.md) before handling this attribute. Accept only exact membership in its priorities array. Do not infer an alternative set from Markdown, memory, another method, legacy labels, numeric patterns, or the supplied task.

Preserve a supplied valid identifier and its actual rationale. There is no default priority, implicit ordering semantics, extra unlabelled value, alias, case conversion, score, or automatic mapping from a prioritization method. A missing priority is an unresolved fact outside the attribute, not a new allowed value. Null or an empty string is not a priority.

If a supplied identifier is not allowed, report that mismatch and ask which current permitted value the user intends if a value is required. Do not silently map it to a valid identifier, add a priority to the registry, or accept an old label as a fallback. Quote invalid source data only as evidence, not as an accepted output attribute. A missing/unreadable/invalid registry blocks priority handling while unrelated writing can proceed.

## Expression rather than assignment

Priority, readiness, actual date constraints, and completion remain separate. A supplied valid priority does not unblock work, satisfy an obligation, or prove the choice was correct. Registry membership is not a ranking decision.

The writing task can preserve or clarify the user's rationale; it does not assign a new priority, rank competing work, rebalance a week, run a review, or choose daily actions. A request to preserve an existing valid priority and polish a title needs no prioritization offer. A request to decide which priority fits or what comes first follows the optional-method handoff and waits for the user's choice before method work.

New levels, meanings, or mappings need a separate explicit configuration decision. The normal writing/tag-extension flow never introduces them.
