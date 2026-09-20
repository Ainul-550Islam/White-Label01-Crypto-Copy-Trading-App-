"""Build scripts/gen_part22_handover.py from scripts/gen_part21_handover.py.

Copied-and-re-pointed is the honest description of the relationship, exactly as Parts 17 to 21 each
described theirs. Every substitution below asserts it matched exactly once, so a stale anchor - the one
way a derived generator can silently ship the previous part's document - fails the build rather than
passing as a no-op.

Run:  python3 /home/user/build_gen22.py
Then: cd whitelabel-copytrade && python3 scripts/gen_part22_handover.py --emit  (and --check)
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("/home/user/whitelabel-copytrade")
SRC = ROOT / "scripts" / "gen_part21_handover.py"
DST = ROOT / "scripts" / "gen_part22_handover.py"

text = SRC.read_text(encoding="utf-8")
subs: list[str] = []


def sub(old: str, new: str, count: int = 1) -> None:
    global text
    found = text.count(old)
    if found != count:
        raise SystemExit(f"ANCHOR MATCHED {found} TIMES (wanted {count}):\n{old[:400]}")
    text = text.replace(old, new, count)
    subs.append(old.splitlines()[0][:60])


def block_span(start_marker: str, end_marker: str) -> tuple[int, int]:
    i = text.index(start_marker)
    j = text.index(end_marker, i)
    return i, j


def replace_block(start_marker: str, end_marker: str, replacement: str) -> None:
    """Swap a whole top-level assignment by its boundaries, avoiding re-typing anchors."""
    global text
    i, j = block_span(start_marker, end_marker)
    text = text[:i] + replacement + text[j:]
    subs.append(f"BLOCK {start_marker[:40]}")


# ----------------------------------------------------------------- the mechanical renames
sub(
    'OUT = ROOT / "docs" / "PART21_HANDOVER_FULL_SOURCE.md"',
    'OUT = ROOT / "docs" / "PART22_HANDOVER_FULL_SOURCE.md"',
)
sub(
    '    ROOT / "docs" / f"PART{n}_HANDOVER_FULL_SOURCE.md" for n in range(20, 0, -1)',
    '    ROOT / "docs" / f"PART{n}_HANDOVER_FULL_SOURCE.md" for n in range(21, 0, -1)',
)
sub(
    '    else frozenset({"scripts/gen_part21_handover.py"})',
    '    else frozenset({"scripts/gen_part22_handover.py"})',
)
# Every remaining reference to the ancestor generator is a fallback path or a comment, and all of
# them point at this script from here on. Counted rather than assumed, because "0 replaced" is how a
# derived generator keeps describing the part above it.
leftovers = text.count('"scripts/gen_part21_handover.py"')
if leftovers == 0:
    raise SystemExit("no leftover generator references; the rename anchors already covered them")
text = text.replace('"scripts/gen_part21_handover.py"', '"scripts/gen_part22_handover.py"')
subs.append(f"{leftovers} leftover generator references re-pointed")

# --------------------------------------------------------------------- the module docstring
docstring = '''"""Part 22 - the deployment side of telemetry, generated from the side that publishes it.

Generated, not written by hand, for the reason Part 15 established and Parts 16 to 21 repeated: a
hand-copied "full source" document starts drifting the moment a file changes, and a document whose
completeness cannot be re-proved is a document that merely claims. This script embeds the complete
content of every file Part 22 added or modified, states its own gate results by RUNNING the suites,
and accepts ``--check``, which regenerates in memory and compares byte for byte against the committed
file.

Copied from ``scripts/gen_part21_handover.py`` and re-pointed. The baseline search, the ancestor
regeneration order (16, 17, 18, 19, 20, 21) and the fence-aware comparison all carry forward unchanged;
what changed is which gates are part-specific (the bundle's own ``--check``/``--emit``/``--rules``, plus
the core suite, with the DR tool set and the TypeScript side kept as unchanged regression gates), and
the fact that the file list now includes four files under ``infrastructure/`` that this document embeds
*and* that a script in this repository renders on demand - which is the property the embedded text is
there to prove.

The file lists were derived, not remembered. With no VCS in this workspace the prior handovers are the
snapshots: every candidate file was compared against the newest handover that embeds it, and the
result - plus the Part 22 sentences this part wrote into the three documents it amended - is the list
below. Two sweep notes belong here rather than in a footnote. The first: the sweep also reports files
whose content has moved since a Part 8/9/10 snapshot and which no later part re-embedded (the SLO
identity constants, the burn-rate rules, the OpenTelemetry ``use_span`` imports, and Part 11's
``dr-manifest.mjs`` ancestors); they are not Part 22's, are not claimed here, and are named in
``docs/PART20_ENGINE_STATUS_EDGE.md`` sec. 6's account of the same phenomenon. The second: every
ancestor document in this chain embeds a copy of ``docs/ROADMAP.md``, ``docs/PART21_DR_OPERATIONS.md``
and ``.env.example``, all three of which this part amended, so the ancestors are regenerated first and
the modified-file deltas below are measured against post-Part-22 text. That is what makes the delta
column zero, and the sentence saying so is in the ledger rather than hidden under it.

One incident belongs in the same place as the code that caused it, because this part's whole subject is
a generator that must not touch what it describes: while a test helper was being written, a symlink tree
was assembled in the wrong order and a "temporary" patched copy of
``services/market-data/app/routers/observability.py`` was written through a symlink into the repository.
The file was restored to the single line its three sibling routers use, the service's 19 tests pass,
``--check`` agrees with the tree again, and the ordering law that would have prevented it is now a
docstring in the helper (sec. 7 of ``docs/PART22_SCRAPE_SIDE.md``).
"""'''
i = text.index('"""Part 21 -')
j = text.index('"""\nfrom __future__ import annotations') + len('"""')
text = text[:i] + docstring + text[j:]
subs.append("MODULE DOCSTRING")

# ---------------------------------------------------------------------------- the NEW list
new_list = '''NEW: Final[list[tuple[str, str]]] = [
    (
        "libs/trading-core/scripts/gen_observability_bundle.py",
        "the generator, the verifier and the reader, in one file: six audits run before any artifact is "
        "returned (`assert_no_invented_numbers`, which compares every numeric literal in an `expr:` "
        "against the `allowed_numbers` the rule DECLARES rather than against the expression it just "
        "rendered, so a rule cannot widen its own allowance; `assert_no_invented_cadence`, which refuses "
        "`scrape_interval`, `evaluation_interval`, `scrape_timeout`, `honor_labels`, `for:`, `interval:` "
        "and `keep_firing_for:` because this repository declares no cadence and no dwell policy; "
        "`assert_no_secret_shapes`; `assert_labels_are_not_invented`, which reads the config's non-comment "
        "lines so that the header explaining an absence cannot trip the check for it; "
        "`assert_job_regex_matches_every_target`, which evaluates the availability alert's regex the way "
        "Prometheus anchors it and thereby caught a real defect during authoring; and "
        "`assert_only_catalog_labels`, which walks the label blocks at rule depth instead of the whole "
        "file), a target discovery step that reads `docker-compose.yml` and each service's own "
        "route declaration (each service's own metrics path in its router), through a hand-rolled "
        "scanner with no YAML dependency, a rules "
        "deriver that renders 4 of the 24 catalog alerts and names the reason for the other 20, the "
        "catalog document with per-field evidence, `--emit` (which plans every write before performing "
        "any and exits 3 rather than overwriting a file it did not generate), and `--dashboard`, which "
        "parses exposition text strictly enough to hand it to the repository's own `DashboardBuilder` "
        "instead of inventing a second dashboard format.",
    ),
    (
        "libs/trading-core/tests/test_part22_scrape_bundle.py",
        "41 tests, most of them assertions that an audit objects: the committed bundle byte-identical to "
        "a fresh render (the test that makes every other line here reviewable) and `--check` writing "
        "nothing; the 4/20 census summing to `len(ALERT_RULES)` so a rule cannot be dropped silently; "
        "each threshold cross-checked against the `AlertRule` it came from, including the ppm scaling and "
        "the inverted `<=` a remaining-budget gauge requires; a smuggled `14400001` refused with the "
        "rule's allowance emptied; a planted `interval:`, a planted token literal, a planted `external_labels` "
        "block and a fourth rule label each raising; `up{job=~...}` evaluated against every job name and "
        "again with the parentheses removed; a compose port moved 8001 to 8111 in a scratch tree and the "
        "generated job following it; a router whose `/metrics` line was removed and the target, the "
        "catalog entry and the availability regex all disappearing with it; exclusion evidence asserted to "
        "be paths that exist; eight mutations of the hand-written overlay each producing exactly the one "
        "message that describes it while the committed file produces none and its comment about the "
        "lifecycle flag does not count as the flag; `--emit` refusing a foreign file with exit 3 and "
        "writing nothing anywhere; a real `ObservabilityRegistry` rendered by `render_prometheus` and "
        "parsed back with counters, histogram buckets, `le`-as-geometry and the service label all "
        "reconstructing the snapshot, with garbage lines, a `summary` type, a `_sum` suffix on a counter, "
        "an oversize file, a NUL byte and an empty pipe each refused; the absence census pinned to the "
        "strict name set so a runtime-built family is never claimed absent; the CLI's exit codes run as "
        "subprocesses because a documented contract that was never executed is a description; and the "
        "generator itself scanned for `socket`/`subprocess`/`yaml` imports - the tool must not reach the "
        "network, and that is a property of the file rather than of one run of it.",
    ),
    (
        "infrastructure/observability/prometheus/prometheus.yml",
        "four scrape jobs and nothing else: `${PROMETHEUS_PATH}` for the API because that is what its "
        "config service reads, literal `/metrics` for the three Python services because that is what "
        "their routers declare, the scrape-token header as an expansion rather than as a value, and "
        "no `scrape_interval`, no `external_labels`, no relabeling. Generated; the header says "
        "so and names the file that regenerates it.",
    ),
    (
        "infrastructure/observability/prometheus/rules/wlct.rules.yml",
        "two groups. `wlct-slo` holds the three burn-rate and budget alerts whose every literal is the "
        "catalog's, and `wlct-platform` holds `TELEMETRY_EXPORT_FAILING`; then `wlct-availability` holds "
        "the one rule that is not in the catalog - the availability rule over every job's `up` series, "
        "whose only literal is the zero that defines a failed scrape, present because a "
        "rule in the catalog is silent while its own target is unreachable, and silence "
        "health is the failure mode four earlier documents name. No `for:` and no group `interval:` "
        "anywhere; the twenty refusals are listed in the header with their reasons, so the file cannot be "
        "read as a complete paging policy.",
    ),
    (
        "infrastructure/observability/metrics-catalog.json",
        "the same facts as data: the four targets with `portEvidence` and `pathEvidence` pointing at the "
        "compose line and the router decorator each came from, the three services not scraped with the "
        "reason and an evidence path, the per-service `familiesNamedInSource` counts named for what they "
        "are (a literal scan, not a statement about an endpoint), the image pin with the minimum version "
        "`http_headers` needs, `cadence` as two `null`s with the sentence explaining why they are null, "
        "the rendered rules with their evidence strings, the refusals, and a `notIncluded` block naming "
        "Alertmanager, Grafana JSON, the OpenTelemetry collector, node-exporter and RED-over-scraped-text "
        "with the reason for each absence.",
    ),
    (
        "infrastructure/observability/README.md",
        "the operator's page for the directory: the three commands, their exit-code ladder quoted from "
        "the implementation, the curl-and-pipe one-liner for `--dashboard` with the note that this tool "
        "never performs the curl, the deploy line for the overlay, what is scraped and what is not, and a "
        "boundary section - not a monitoring product, observes nothing, cannot change a trading decision, "
        "holds no credential, and if Prometheus is switched off nothing about trading changes.",
    ),
    (
        "docker-compose.observability.yml",
        "the one hand-written file in the set, because it is a deployment choice rather than a rendering: "
        "`prom/prometheus:v3.5.0` pinned (the config uses `http_headers`, which needs >= 2.53, and "
        "`latest` is a tag that can change a format underneath a committed file), the bundle mounted "
        "read-only at `/etc/prometheus`, the TSDB on a named volume, `127.0.0.1:${PROMETHEUS_PORT:-9090}` "
        "and nothing else published, `wlct-internal`, no `--web.enable-lifecycle`, no retention flag and "
        "no cadence, plus a banner listing the five things it deliberately does not add with the reason "
        "for each. `--check` reads it back structurally, so that banner cannot trip its own check.",
    ),
    (
        "docs/PART22_SCRAPE_SIDE.md",
        "the part's own document, eight sections: the law every artifact is held to, the six audits and "
        "what each one refuses; how the four targets were derived and which three were named absent with "
        "evidence; the 4-of-24 census with the ppm scaling, the inverted comparison and the single "
        "non-catalog rule each argued; the overlay's eight laws; `--dashboard` and why an unreadable line "
        "is a refusal rather than a skip; the two family-name sets and the two different harms that "
        "justify keeping them apart; the measured gates with their exact outputs; and the verification edge "
        "stated plainly - no Prometheus binary has ever read this config, because this sandbox has no "
        "`docker` CLI, and `promtool` on a real host is the referee this part cannot appoint.",
    ),
    (
        "scripts/gen_part22_handover.py",
        "this generator. It is in the list because it is a source file of the part and its content is what "
        "makes the document reproducible; it is exempt from its own suppression-token scan via `__file__`, "
        "which is also why that exemption is computed rather than hardcoded.",
    ),
]

'''
replace_block("NEW: Final[list[tuple[str, str]]] = [", "\nMODIFIED: Final[list[tuple[str, str]]] = [", new_list)

# ------------------------------------------------------------------------ the MODIFIED list
mod_list = '''MODIFIED: Final[list[tuple[str, str]]] = [
    (
        "docs/ROADMAP.md",
        "two edits, not one. The Part 21 paragraph's closing clause claimed the dashboards 'still have no "
        "Grafana/Prometheus file in this tree'; that became false while this part was running, and a "
        "roadmap that overstates an absence is as wrong as one that restates an open row as finished, so "
        "the sentence was amended to say what Part 22 took and what the 17 `threshold: None` rules still "
        "refuse to give. Then a Part 22 paragraph, in the shape Part 20 and Part 21 used: the four jobs "
        "and where each came from, the audits, the census, the overlay's constraints, the four things not "
        "built, and the container that was never run.",
    ),
    (
        "docs/PART21_DR_OPERATIONS.md",
        "sec. 8's 'Grafana/Prometheus files, and a derived alert-rule file' bullet was the part's own "
        "record of what it left undone, and Part 22 did half of it. The bullet now separates the two "
        "halves instead of being deleted: the Grafana and paging objections still hold (no datasource UID "
        "exists here, and the application owns the alert lifecycle), while the Prometheus half points at "
        "the generated bundle and records that the fabricated-number objection was the right objection - "
        "the answer was to derive only what already had a number, which is why 20 of 24 rules are "
        "refusals rather than expressions.",
    ),
    (
        "docs/PART20_ENGINE_STATUS_EDGE.md",
        "the same class of correction, one sentence: Part 20 had written that there is 'no "
        "`infrastructure/observability/` to write it into', and there is now. The paragraph is annotated "
        "rather than rewritten, because the arithmetic objection two lines above it is the one that still "
        "matters and the document should not be made to look prescient after the fact.",
    ),
    (
        ".env.example",
        "one new name, `PROMETHEUS_PORT`, beside `PROMETHEUS_PATH` in the observability block, with the "
        "comment saying that the optional overlay is its only reader and that 9090 is the image's own "
        "default. Nothing else moved: `METRICS_TOKEN` and `PROMETHEUS_PATH` were already documented as "
        "the deployment's, which is the reason the generated config could name them as expansions instead "
        "of inventing values, and no file in this part contains a credential to begin with.",
    ),
    (
        "README.md",
        "the repository tree in the root README enumerated `infrastructure/` as `docker/` plus "
        "`database/`, a sentence Part 20 relied on and Part 22 made false. The enumeration now "
        "lists `observability/`, and the `docker-compose.yml` line says plainly that an optional "
        "overlay layers on it, because a diagram that lists every child of a directory has to keep "
        "listing them. README.md carries no line-count delta in the ledger below for a reason worth "
        "stating: no earlier handover embedded the root README, so no prior size exists to subtract, "
        "and the part's own document keeps that gap visible instead of rounding it to zero.",
    ),
]

'''
replace_block(
    "MODIFIED: Final[list[tuple[str, str]]] = [",
    "\nELISION_TOKENS: Final[tuple[str, ...]] = (",
    mod_list,
)

# ------------------------------------------------------------------------ measure(): the gates
old_gates = '''    # Part 21's tests, in the two places they actually live: the core suite and scripts/.
    core = ROOT / "libs" / "trading-core"
    code, text = run(
        ["python3", "-m", "pytest", "-q", "tests/test_part21_chaos_matrix.py", "tests/test_part21_red_view.py"],
        core,
    )
    out["core_part21"] = (
        f"{last_match(r'(\\d+) passed', text)} passed" if code == 0 else f"FAILED: {text[-300:]}"
    )'''
new_gates = '''    # Part 22's tests, in the one place they live: the core suite.
    core = ROOT / "libs" / "trading-core"
    code, text = run(
        ["python3", "-m", "pytest", "-q", "tests/test_part22_scrape_bundle.py"],
        core,
    )
    out["core_part22"] = (
        f"{last_match(r'(\\d+) passed', text)} passed" if code == 0 else f"FAILED: {text[-300:]}"
    )
    # The bundle's own contract, run as its CLI runs it, because the claim "the committed deployment
    # files match a fresh render" is the one the rest of this part rests on. `--emit` is included and is
    # expected to write nothing: it is idempotent against an in-sync tree, so the line counts below are
    # evidence that the two commands agree with each other and not only with the generator. The census
    # is counted out of `--rules`' own text rather than asserted from this script's memory.
    tool = "libs/trading-core/scripts/gen_observability_bundle.py"
    for key, argv in (
        ("bundle_check", ["--check"]),
        ("bundle_emit", ["--emit"]),
        ("bundle_recheck", ["--check"]),
        ("bundle_rules", ["--rules"]),
        ("bundle_catalog", ["--catalog"]),
    ):
        code, text = run(["python3", tool, *argv], ROOT)
        body = text.strip().splitlines()
        tail = body[-1] if body else "no output"
        if key == "bundle_rules":
            tail = f"{text.count('rendered ')} rendered, {text.count('refused ')} refused"
        elif key == "bundle_catalog":
            tail = (body[0] if body else "no output") + f" ({len(body)} lines printed)"
        elif key == "bundle_emit":
            writes = sum(1 for line in body if line.startswith("wrote"))
            tail = f"{len(body) - writes} unchanged, {writes} written"
        out[key] = f"exit {code}: {tail[:160]}"'''
sub(old_gates, new_gates)
sub(
    '''            "tests/test_part21_chaos_matrix.py",
            "tests/test_part21_red_view.py",''',
    '''            "tests/test_part22_scrape_bundle.py",''',
)

# --------------------------------------------------------------------------- HEADER_TEMPLATE
header = '''HEADER_TEMPLATE = """
# Part 22 - the scrape side: one reader, one generated bundle, nothing invented

> **What this part changed, and what it did not:** the deployment half of Part 18's telemetry boundary
> became files in the tree. `libs/trading-core/scripts/gen_observability_bundle.py` renders
> `infrastructure/observability/` - a Prometheus scrape config (four jobs, `${{PROMETHEUS_PATH}}` plus the
> API's `x-metrics-token` header for the API and literal `/metrics` for the three Python services, no
> cadence and no relabeling anywhere), a rule file (4 of the 24 `ALERT_RULES` entries, every literal in
> them attributable to the rule it came from, plus the one availability rule the catalog cannot express),
> a catalog document carrying evidence field by field, and a README; `docker-compose.observability.yml`
> adds exactly one service, `prom/prometheus:v3.5.0`, mounted read-only, published on loopback, with no
> lifecycle endpoint and no retention flag. **The 20 rules that did not render are named in both the
> rules file and the catalog, each with its reason** (17 carry `threshold: None`, 3 name a unit no
> registered family in this tree exposes), because a rules file is where an invented number goes to look
> official. **`EXECUTION_MODE=live` is still refused at startup, unchanged**; no engine, API, worker,
> schema, migration, risk or placement file was touched; no metric, family, label, alert rule, SLO or
> fault point was added anywhere in `wlct_trading/`; no Alertmanager, Grafana provisioning, collector,
> exporter or second dashboard format was introduced; and the platform's behaviour with this bundle
> switched off is exactly its behaviour before Part 22, since nothing in the trading path imports any of
> it (docs/PART22_SCRAPE_SIDE.md states the laws and the refusals).

Complete content of every file created or modified by Part 22. Nothing is abbreviated,
quoted-with-ellipsis, or referred to by path: each block carries the whole current file, so this
document alone can be reviewed, diffed against an earlier part's handover, or used to
reconstruct the tree.

## Gates (run while this document was generated)

* The bundle's own contract, executed as its CLI executes it: `--check` -> **{bundle_check}**; then
  `--emit` -> **{bundle_emit}**; then `--check` again -> **{bundle_recheck}**. The middle command writes
  nothing when the tree is in sync, and "unchanged, 0 written" is the whole point of running it inside a
  document that claims reproducibility. `--rules` -> **{bundle_rules}** (the census, counted from the
  command's own output rather than from a number remembered here), and `--catalog` -> **{bundle_catalog}**.
* `cd libs/trading-core && python3 -m pytest -q` -> **{core_pytest}** (1,696 before Part 22; the +41 is
  this part's file alone, which on its own -> **{core_part22}**, and `tests/test_observability_boundaries.py`
  derives no cases from anything here because no module in `wlct_trading/` was added). `ruff check
  wlct_trading tests` -> {core_ruff}; `ruff check scripts` -> {core_ruff_scripts} in
  `libs/trading-core/scripts`, of which exactly one belongs to this part: a single `E402` for the import
  that must follow the `sys.path` bootstrap, the same finding every sibling standalone script already
  carries, left unsuppressed because suppression tokens are refused in new files here - so the figure
  above is what a reviewer sees, not what an audit hides. `mypy wlct_trading` -> no issues in
  **{core_mypy} source files** (152 before this part and 152 now: nothing in the package changed);
  `mypy` over the new test file -> {core_mypy_new_tests}, which the core's gate does not cover because
  tests sit outside it, as in every part since Part 8.
* `cd services/execution-engine && PYTHONPATH=../../libs/trading-core python3 -m pytest -q` ->
  **{engine_pytest}**, `ruff check app tests` -> {engine_ruff}, `mypy app` -> no issues in
  **{engine_mypy} source files**. Regression gates and nothing else: Part 22 added no engine file, no
  test and no behaviour, so the expectation is that these numbers equal Part 21's - 428 passed / 12
  skipped, clean, 24 files - and if they do not, something here leaked.
* `cd apps/api && npx jest --silent` -> **{api_tests}** (Part 21: 425 passed / 20 suites; no
  part-specific run because this part added no API test), `npx tsc -p tsconfig.json --noEmit` ->
  {api_typecheck}, `npx eslint src --max-warnings 0` -> {api_lint}, `npx prisma validate` ->
  {prisma}; in `apps/admin-web`, `npx tsc --noEmit` -> {admin_typecheck}. Sibling suites: trading-engine
  **{trading_service}**, market-data **{market_service}**. The market-data number matters more here than
  it looks: a test helper wrote through a symlink into that service's `observability.py` while this part
  was being written, the file was restored to the one line its three siblings use, and these 19 tests are
  the check that the restoration is behaviourally identical rather than merely plausible.
* `node --test scripts/` -> **{node_scripts}** (installer **{node_install}**, rehearsal runner
  **{node_rehearsal}**, manifest validator **{node_manifest}**) and the DR command set, unchanged by this
  part and re-run as a regression gate because three of its documents were amended: `--check` ->
  {manifest_check}; `--check-schedule` -> {schedule_check}; `--check-rls` -> {check_rls}; `--verify-rls`
  -> **{verify_rls}**; `dr-schedule-install.mjs --check` -> **{install_check}**;
  `dr-rehearsal.mjs --target local` -> **{rehearsal_dry}**; `--status --no-out --no-probe` ->
  **{rehearsal_status}**; `--due` -> **{rehearsal_due}**. The non-zero exits are the honest state of a
  fresh checkout (no backup recorded, no RLS audit recorded, no `crontab` binary in this sandbox) and the
  status line is pinned with `--at` for the same reason this document pins a clock: an unpinned run
  prints the instant it read, and a generated document that embedded one could never regenerate itself.
* **Suppression tokens: {suppression_new} in the files Part 22 added and {suppression_modified} in the
  files it modified**, counted by this script over `.py`, `.ts`, `.tsx` and `.mjs`. The generator's own
  exclusion is computed from `__file__`, exactly as in every part since Part 16, and is the only one.
  This part earned the paragraph the hard way: the first draft of the new test file asserted that the
  generator contains no `noqa`-class tokens by *naming* them, which is itself a new file containing the
  token, and the part's audit failed on the test written to prevent exactly that. The tokens are now
  spelled by concatenation, which keeps the assertion real and keeps the file clean; the earlier
  instance of the same trap is on record in sec. 7 of ``docs/PART21_DR_OPERATIONS.md``.

## Ledger

Measured at generation time, with code and documents counted separately because a tree-size figure
that mixes them is not a size. Part 22 shipped **{total:,} lines** - **{new_code:,}** across the
{new_code_count} new code files, **{new_docs:,}** in the {new_docs_count} new document{new_docs_s}, and
**+{mod_code:,}** code / **+{mod_docs:,}** document lines across the {mod_count} modified files (each
delta measured against the newest prior handover that lists that file - which leaves
{unbaselined_count} of them, {unbaselined_size} lines, with no delta at all because no earlier document
recorded their prior size: {unbaselined_list}. Their full text is embedded below, and their size is not
presented as a change). Whole-tree counts under the standing rule set: **{tree_source:,} source
lines**; adding the narrative documents under `docs/`: **{tree_with_docs:,}**.

Three provenance notes, because each is a sentence this part could have copied and should not.

* The modified-file deltas read **zero**, and that is a property of the procedure rather than of the
  size of the change. The ancestors (16, 17, 18, 19, 20, 21) are regenerated in order before this
  document is written, because each embeds its own copy of `docs/ROADMAP.md`, `.env.example`,
  `docs/PART21_DR_OPERATIONS.md` and `docs/PART20_ENGINE_STATUS_EDGE.md`; regenerating them moves those
  copies forward to post-Part-22 text, which is the state the deltas are then measured from. With no VCS
  in the workspace, no baseline predating these edits survives inside the tree, so the honest figure for
  "what Part 22 typed into those four files" is not recoverable here; what is recoverable is their
  complete current text, embedded below, and the 14-entry file list, which is a derived diff rather than
  a remembered one. `--check` on any of the seven documents reproduces what each prints, including this
  one.
* Four of the files above - `prometheus.yml`, `wlct.rules.yml`, `metrics-catalog.json` and the directory
  `README.md` - are themselves generated, by a script in this part, from files outside that directory.
  They are embedded anyway, because the claim being documented is not "the generator can print these"
  but "these exact bytes are what the generator prints from the tree as it stands", and only the
  rendered text can be compared against a host's copy. The test suite checks that equality on every
  run; this document makes it inspectable without running anything.
* What Part 22 did not do is listed rather than implied: no `promtool` or `docker compose config`
  verification (this sandbox has no `docker` CLI, so no Prometheus binary has ever read these files, and
  `promtool` on a real host remains the referee - the part document says so in its own section rather
  than leaving it to be inferred); no Alertmanager, no paging, no receiver routing, because the
  application already owns the alert lifecycle and a second store of the same alerts is a second truth to
  reconcile; no Grafana JSON, no datasource, no panel layout, and no cadence - the format this repository
  owns is the section/row document, which `--dashboard` renders from scraped exposition with a strict-name
  absence census printed beside it; no time-series retention policy, because Part 14's retention law is
  about the execution store's tables and nothing in this tree declares one for a monitoring volume; no
  scrape of `notification-service`, `worker` or `admin-web`, each refused in writing with an evidence path
  rather than omitted; and no invented threshold for the 17 catalog rules that have none.
"""


'''
i = text.index('HEADER_TEMPLATE = """')
j = text.index('\n\ndef ', text.index('reproduces what each prints, including this one.'))
text = text[:i] + header + text[j + 2:]
subs.append("HEADER_TEMPLATE")

# ------------------------------------------------------------------ main(): the format kwargs
sub(
    "    header = HEADER_TEMPLATE.format(\n",
    "    header = HEADER_TEMPLATE.format(\n        **measured,\n",
    1,
)
drop = re.compile(r"\n^        [a-z_0-9]+=measured\[\"[a-z_0-9]+\"\],(?: [a-z_0-9]+=measured\[\"[a-z_0-9]+\"\],)*$", re.M)
text, dropped = drop.subn("", text)
if dropped < 1:
    raise SystemExit("no measured[...] kwargs were removed; the format call is not what this build expects")
subs.append(f"format kwargs -> **measured ({dropped} lines dropped)")

sub('    parts = [reflow_header(header), "## Created in Part 21 (full files)\\n"]',
    '    parts = [reflow_header(header), "## Created in Part 22 (full files)\\n"]')
sub('    parts.append("## Modified in Part 21 (full files, prior content preserved inside)\\n")',
    '    parts.append("## Modified in Part 22 (full files, prior content preserved inside)\\n")')

# ------------------------------------------------- stale cross-references inside retained prose
sub(
"    # it must match Part 20's measurement exactly. `mypy app` above already set",
"    # it must match Part 21's measurement exactly. `mypy app` above already set",
)

# A retained comment that still credits the part above this one with the reason the token scan
# covers four languages. Re-pointing it keeps the generator's own prose true about this part.
sub(
    "    # Python only. Part 21 is a scripts-and-core part, so the scan keeps covering",
    "    # Python only. Part 22 is a scripts-and-core part too, so the scan keeps covering",
)

DST.write_text(text, encoding="utf-8")
print(f"wrote {DST.relative_to(ROOT)} ({len(text.splitlines())} lines) via {len(subs)} substitutions")
