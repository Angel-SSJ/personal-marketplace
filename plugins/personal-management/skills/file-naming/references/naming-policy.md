# Naming policy

## Ordinary files

The final pattern is `[number-]<file-name>-<entity-name>.<extension>`; brackets mean optional text, not literal characters. Examples: `kpis-q4-terrivo.pdf`, `05-kpis-q4-terrivo.pdf`, `maintenance-log-home.xlsx`, `reading-notes-machine-learning.md`. This applies to ordinary notes, documents, images, archives, datasets and deliverables, independent of origin or file format.

Use a concise descriptive stem and one verified owning entity. Match against the known entity slug rather than splitting hyphenated names by guesswork. Do not append the same entity suffix twice. Several associations call for one confirmed canonical owner and links, not multiple suffixes or uncontrolled copies. A naming suffix expresses ownership/context, not independent evidence of the original author or publisher.

For freely chosen words use lowercase kebab-case: replace spaces and underscores between words with a single hyphen, collapse repeated separators, and remove leading/trailing separators. Preserve meaningful numbers. Prefer existing canonical entity slugs; otherwise derive a readable lowercase hyphenated form from the verified display name without renaming the entity. Preserve Unicode letters/accents unless the actual destination requires another encoding or an agreed slug exists. If normalization makes distinct entities or filenames indistinguishable, ask rather than merge. Entity display names and file slugs can differ; retain their identity association in existing context without requiring a new metadata file.

Preserve the real extension, including compound extensions such as `.tar.gz`; never change it to claim format conversion. Apply word normalization to the stem, not mandatory extension syntax. Files intentionally lacking extensions may remain extensionless with the same stem policy. Respect destination restrictions, reserved names and path limits; propose a shorter meaningful stem when necessary rather than inventing a different owner.

## Source, executable and technical names

Role matters more than extension alone. Freely named source files and scripts, such as `generate-report.py` or `sync-catalog.ts`, use hyphens between words and have no mandatory entity suffix or sequence number. A Python module that must be imported as an identifier is technically constrained; preserve its valid module name, including necessary underscores. Shell entrypoints, tools and build conventions may impose other names.

Preserve filenames required by tools, languages, frameworks, protocols or published interfaces: examples include `__init__.py`, `package.json`, `tsconfig.json`, `SKILL.md`, `README.md`, `.gitignore` and files referenced by an immutable external contract. Such files do not gain an entity suffix or sequence prefix. Preserve conventional extension/dot syntax. Explain the concrete contract for an exception; arbitrary legacy underscores alone are not proof of a technical requirement. Do not rename symbols, JSON keys, environment variables or directories as a side effect of this filename policy.

For an imported filename required for source integrity, signature verification, reproducibility or a frozen delivery record, preserve the original name as an explicit technical/record exception and retain the association through existing provenance or links. Ordinary external origin alone does not exempt a file from naming.

## Optional numeric prefix

Numbering expresses requested order, not priority, date, version or entity identity. It is ascending: `00`, `01`, … `09`, `10`, … `99`, `100`. Two digits are a minimum; never emit `1-` or `6-`. Do not introduce numbering by default.

Scope the series to the explicitly selected folder or collection; clarify if multiple plausible series affect the next number. Continue an existing selected series using the next unused value above its maximum. A new series starts at `00`. Do not automatically fill gaps, reset counters on re-ingestion or renumber other files. If the user requests insertion/reordering, show affected names and references before a bounded correction. Lexicographic order across `99`/`100` is not guaranteed with minimum two-digit padding; flag that limitation when relevant and ask before widening an entire series.

## Entity resolution and provisional capture

Use explicit current-work ownership, verified destination records/folders or an authoritative entity registry. Search relevant existing Projects, Areas, Resources and any other entity type actually supported by the user's workspace. Do not assume this catalog repository is their personal storage root, require a new registry or infer existence from a matching document filename. Prefer the current canonical owner over a generic topic match; if several owners remain plausible ask directly.

Verify inferred entities as well as user-supplied ones. If no matching entity exists, alert the user: the name may be wrong or the entity must be created first through its owning workflow. Block the final entity-qualified filename; do not create a folder/entity automatically or substitute a nearby match. If access is unavailable, say existence is unverified, not that the entity is absent. Naming never grants connector access.

An unclarified Inbox capture may proceed as `[number-]<file-name>.<extension>` using the same word separators and optional numbering, without an invented `inbox`, `unknown` or guessed entity suffix. Example: `Q4_KPIs.pdf` → provisional `q4-kpis.pdf` → final `q4-kpis-terrivo.pdf` after Terrivo is verified. Retain original provenance when renaming a source. Ask for the association during clarification; provisional capture is not final compliance. A technically constrained filename keeps its exception even in Inbox.

Archives are locations/lifecycle states, not replacement owners. Preserve the original entity association and frozen record names; naming alone never authorizes archive edits or reactivation.
