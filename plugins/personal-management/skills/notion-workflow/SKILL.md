---

name: "notion-workflow"
description: "Use whenever the user explicitly requests or implicitly needs interaction with Notion, including reading, searching, creating, updating, mapping or reviewing pages, databases and views."
---

# Notion Workflow

Use whenever interaction with Notion is explicitly requested or reasonably inferred from the user's intent, including searching, reading, creating, updating, mapping and reviewing pages, databases, views, properties, records, relations or transitions. Invoke before the relevant Notion operation without requiring an explicit skill name. The bundled workspace map describes Personal Workflow. For other Notion pages or workspaces, discover and verify their actual structure and apply only policies relevant to the requested scope; do not assume they share Personal Workflow's IDs, schema or methodology. Translate accepted method outputs into the actual workspace. Read [authority](references/authority.md), [workspace navigation](references/workspace.md), and [transitions](references/transitions.md) first. Explicitly read the current [structural snapshot](assets/workspace-map.json) for IDs, exact property names, options, relation targets and views. For operations read [operations](references/operations.md); for method outputs read [method-mapping](references/method-mapping.md); for drift and review read [diagnostics](references/diagnostics.md).

1. Establish the user's requested scope and actual decisions. Use the snapshot as a locator, then fetch the relevant live page, data sources, view configuration and target records before operating.
2. Compare live structure with the snapshot. Distinguish observed configuration, agreed policy, accepted method outputs, inferred proposals and unavailable evidence. Continue independent operations when a difference does not affect them. Ask when a missing equivalence or changed meaning affects the requested write.
3. Read available method skills when their decision is needed. The user need not name each skill. Preserve their accepted output, including task vocabulary and real-date semantics.
4. Plan the smallest record changes using exact live properties and relation IDs. Create/edit records within requested scope. Ask for missing intent that changes a commitment; structure or filter modifications require explicit request.
5. Execute with actual connector access, inspect errors/warnings, verify material results and report partial state honestly. Creating a record or mapping a transition does not prove execution of the underlying work.
6. Update the bundled map only when the user explicitly asks to synchronize it. Perform structural-only capture, version/catalog maintenance and verification as described locally. Ordinary Notion writes do not silently update this package.

Keep explanations proportional. Return the resulting records/links, material changes, unresolved decisions and limits. A bounded maintenance request does not authorize a workspace redesign or a broad audit. Installation of this skill grants no connector access.

For goal creation, planning, review, evidence, progress, or relationships, read the [Goals contract](references/goals.md). Goals can use direct tasks without a Project and support horizons from two days to ten weeks or any user-chosen duration. Preserve the distinction between an accepted goal result and a project deliverable.
