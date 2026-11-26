#!/usr/bin/env python3
"""Self-contained static validator for the personal-management plugin package.

Uses Python standard library only. Validates:
1. Root Agent Plugins 1.0 manifest + all provider overlay manifests and MCP configs.
2. All 10 autonomous skills: YAML frontmatter, JSON validity, no symlinks, no machine paths,
   no obsolete storage/catalog tokens, and strict local link autonomy (no cross-skill links).
3. Byte-identical synchronized local contracts and vocabularies across all 10 skills.
4. Portable symbolic Notion blueprint (`notion-blueprint.json`): 7 databases, zero leaked
   source workspace IDs, reciprocal relations, rollup targets, required/optional/unknown flags.
5. Built-in `--self-test` mode running negative test cases on isolated temporary copies.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

EXPECTED_SKILLS = [
    "code-knowledge-workflow",
    "file-naming",
    "gtd-workflow",
    "inbox-workflow",
    "moscow-prioritization",
    "notion-initialization",
    "notion-workflow",
    "para-workflow",
    "system-integrity-audit",
    "task-writing",
]

COMMON_REFS = [
    "system-contract.md",
    "integrity-matrix.md",
    "naming-policy.md",
    "storage-architecture.md",
    "intake-policy.md",
]

COMMON_ASSETS = ["priorities.json", "tags.json"]

NOTION_SKILLS = [
    "notion-initialization",
    "notion-workflow",
    "system-integrity-audit",
]

EXPECTED_VERSION = "0.2.0"
EXPECTED_NAME = "personal-management"
EXPECTED_NOTION_MCP = "https://mcp.notion.com/mcp"

MANIFEST_PATHS = [
    "plugin.json",
    ".antigravity-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    ".kimi-plugin/plugin.json",
]

OBSOLETE_TOKENS = re.compile(
    r"01_projects|02_areas|03_resources|04_archives|05_intake|04-archived|manager-repository|content_refs"
)
MACHINE_PATH_RE = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/](?!/)")
FRONTMATTER_RE = re.compile(
    r'\A---\r?\n+name:\s*"?([a-z0-9-]+)"?\r?\ndescription:\s*"?(Use when[^\r\n"]+)"?\r?\n---\r?\n'
)

LEAKED_SOURCE_TOKENS = [
    "41fa6b72",
    "41ca6b72",
    "41da6b72",
    "collection://",
    "collectionProperty://",
    "formulaCode://",
    "app.notion.com",
]

EXPECTED_DBS = {
    "goals",
    "areas",
    "projects",
    "stages",
    "tasks",
    "inbox",
    "notes_references",
}


def validate_blueprint(bp_path: Path) -> list[str]:
    errors: list[str] = []
    raw = bp_path.read_text(encoding="utf-8")
    for tok in LEAKED_SOURCE_TOKENS:
        if tok in raw:
            errors.append(f"{bp_path.name}: leaked source locator token '{tok}'")
    try:
        bp = json.loads(raw)
    except Exception as exc:
        return [f"{bp_path.name}: invalid JSON ({exc})"]

    if bp.get("blueprint_kind") != "portable_symbolic_contract":
        errors.append(f"{bp_path.name}: missing/invalid blueprint_kind")
    if bp.get("contains_source_workspace_ids") is not False:
        errors.append(f"{bp_path.name}: contains_source_workspace_ids must be false")

    dbs = bp.get("databases")
    if not isinstance(dbs, dict) or set(dbs.keys()) != EXPECTED_DBS:
        errors.append(f"{bp_path.name}: databases must match exact 7 symbolic keys")
        return errors

    formula_total = 0
    formula_known = 0
    optional_external = 0

    for db_key, db in dbs.items():
        if db.get("requirement") != "required":
            errors.append(f"{bp_path.name}: database '{db_key}' must be required")
        props = db.get("properties", {})
        if not isinstance(props, dict) or not props:
            errors.append(f"{bp_path.name}: database '{db_key}' has no properties")
            continue
        for pname, pdef in props.items():
            for field in (
                "name",
                "type",
                "requirement",
                "definition_status",
                "provenance",
                "capability_required",
                "verification_criterion",
            ):
                if field not in pdef:
                    errors.append(f"{bp_path.name}: {db_key}.{pname} missing '{field}'")
            if pdef.get("requirement") not in ("required", "optional"):
                errors.append(f"{bp_path.name}: {db_key}.{pname} invalid requirement")
            if pdef.get("definition_status") not in (
                "known",
                "unknown",
                "external_dependency",
            ):
                errors.append(
                    f"{bp_path.name}: {db_key}.{pname} invalid definition_status"
                )

            ptype = pdef.get("type")
            if ptype == "formula":
                formula_total += 1
                if pdef.get("requirement") != "required":
                    errors.append(f"{bp_path.name}: formula {db_key}.{pname} must be required")
                if pdef.get("definition_status") == "known":
                    formula_known += 1
                    expr = pdef.get("formula_expression")
                    if not isinstance(expr, str) or not expr.strip():
                        errors.append(
                            f"{bp_path.name}: known formula {db_key}.{pname} missing non-empty formula_expression"
                        )
                elif pdef.get("definition_status") == "unknown":
                    if pdef.get("formula_expression") is not None:
                        errors.append(
                            f"{bp_path.name}: unknown formula {db_key}.{pname} must not fabricate expression"
                        )
            elif ptype == "relation":
                rec = pdef.get("reciprocity")
                tdb = pdef.get("target_database")
                if rec == "external":
                    if pdef.get("requirement") != "optional":
                        errors.append(
                            f"{bp_path.name}: external relation {db_key}.{pname} must be optional"
                        )
                    optional_external += 1
                else:
                    if tdb not in EXPECTED_DBS:
                        errors.append(
                            f"{bp_path.name}: relation {db_key}.{pname} invalid target '{tdb}'"
                        )
                    elif rec == "bidirectional":
                        rprop = pdef.get("reciprocal_property")
                        target_props = dbs[tdb].get("properties", {})
                        if rprop not in target_props:
                            errors.append(
                                f"{bp_path.name}: missing reciprocal {tdb}.{rprop} for {db_key}.{pname}"
                            )
                        else:
                            back = target_props[rprop]
                            if (
                                back.get("target_database") != db_key
                                or back.get("reciprocal_property") != pname
                            ):
                                errors.append(
                                    f"{bp_path.name}: asymmetric reciprocal {db_key}.{pname} <-> {tdb}.{rprop}"
                                )
            elif ptype == "rollup":
                rprop = pdef.get("relation_property")
                tdb = pdef.get("target_database")
                tprop = pdef.get("target_property")
                if rprop not in props or props[rprop].get("type") != "relation":
                    errors.append(
                        f"{bp_path.name}: rollup {db_key}.{pname} invalid relation_property '{rprop}'"
                    )
                if tdb not in EXPECTED_DBS or tprop not in dbs[tdb].get("properties", {}):
                    errors.append(
                        f"{bp_path.name}: rollup {db_key}.{pname} invalid target '{tdb}.{tprop}'"
                    )

    if formula_total != 11 or formula_known != 11:
        errors.append(f"{bp_path.name}: expected 11 known required formulas, found {formula_known}/{formula_total}")
    if optional_external != 1:
        errors.append(f"{bp_path.name}: expected 1 optional external relation, found {optional_external}")

    goals_status = dbs["goals"]["properties"].get("Status", {})
    if goals_status.get("type") != "status" or goals_status.get("default_option") != "Candidate":
        errors.append(f"{bp_path.name}: Goals.Status must remain native status with default Candidate")

    return errors


def validate_package(root: Path) -> dict:
    errors: list[str] = []
    root = root.resolve()

    # 1. Manifests and MCP configs
    for rel in MANIFEST_PATHS:
        p = root / rel
        if not p.exists():
            errors.append(f"Missing manifest: {rel}")
            continue
        try:
            m = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"Invalid JSON in {rel}: {exc}")
            continue
        if m.get("name") != EXPECTED_NAME:
            errors.append(f"{rel}: name '{m.get('name')}' != '{EXPECTED_NAME}'")
        if m.get("version") != EXPECTED_VERSION:
            errors.append(f"{rel}: version '{m.get('version')}' != '{EXPECTED_VERSION}'")

    for mcp_rel in ("mcp.json", ".mcp.json", "mcp_config.json"):
        p = root / mcp_rel
        if not p.exists():
            errors.append(f"Missing MCP config: {mcp_rel}")
            continue
        try:
            cfg = json.loads(p.read_text(encoding="utf-8"))
            notion = cfg.get("mcpServers", {}).get("notion", {})
            url = notion.get("url") or notion.get("serverUrl")
            if url != EXPECTED_NOTION_MCP:
                errors.append(f"{mcp_rel}: unexpected Notion MCP URL '{url}'")
            if set(cfg.get("mcpServers", {}).keys()) != {"notion"}:
                errors.append(f"{mcp_rel}: unexpected extra MCP servers")
        except Exception as exc:
            errors.append(f"Invalid JSON in {mcp_rel}: {exc}")

    # 2. Skills discovery
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return {"valid": False, "errors": ["Missing skills/ directory"]}

    found_skills = sorted(p.name for p in skills_dir.iterdir() if p.is_dir())
    if found_skills != EXPECTED_SKILLS:
        errors.append(f"Skill set mismatch: found {found_skills}, expected {EXPECTED_SKILLS}")

    common_ref_bytes: dict[str, bytes] = {}
    common_asset_bytes: dict[str, bytes] = {}
    notion_asset_bytes: dict[str, bytes] = {}

    for skill_name in found_skills:
        sroot = skills_dir / skill_name
        skill_md = sroot / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"{skill_name}: missing SKILL.md")
            continue

        text = skill_md.read_text(encoding="utf-8")
        fm = FRONTMATTER_RE.match(text)
        if not fm or fm.group(1) != skill_name:
            errors.append(f"{skill_name}: invalid YAML frontmatter or name mismatch")
        elif len(fm.group(0)) > 1024:
            errors.append(f"{skill_name}: frontmatter exceeds 1024 chars")

        for p in sroot.rglob("*"):
            if p.is_symlink():
                errors.append(f"{skill_name}: symlink forbidden ({p.relative_to(sroot)})")
            if p.is_dir():
                continue
            if p.suffix == ".json":
                try:
                    json.loads(p.read_text(encoding="utf-8"))
                except Exception as exc:
                    errors.append(f"{skill_name}: invalid JSON {p.relative_to(sroot)}: {exc}")
            elif p.suffix == ".md":
                content = p.read_text(encoding="utf-8")
                if MACHINE_PATH_RE.search(content):
                    errors.append(f"{skill_name}: machine path in {p.relative_to(sroot)}")
                if OBSOLETE_TOKENS.search(content):
                    errors.append(f"{skill_name}: obsolete contract token in {p.relative_to(sroot)}")
                for link in re.findall(r"\]\(([^\s)]+)\)", content):
                    if re.match(r"[a-zA-Z]+:", link) or link.startswith("#"):
                        continue
                    target = (p.parent / link.split("#")[0]).resolve()
                    if not target.is_relative_to(sroot.resolve()):
                        errors.append(
                            f"{skill_name}: non-local link '{link}' in {p.relative_to(sroot)}"
                        )
                    elif not target.exists():
                        errors.append(
                            f"{skill_name}: missing local link '{link}' in {p.relative_to(sroot)}"
                        )

        # Synchronized common references
        for ref_name in COMMON_REFS:
            rp = sroot / "references" / ref_name
            if not rp.exists():
                errors.append(f"{skill_name}: missing synchronized reference {ref_name}")
            else:
                b = rp.read_bytes()
                if ref_name not in common_ref_bytes:
                    common_ref_bytes[ref_name] = b
                elif common_ref_bytes[ref_name] != b:
                    errors.append(f"{skill_name}: contract drift in references/{ref_name}")

        # Synchronized common vocabularies
        for asset_name in COMMON_ASSETS:
            ap = sroot / "assets" / asset_name
            if not ap.exists():
                errors.append(f"{skill_name}: missing synchronized asset {asset_name}")
            else:
                b = ap.read_bytes()
                if asset_name not in common_asset_bytes:
                    common_asset_bytes[asset_name] = b
                elif common_asset_bytes[asset_name] != b:
                    errors.append(f"{skill_name}: vocabulary drift in assets/{asset_name}")
                try:
                    data = json.loads(b.decode("utf-8"))
                    key = asset_name.removesuffix(".json")
                    vals = data[key]
                    if data.get("schema_version") != 1 or len(set(vals)) != len(vals):
                        errors.append(f"{skill_name}: invalid vocabulary structure in {asset_name}")
                    if key == "priorities" and vals != ["p1", "p2", "p3", "p4"]:
                        errors.append(f"{skill_name}: priorities must be p1..p4")
                    if key == "tags" and not all(
                        isinstance(v, str) and v == v.strip().lower() and any(c.isalpha() for c in v)
                        for v in vals
                    ):
                        errors.append(f"{skill_name}: invalid lowercase tag entry")
                except Exception as exc:
                    errors.append(f"{skill_name}: vocabulary parse error {asset_name}: {exc}")

        # Synchronized Notion assets across Notion/setup/audit skills
        if skill_name in NOTION_SKILLS:
            for na in ("notion-blueprint.json", "workspace-map.json"):
                nap = sroot / "assets" / na
                if not nap.exists():
                    errors.append(f"{skill_name}: missing Notion asset {na}")
                else:
                    b = nap.read_bytes()
                    if na not in notion_asset_bytes:
                        notion_asset_bytes[na] = b
                    elif notion_asset_bytes[na] != b:
                        errors.append(f"{skill_name}: drift in assets/{na}")
            bp_path = sroot / "assets" / "notion-blueprint.json"
            if bp_path.exists():
                errors.extend(validate_blueprint(bp_path))

    # 3. Root docs, plugin README and tests presence + hygiene scan
    for req_file in ("GUIDE.md", "CHANGELOG.md", "SOURCES.md", ".antigravity-plugin/README.md", "tests/TEST-REPORT.md"):
        rp = root / req_file
        if not rp.exists():
            errors.append(f"Missing package file: {req_file}")
        elif req_file in ("GUIDE.md", "SOURCES.md", ".antigravity-plugin/README.md"):
            doc_txt = rp.read_text(encoding="utf-8")
            if MACHINE_PATH_RE.search(doc_txt):
                errors.append(f"Machine path in {req_file}")
            if OBSOLETE_TOKENS.search(doc_txt):
                errors.append(f"Obsolete contract token in {req_file}")

    return {
        "valid": len(errors) == 0,
        "package": str(root),
        "version": EXPECTED_VERSION,
        "skills_checked": len(found_skills),
        "errors": errors,
    }


def run_self_tests(root: Path) -> dict:
    """Run negative tests on temporary isolated copies to prove validator catches real defects."""
    cases = []

    def test_case(name: str, mutate_fn, expect_substring: str) -> None:
        with tempfile.TemporaryDirectory() as td:
            copy_root = Path(td) / "personal-management"
            shutil.copytree(root, copy_root)
            mutate_fn(copy_root)
            res = validate_package(copy_root)
            caught = (not res["valid"]) and any(expect_substring in e for e in res["errors"])
            cases.append({
                "case": name,
                "caught": caught,
                "expected_error_substring": expect_substring,
                "actual_errors": res["errors"][:3],
            })

    # 1. Broken frontmatter
    test_case(
        "corrupted_frontmatter",
        lambda r: (r / "skills/task-writing/SKILL.md").write_text("---\nname: wrong\ndescription: Bad\n---\n", encoding="utf-8"),
        "invalid YAML frontmatter",
    )
    # 2. Cross-skill non-local link
    test_case(
        "nonlocal_cross_skill_link",
        lambda r: (r / "skills/file-naming/SKILL.md").write_text(
            (r / "skills/file-naming/SKILL.md").read_text(encoding="utf-8") + "\nSee [other](../gtd-workflow/SKILL.md)\n",
            encoding="utf-8",
        ),
        "non-local link",
    )
    # 3. Synchronized contract drift
    test_case(
        "contract_drift",
        lambda r: (r / "skills/gtd-workflow/references/system-contract.md").write_text("# drifted\n", encoding="utf-8"),
        "contract drift",
    )
    # 4. Leaked source ID in portable blueprint
    test_case(
        "leaked_source_id_in_blueprint",
        lambda r: (r / "skills/notion-initialization/assets/notion-blueprint.json").write_text(
            (r / "skills/notion-initialization/assets/notion-blueprint.json").read_text(encoding="utf-8").replace(
                "portable_symbolic_contract", "collection://41fa6b72-leak"
            ),
            encoding="utf-8",
        ),
        "leaked source locator token",
    )
    # 5. Version mismatch across manifests
    test_case(
        "manifest_version_mismatch",
        lambda r: (r / ".claude-plugin/plugin.json").write_text(
            (r / ".claude-plugin/plugin.json").read_text(encoding="utf-8").replace("0.2.0", "0.1.0"),
            encoding="utf-8",
        ),
        "version '0.1.0' != '0.2.0'",
    )
    # 6. Obsolete storage root token
    test_case(
        "obsolete_storage_token",
        lambda r: (r / "skills/para-workflow/SKILL.md").write_text(
            (r / "skills/para-workflow/SKILL.md").read_text(encoding="utf-8") + "\nUse 04-archived.\n",
            encoding="utf-8",
        ),
        "obsolete contract token",
    )

    all_passed = all(c["caught"] for c in cases)
    return {"self_test_passed": all_passed, "cases": cases}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate personal-management plugin package.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Path to personal-management package root",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run negative self-tests on temporary copies",
    )
    args = parser.parse_args()

    result = validate_package(args.root)
    if args.self_test:
        st = run_self_tests(args.root)
        result["self_test"] = st
        print(json.dumps(result, indent=2))
        return 0 if (result["valid"] and st["self_test_passed"]) else 1

    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
