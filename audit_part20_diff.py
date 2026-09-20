"""Part 20's version of the change-set derivation, widened to the TypeScript apps.

Same rule as `audit_part19_diff.py`: with no VCS in this workspace the handovers ARE the
snapshots, so a file's true state since the last recorded point is "does the newest handover
that embeds it still match it byte for byte". Part 19 only had to look at Python plus `docs/`
and `scripts/`; Part 20 touched `apps/api`, `apps/admin-web` and `docker-compose.yml`, so the
candidate trees and the suffix set grew accordingly and the comparison stays fence-aware (an
embedded markdown document is fenced with four backticks, and a three-backtick parser reports
an untouched document as wholly rewritten).

Three groups: MODIFIED (embedded, content differs), SAME (embedded, identical), and
UNrecorded (never embedded by any handover - either new this part or older than the practice).
The script's output is the raw material for `scripts/gen_part20_handover.py`'s file lists; the
lists stay curated because a part's change set is what the part did, not everything that has
ever moved - which is why the UNrecorded group is printed with its sizes and read by a human.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("/home/user/whitelabel-copytrade")

CANDIDATE_TREES = (
    "libs/trading-core/wlct_trading",
    "libs/trading-core/tests",
    "services/execution-engine/app",
    "services/execution-engine/tests",
    "services/trading-engine",
    "services/market-data",
    "apps/api/src",
    "apps/api/test",
    "apps/admin-web/src",
    "packages",
    "docs",
    "scripts",
    "infrastructure",
)
CANDIDATE_FILES = (
    "docker-compose.yml",
    ".env.example",
    "README.md",
    "package.json",
    "services/execution-engine/pyproject.toml",
    "services/execution-engine/requirements.txt",
    "services/execution-engine/requirements-dev.txt",
    "services/execution-engine/.env.example",
    "libs/trading-core/pyproject.toml",
)
SUFFIXES = {
    ".py",
    ".md",
    ".mjs",
    ".toml",
    ".json",
    ".txt",
    ".sql",
    ".ts",
    ".tsx",
    ".prisma",
    ".yml",
    ".yaml",
    ".sh",
    ".dockerfile",
}
SKIP_PARTS = frozenset(
    {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        "dist",
        "build",
        ".next",
        "coverage",
    }
)


def candidates() -> list[str]:
    out: list[str] = []
    for tree in CANDIDATE_TREES:
        base = ROOT / tree
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or SKIP_PARTS & set(path.parts):
                continue
            name = path.name
            if path.suffix not in SUFFIXES and name != ".env.example":
                continue
            rel = str(path.relative_to(ROOT))
            if rel.startswith("docs/source/"):
                continue  # the regenerable dump, not a source file
            if re.match(r"^docs/PART\d+_HANDOVER_FULL_SOURCE\.md$", rel):
                continue  # handovers are snapshots, not candidates
            out.append(rel)
    for rel in CANDIDATE_FILES:
        if (ROOT / rel).exists():
            out.append(rel)
    return sorted(set(out))


def embedded_blocks(text: str) -> dict[str, str]:
    found = {}
    head = re.compile(r"^## FILE: (.+?) \((\d+) lines\)\s*$", re.MULTILINE)
    fence = re.compile(r"^(\x60{3,6})[a-zA-Z0-9]*$", re.MULTILINE)
    matches = list(head.finditer(text))
    for index, match in enumerate(matches):
        stop = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        segment = text[match.end() : stop]
        opened = fence.search(segment)
        if opened is None:
            continue
        body = segment[opened.end() :]
        closer = re.compile(r"^\x60{" + str(len(opened.group(1))) + r"}$", re.MULTILINE)
        end = closer.search(body)
        if end is None:
            continue
        found[match.group(1).strip()] = body[: end.start()].strip("\n")
    return found


def main() -> int:
    def index(path: Path) -> int:
        return int(path.name.removeprefix("PART").split("_")[0])

    handovers = sorted(ROOT.glob("docs/PART*_HANDOVER_FULL_SOURCE.md"), key=index)
    snapshots: dict[str, str] = {}
    origin: dict[str, str] = {}
    for handover in handovers:
        for path, content in embedded_blocks(handover.read_text(encoding="utf-8")).items():
            snapshots[path] = content
            origin[path] = handover.name

    modified: list[str] = []
    same = 0
    unrecorded: list[tuple[str, int]] = []
    for rel in candidates():
        current = (ROOT / rel).read_text(encoding="utf-8").strip("\n")
        if rel not in snapshots:
            unrecorded.append((rel, len(current.splitlines())))
        elif snapshots[rel] != current:
            modified.append(rel)
        else:
            same += 1

    print(f"== MODIFIED since their last recorded state ({len(modified)}) ==")
    for rel in modified:
        print(f"  {rel}   [baseline: {origin[rel]}]")
    print(f"\n== never embedded in any handover ({len(unrecorded)}) ==")
    for rel, size in unrecorded:
        print(f"  {rel}  ({size} lines)")
    print(f"\n== identical to the last embedded content ({same}) ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
