"""Spec traceability: links metric ids in docs/metrics.md to tests marked @pytest.mark.spec("ID").

Fails on tests that reference an id the spec does not define (drift between spec and code).
Reports spec ids without any test, so unimplemented parts of the spec stay visible.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ID = r"M-[A-Z]{3}-\d{2}"


def spec_ids() -> set[str]:
    text = (ROOT / "docs" / "metrics.md").read_text(encoding="utf-8")
    return set(re.findall(rf"^#+\s+({ID})\b", text, flags=re.MULTILINE))


def tested_ids() -> set[str]:
    found: set[str] = set()
    for path in (ROOT / "tests").rglob("*.py"):
        found |= set(re.findall(rf"spec\(\s*[\"']({ID})[\"']", path.read_text(encoding="utf-8")))
    return found


def main() -> int:
    spec, tested = spec_ids(), tested_ids()
    orphans = sorted(tested - spec)
    untested = sorted(spec - tested)
    print(f"spec-trace: {len(spec & tested)}/{len(spec)} metric ids covered by tests")
    if untested:
        print("  not yet covered: " + ", ".join(untested))
    if orphans:
        missing = ", ".join(orphans)
        print(f"  tests reference ids missing from docs/metrics.md: {missing}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
