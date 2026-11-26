#!/usr/bin/env python3
"""Self-contained static validator for the design-system plugin package (Python 3 stdlib only)."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

EXPECTED_NAME = "design-system"
EXPECTED_VERSION = "0.2.0"
EXPECTED_SKILLS = [
    "accessibility-audit",
    "component-design",
    "design-system-audit",
    "design-system-create",
    "design-system-update",
]
COMMON_REFS = [
    "audit-matrix.md",
    "color-and-accessibility.md",
    "deliverables-schema.md",
    "system-contract.md",
    "token-architecture.md",
]
COMMON_ASSETS = ["apca-lookup-table.json", "design-system-schema.json"]
MANIFEST_PATHS = [
    "plugin.json",
    ".antigravity-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    ".kimi-plugin/plugin.json",
]
MACHINE_PATH_RE = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/](?!/)")
FRONTMATTER_RE = re.compile(
    r'\A---\r?\n+name:\s*"?([a-z0-9-]+)"?\r?\ndescription:\s*"?(Use when[^\r\n"]+)"?\r?\n---\r?\n'
)


def validate_package(root: Path) -> dict:
    errors: list[str] = []
    root = root.resolve()

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
            if not isinstance(cfg.get("mcpServers"), dict):
                errors.append(f"{mcp_rel}: missing mcpServers object")
        except Exception as exc:
            errors.append(f"Invalid JSON in {mcp_rel}: {exc}")

    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return {"valid": False, "errors": ["Missing skills/ directory"]}

    found_skills = sorted(p.name for p in skills_dir.iterdir() if p.is_dir())
    if found_skills != EXPECTED_SKILLS:
        errors.append(f"Skill set mismatch: found {found_skills}, expected {EXPECTED_SKILLS}")

    ref_bytes: dict[str, bytes] = {}
    asset_bytes: dict[str, bytes] = {}
    engine_bytes: bytes | None = None

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
                stripped = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
                stripped = re.sub(r"`[^`]+`", "", stripped)
                for link in re.findall(r"\]\(([^\s)]+)\)", stripped):
                    if re.match(r"[a-zA-Z]+:", link) or link.startswith("#"):
                        continue
                    target = (p.parent / link.split("#")[0]).resolve()
                    if not target.is_relative_to(sroot.resolve()):
                        errors.append(f"{skill_name}: non-local link '{link}' in {p.relative_to(sroot)}")
                    elif not target.exists():
                        errors.append(f"{skill_name}: missing local link '{link}' in {p.relative_to(sroot)}")

        for rname in COMMON_REFS:
            rp = sroot / "references" / rname
            if not rp.exists():
                errors.append(f"{skill_name}: missing synchronized reference {rname}")
            else:
                b = rp.read_bytes()
                if rname not in ref_bytes:
                    ref_bytes[rname] = b
                elif ref_bytes[rname] != b:
                    errors.append(f"{skill_name}: reference contract drift in references/{rname}")

        for aname in COMMON_ASSETS:
            ap = sroot / "assets" / aname
            if not ap.exists():
                errors.append(f"{skill_name}: missing synchronized asset {aname}")
            else:
                b = ap.read_bytes()
                if aname not in asset_bytes:
                    asset_bytes[aname] = b
                elif asset_bytes[aname] != b:
                    errors.append(f"{skill_name}: asset drift in assets/{aname}")

        ep = sroot / "scripts" / "design_system_engine.py"
        if not ep.exists():
            errors.append(f"{skill_name}: missing scripts/design_system_engine.py")
        else:
            eb = ep.read_bytes()
            if engine_bytes is None:
                engine_bytes = eb
            elif engine_bytes != eb:
                errors.append(f"{skill_name}: engine script drift in scripts/design_system_engine.py")

    for req_file in ("GUIDE.md", "CHANGELOG.md", "SOURCES.md", ".antigravity-plugin/README.md", "tests/TEST-REPORT.md"):
        rp = root / req_file
        if not rp.exists():
            errors.append(f"Missing package file: {req_file}")
        else:
            if MACHINE_PATH_RE.search(rp.read_text(encoding="utf-8")):
                errors.append(f"Machine path in {req_file}")

    return {
        "valid": len(errors) == 0,
        "package": str(root),
        "version": EXPECTED_VERSION,
        "skills_checked": len(found_skills),
        "errors": errors,
    }


def run_self_tests(root: Path) -> dict:
    cases = []

    def test_case(name: str, mutate_fn, expect_substring: str) -> None:
        with tempfile.TemporaryDirectory() as td:
            copy_root = Path(td) / EXPECTED_NAME
            shutil.copytree(root, copy_root)
            mutate_fn(copy_root)
            res = validate_package(copy_root)
            caught = (not res["valid"]) and any(expect_substring in e for e in res["errors"])
            cases.append({"case": name, "caught": caught, "expected": expect_substring, "errors": res["errors"][:3]})

    test_case(
        "corrupted_frontmatter",
        lambda r: (r / "skills/design-system-create/SKILL.md").write_text("---\nname: wrong\ndescription: Bad\n---\n", encoding="utf-8"),
        "invalid YAML frontmatter",
    )
    test_case(
        "nonlocal_cross_skill_link",
        lambda r: (r / "skills/component-design/SKILL.md").write_text(
            (r / "skills/component-design/SKILL.md").read_text(encoding="utf-8") + "\nSee [other](../design-system-create/SKILL.md)\n",
            encoding="utf-8",
        ),
        "non-local link",
    )
    test_case(
        "reference_contract_drift",
        lambda r: (r / "skills/design-system-audit/references/system-contract.md").write_text("# drifted\n", encoding="utf-8"),
        "reference contract drift",
    )
    test_case(
        "engine_script_drift",
        lambda r: (r / "skills/accessibility-audit/scripts/design_system_engine.py").write_text("# drifted\n", encoding="utf-8"),
        "engine script drift",
    )
    test_case(
        "manifest_version_mismatch",
        lambda r: (r / ".claude-plugin/plugin.json").write_text(
            (r / ".claude-plugin/plugin.json").read_text(encoding="utf-8").replace(EXPECTED_VERSION, "9.9.9"),
            encoding="utf-8",
        ),
        f"version '9.9.9' != '{EXPECTED_VERSION}'",
    )
    test_case(
        "leaked_machine_path",
        lambda r: (r / "skills/design-system-update/SKILL.md").write_text(
            (r / "skills/design-system-update/SKILL.md").read_text(encoding="utf-8") + "\nSee C:\\Users\\leak\\file.md\n",
            encoding="utf-8",
        ),
        "machine path",
    )

    return {"self_test_passed": all(c["caught"] for c in cases), "cases": cases}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate design-system plugin package.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    res = validate_package(args.root)
    if args.self_test:
        st = run_self_tests(args.root)
        res["self_test"] = st
        print(json.dumps(res, indent=2))
        return 0 if (res["valid"] and st["self_test_passed"]) else 1
    print(json.dumps(res, indent=2))
    return 0 if res["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
