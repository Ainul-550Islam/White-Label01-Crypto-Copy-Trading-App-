#!/usr/bin/env python3
"""Per-language line census of the whitelabel-copytrade monorepo.

Deliberately lives OUTSIDE the repository: adding a file inside the tree would
change the tree totals this script reports, which is the kind of self-referential
drift the project's own handover generator spends effort avoiding.

Rule set is copied verbatim from scripts/gen_part16_handover.py::count_tree_lines
so the "source" total here is comparable to the number printed in
docs/PART16_HANDOVER_FULL_SOURCE.md. Nothing is dropped silently: every file in
the tree lands in exactly one bucket, and the excluded buckets are reported with
their own sizes.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path("/home/user/whitelabel-copytrade")

EXCLUDE_DIRS = frozenset(
    {
        "node_modules", "dist", ".next", ".git", "build", "coverage", "__pycache__",
        ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "venv",
        "target", "out", "site-packages",
    }
)

#: extension (or special filename) -> language label
LANG = {
    ".py": "Python",
    ".pyi": "Python (stubs)",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".mts": "TypeScript",
    ".js": "JavaScript",
    ".mjs": "JavaScript (ESM)",
    ".cjs": "JavaScript (CJS)",
    ".sql": "SQL",
    ".prisma": "Prisma schema",
    ".json": "JSON",
    ".md": "Markdown",
    ".mdx": "Markdown",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".toml": "TOML",
    ".sh": "Shell",
    ".bash": "Shell",
    ".mjs.test": "JavaScript (ESM)",
    ".css": "CSS",
    ".scss": "SCSS",
    ".html": "HTML",
    ".svg": "SVG",
    ".txt": "Text",
    ".dart": "Dart",
    ".arb": "ARB (Flutter l10n)",
    ".typed": "packaging marker",
    ".tsbuildinfo": "build artifact",
    ".rs": "Rust",
    ".c": "C",
    ".h": "C/C++ header",
    ".cpp": "C++",
    ".cc": "C++",
    ".hpp": "C/C++ header",
    ".go": "Go",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".ex": "Elixir",
    ".lua": "Lua",
    ".lock": "Lockfile",
    ".node": "Node binary",
    ".wasm": "Wasm",
    ".png": "Image",
    ".ico": "Image",
    ".gz": "Archive",
    ".env": "dotenv",
}

SPECIAL = {
    "Dockerfile": "Dockerfile",
    "dockerfile": "Dockerfile",
    "Makefile": "Make",
    "LICENSE": "Text",
    "NOTICE": "Text",
    ".gitignore": "git ignore",
    ".dockerignore": "docker ignore",
    ".env.example": "dotenv (example)",
    "README": "Markdown",
}


def label(rel: Path) -> str:
    """Language by the LAST extension, which is the one a compiler or runtime
    dispatches on: `orders.service.ts` is TypeScript (.service is the file's
    role in the NestJS convention, not its language)."""
    name = rel.name
    for special, lang in SPECIAL.items():
        if name == special or name.startswith(special + "."):
            return lang
    if name.lower().endswith("dockerfile"):
        return "Dockerfile"
    suffix = rel.suffix
    if suffix:
        return LANG.get(suffix.lower(), f"other ({suffix})")
    return "no extension"


def is_excluded(rel: Path) -> str | None:
    parts = rel.parts
    for part in parts:
        if part in EXCLUDE_DIRS:
            return f"dir:{part}"
    name = rel.as_posix()
    if name.endswith("package-lock.json") or name.endswith("yarn.lock") or name.endswith("pnpm-lock.yaml"):
        return "lockfile"
    if name.startswith("docs/source/"):
        return "docs/source dump"
    if re.match(r"docs/PART[^/]*_HANDOVER", name):
        return "PART*HANDOVER dump"
    return None



def name_is_test(name: str) -> bool:
    low = name.lower()
    return (
        low.startswith("test_")
        or low.endswith(".test.ts")
        or low.endswith(".spec.ts")
        or low.endswith("_test.py")
        or low.endswith(".test.tsx")
    )


def count(path: Path) -> tuple[int, int, int]:
    """(lines, non-blank lines, code-ish lines) - comments counted as code."""
    try:
        raw = path.read_bytes()
    except OSError:
        return (0, 0, 0)
    lines = raw.count(b"\n") + (1 if raw and not raw.endswith(b"\n") else 0)
    text_lines = raw.splitlines()
    non_blank = sum(1 for ln in text_lines if ln.strip())
    return (lines, non_blank, non_blank)


def main() -> None:
    per_lang: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    area_lang: dict[tuple[str, str], int] = defaultdict(int)
    test_lines: dict[str, int] = {}
    impl_lines: dict[str, int] = {}
    excluded: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    total_lines = 0
    total_files = 0
    source_lines = 0

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        why = is_excluded(rel)
        lines, non_blank, _ = (0, 0, 0) if why == "dir:node_modules" else count(path)
        if why:
            excluded[why][0] += 1
            # node_modules is a quarter-million files; the bucket exists to show
            # what the rule leaves out, not to bill time reading vendored code.
            if why != "dir:node_modules":
                el, _, _ = count(path)
                excluded[why][1] += el
            continue
        total_files += 1
        total_lines += lines
        if not rel.as_posix().startswith("docs/"):
            source_lines += lines
        bucket = per_lang[label(rel)]
        bucket[0] += 1
        bucket[1] += lines
        bucket[2] += non_blank
        area = rel.parts[0] if len(rel.parts) > 1 else "(repo root)"
        if area == "libs" and len(rel.parts) > 2:
            area = f"libs/{rel.parts[1]}"
        elif area == "services" and len(rel.parts) > 2:
            area = f"services/{rel.parts[1]}"
        elif area == "apps" and len(rel.parts) > 2:
            area = f"apps/{rel.parts[1]}"
        elif area == "packages" and len(rel.parts) > 2:
            area = f"packages/{rel.parts[1]}"
        area_lang[(area, lang := label(rel))] += lines
        parts_l = [q.lower() for q in rel.parts]
        if "tests" in parts_l or "test" in parts_l or name_is_test(rel.name):
            test_lines[lang] = test_lines.get(lang, 0) + lines
        else:
            impl_lines[lang] = impl_lines.get(lang, 0) + lines

    print(f"counted under the handover generator's rule set: {total_files:,} files, {total_lines:,} lines")
    print(
        f"reconciliation with the repo's own figures: source (docs/ excluded) = {source_lines:,}; "
        f"with narrative docs = {total_lines:,}  <- docs/PART16_HANDOVER_FULL_SOURCE.md prints both"
    )
    print()
    print(f"{'language':28s} {'files':>7s} {'lines':>10s} {'non-blank':>10s}")
    for lang, (files, lines, non_blank) in sorted(per_lang.items(), key=lambda kv: -kv[1][1]):
        print(f"{lang:28s} {files:7,d} {lines:10,d} {non_blank:10,d}")
    print()
    print("tests beside implementation (lines):")
    for lang in ("Python", "TypeScript", "TypeScript (React)", "Dart"):
        t_lines = a_lines = 0
        for area_lang_key, lines in area_lang.items():
            pass
        print(f"  {lang}: see the per-area table below" if False else "", end="")
        t_lines = sum(v for (a, l), v in area_lang.items() if l == lang and False)
        print(f"  {lang:20s} tests {test_lines.get(lang, 0):>7,d}   implementation {impl_lines.get(lang, 0):>8,d}")
    print()
    print("specifically asked about:")
    per_lang.setdefault("Swift", [0, 0, 0])
    per_lang.setdefault("Scala", [0, 0, 0])
    for lang in ("Python", "TypeScript", "TypeScript (React)", "JavaScript (ESM)", "Dart", "Rust", "C", "C++", "C/C++ header", "Go", "Java", "Kotlin", "Ruby", "PHP", "Swift", "Scala"):
        files = sum(b[0] for l, b in per_lang.items() if l == lang)
        lines = sum(b[1] for l, b in per_lang.items() if l == lang)
        print(f"  {lang:14s} {files:4,d} files {lines:>9,d} lines")
    print()
    print("by area (lines):")
    areas: dict[str, dict[str, int]] = defaultdict(dict)
    for (area, lang), lines in area_lang.items():
        areas[area][lang] = areas[area].get(lang, 0) + lines
    for area in sorted(areas, key=lambda a: -sum(areas[a].values())):
        langs = ", ".join(f"{l} {v:,}" for l, v in sorted(areas[area].items(), key=lambda kv: -kv[1]))
        print(f"  {area:26s} {sum(areas[area].values()):>9,d}  {langs}")
    print()
    print("excluded buckets (reported, not hidden):")
    for why, (files, lines) in sorted(excluded.items(), key=lambda kv: -kv[1][1]):
        shown = "     (not read)" if why == "dir:node_modules" else f"{lines:>10,d} lines"
        print(f"  {why:26s} {files:>7,d} files {shown}")


if __name__ == "__main__":
    main()
