# Read-only system integrity audit protocol

## Scope, evidence and coverage discipline

- Every audit is **read-only** by default. Never execute repairs, delete records, erase dependency history, cascade statuses, rename files, alter views/schema or set up background monitoring during an audit. Repairs require a separate, explicitly authorized bounded scope.
- Begin every report with an explicit **Coverage & Limits** block:
  - Requested scope and observation date.
  - Available capabilities and inspected sources/denominator.
  - Uninspected gaps: inaccessible collections/folders, truncated queries (`has_more=true`) and unexposed formula bodies (`I02`, `I45`).
- **No health percentages or completeness claims without full denominators:** Never compute a health score (e.g. "85% healthy") or certify system-wide integrity when any collection is inaccessible or any query returned `has_more=true`.

## Finding classification

Separate findings into four explicit buckets so real defects are never conflated with valid local practices:

1. **Confirmed defects (High / Medium / Low):**
   - **High:** Operational or structural contradictions that break execution or truthfulness—for example:
     - `I05`: Dependency cycle (`A -> B -> A`) or self-dependency (remember: normal bidirectional reciprocal properties such as `Blocked by` <-> `Blocking` are NOT dependency cycles).
     - `I39`: Inbox item marked `Processed` while a required Notion link or Drive output is still failed/unverified.
   - **Medium:** Relational or lifecycle inconsistencies—for example:
     - `I06`: Task (`Q`) and its linked `Stage` belong to incompatible `Projects`.
     - `I23`: `Next Action` with an active unresolved blocker or `Waiting For` missing expected result/owner.
     - `I32`/`I33`/`I36`: Wrong-owner Drive path, name collision, or unauthorized edit inside frozen `04-archives`/submissions.
   - **Low:** Representation drift or cleanup opportunities—for example:
     - `I40`: Native relation (`Project`, `Area`, etc.) duplicated as a metadata inventory inside a page body.
2. **Conditional / unresolved semantic risk:**
   - Conditions whose severity depends on a missing user fact—for example:
     - `I10`/`I11`: Necessary Task `T` due Dec 12 after Goal `G` target Dec 10 when target hardness is unknown. Keep both factual dates untouched; clarify whether Dec 10 is a hard deadline (`I10` blocking incoherence) or a soft planning target (`I11` viability warning) before proposing date/scope changes.
3. **Not defects (explicitly preserved valid patterns):**
   - `I12`/`I16`: Explicit retrospective follow-up (`R` on Dec 15 after Dec 10 goal).
   - Confirmed Drive structure `04-archives/01-projects/` (preserve exact root name and hierarchy).
   - Meaningful Area subdivisions such as `personal/private` or `software-development/certifications` (do NOT flatten).
   - Multiple compatible relations (`I08`) and independent compliant records (leave completely unchanged).
4. **Optional improvements:** Low-risk suggestions clearly separated from defects, never presented as mandatory compliance.

## Finding format

For each finding, state: **Severity & Category**, **Rule ID (`I01`–`I46`)**, **Observed Evidence**, **Affected Entities/Layers**, **Operational Effect**, and **Smallest Safe Repair Options** (requiring user authorization). Never auto-cascade parent holds/closures to children or erase factual history to make a report look clean.
