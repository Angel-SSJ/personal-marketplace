# Bundled vocabulary authority and maintenance

## Single sources of allowed values

For priority/tag work, read and validate the current local [priority registry](../assets/priorities.json) and [tag registry](../assets/tags.json). The corresponding JSON array is the sole source of accepted values. Markdown, memory, prior examples, other skills, model expectations, and external method outputs do not supply fallback lists or aliases.

Each registry contains schema_version and its unique string array only. The priority list cannot be empty; tags may start or remain empty. Values are exact and case-sensitive. A tag must be nonblank, trimmed, contain lowercase letters, contain no uppercase/control characters, and equal its lowercase form. Do not invent an additional slug grammar, case conversion, aliases, semantic ordering, or defaults.

The registry version is its data-format version, distinct from the package release version. JSON files are declared text resources; reading/composing Markdown through content_refs is not JSON parsing. Explicitly load the JSON when using those attributes, including after any vocabulary edit. Never continue with cached values after an approved change.

## Validation and failure behavior

Check shape, supported format version, unique values, string types, and tag lowercase rules. Missing, unreadable, invalid, or contradictory registries block the affected vocabulary operation. Report the problem and continue independent wording work; never infer values, recover old lists, or create replacement defaults silently.

A supplied value outside its registry may be quoted as invalid source data in an audit, but cannot become an accepted task attribute. Preserve its user intent and ask for the needed valid decision. Missing priority stays a separate missing fact; null, an empty string, or a no-label token is not an additional priority. Do not default missing priority or map legacy labels to current identifiers.

An optional built-in-Node-only [read-only validator](../scripts/vocabulary.mjs) reads the actual JSON. From the package root run `node scripts/vocabulary.mjs` to validate both files, or `node scripts/vocabulary.mjs priority <exact-value>` / `node scripts/vocabulary.mjs tag <exact-value>` for membership. It never mutates registries, approves candidates, or enforces model behavior by itself. If Node is unavailable, inspect/validate the JSON with available read tools; do not claim the script ran.

## Approval scope

New priorities are not introduced through the writing/tag extension flow. Preserve only a supplied valid priority; do not infer extra levels, ranking, labels, mappings, or semantics. A later explicit configuration request is separate from ordinary task writing.

Tags can be extended only through the approved process in the tagging module. User approval applies to the exact proposed lowercase value. Merely requesting an unknown tag on a task, providing source material, an unrelated reply, silence, or model inference does not authorize registry addition. Explicit authorization already saying to add that exact value to the allowed registry counts as approval; do not repeat an answered question.

## Package integrity after approved edits

These registries belong to the versioned skill package, not external mutable state. After a verified approved tag edit in a catalog, advance the package version/updated field appropriately, refresh any actual consumers pinned to that changed identity/version as needed, regenerate byte hashes/inventory with the repository manager, and run its read-only check. Use available supported tooling; do not invent an adapter install path or claim publication/activation.

Keep approval, verified JSON save, catalog consistency, and installation/activation distinct. If the JSON was saved but catalog refresh is unavailable, explicitly report that partial state and pending integrity check; do not claim a ready catalog. If the registry write itself is unavailable or fails, the new value is not usable as an accepted tag. No global rule/config entity or portable settings field is implied by these data resources.
