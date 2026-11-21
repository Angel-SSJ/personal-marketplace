# Safe operation and explicit map synchronization

## Read and operate

Discover actual connected Notion capabilities. Fetch the root/source/view needed, compare IDs, types, options, relation targets and filters. Read only records needed for the bounded task. Query source schema-backed names; SQL loses some rich text so use rows/fetch before rich-text edits. Follow cursors until scope is complete. Do not copy record content into this skill.

Before creating a record, search the relevant collection for the intended entity and inspect plausible matches. Reuse an actual matching entity, not a merely similar title. Before mutation, inspect current values and preserve unrelated edits. Check links, source status and authority. Retry by inspecting partial results; avoid duplicate tasks/notes on a resumed Inbox operation. Cross-record changes are not assumed transactional. If linking or verification fails, report exactly what persisted and what remains pending. Do not erase successful records as automatic rollback.

Write exact observed option values and relation page IDs/URLs supported by the connector. Separate page body from properties, read provider markdown instructions before content edits, preserve child database blocks, and prefer targeted edits. For unavailable UI-only formatting use a supported UI pathway if authorized and available, otherwise report that limitation. Never send unsupported display options and claim success.

## Structural request

When explicitly asked to edit schema, filters, views or layout, inspect both source and affected linked surfaces first. Preserve existing views by ID when equivalent. Propose semantic decisions when a requested change has ambiguous scope. Verify actual returned filter operators and values; some unsupported filters can be silently omitted. A successful API status alone does not prove the requested filter was saved. Preserve dates, Number percentages, reciprocal links, data and unrelated presentation.

## Synchronize the bundled map only on request

Fetch the root, canonical databases, each exposed data source and all linked surfaces in scope. Capture structural metadata only: IDs, property definitions, allowed options, relation targets, view filters/sorts/grouping/display, layout when exposed, root sections and observation timestamp. Exclude row/page content, person records, signed download URLs and secrets. Formula code locators may be retained as structural metadata; mark any unexposed body unknown. Record source/linked differences without repairing them unless separately requested.

Validate JSON and internal references, preserve explicit policy versus observation, then write assets/workspace-map.json. Preserve the prior package until the new snapshot is validated. Update package version/updated and catalog using manager-repository without editing other skill packages. Read-only catalog check must pass before reporting a synchronized package. If filesystem/catalog access fails after a map save, disclose partial state. Synchronization is not installation, activation, permissions or a recurring background job.
