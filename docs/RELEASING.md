# Releasing & Branch Protection Guide

This repository uses a Superpowers-style lockstep release workflow (`vX.Y.Z`) driven by `.version-bump.json`, `scripts/bump-version.ts`, `RELEASE-NOTES.md`, and `.github/workflows/release.yml`.

## 1. Cut a New Release

1. Ensure `main` is clean and all checks pass:

   ```powershell
   pnpm run check
   ```

2. Bump all tracked manifests in lockstep (`patch`, `minor`, `major`, or explicit `X.Y.Z`):

   ```powershell
   pnpm run version:bump -- minor
   ```

3. Audit for drift or stale references to the previous version:

   ```powershell
   pnpm run version:audit -- 0.1.0
   ```

4. Add a matching `## vX.Y.Z (YYYY-MM-DD)` section to `RELEASE-NOTES.md`.
5. Commit, tag, and push:

   ```powershell
   git add -A
   git commit -m "chore(release): prepare v0.2.0"
   git tag v0.2.0
   git push origin main --follow-tags
   ```

Pushing a `v*.*.*` tag triggers `.github/workflows/release.yml`, which verifies manifest alignment, extracts the section from `RELEASE-NOTES.md`, and publishes the GitHub Release automatically.

## 2. Apply the Solo-Friendly `main` Branch Ruleset on GitHub

Branch rules live on GitHub, not in Git alone. A ready-to-import solo-maintainer ruleset is committed at `.github/rulesets/main-branch-ruleset.json` (blocks force-push and branch deletion, requires `Quality & Validation` and `Actionlint`, and grants Repository Admin bypass so solo work never deadlocks).

Apply it via GitHub CLI once your initial commit is pushed:

```powershell
gh api --method POST repos/Angel-SSJ/personal-marketplace/rulesets --input .github/rulesets/main-branch-ruleset.json
```

Or import `.github/rulesets/main-branch-ruleset.json` manually in **GitHub -> Settings -> Rules -> Rulesets -> New ruleset -> Import a ruleset**.
