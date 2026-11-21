# Approved lowercase tag representation

## Allowed values come from JSON only

Read the current [tag registry](../assets/tags.json) and [vocabulary policy](vocabulary.md). Only exact existing tags-array members may be used as accepted tags. The initial set is intentionally empty. There is no fallback vocabulary, inferred alias, automatic case normalization, or tag supplied by a Markdown example.

Every stored/used tag must meet the lowercase format rule. If uppercase or otherwise invalid input is supplied, explain the format issue and, where relevant, ask about the exact lowercase candidate rather than silently changing it. Format alone does not grant membership.

This registry policy replaces the former open context-example policy. Do not apply a second hidden category gate that rejects an explicitly approved lowercase registry member. Context, theme, state, and priority remain different meanings, but a tag's allowed status is determined by this JSON and the approved addition process. A tag does not change actual task state or priority.

## Requested or inferred new tag

1. Check current exact membership and format. If already present, no addition/approval question is needed; preserve the supplied valid value within the requested writing edit.
2. If a relevant requested or inferred candidate is absent, present the exact lowercase value and its intended meaning, then ask whether to add it to the allowed set. An inferred candidate is a proposal, not an accepted tag. Do not use it in an accepted task attribute while approval is pending.
3. A clear yes or explicit authorization to add that exact value to the registry supplies approval. Refusal, silence, an ambiguous answer, or a different request does not. If the user changes the candidate, resolve approval for the actual lowercase value to be stored. Approval for one value does not authorize related tags, aliases, or a taxonomy.
4. After approval, re-read both registries and validate them. Preserve unrelated concurrent edits; if the candidate already exists, do not duplicate it. If the registry changed incompatibly or is invalid, pause the update and report the conflict instead of overwriting it.
5. Append only the approved value, save valid JSON, and read back/validate the actual persisted file. Use available supported file tools. The bundled validator is read-only; it does not perform or authorize this write.
6. Only after verified persistence can the new value be used as a registry member. Apply it to a task only when that task edit is also authorized; adding vocabulary alone does not authorize bulk retagging. Refresh package/catalog integrity as described in vocabulary.md and distinguish pending catalog checks from the verified JSON update.

If the file is unavailable, read-only, or cannot be saved/verified, report an approved proposal still pending; do not claim addition, accept the tag, or continue from an in-memory substitute. A task wording edit can continue without assigning that candidate.

## Narrow maintenance permission

The user-authorized addition process is a specific vocabulary-maintenance exception to writing-only scope. It does not permit creating priorities, changing tag spellings/removing tags without a separate request, selecting a task's substantive context without facts, modifying other packages, or performing actual task/calendar/storage operations.
