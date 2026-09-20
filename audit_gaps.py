#!/usr/bin/env python3
"""Gap audit for the whitelabel-copytrade tree. Lives OUTSIDE the repository.

Nine independent checks, each answering a question a reviewer can falsify:

  A empty or trivially small shipped files
  B python functions whose whole body is `pass` outside abstract interfaces
  C markdown path references that do not resolve to a file in the tree
  D settings fields a service reads that .env.example never mentions
  E docker-compose references (build contexts, dockerfiles, named volumes, networks)
  F first-party python imports that do not resolve
  G wlct_trading modules no test file names
  H dart/TS unimplemented markers
  I handover file lists vs the tree (created/modified entries that are absent)

Nothing is written. Every finding is printed with the file and line a human can open.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO = Path("/home/user/whitelabel-copytrade")

SKIP_DIR_PARTS = {
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "dist",
    "build",
    ".next",
    "coverage",
    ".venv",
    ".git",
}
CODE_SUFFIXES = {".py", ".ts", ".tsx", ".dart", ".mjs", ".sql", ".prisma", ".json", ".yml", ".yaml"}


def walk(*, code_only: bool = True):
    for path in sorted(REPO.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(REPO).as_posix()
        if any(part in SKIP_DIR_PARTS for part in path.parts):
            continue
        if rel.startswith("docs/source/"):
            continue
        if code_only and path.suffix not in CODE_SUFFIXES and path.suffix != ".md":
            continue
        yield rel, path


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def is_abstract(tree: ast.Module) -> set[int]:
    """Line numbers of functions that are legitimately bodyless (protocols/abc/overload)."""
    legit: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            deco = {d.id if isinstance(d, ast.Name) else getattr(d, "attr", "") for d in node.decorator_list}
            if deco & {"abstractproperty", "abstractmethod", "overload", "property", "classmethod", "staticmethod"}:
                legit.add(node.lineno)
            if len(node.body) == 1 and isinstance(node.body[0], ast.Expr) and isinstance(
                node.body[0].value, (ast.Constant, ast.Ellipsis)
            ):
                legit.add(node.lineno)  # docstring-only protocol method
    return legit


def class_is_abstract(tree: ast.Module) -> dict[int, str]:
    """lineno -> class name, for classes that inherit abc.ABC or typing.Protocol."""
    out: dict[int, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = []
            for b in node.bases:
                if isinstance(b, ast.Name):
                    bases.append(b.id)
                elif isinstance(b, ast.Attribute):
                    bases.append(b.attr)
            if any(x in {"ABC", "Protocol", "Interface", "RuntimeProtocol"} for x in bases):
                for sub in ast.walk(node):
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        out[sub.lineno] = node.name
    return out


def report(title: str, lines: list[str]) -> int:
    print(f"\n### {title}")
    if not lines:
        print("  clean - no findings")
        return 0
    for line in lines:
        print(f"  {line}")
    return len(lines)


def check_a() -> int:
    lines = []
    for rel, path in walk(code_only=True):
        if rel.endswith((".lock", ".min.js")) or "package-lock" in rel:
            continue
        text = read(path)
        stripped = text.strip()
        if not stripped:
            lines.append(f"EMPTY FILE: {rel}")
        elif path.suffix in {".py", ".ts", ".tsx", ".dart"} and len(stripped.splitlines()) < 6:
            # A 1-5 line source file is either a re-export barrel (fine) or a stub (not fine).
            looks_like_barrel = bool(re.match(r'^(export|from|import|const|/\*\*|//|@)', stripped))
            if not looks_like_barrel:
                lines.append(f"TINY SOURCE FILE ({len(stripped.splitlines())} lines): {rel} :: {stripped[:60]!r}")
    return report("A. empty / trivially small source files", lines)


def check_b() -> int:
    lines = []
    for rel, path in walk():
        if path.suffix != ".py" or rel.startswith("libs/trading-core/tests/"):
            continue
        text = read(path)
        try:
            tree = ast.parse(text)
        except SyntaxError:
            lines.append(f"UNPARSABLE PYTHON: {rel}")
            continue
        legit = is_abstract(tree) | set(class_is_abstract(tree))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.lineno in legit:
                continue
            body = node.body
            if len(body) == 1 and isinstance(body[0], ast.Pass):
                lines.append(f"BODY IS ONLY pass: {rel}:{node.lineno} def {node.name}()")
    return report("B. functions whose entire body is `pass` (non-abstract)", lines)


def check_c() -> int:
    lines = []
    existing = {rel for rel, _ in walk(code_only=False)} | {
        p for p in (x.relative_to(REPO).as_posix() for x in REPO.rglob("*") if x.is_dir())
    }
    pattern = re.compile(r"[`\s(\"'|]((?:libs|apps|services|packages|infrastructure|scripts|docs)/[A-Za-z0-9_./*-]+)")
    for rel, path in walk():
        if path.suffix != ".md" or rel.startswith("docs/source/"):
            continue
        text = read(path)
        for match in pattern.finditer(text):
            target = match.group(1).rstrip(".,;:")
            if "*" in target or target.endswith("/"):
                continue
            if target not in existing and not (REPO / target).exists():
                lines.append(f"DANGLING REFERENCE in {rel}: {target}")
    # collapse repeats
    seen: dict[str, int] = {}
    for line in lines:
        seen[line] = seen.get(line, 0) + 1
    return report("C. markdown references to paths that are not in the tree", [f"{k}" for k in sorted(seen)])


def env_keys(text: str) -> set[str]:
    return set(re.findall(r"^([A-Z][A-Z0-9_]{2,})=", text, re.M)) | set(
        re.findall(r'^\s*#?\s*([A-Z][A-Z0-9_]{2,})=', text, re.M)
    )


def check_d() -> int:
    """Settings fields a service reads that NO example file names.

    Corrected after the first pass: the root .env.example defers engine knobs to
    services/execution-engine/.env.example, so both files are read, and only the
    environment-facing fields declared inside a settings class count - a module-level
    frozenset of DSN query parameters is not a knob.
    """
    lines = []
    for rel, path in walk():
        if path.suffix != ".py" or path.name != "config.py":
            continue
        if not rel.startswith("services/"):
            continue
        text = read(path)
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        fields: set[str] = set()
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                bases = {b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in node.bases}
                if bases & {"BaseSettings", "Settings"} or node.name.endswith("Settings"):
                    for stmt in node.body:
                        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                            if re.fullmatch(r"[A-Z][A-Z0-9_]{2,}", stmt.target.id):
                                fields.add(stmt.target.id)
        corpus = read(REPO / ".env.example") + read(path.parent.parent / ".env.example")
        missing = sorted(f for f in fields if f not in corpus)
        if missing:
            lines.append(f"{rel}: {len(missing)} field(s) in no example file -> {', '.join(missing)}")
    return report("D. settings fields a service reads that no example file names", lines)


def check_e() -> int:
    lines = []
    import yaml  # type: ignore

    for compose in [REPO / "docker-compose.yml", REPO / "docker-compose.observability.yml"]:
        if not compose.exists():
            lines.append(f"MISSING COMPOSE FILE: {compose.name}")
            continue
        doc = yaml.safe_load(compose.read_text()) or {}
        services = doc.get("services") or {}
        for name, svc in services.items():
            build = svc.get("build") or {}
            if isinstance(build, dict):
                ctx = build.get("context")
                dockerfile = build.get("dockerfile") or "Dockerfile"
                if ctx:
                    ctx_path = REPO / ctx
                    if not ctx_path.exists():
                        lines.append(f"{compose.name}: service {name} build.context {ctx} does not exist")
                    elif not (ctx_path / dockerfile).exists():
                        lines.append(f"{compose.name}: service {name} has no {dockerfile} in {ctx}")
                elif not svc.get("image"):
                    lines.append(f"{compose.name}: service {name} has neither build.context nor image")
            for vol in svc.get("volumes") or []:
                if isinstance(vol, str) and not vol.startswith((".", "/", "~")):
                    src = vol.split(":")[0]
                    if src not in (doc.get("volumes") or {}) and not src.startswith("."):
                        lines.append(f"{compose.name}: service {name} mounts undeclared named volume {src!r}")
            for net in svc.get("networks") or []:
                if net not in (doc.get("networks") or {}):
                    lines.append(f"{compose.name}: service {name} joins network {net!r} that this file does not declare")
    return report("E. compose references that do not resolve", lines)


def first_party_names() -> tuple[set[str], set[Path]]:
    mods: set[str] = set()
    roots = {
        "libs/trading-core": "wlct_trading",
    }
    for rel_root, pkg in roots.items():
        for path in (REPO / rel_root / pkg).rglob("*.py"):
            rel = path.relative_to(REPO / rel_root).with_suffix("")
            mods.add(".".join(rel.parts))
    return mods, {REPO / rel_root for rel_root in roots}


def check_f() -> int:
    lines = []
    syspath_roots = [REPO / "libs/trading-core", REPO / "services/execution-engine", REPO / "services/trading-engine", REPO / "services/market-data"]
    for rel, path in walk():
        if path.suffix != ".py":
            continue
        text = read(path)
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        service_dir = None
        parts = Path(rel).parts
        if parts[0] == "services" and len(parts) > 1:
            service_dir = REPO / "services" / parts[1]
        for node in ast.walk(tree):
            mods: list[str] = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                mods = [node.module]
            for mod in mods:
                top = mod.split(".")[0]
                if top in {"app", "wlct_trading", "scripts"}:
                    tail = mod.split(".", 1)[1] if "." in mod else ""
                    stem = top.replace("app", "app")
                    base = service_dir if top == "app" and service_dir else None
                    if top == "wlct_trading":
                        target = REPO / "libs/trading-core" / Path(*mod.split("."))
                    elif base:
                        target = base / Path(stem) / Path(*tail.split(".")) if tail else base / "app"
                    else:
                        continue
                    if not (target.with_suffix(".py").exists() or (target / "__init__.py").exists() or target.is_dir()):
                        lines.append(f"UNRESOLVED IMPORT {mod!r} in {rel}:{node.lineno}")
    uniq = sorted(set(lines))
    return report("F. first-party imports that do not resolve to a file", uniq)


def check_g() -> int:
    """Modules whose public symbols no test file names.

    Corrected after the first pass, which compared *module* names and reported five
    false positives: tests import functions, not modules.
    """
    lines = []
    tests_text = "\n".join(read(p) for p in (REPO / "libs/trading-core/tests").rglob("*.py"))
    tests_text += "\n".join(read(p) for p in REPO.glob("services/*/tests/*.py"))
    tests_text += "\n".join(read(p) for p in (REPO / "apps/api/src").rglob("*.spec.ts"))
    for path in sorted((REPO / "libs/trading-core/wlct_trading").rglob("*.py")):
        if path.name == "__init__.py":
            continue
        text = read(path)
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        exported = set(re.findall(r'"([A-Za-z_][A-Za-z0-9_]*)"', (re.search(r"__all__\s*=\s*\(?([^)\]]*)\)?", text) or re.match("", "")).group(1) if re.search(r"__all__", text) else ""))
        tops = {n.name for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and not n.name.startswith("_")}
        symbols = (exported | tops) - {"annotations"}
        if not symbols:
            continue
        named = {s for s in symbols if re.search(r"\b" + re.escape(s) + r"\b", tests_text)}
        if not named:
            rel = path.relative_to(REPO / "libs/trading-core").with_suffix("").as_posix().replace("/", ".")
            lines.append(f"no test names any public symbol of {rel} ({len(symbols)} symbols)")
    return report("G. wlct_trading modules whose public symbols no test file names", lines)


def check_h() -> int:
    lines = []
    for rel, path in walk():
        if path.suffix not in {".dart", ".ts", ".tsx"}:
            continue
        text = read(path)
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(r"UnimplementedError|throw\s+Error\(\s*[\"']not implemented|@ts-ignore\s*$|eslint-disable-next-line\s+no-unreachable", line):
                lines.append(f"{rel}:{i}: {line.strip()[:100]}")
    return report("H. TS/Dart unimplemented markers", lines)


def check_i() -> int:
    lines = []
    existing = {rel for rel, _ in walk(code_only=False)}
    for gen in sorted((REPO / "scripts").glob("gen_part*_handover.py")):
        text = read(gen)
        for m in re.finditer(r'"((?:libs|apps|services|packages|infrastructure|scripts|docs|\.env\.example|README\.md)[^"]*)"', text):
            target = m.group(1)
            if "/" not in target and not target.endswith((".md", ".example")):
                continue
            if target.endswith("/") or "*" in target:
                continue
            if target not in existing and not (REPO / target).exists():
                lines.append(f"{gen.name} lists a file that is not in the tree: {target}")
    return report("I. handover generator file lists vs the tree", sorted(set(lines)))


def main() -> int:
    total = 0
    for fn in (check_a, check_b, check_c, check_d, check_e, check_f, check_g, check_h, check_i):
        try:
            total += fn()
        except Exception as exc:  # a crash in one check must not hide the others
            print(f"\n### {fn.__name__} crashed: {type(exc).__name__}: {exc}")
    print(f"\nTOTAL FINDINGS: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
