"""CRAP gate (Savoia & Evans, 2007) for functions in changed source files.

CRAP(m) = comp(m)^2 * (1 - cov(m))^3 + comp(m), where comp is cyclomatic complexity and
cov is the share of the function's statements executed by tests. Reads coverage.json
produced by pytest-cov. Fails when any function in a changed file exceeds the threshold.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from radon.complexity import cc_visit

ROOT = Path(__file__).resolve().parent.parent


def changed_sources(base: str) -> list[str]:
    ok = subprocess.run(["git", "rev-parse", "--verify", "-q", base], cwd=ROOT, capture_output=True)
    if ok.returncode != 0:
        return [str(p.relative_to(ROOT)) for p in (ROOT / "src").rglob("*.py")]
    out = subprocess.run(
        ["git", "diff", "--name-only", base, "--", "src"], cwd=ROOT, capture_output=True, text=True
    ).stdout.split()
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "--", "src"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout.split()
    return sorted({f for f in out + untracked if f.endswith(".py") and (ROOT / f).exists()})


def crap(complexity: int, coverage: float) -> float:
    return complexity**2 * (1 - coverage) ** 3 + complexity


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--changed-from", default="origin/main")
    parser.add_argument("--threshold", type=float, default=15.0)
    args = parser.parse_args()

    report = json.loads((ROOT / "coverage.json").read_text())["files"]
    failures = []
    checked = 0
    for rel in changed_sources(args.changed_from):
        cov = report.get(rel, {"executed_lines": [], "missing_lines": []})
        executed, missing = set(cov["executed_lines"]), set(cov["missing_lines"])
        for block in cc_visit((ROOT / rel).read_text()):
            lines = range(block.lineno, block.endline + 1)
            hit = sum(1 for n in lines if n in executed)
            total = hit + sum(1 for n in lines if n in missing)
            score = crap(block.complexity, hit / total if total else 1.0)
            checked += 1
            if score > args.threshold:
                failures.append(f"  {rel}:{block.lineno} {block.name} CRAP={score:.1f}")
    print(f"crap: {checked} functions checked in changed files, threshold {args.threshold}")
    if failures:
        message = "Functions too complex for their test coverage:\n" + "\n".join(failures)
        print(message, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
