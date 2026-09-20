"""Build scripts/gen_part20_handover.py from scripts/gen_part19_handover.py.

Same relationship every part has had since Part 16: the machinery (the fence helper, the
baseline search, the elision sweep, the measured header, the emission-count guard, ``--check``)
is the predecessor's; what moves is the docstring, the pointers, the two file lists, the gate
set and the narrative header. Every substitution is asserted against exactly one anchor, so a
silent no-op - the failure mode that would ship a Part 20 document describing Part 19 - cannot
pass as success.
"""

from __future__ import annotations

import pathlib

ROOT = pathlib.Path("/home/user/whitelabel-copytrade")
SRC = ROOT / "scripts" / "gen_part19_handover.py"
DST = ROOT / "scripts" / "gen_part20_handover.py"

text = SRC.read_text(encoding="utf-8")


def sub(old: str, new: str, count: int = 1) -> None:
    global text
    found = text.count(old)
    assert found == count, f"anchor found {found}x, expected {count}: {old[:90]!r}"
    text = text.replace(old, new)


def region(start_marker: str, end_marker: str, new: str) -> None:
    """Replace everything between start_marker (inclusive) and end_marker (exclusive)."""
    global text
    assert text.count(start_marker) == 1, f"start anchor {text.count(start_marker)}x"
    start = text.index(start_marker)
    stop = text.index(end_marker, start)
    assert stop > start
    text = text[:start] + new + text[stop:]


# ---------------------------------------------------------------- docstring
DOCSTRING = '''"""Part 20 - the engine's own account, read; and the checker, run. The full-source handover.

Generated, not written by hand, for the reason Part 15 established and Parts 16, 17, 18 and 19
repeated: a hand-copied "full source" document starts drifting the moment a file changes, and a
document whose completeness cannot be re-proved is a document that merely claims. This script
embeds the complete content of every file Part 20 added or modified, states its own gate results
by RUNNING the suites, and accepts ``--check``, which regenerates in memory and compares byte for
byte against the committed file.

Copied from ``scripts/gen_part19_handover.py`` and re-pointed, which is the honest description of
the relationship. What changed in the machinery: the gate list gained ``--check-schedule`` (this
part is the one that installed the scheduler, so its generator runs that check rather than
quoting it), the two part-specific test runs moved from "core + service" to "API + service"
because this part's new tests live in those two suites, and the suppression-token count now
sweeps ``.py``, ``.ts``, ``.tsx`` and ``.mjs`` - a display-layer part lives in TypeScript, and
counting only the Python half would have been the flattering half.

The file lists were derived rather than remembered. There is no VCS in this workspace, so the
prior handovers ARE the snapshots: comparing every candidate file against the newest handover
that embeds it yields the real change set since the last recorded state. That sweep named 26
files whose content had moved; 15 of them carry Part 20 markers and are listed below. The other
eleven - `apps/api/src/infrastructure/metrics/metrics.registry.ts`,
`apps/api/src/modules/observability/alert.constants.ts`, `docs/fixtures/observability_fixtures.json`,
`libs/trading-core/wlct_trading/backtest/engine.py`, `libs/trading-core/wlct_trading/observability/alerts.py`,
`libs/trading-core/wlct_trading/risk/evaluator.py`, `packages/shared-types/src/audit.ts`,
`packages/shared-types/src/rbac.ts`, `services/market-data/app/config.py`,
`services/market-data/app/main.py`, `services/market-data/app/observability.py` - differ from a
Part 8 or Part 9 snapshot in exactly the shape Part 10 left them (the SLO identity constants, the
burn-rate rules, the OpenTelemetry `use_span` imports), were never re-embedded by the part that
changed them, and are neither claimed nor repaired here. The comparison must be fence-aware,
because an embedded markdown document is fenced with four backticks and a three-backtick parser
reports an untouched document as wholly rewritten. The audit script is
``/home/user/audit_part20_diff.py`` in the session workspace, and
``/home/user/part20_deltas_pre_regen.txt`` holds the same sweep's line-count deltas taken BEFORE
the ancestors were regenerated; their results, not their existence, are what this paragraph
asserts.
"""
'''
region('"""Part 19 - live enablement', "from __future__ import annotations\n", DOCSTRING + "\n")

# ---------------------------------------------------------------- pointers
sub(
    'OUT = ROOT / "docs" / "PART19_HANDOVER_FULL_SOURCE.md"',
    'OUT = ROOT / "docs" / "PART20_HANDOVER_FULL_SOURCE.md"',
)
sub("ROOT / \"docs\" / f\"PART{n}_HANDOVER_FULL_SOURCE.md\" for n in range(18, 0, -1)",
    "ROOT / \"docs\" / f\"PART{n}_HANDOVER_FULL_SOURCE.md\" for n in range(19, 0, -1)")
sub('else frozenset({"scripts/gen_part19_handover.py"})',
    'else frozenset({"scripts/gen_part20_handover.py"})')
sub("failing on itself - which is exactly what happened when this script was derived\n#: from Part 16's.",
    "failing on itself - which is exactly what happened when this script was derived\n#: from Part 16's, and again on the way to Part 20's.")

# ---------------------------------------------------------------- file lists
NEW_BLOCK = '''NEW: Final[list[tuple[str, str]]] = [
    (
        "apps/api/src/modules/worker/engine-status-contract.ts",
        "the mirror of `services/execution-engine/app/schemas.py::StatusResponse`, one table wide: `ENGINE_STATUS_FIELDS` carries every wire key with its TypeScript type, whether the engine defaults it, and the default spelled out verbatim; `parseEngineStatus` refuses a non-object body, a missing required key, a wrong primitive and an unknown key at the top level, preserves an explicit `null` on a declared-nullable field instead of substituting the default, and reports `unmappedKeys` rather than discarding them. The two absence laws are the point of the file: the mirror's defaults ARE the engine's defaults, so an engine too old to answer reads as too old to answer, never as healthy.",
    ),
    (
        "apps/api/src/modules/worker/engine-status-contract.spec.ts",
        "16 tests on the mirror: the 20-key set is spelled out as data (a key added to the schema without a row here fails), the nine required keys refuse absence individually, declared-nullable keys keep `null` where an absent key takes the default, `simulated` is reported and never silently folded into `mode`, wrong-typed values name the field that moved, and the refusal objects carry a `field` so a UI can point at it.",
    ),
    (
        "apps/api/src/modules/worker/engine-status-parity.spec.ts",
        "the three-sided law, checked in CI: this spec parses `app/schemas.py` with a small reader and asserts that its field set equals this part's alias table equals what `parseEngineStatus` accepts. A rename, an addition or a deletion on the Python side fails here with the key named, which is what makes the mirror maintainable instead of merely current.",
    ),
    (
        "apps/api/src/modules/observability/engine-posture.service.ts",
        "the `ENGINE POSTURE` section: a 10-second cached read through the existing engine client, a 2-second panel budget, three states (`reported`, `unverified`, `unconfigured`) with a `code` and a truncated `reason` on the unhappy ones, the tone law in which no absence renders as success, and rows for instance, mode, dry-run, adapter, store, durability, retention, enablement age, credential source, fetcher, operator confirmation, placement policy, incidents, metrics, locks and command count. It never invents a value: with no client it says so instead of throwing at request time, and it is a `readiness`-shaped sibling of the module's existing views, not a new endpoint.",
    ),
    (
        "apps/api/src/modules/observability/engine-posture.service.spec.ts",
        "18 tests around that service, including the ones that make a panel honest: a shape error reports the key name rather than an HTTP 500, a timeout says the read is still running, an error before the first success does not claim to show a stale-but-real answer, `unconfigured` explains what to set, the cache is not a second TTL implementation, and a posture that reports `simulated: true` cannot render as a green live deployment.",
    ),
    (
        "docs/PART20_ENGINE_STATUS_EDGE.md",
        "the part's own document, nine sections: what the audit found in the tree as it stood, the mirror and its two absence laws, the parity law, the panel and its tone law, the nine refusals with reasons, in the order the section lists them (no engine health-mirror publisher, no worker-side placement gate, no published readiness gates, no console renderer for `sections`, no re-badging of the four open ROADMAP rows, no Prometheus/Alertmanager rule generation out of prose conditions and `threshold: float | None`, no cron container in compose, no change to `/health/ready`'s unauthenticated posture, no configuration knob beyond `--manifest`), the scheduler wiring, the defect that running the composition found with its before/after measurements, every gate number transcribed from the run, and what an operator does with any of it.",
    ),
    (
        "docs/dr/schedule/dr.cron",
        "the generated schedule: `wlctRoot=.`, one `SHELL=/bin/sh`, and three job lines (`--due` daily, `--check` daily, `--check-rls` at the tightest declared cadence), with redis's no-obligation waiver echoed as a comment and no job line of its own. Generated by `node scripts/dr-manifest.mjs --emit-schedule` and drift-gated by `--check-schedule`; it may schedule reads and never a ledger write, and the installation step stays a documented `crontab` command because this repository does not own a host's cron.",
    ),
    (
        "services/execution-engine/tests/test_part20_status_read.py",
        "19 tests for the engine side of section 7: the read answers tenantless with exactly the 20 contract keys and real values; a tenant-naming caller gets a byte-identical document; correlation round-trips; an empty `x-tenant-id` equals an absent one on both scopes; a malformed tenant still 400s under the read scope; no token, an empty token, a same-length wrong token and a truncated token all 401 before the tenant branch is reached; the command scope's refusal code and sentence are pinned to the byte; the read scope is asserted to sit on exactly one route by walking `app.routes`; every other internal route is swept over HTTP to confirm a tenantless POST still gets `TENANT_HEADER_REQUIRED`; and `/health/ready`'s key set stays a superset of `/status`'s, which is the disclosure argument for the exemption held as an invariant.",
    ),
    (
        "scripts/gen_part20_handover.py",
        "this generator. It is in the list because it is a source file of the part and its content is what makes the document reproducible; it is exempt from its own suppression-token scan via `__file__`, which is also why that exemption is computed rather than hardcoded.",
    ),
]

MODIFIED: Final[list[tuple[str, str]]] = [
    (
        "apps/api/src/modules/worker/engine-internal.client.ts",
        "`getStatus()` now answers `EngineStatus` (the mirror's type) instead of a hand-shaped object, reading the parsed body through `parseEngineStatus`; the two consumed fields (`mode`, `storeBackend`) and every assertion the startup gate makes are unchanged, and the terminal-versus-retryable status classification was deliberately not widened - the fix for the 400 was made where the 400 came from.",
    ),
    (
        "apps/api/src/modules/observability/observability.module.ts",
        "the client is provided by a factory that asks `engineInternalClientConfigured` before constructing one, so an API process with no engine wiring boots and reports `unconfigured` rather than failing to start, and `EnginePostureService` is registered beside the module's other read-only views with the client injected optionally.",
    ),
    (
        "apps/api/src/modules/observability/observability.service.ts",
        "`execution` gained `sections`, rendered from the posture view, and the existing `enginePosture` readiness-gate summary is untouched: the panel row is a second reader of one fact, not a second source of it.",
    ),
    (
        "services/execution-engine/app/security.py",
        "the part's behaviour change: one law, two scopes. `_authenticate` (the constant-time token comparison), `_tenant_or_none` (validate-what-is-sent, refuse-what-is-required) and `_request_id` are shared, `TENANT_REQUIRED_CODE` names the refusal the worker matches on, `require_internal_auth` keeps its command semantics and its exact message, and `require_internal_auth_readonly` tolerates the absence of a tenant header for a route that acts on no tenant while still refusing a malformed one and still returning `tenant_id == \\"\\"` rather than an invented pseudo-tenant.",
    ),
    (
        "services/execution-engine/app/routers/internal.py",
        "one `Depends` line and its comment: `engine_status` reads through `ReadAuthDep`, and the comment records why (a process-level read has no tenant to name) and that every command route keeps the tenant law. The route body never touched the caller before and does not now.",
    ),
    (
        "services/execution-engine/tests/conftest.py",
        "the `client` fixture's annotation was `-> TestClient` on a generator function, which mypy could only report as an error; it now says `Iterator[TestClient]`. Fixed because Part 20's suite came to depend on it, and left as the one typing repair this part made in a file it did not author.",
    ),
    (
        "scripts/dr-manifest.mjs",
        "the schedule half of the tool: `SCHEDULE_PATH`, `scheduleCheckIntervalHours`, `scheduleCronFor`, `scheduleTightestCadenceHours`, `renderSchedule`, `scheduleDrift`, `SCHEDULE_FORBIDDEN_MODES` and `SCHEDULE_ROOT_LINE`, the two new modes answered before `--check-rls`, and `--manifest` as an override so the derived schedule can be exercised against a hypothetical board - including the all-waived board that must emit no job lines at all. `--record` stays human-only, and the generator refuses a manifest without its `wlctRoot=` line, an empty file, secret-shaped values, and any byte difference on a drift check.",
    ),
    (
        "scripts/dr-manifest.test.mjs",
        "13 tests for that derivation: the interval law (`min(tightest cadence, 24h)`), the hour-field wrap that makes `0 */N * * *` valid for any N in 1..24, `--check` staying daily regardless, waivers rendered as comments, the all-waived board, the RLS waiver removing `--check-rls`, `--record` and `--record-rls` refused and reported as their own finding ahead of the byte comparison, and the tamper cases landing on JOB lines because a comment-only edit is correctly a byte mismatch.",
    ),
    (
        "docker-compose.yml",
        "`EXECUTION_ENGINE_URL: http://execution-engine:8093` and `EXECUTION_ENGINE_TOKEN: ${EXECUTION_INTERNAL_TOKEN:-}` on the `api` service, which the worker already had and the panel now needs: the value in `.env.example` is a loopback URL that aims the API container at itself, and the token the engine validates is documented under a different name than the client reads, so without this the panel would report `unverified` on a healthy deployment - a wrong panel row being the exact failure this part was written against.",
    ),
    (
        "docs/SECURITY.md",
        "the `OPS_READ` bullet extended with what the panel actually shows, and section 14's \\"no tenantless command\\" claim amended to say *command* and name the one exempt read, its ordering, its bounds and the `/health/ready` superset invariant - a security document that stays accurate across a part that touched an auth boundary is the point of the cross-link, not a courtesy.",
    ),
    (
        "docs/ARCHITECTURE.md",
        "the engine section now names who reads `/internal/v1/status` (the worker's gate and the ops panel, one mirror, two consumers) and states that the panel adds no authority: it renders what the engine already published.",
    ),
    (
        "docs/GETTING_STARTED.md",
        "the operational tail's two commands and the posture curl, both run before being written down - which is why this document says `localhost:8093` for the engine (dev-run; the compose engine publishes no host port at all) and describes the panel as an authenticated route rather than inventing a curl for it, after an earlier draft named a port the API does not use.",
    ),
    (
        "docs/ROADMAP.md",
        "row 20, written from the diff rather than the intent: mirror, panel, generated schedule, and the defect the audit only found by running the composition - with the Python and compose files it moved counted, because a row that says \\"display only\\" over a commit that changed an auth boundary is how a roadmap stops being evidence.",
    ),
    (
        "docs/PART11_WORKER_SCALING.md",
        "section 7's `/status` bullet: the read is now token-scoped only, with the before/after failure recorded in place so a reader of the part that BUILT the gate learns that the gate could not boot.",
    ),
    (
        "docs/PART19_LIVE_ENABLEMENT.md",
        "section 8 points at the reader that Part 19 left without one - the enablement and placement facts published on `/status` now reach an operator, which is the difference between a refusal that is computable and one that is visible.",
    ),
    (
        "docs/DR.md",
        "the section headed 'What is NOT yet automated, plainly' still claimed this part's scheduler as remaining work, and `--check-rls` as unwired, so it now describes what shipped (derived schedule, `min(tightest cadence, 24h)` interval law, waivers echoed as comments with no job line, `--check-schedule` as the byte-exact drift gate that refuses `--record` as its own finding) and shrinks the open list to `crontab`, the drill calendar, and the first real `--record`. The heading is kept verbatim because Part 15's document links to it by name; a renamed section would turn a live document into a broken reference.",
    ),
    (
        "docs/PART15_RLS_ENABLEMENT.md",
        "one supersession note, in the style this repository uses for exactly this situation (Part 11's 'RESOLVED IN PART 13', Part 13's 'SUPERSEDES THE CAPABILITY, NOT THE LAW'): the bullet that named the scheduler as an open item now says Part 20 supplied the timer, while what Part 15 did - making the check exist and be honest enough to exit 1 - stands unchanged.",
    ),
    (
        ".env.example",
        "the engine-client block gained the second consumer and the two facts an operator needs with it: the pair is required by the worker's startup gate and read by the panel since Part 20, and with either name absent nothing fails - the module declines to construct a client and `ENGINE POSTURE` reports `unconfigured` - plus the warning that the file's own `127.0.0.1` URL is a developer's loopback that `docker-compose.yml` overrides per service. No new variable is declared, and none could be added by accident here: `dr-manifest.mjs::collectEnvNames` reads this file for `KEY=` lines (commented secrets included) to learn which names a deployment must provide, so prose edits are invisible to it by design while a new name would not be.",
    ),
]
'''
region("NEW: Final[list[tuple[str, str]]] = [\n", "ELISION_TOKENS: Final[tuple[str, ...]] = (", NEW_BLOCK + "\n")

# ---------------------------------------------------------------- gates
MEASURE = '''def measure() -> dict[str, object]:
    """Every gate the part must pass, executed now, parsed from its own
    output. A number that cannot be parsed is reported as 'UNPARSED', not
    defaulted to something flattering - this header is evidence, and
    evidence with a soft spot in it is the thing Part 15 exists to replace."""
    out: dict[str, object] = {}

    code, text = run(["python3", "-m", "pytest", "-q"], ROOT / "libs" / "trading-core")
    out["core_pytest"] = (last_match(r"(\\d+) passed", text) if code == 0 else f"FAILED: {text[-300:]}")
    out["core_pytest_code"] = code
    code, text = run(["python3", "-m", "ruff", "check", "wlct_trading", "tests"], ROOT / "libs" / "trading-core")
    out["core_ruff"] = "green" if code == 0 else text[-300:]
    # The core gate covers the library and its tests. The standalone fixture
    # generators under scripts/ are outside it by design (they must run with a
    # bare `python3` and no installed package, so their import order is
    # deliberate); counting their findings here keeps "green" from being read
    # as "whole directory swept".
    code, text = run(["python3", "-m", "ruff", "check", "scripts"], ROOT / "libs" / "trading-core")
    out["core_ruff_scripts"] = "0 findings" if code == 0 else (last_match(r"Found (\\d+) errors?", text) or "?") + " findings"
    code, text = run(["python3", "-m", "mypy", "wlct_trading"], ROOT / "libs" / "trading-core")
    out["core_mypy"] = last_match(r"no issues found in (\\d+) source files", text) or text[-160:]

    # "Zero suppression tokens" is a claim this header used to make by hand, over
    # Python only. Part 20 is a TypeScript part, so the scan covers `.py`, `.ts`,
    # `.tsx` and `.mjs` - over the files the part added and, separately, over the
    # files it only modified, because the modified ones carry pre-existing lines from
    # Parts 5/12/14 and a header reporting "0" by scanning only its own new files
    # would be measuring the flattering half.
    #
    # The one exclusion is this generator, computed from __file__ exactly as the sweep's
    # own marker list is: the tokens are its GUARD DATA, in a tuple, and a scan that
    # counted them would report "11 suppression tokens" for a file whose only sin is
    # naming what is forbidden. The first draft of this function had no exclusion and
    # printed precisely that, which is the reason the exemption is stated here rather
    # than slipped in - and the count below is independently confirmed against the
    # files themselves:
    #   grep -rn "type: ignore|noqa|eslint-disable|prettier-ignore|@ts-" <every file in both lists>
    # returns nothing at all.
    tokens = ("type: ignore", "noqa", "eslint-disable", "prettier-ignore", "@ts-ignore", "@ts-expect-error")
    guard_data = Path(__file__).resolve().relative_to(ROOT).as_posix() if "__file__" in globals() else "scripts/gen_part20_handover.py"

    def _count(entries: list[tuple[str, str]]) -> int:
        total = 0
        for rel, _note in entries:
            if rel == guard_data or not rel.endswith((".py", ".ts", ".tsx", ".mjs")):
                continue
            for line in (ROOT / rel).read_text(encoding="utf-8").splitlines():
                total += sum(1 for tok in tokens if tok in line)
        return total

    out["suppression_new"] = _count(NEW)
    out["suppression_modified"] = _count(MODIFIED)

    engine = ROOT / "services" / "execution-engine"
    code, text = run(
        ["python3", "-m", "pytest", "-q"],
        engine,
        {"PYTHONPATH": str(ROOT / "libs" / "trading-core")},
    )
    out["engine_pytest"] = (
        f"{last_match(r'(\\d+) passed', text)} passed, {last_match(r'(\\d+) skipped', text) or '0'} skipped"
        if code == 0
        else f"FAILED: {text[-300:]}"
    )
    code, text = run(["python3", "-m", "ruff", "check", "app", "tests"], engine)
    out["engine_ruff"] = "green" if code == 0 else text[-300:]
    code, text = run(
        ["python3", "-m", "mypy", "app"],
        engine,
        {"PYTHONPATH": str(ROOT / "libs" / "trading-core")},
    )
    out["engine_mypy"] = last_match(r"no issues found in (\\d+) source files", text) or text[-160:]
    # `mypy app` is the service's own gate and excludes tests, as it has since Part 11.
    # This part added a test file that reaches into a typed exception, so it is handed
    # to mypy directly here as well - the number below is the new file alone, and the
    # one known finding in `tests/conftest.py` was fixed rather than annotated away.
    code, text = run(
        ["python3", "-m", "mypy", "tests/test_part20_status_read.py"],
        engine,
        {"PYTHONPATH": str(ROOT / "libs" / "trading-core"), "MYPYPATH": str(ROOT / "libs" / "trading-core")},
    )
    out["engine_mypy_new_test"] = (
        "clean" if code == 0 else f"FAILED: {text[-200:]}"
    )
    code, text = run(
        ["python3", "-m", "pytest", "-q", "tests/test_part20_status_read.py"],
        engine,
        {"PYTHONPATH": str(ROOT / "libs" / "trading-core")},
    )
    out["engine_part20"] = (
        f"{last_match(r'(\\d+) passed', text)} passed"
        if code == 0
        else f"FAILED: {text[-300:]}"
    )

    code, text = run(["node", "--test", "scripts/"], ROOT)
    out["node_scripts"] = (
        f"{last_match(r'# pass (\\d+)', text)} passed / {last_match(r'# fail (\\d+)', text)} failed"
        if code == 0
        else f"FAILED: {text[-400:]}"
    )
    code, text = run(["node", "scripts/dr-manifest.mjs", "--check"], ROOT)
    out["manifest_check"] = text.strip().splitlines()[0] if code == 0 else f"FAILED: {text[-300:]}"
    code, text = run(["node", "scripts/dr-manifest.mjs", "--check-schedule"], ROOT)
    # The gate this part installed. Its full sentence is quoted rather than reduced to
    # "green", because the counts inside it (job lines, components) are the evidence that
    # the schedule was derived from the manifest and not typed under it.
    out["schedule_check"] = (
        "exit 0: " + text.strip().splitlines()[0]
        if code == 0
        else f"FAILED (exit {code}): {text[-300:]}"
    )
    code, text = run(["node", "scripts/dr-manifest.mjs", "--check-rls"], ROOT)
    # exit 1 here is the HONEST answer (no audit recorded yet in this repo),
    # so the text is quoted and the code explained, not smoothed over.
    out["check_rls"] = f"exit {code}: {text.strip().splitlines()[0]}" if text.strip() else f"exit {code}"

    api = ROOT / "apps" / "api"
    code, text = run(["npx", "jest", "--silent"], api)
    out["api_tests"] = (
        f"{last_match(r'Tests:\\s+(\\d+) passed', text)} passed / {last_match(r'Test Suites:\\s+(\\d+) passed', text)} suites"
        if code == 0
        else f"FAILED: {text[-400:]}"
    )
    # This part's three new API specs, run on their own: one number for all of them
    # would hide which of the mirror, the parity law or the panel broke.
    code, text = run(
        [
            "npx",
            "jest",
            "--silent",
            "src/modules/worker/engine-status-contract.spec.ts",
            "src/modules/worker/engine-status-parity.spec.ts",
            "src/modules/observability/engine-posture.service.spec.ts",
        ],
        api,
    )
    out["api_part20"] = (
        f"{last_match(r'Tests:\\s+(\\d+) passed', text)} passed / {last_match(r'Test Suites:\\s+(\\d+) passed', text)} suites"
        if code == 0
        else f"FAILED: {text[-400:]}"
    )
    code, text = run(["npx", "tsc", "-p", "tsconfig.json", "--noEmit"], api)
    out["api_typecheck"] = "0 errors" if code == 0 else f"FAILED: {text[-300:]}"
    # `prisma validate` resolves every env() reference before it will parse
    # the datasource, so it exits 1 in a checkout with no .env (correctly:
    # nothing is committed to satisfy it). The placeholders below are not
    # credentials - validation never opens a connection - and naming them here
    # is what keeps this gate reproducible on a fresh clone instead of a
    # command that only passes on the machine that happened to export a DSN.
    code, text = run(
        ["npx", "prisma", "validate", "--schema", "prisma/schema.prisma"],
        api,
        {
            "DATABASE_URL": "postgresql://validate:validate@localhost:5432/validate",
            "DIRECT_DATABASE_URL": "postgresql://validate:validate@localhost:5432/validate",
        },
    )
    out["prisma"] = "valid" if code == 0 else f"FAILED: {text[-200:]}"
    code, text = run(["npx", "eslint", "src", "--max-warnings", "0"], api)
    out["api_lint"] = "clean" if code == 0 else f"FAILED: {text[-400:]}"

    code, text = run(["npx", "tsc", "--noEmit"], ROOT / "apps" / "admin-web")
    out["admin_typecheck"] = "0 errors" if code == 0 else f"FAILED: {text[-300:]}"

    for service, name in (("trading-engine", "trading"), ("market-data", "market")):
        code, text = run(
            ["python3", "-m", "pytest", "-q"],
            ROOT / "services" / service,
            {"PYTHONPATH": str(ROOT / "libs" / "trading-core")},
        )
        out[f"{name}_service"] = (last_match(r"(\\d+) passed", text) if code == 0 else "FAILED") or "FAILED"

    out["tree"] = count_tree_lines()
    return out


'''
region("def measure() -> dict[str, object]:", "EXCLUDE_DIRS: Final[frozenset[str]] = frozenset(", MEASURE)

# ---------------------------------------------------------------- header
HEADER = '''HEADER_TEMPLATE = """
# Part 20 - the engine's own account, read; and the checker, run

> **What this part changed, and what it did not:** `/internal/v1/status` gained one strict
> TypeScript mirror and two consumers (the worker's startup gate keeps its assertions, the ops
> panel gains an `ENGINE POSTURE` section in which absence never reads as health); the DR
> obligations board gained the scheduler that `docs/DR.md` had only described, derived from the
> manifest's own cadences and drift-gated; and one defect the audit found by *running* the
> composition was fixed on the engine side, because a control that cannot boot is not a control -
> the internal tenant law is now scoped to **commands**, with one named read
> (`GET /internal/v1/status`) exempt and that exemption pinned to a single route by a test.
> **`EXECUTION_MODE=live` is still refused at startup, unchanged**; no gate, verdict,
> credential, order path or refusal threshold moved; no command route's requirements or refusal
> text changed; no metric, table, alert rule or console renderer was added. Three documents that
> still described this part's scheduler as missing (`docs/DR.md`, `docs/PART15_RLS_ENABLEMENT.md`,
> `.env.example`) are in the change set rather than left as stale prose, because a control shipped
> while being described as absent is a control nobody looks for; and sec. 5 of
> `docs/PART20_ENGINE_STATUS_EDGE.md` names nine refusals with their reasons - no engine health
> mirror, no worker-side placement gate, no published readiness gates, no console renderer, no
> restating open ROADMAP rows as finished, no Prometheus/Alertmanager rule files (`ALERT_RULES`
> carries prose conditions and `threshold: float | None`), no cron container, no change to
> `/health/ready`'s unauthenticated posture, and no configuration knob for the exempt read.

Complete content of every file created or modified by Part 20. Nothing is abbreviated,
quoted-with-ellipsis, or referred to by path: each block carries the whole current file, so this
document alone can be reviewed, diffed against an earlier part's handover, or used to
reconstruct the tree.

## Gates (run while this document was generated)

* `cd services/execution-engine && PYTHONPATH=../../libs/trading-core python3 -m pytest -q` ->
  **{engine_pytest}**. This part is the first since Part 13 to change behaviour at the engine's
  auth boundary, so the service's own suite is the interesting one: it was
  **409 passed, 12 skipped** before Part 20's file existed and moves by exactly that file's
  count - the 12 skips stay Parts 13-15's live-Postgres suites, skipping BY NAME without
  `EXECUTION_TEST_POSTGRES_DSN`. This part's file on its own -> **{engine_part20}**.
  `ruff check app tests` -> {engine_ruff}; `mypy app` -> no issues in **{engine_mypy} source
  files** (the same 24: two scopes were added inside existing modules, no new module);
  `mypy tests/test_part20_status_read.py` -> {engine_mypy_new_test}, which the service's gate
  does not cover because tests sit outside it, as in every part since Part 11.
* `cd apps/api && npx jest --silent` -> **{api_tests}**; this part's three specs on their own ->
  **{api_part20}**. `npx tsc -p tsconfig.json --noEmit` -> {api_typecheck};
  `npx eslint src --max-warnings 0` -> {api_lint}; `npx prisma validate` -> {prisma}. In
  `apps/admin-web`, `npx tsc --noEmit` -> {admin_typecheck}. The console renders no new field:
  `sections` is additive on the execution view and the admin web's table is untouched, so the
  panel section is reachable through the existing endpoint rather than by teaching a second UI
  to interpret engine facts.
* `cd libs/trading-core && python3 -m pytest -q` -> **{core_pytest}**, `ruff check wlct_trading
  tests` -> {core_ruff} ({core_ruff_scripts} in `libs/trading-core/scripts`, standalone by
  design), `mypy wlct_trading` -> no issues in **{core_mypy} source files**. The core is
  untouched by this part and these three numbers are here to prove it rather than to be
  admired: the mirror reads `schemas.py` as text and never imports Python, so a core change
  could not have been smuggled in. Sibling suites: trading-engine **{trading_service}**,
  market-data **{market_service}**, both untouched.
* `node --test scripts/` -> **{node_scripts}** (the 13 new schedule tests included);
  `node scripts/dr-manifest.mjs --check-schedule` -> {schedule_check};
  `node scripts/dr-manifest.mjs --check` -> {manifest_check}; `node scripts/dr-manifest.mjs
  --check-rls` -> {check_rls} - that exit 1 is the honest answer, no audit recorded yet, and
  unchanged by this part. No table was added, so RLS coverage stays at 43 and `PROBE_TABLES` at
  5, and the enablement audit remains owed by the operator rather than by this document.
* **Suppression tokens: {suppression_new} in the files Part 20 added and {suppression_modified}
  in the files it modified**, counted by this script over `.py`, `.ts`, `.tsx` and `.mjs`
  instead of asserted, and confirmed by an independent `grep` over the same 27 files. The scan
  was widened this part precisely because Part 19 could only count Python: a display layer is
  TypeScript, and a rule that measures the half it is convenient to measure is not a rule. The
  generator itself is excluded, because it stores the forbidden tokens as guard data - and that
  exclusion is the only one, so the {suppression_modified} covers real inherited lines in other
  parts' files rather than being smoothed away.

## Ledger

Measured at generation time, with code and documents counted separately because a tree-size
figure that mixes them is not a size. Part 20 shipped **{total:,} lines** - **{new_code:,}**
across the {new_code_count} new code files, **{new_docs:,}** in the {new_docs_count} new
document{new_docs_s}, and **+{mod_code:,}** code / **+{mod_docs:,}** document lines across the
{mod_count} modified files (each delta measured against the newest prior handover that lists
that file - which leaves {unbaselined_count} of them, {unbaselined_size} lines, with no delta at
all because no earlier document recorded their prior size: {unbaselined_list}. Their full text is
embedded below, and their size is not presented as a change). Whole-tree counts under the
standing rule set: **{tree_source:,} source lines**; adding the narrative documents under
`docs/` (the regenerable `docs/source/` views and every handover dump are out of both figures):
**{tree_with_docs:,}**.

Three provenance notes, because each is a sentence this part could have copied and should not.

* The header's deltas are small by construction, and the reason is this repository's own rule
  rather than a shortfall. A part's change set includes documents every earlier part also
  embedded, so the ancestors must be regenerated before this document is written (else they
  are stale, which `--check` reports as a failure); regenerating them moves the copies inside
  them forward to post-Part-20 text, which is the state the delta is then measured from. Parts
  16, 17, 18 and 19 were regenerated in that order first, and `--check` on any of the five
  reproduces what each prints. The un-regenerated figure - the same sweep taken before that
  chain, in `/home/user/part20_deltas_pre_regen.txt` - is **+799 delta lines and 2,362 new
  lines**, and that is the number to read as "what Part 20 typed"; the file list itself is
  identical in both, which is the part that actually has to be complete.
* The file lists are a derived diff, not a remembered one. With no VCS in the workspace the
  prior handovers are the snapshots: 26 files had moved since their last recorded state, 15
  carry Part 20 markers and are listed below, and the other eleven are named in this script's
  docstring with the part that actually left them changed (Part 10's SLO and tracing additions,
  never re-embedded) so that "not ours" is a checked statement rather than an excuse. The
  comparison must be fence-aware, because an embedded markdown document is fenced with four
  backticks and a three-backtick parser reports nine untouched documents as wholly rewritten.
* One behaviour change is not display. `GET /internal/v1/status` is answered under
  `require_internal_auth_readonly`; every other internal route is under `require_internal_auth`
  unchanged, the exemption is pinned by a route-table walk and by an HTTP sweep of the command
  routes, and `/health/ready` is asserted to keep publishing a superset of the same keys so the
  exemption discloses nothing new. `docs/PART20_ENGINE_STATUS_EDGE.md` sec. 7 carries the
  before/after measurements, including that this whole part was green (409 engine tests, 425 API
  tests, 65 script tests) while the reference worker could not start, because every test of that
  client stubs `fetch`.
"""

'''
region('HEADER_TEMPLATE = """', "def reflow_header(text: str) -> str:", HEADER + "\n")

# ---------------------------------------------------------------- main() plumbing
sub(
    "        engine_part19=measured[\"engine_part19\"],\n        core_part19=measured[\"core_part19\"],",
    "        engine_part20=measured[\"engine_part20\"],\n"
    "        engine_mypy_new_test=measured[\"engine_mypy_new_test\"],\n"
    "        api_part20=measured[\"api_part20\"],\n"
    "        schedule_check=measured[\"schedule_check\"],",
)
sub('parts = [reflow_header(header), "## Created in Part 19 (full files)\\n"]',
    'parts = [reflow_header(header), "## Created in Part 20 (full files)\\n"]')
sub('"## Modified in Part 19 (full files, prior content preserved inside)\\n"',
    '"## Modified in Part 20 (full files, prior content preserved inside)\\n"')
sub("""    ``measure`` returns one heterogeneous dict because it collects a dozen
    different gate outputs, and the tree entry is the only nested one. Narrowing
    it with ``isinstance`` here means the two ledger figures are checked rather
    than trusted, with no suppression comment to explain away - the generator is
    a new file in this part, and new files in this part carry none.""",
    """    ``measure`` returns one heterogeneous dict because it collects a dozen
    different gate outputs, and the tree entry is the only nested one. Narrowing
    it with ``isinstance`` here means the two ledger figures are checked rather
    than trusted, with no suppression comment to explain away - which is the same
    discipline Part 20 holds its own files to: this part's new and modified
    sources carry zero tokens, counted above rather than claimed.""")

DST.write_text(text, encoding="utf-8")
print(f"wrote {DST} ({len(text.splitlines())} lines)")
