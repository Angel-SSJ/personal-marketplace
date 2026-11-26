---

name: file-naming
description: Use when files or folders need creation, naming, import, re-ingestion, renaming or naming audits across personal storage and connected platforms.
---

# File and folder naming

Names represent verified identity and purpose; they do not create an entity or authorize a migration. This global naming policy applies regardless of the workflow that initiated a file/folder operation.

Read the local [system contract](references/system-contract.md), [naming policy](references/naming-policy.md) and [operations](references/operations.md). Read [storage](references/storage-architecture.md) for placement and [integrity cases](references/integrity-matrix.md) for impacted relationships or conflicts. All required rules are local; another skill or source research document is unnecessary.

## Recipe

1. Bound the requested creation/rename/audit. Inspect role, original format, actual parent, owner identity, canonical slug, existing equivalents and technical/frozen exceptions. Existing conversation authorization remains valid. Audit alone does not authorize correction.
2. Verify the owner in the relevant accessible system; matching names and user-supplied intent are not existence evidence. Access denied means unverified. Hold final owner-qualified naming when identity is unresolved; permit provisional unclarified capture without inventing a suffix or entity.
3. Produce an idempotent name using the table. Preserve meaningful Unicode, true/compound extensions and technically constrained names. Native cloud documents use the compliant display stem, not a fabricated file extension.
4. Check exact, case-insensitive and Unicode-normalized collisions, affected links/imports, path restrictions, provenance and frozen records before mutation. Do not invent `-copy`, timestamps, versions or a new owner to escape a collision. Ask the decisive question and continue unrelated work.
5. Execute only the bounded authorized changes. Renaming an entity does not silently rename its files, folder, descendants or historical deliveries. Preserve bytes for a naming-only operation; distinguish native document identity from local pointer-file bytes.
6. Verify destination name/parent, content preservation and necessary reference repairs. After timeout inspect IDs and state before retrying. Report partial results rather than claiming cross-layer synchronization.

## Quick reference

| Role                                      | Naming contract                                                                         |
| ----------------------------------------- | --------------------------------------------------------------------------------------- |
| Ordinary final file                       | `[number-]<file-name>-<verified-entity-slug>.<extension>`                               |
| Unclarified capture                       | `[number-]<file-name>.<extension>` provisionally                                        |
| Freely named folder                       | Canonical lowercase kebab-case entity/role/topic, no repeated entity suffix             |
| Source/script                             | Free names use hyphens; no mandatory owner suffix; preserve import-required identifiers |
| Fixed roots/roles/technical/frozen record | Preserve concrete contract; no cosmetic normalization                                   |
| Optional selected numbering               | New series 00; next unused above maximum; 99 → 100, no gap filling                      |

## Example

Verified Product Launch owns `Market_Study.pdf` in its approved assets. A new supporting folder is `research-notes`; the file is `market-study-product-launch.pdf`. Keep `README.md` and a frozen `03_Final_Record.pdf` intact. If ownership access fails, `market-study.pdf` is provisional capture, not verified final naming.

## Common mistakes and red flags

Owner-first `product-launch-market-study.pdf` breaks the ordinary-file contract. Folders do not get ordinary-file suffixes. A technical exception needs a real contract, not merely legacy underscores. Neither numbering nor directory names choose priority, commitment, lifecycle or a Notion title. “The move succeeded” does not prove links were repaired. Apply the local pressure traps rather than bypass these checks under time pressure.
