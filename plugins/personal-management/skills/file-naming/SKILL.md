---

name: "file-naming"
description: "Use when creating, updating, ingesting, re-ingesting, renaming, managing or auditing filenames for documents, media, data, scripts or source files from any origin."
---

# File naming

Use when creating, updating, importing, re-ingesting, renaming, managing or auditing filenames, regardless of origin. Apply the same policy to authored files, exports, downloads and external material. This skill governs filenames, not directory names, task titles, content structure or entity creation.

Read [naming policy](references/naming-policy.md) and [operations and integration](references/operations.md) before acting. They are bundled and sufficient without companion skills or network access.

## Working recipe

1. Establish the authorized files and operation. Inspect existing names, file roles, technical contracts, destination and available conversation context. Updating content does not authorize an unrelated mass rename; audit is read-only unless correction is requested.
2. Classify each file by role: a technically constrained filename, freely named executable/source file, or ordinary support document/media/data file. Apply the corresponding policy, preserving extensions and file contents.
3. For ordinary files infer the owning entity from current work and explicit context, then verify its actual identity and existence in the relevant accessible workspace or authoritative system. If uncertain, ask which entity owns it and verify the answer. A name supplied by the user is intent, not proof of existence. Never create an entity merely to satisfy naming.
4. Build the ordinary final name as `[number-]<file-name>-<entity-name>.<extension>`. Executable/source filenames need no entity suffix; freely named ones use hyphens between words. Technical names follow their required contracts. Unknown-entity Inbox capture uses `[number-]<file-name>.<extension>` provisionally.
5. Use numbering only on request or when continuing a clearly established requested series. Start a new series at `00`, increase upward, pad to at least two digits and permit `100` onward. Keep existing numbers stable.
6. Before a rename check collisions, identity, links/imports and provenance; follow the operations reference. Execute only the authorized bounded changes, inspect results and report actual changes and remaining blockers. Re-ingestion must first find existing equivalents; it does not justify a second canonical copy.

## Response shape

For a simple creation, return the actual filename and any material unresolved association. For renaming or audit, give the relevant current → proposed/actual names, entity evidence, technical exceptions, collisions, pending questions and verification limits. Distinguish proposals from completed changes. Keep the response proportional.
