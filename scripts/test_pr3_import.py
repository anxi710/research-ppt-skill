#!/usr/bin/env python3
"""Run PR #3's PDF import regression against its exact backend commits."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

import check_pdf_fidelity as fidelity


COMMITS = {
    "baseline": "8070d3df1f6f54b5fb60a9ae66e79c664f050212",
    "candidate": "b113d23720260c411ee47b2b05a73615f954deeb",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    roots = {name: getattr(args, name).resolve() for name in COMMITS}
    out = args.out.resolve()
    if any(out.is_relative_to(root) for root in roots.values()):
        parser.error("Use an output directory outside both backend checkouts.")
    try:
        out.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
        parser.error(f"Use a fresh output directory: {exc}")

    report = {
        "status": "fail",
        "scope": "PR #3 PDF import regression only",
        "end_to_end": {"status": "pending", "reason": "PPTX production and independent review run separately."},
        "started_at": datetime.now(timezone.utc).isoformat(),
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "backends": {}, "commands": [], "errors": [],
        "test_code": {str(Path(__file__).resolve()): sha256(Path(__file__)),
                      str(Path(fidelity.__file__).resolve()): sha256(Path(fidelity.__file__))},
    }

    def run(label: str, argv: list[str]) -> subprocess.CompletedProcess:
        result = subprocess.run(argv, cwd=out, capture_output=True, text=True)
        stdout = out / f"{label}.stdout.log"
        stderr = out / f"{label}.stderr.log"
        stdout.write_text(result.stdout, encoding="utf-8")
        stderr.write_text(result.stderr, encoding="utf-8")
        report["commands"].append({"argv": argv, "cwd": str(out), "exit_code": result.returncode,
                                   "stdout": stdout.name, "stderr": stderr.name})
        if result.returncode:
            raise ValueError(f"{label} exited {result.returncode}. Read {stderr.name}.")
        return result

    try:
        import fitz

        report["pymupdf_version"] = fitz.VersionBind
        for name, root in roots.items():
            actual_root = run(f"{name}-root", ["git", "-C", str(root), "rev-parse", "--show-toplevel"])
            if Path(actual_root.stdout.strip()).resolve() != root:
                raise ValueError(f"{name} must name the backend repository root.")
            revision = run(f"{name}-sha", ["git", "-C", str(root), "rev-parse", "HEAD"]).stdout.strip()
            state = run(f"{name}-status", ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"]).stdout
            if revision != COMMITS[name] or state:
                raise ValueError(f"{name} must be clean at {COMMITS[name]}.")
            skill = root / "skills/ppt-master"
            report["backends"][name] = {
                "root": str(root), "sha": revision, "dirty": False,
                "entry_hashes": {str(path.relative_to(root)): sha256(path)
                                 for path in [root / "AGENTS.md", skill / "SKILL.md", skill / "workflows/routing.md"]},
            }
            run(f"{name}-attribution", [sys.executable, str(skill / "scripts/attribution_guard.py")])

        candidate = roots["candidate"] / "skills/ppt-master/scripts"
        tests = run("upstream-tests", [sys.executable, "-m", "unittest", "discover", "-s",
                    str(candidate / "tests"), "-p", "test_pdf_content_preservation.py", "-v"])
        test_output = tests.stdout + tests.stderr
        if not re.search(r"\bRan 6 tests\b", test_output) or "skipped" in test_output:
            raise ValueError("The candidate must run all six preservation tests without skips.")
        report["upstream_tests"] = {"status": "pass", "tests_run": 6}
        fidelity.make_fixture(out / "fixture")
        expected_path = out / "fixture/expected.json"
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        comparisons = {}
        for name, root in roots.items():
            target = out / name
            target.mkdir()
            markdown = target / "paper.md"
            run(f"{name}-import", [sys.executable, str(root / "skills/ppt-master/scripts/source_to_md.py"),
                str(out / "fixture/paper.pdf"), "-o", str(markdown), "--images", "all"])
            comparisons[name] = fidelity.compare(expected_path, markdown)
            (target / "fidelity.json").write_text(json.dumps(comparisons[name], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        tables = comparisons["baseline"]["tables"]
        reproduced = (len(tables) == 1 and len(tables[0]) == 2
                      and all(len(row) == 10 for row in tables[0])
                      and tables[0][0] != expected["table"][0][:10]
                      and tables[0][1] == expected["table"][2][:10])
        report["baseline_reproduction"] = {
            "status": "pass" if reproduced else "fail",
            "expected_source_shape": [4, 11], "expected_baseline_shape": [2, 10],
            "expected_change": "Header changed. Secondary header, total row, and last column dropped.",
        }
        report["candidate_fidelity"] = {"status": comparisons["candidate"]["status"],
                                        "errors": comparisons["candidate"]["errors"]}
        if not reproduced or comparisons["candidate"]["status"] != "pass":
            raise ValueError("The baseline reproduction or candidate fidelity did not pass. Read the fidelity reports.")
        for name, root in roots.items():
            state = run(f"{name}-status-after", ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"]).stdout
            if state:
                raise ValueError(f"{name} changed during the test.")
        report["status"] = "pass"
    except (OSError, ValueError, ImportError, subprocess.SubprocessError) as exc:
        report["errors"].append(str(exc))
    finally:
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        report["files"] = {str(path.relative_to(out)): sha256(path)
                           for path in sorted(out.rglob("*")) if path.is_file()}
        (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "scope": report["scope"],
                      "end_to_end": "pending", "report": str(out / "report.json"),
                      "errors": report["errors"]}, ensure_ascii=False))
    return int(report["status"] != "pass")


if __name__ == "__main__":
    raise SystemExit(main())
