# Provenance and Sources

This file records optional design provenance for the `personal-management` v0.2.0 package. **None of these external sources are required at runtime**; all operational rules, schemas, vocabularies, and contracts are bundled locally inside each autonomous skill directory. No copies of private documents, credentials, or user records are included in this package.

## Structural Observations (Read-Only, 2026-11-24)

- **Notion workspace structure:** Seven databases (`Goals`, `Areas`, `Projects`, `Stages`, `Tasks`, `Inbox`, `Notes & References`) observed read-only on `2026-11-24` to derive the portable symbolic contract (`assets/notion-blueprint.json`) and observed locator snapshot (`assets/workspace-map.json`).
  - All 11 required Notion formula expressions were supplied and verified by the user on `2026-11-25` and recorded in `assets/notion-blueprint.json` as `definition_status: "known"` (`provenance: "user_verified_2026-11-25"`). Any future unexposed formula must still remain `unknown` rather than fabricated.
  - External `Tasks.Google Drive File` relation was recorded as `requirement: "optional"` (`definition_status: "external_dependency"`).
- **Google Drive layout:** Observed read-only on `2026-11-24` confirming five kebab-case roots (`01-projects`, `02-areas`, `03-resources`, `04-archives`, `05-intake`), project role subfolders (`docs`, `drafts`, `submissions`, `assets`), archived project layout (`04-archives/01-projects/`), and legitimate Area subdivisions (`personal/private`, `software-development/certifications`).

## Methodological & Policy Baselines

- Original `plugins/personal-management` v0.1.0 skill suite in the source repository (preserved unchanged).
- Confirmed user design decisions documented in the approved integrity specification (2026-11-24): autonomous ten-skill architecture, native-property relations, explicit date/timeline semantics (hard deadlines vs. planning targets vs. retrospective follow-ups), JSON-backed task vocabulary (`p1`–`p4`, empty initial `tags`), two-phase Notion initialization gate, and read-only integrity auditing.
