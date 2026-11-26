# Personal Management v0.2.0 — Test & Validation Report

Date: 2026-11-24

## Scope and Honest Evidence Boundaries

This report separates three distinct kinds of verification:

1. **Static package validation:** Executed locally with `python scripts/validate-package.py`, `python scripts/validate-package.py --self-test`, and `node skills/task-writing/scripts/vocabulary.mjs`. Verifies manifests, YAML frontmatter, JSON schemas, local link autonomy, synchronized contract equality across all 10 skills, symbolic Notion blueprint integrity, and vocabulary validity.
2. **Simulated behavioral testing (fresh isolated contexts):** Executed against `tests/behavior/scenarios.json` using isolated single-skill folders (no companion skills, no live Notion/Drive/network access). Each of the 10 skills has 5 fresh guided samples (50 guided samples total) compared against 5 legacy unguided controls (`control-1.json`..`control-5.json`) plus 1 supplementary unguided control (`terra-control-1.json`).
3. **Not verified here (known limits):**
   - No live Notion or Google Drive writes were performed.
   - Passing static validation and simulated behavioral scenarios does **not** prove live connector/API runtime execution, plugin installation, or every possible combination of the 46 integrity rules (`I01`–`I46`).
   - All 11 required Notion formula expressions were subsequently supplied and verified by the user (`2026-11-25`) and added to `assets/notion-blueprint.json` as `definition_status: "known"`. The `notion-initialization` skill continues to enforce that any _unknown_ required formula blocks Phase A completion rather than fabricating an expression.

## Exact Model Attribution for Behavioral Evidence

| Skill                     | Unguided Baselines        | Guided Samples (5 per skill)      | Manual Review Result                                                                              |
| :------------------------ | :------------------------ | :-------------------------------- | :------------------------------------------------------------------------------------------------ |
| `file-naming`             | 5 legacy + 1 Terra Medium | 5 legacy model                    | 5/5 pass (note: one prompt phrasing left artifact cardinality slightly ambiguous; no live writes) |
| `para-workflow`           | 5 legacy + 1 Terra Medium | 5 legacy model                    | 5/5 pass                                                                                          |
| `code-knowledge-workflow` | 5 legacy + 1 Terra Medium | 3 legacy + 2 GPT-6.1 Terra Medium | 5/5 pass                                                                                          |
| `gtd-workflow`            | 5 legacy + 1 Terra Medium | 5 GPT-6.1 Terra Medium            | 5/5 pass                                                                                          |
| `inbox-workflow`          | 5 legacy + 1 Terra Medium | 5 GPT-6.1 Terra Medium            | 5/5 pass                                                                                          |
| `task-writing`            | 5 legacy + 1 Terra Medium | 5 Gemini 4 Neon Medium            | 5/5 pass                                                                                          |
| `moscow-prioritization`   | 5 legacy + 1 Terra Medium | 5 Gemini 4 Neon Medium            | 5/5 pass                                                                                          |
| `notion-workflow`         | 5 legacy + 1 Terra Medium | 5 Gemini 4 Neon Medium            | 5/5 pass                                                                                          |
| `notion-initialization`   | 5 legacy + 1 Terra Medium | 5 Gemini 4 Neon Medium            | 5/5 pass                                                                                          |
| `system-integrity-audit`  | 5 legacy + 1 Terra Medium | 5 Gemini 4 Neon Medium            | 5/5 pass                                                                                          |

## Key Baseline Failures Addressed

- **Naming & PARA:** Unguided baselines omitted owner suffixes or inverted owner-first names and placed current editable work in `drafts`; guided samples enforced `[number-]<file-name>-<entity-name>.<ext>`, preserved `04-archives/01-projects/` and `personal/private`, and separated `docs` vs. `assets`.
- **Notion dependency history & visibility:** Unguided baselines sometimes proposed clearing historical `Blocked by` links to restore `Next Actions` visibility; guided `notion-workflow` samples preserved dependency history, avoided implicit view edits, and warned about the empty-`Blocked by` filter conflict.
- **Two-phase Notion initialization gate:** Several unguided baselines allowed inserting `launch` and its task once _their_ two databases verified; all 5 guided `notion-initialization` samples enforced the full seven-database Phase A verification gate, held new database creation while `has_more=true`, treated unreadable `Tasks` as `U`, refused to fabricate `Days Remaining` formula code, and confirmed unavailable optional `Google Drive File` does not block setup.
- **Task vocabulary & MoSCoW boundaries:** Guided `task-writing` and `moscow-prioritization` samples consistently blocked unlisted tag `urgent` against empty `tags.json`, left `Priority` unset without mapping MoSCoW categories to `p1`–`p4`, enforced dependency closure and real capacity (7h > 5h), and kept native relations out of page bodies.
- **Read-only system integrity audit:** All 5 guided `system-integrity-audit` samples reported incomplete coverage (`U` / `I02`) with no health percentage, classified `A->B->A` (`I05`), false `Processed` (`I39`), cross-project `Q`/Stage (`I06`), and body duplication (`I40`), kept `G` Dec 10 vs. `T` Dec 12 as conditional pending hardness, and preserved retrospective `R` Dec 15, `04-archives/01-projects/`, `area/private`, and compliant records untouched.

## Supplemental Integrity Matrix Behavioral Suite (`M1`–`M8`, 100% `I01`–`I46` Rule Coverage)

To ensure every single rule in `references/integrity-matrix.md` (`I01`–`I46`) has direct behavioral test evidence (in addition to the 50 per-skill samples from `scenarios.json`), eight cross-rule isolated scenarios (`tests/behavior/matrix-scenarios.json`) were executed using **Gemini 4 Neon Medium** against isolated single-skill folders (`tests/behavior/matrix-M1.json`..`matrix-M8.json`):

| Matrix Scenario                    | Isolated Skill           | Rules Exercised                                                             | Result                           |
| :--------------------------------- | :----------------------- | :-------------------------------------------------------------------------- | :------------------------------- |
| `M1_identity_schema_relations`     | `notion-workflow`        | `I01`, `I03`, `I04`, `I07`, `I08`                                           | PASS (5/5 items)                 |
| `M2_dates_and_sequencing`          | `gtd-workflow`           | `I09`, `I13`, `I14`, `I15`, `I17`, `I18`, `I19`                             | PASS (7/7 items)                 |
| `M3_lifecycle_and_cascades`        | `gtd-workflow`           | `I20`, `I21`, `I22`, `I23`, `I25`                                           | PASS (5/5 items)                 |
| `M4_numeric_managed_concurrency`   | `notion-workflow`        | `I26`, `I27`, `I43`, `I46`                                                  | PASS (4/4 items)                 |
| `M5_files_collisions_formats`      | `file-naming`            | `I32`, `I33`, `I34`, `I35`, `I37`                                           | PASS (5/5 items)                 |
| `M6_para_archive_and_intake_edges` | `para-workflow`          | `I25`, `I32`, `I35`, `I36`                                                  | PASS (4/4 items)                 |
| `M7_inbox_retry_and_injection`     | `inbox-workflow`         | `I38`, `I39`, `I42`, `I43`, `I46`                                           | PASS (4/4 items)                 |
| `M8_audit_full_matrix_triage`      | `system-integrity-audit` | `I01`, `I08`, `I09`, `I14`, `I17`, `I20`, `I22`, `I26`, `I33`, `I35`, `I42` | PASS (all defects & non-defects) |

Combined with `scenarios.json` (`I02`, `I05`, `I06`, `I10`–`I12`, `I16`, `I24`, `I28`–`I31`, `I36`, `I38`–`I42`, `I44`, `I45`), all **46 of 46 rules (`I01`–`I46`)** have recorded isolated behavioral test evidence. Note: these remain simulated fixture tests (not live Notion/Drive API runtime execution and not the exhaustive Cartesian product of every arbitrary rule subset).

## Negative Static Validator Tests (`--self-test`)

Six synthetic defect tests are built into `scripts/validate-package.py --self-test` and verified on temporary isolated copies:

1. `corrupted_frontmatter`
2. `nonlocal_cross_skill_link`
3. `contract_drift`
4. `leaked_source_id_in_blueprint`
5. `manifest_version_mismatch`
6. `obsolete_storage_token`

## Independent Review (2026-11-24)

Conducted in a fresh read-only context using **Gemini 4 Neon Medium** against the approved integrity design spec and implementation plan:

- **Material finding caught & fixed:** `.antigravity-plugin/README.md` still reflected v0.1.0 (listed 8 skills and contained obsolete `05_intake`). Updated to all 10 skills with `05-intake`, and extended `scripts/validate-package.py` to scan `GUIDE.md`, `SOURCES.md`, and `.antigravity-plugin/README.md` for obsolete tokens and machine paths.
- **Minor observation fixed:** Clarified the skill-root vs. plugin-root `vocabulary.mjs` command path in `skills/task-writing/references/vocabulary.md`.
- **Re-verification:** Re-ran `validate-package.py --self-test` and `vocabulary.mjs` after fixes with zero errors.
