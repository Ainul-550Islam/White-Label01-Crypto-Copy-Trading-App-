"""Which files differ from the last handover that embedded them?

No VCS in this repository, so the handovers ARE the snapshots: each one embeds the complete
content of every file its part added or modified. Comparing the current file against the newest
handover that carries it therefore yields the real change set since the last recorded state,
which is exactly the list the Part 19 handover must equal - the user's standing rule is that the
enumeration is the enforcement point, so it is derived rather than remembered.

Prints three groups: MODIFIED (embedded, content differs), SAME (embedded, identical), and
UNrecorded (never embedded by any handover - either new this part or older than the practice).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("/home/user/whitelabel-copytrade")
HEAD = re.compile(r"^## FILE: (.+?) \((\d+) lines\)$", re.MULTILINE)

CANDIDATE_TREES = (
    "libs/trading-core/wlct_trading",
    "libs/trading-core/tests",
    "services/execution-engine/app",
    "services/execution-engine/tests",
    "docs",
    "scripts",
)
CANDIDATE_FILES = (
    "services/execution-engine/.env.example",
    "services/execution-engine/requirements.txt",
    "services/execution-engine/requirements-dev.txt",
    "services/execution-engine/pyproject.toml",
    "services/execution-engine/Dockerfile",
    "libs/trading-core/pyproject.toml",
    "libs/trading-core/requirements.txt",
)
SKIP_PARTS = frozenset({"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules"})


def candidates() -> list[str]:
    out: list[str] = []
    for tree in CANDIDATE_TREES:
        base = ROOT / tree
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or SKIP_PARTS & set(path.parts):
                continue
            if path.suffix not in {".py", ".md", ".mjs", ".toml", ".json", ".txt", ".sql"}:
                continue
            out.append(str(path.relative_to(ROOT)))
    for rel in CANDIDATE_FILES:
        if (ROOT / rel).exists():
            out.append(rel)
    return sorted(set(out))


def embedded_blocks(text: str) -> dict[str, str]:
    """path -> embedded content, for one handover document."""
    found = {}
    head = re.compile(r"^## FILE: (.+?) \((\d+) lines\)\s*$", re.MULTILINE)
    fence = re.compile(r"^(\x60{3,6})[a-zA-Z0-9]*$", re.MULTILINE)
    matches = list(head.finditer(text))
    for index, match in enumerate(matches):
        stop = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        segment = text[match.end():stop]
        opened = fence.search(segment)
        if opened is None:
            continue
        body = segment[opened.end():]
        closer = re.compile(r"^\x60{" + str(len(opened.group(1))) + r"}$", re.MULTILINE)
        end = closer.search(body)
        if end is None:
            continue
        found[match.group(1).strip()] = body[:end.start()].strip("\n")
    return found


def main() -> int:
    def index(path: Path) -> int:
        # Numeric, not lexicographic: a string sort puts PART2 after PART18, which
        # would make a Part 2 snapshot the "newest" state of a file Part 18 rewrote.
        return int(path.name.removeprefix("PART").split("_")[0])

    handovers = sorted(ROOT.glob("docs/PART*_HANDOVER_FULL_SOURCE.md"), key=index)
    snapshots: dict[str, str] = {}
    origin: dict[str, str] = {}
    for handover in handovers:  # oldest first, so the newest wins
        blocks = embedded_blocks(handover.read_text(encoding="utf-8"))
        for path, content in blocks.items():
            snapshots[path] = content
            origin[path] = handover.name

    modified: list[str] = []
    same: list[str] = []
    unrecorded: list[str] = []
    for rel in candidates():
        current = (ROOT / rel).read_text(encoding="utf-8").strip("\n")
        if rel not in snapshots:
            unrecorded.append(rel)
        elif snapshots[rel] != current:
            modified.append(rel)
        else:
            same.append(rel)

    print(f"== MODIFIED since their last recorded state ({len(modified)}) ==")
    for rel in modified:
        print(f"  {rel}   [baseline: {origin[rel]}]")
    print(f"\n== never embedded in any handover ({len(unrecorded)}) ==")
    for rel in unrecorded:
        print(f"  {rel}")
    print(f"\n== identical to the last embedded content ({len(same)}) ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
