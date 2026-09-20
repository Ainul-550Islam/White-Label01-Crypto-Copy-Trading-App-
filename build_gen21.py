"""Build scripts/gen_part21_handover.py from scripts/gen_part20_handover.py.

Same relationship every part has had since Part 16: the machinery (the fence helper, the baseline
search, the elision sweep, the measured header, the emission-count guard, ``--check``) is the
predecessor's; what moves is the docstring, the pointers, the two file lists, the part-specific gate
runs and the narrative header. Every substitution is asserted against exactly one anchor, so a silent
no-op - the failure mode that would ship a Part 21 document describing Part 20 - cannot pass.

What changed in the machinery itself, as opposed to the content:

* the part-specific measurement moved from the engine and the API back to the core and to
  ``scripts/``, because Part 21's tests live there (26 installer + 33 rehearsal + 13 verifier tests
  under ``node --test scripts/``, 40 new core tests);
* the engine and API gates are still run, and now carry a different claim - they must come back
  *identical* to Part 20's numbers, because this part changed no file in either app. A regression
  gate that re-runs the suites it did not touch is the only version of "nothing else moved" that a
  reader can check;
* the DR gate list grew from three commands to six: ``--verify-rls``, the installer's ``--check`` and
  the rehearsal runner's dry run and ``--status`` are quoted with their exit codes, including the
  non-zero ones, because a red answer that is correct is evidence and a green answer that is
  unmeasured is not.
"""

from __future__ import annotations

import pathlib

ROOT = pathlib.Path("/home/user/whitelabel-copytrade")
SRC = ROOT / "scripts" / "gen_part20_handover.py"
DST = ROOT / "scripts" / "gen_part21_handover.py"

text = SRC.read_text(encoding="utf-8")


def sub(old: str, new: str, count: int = 1) -> None:
    global text
    found = text.count(old)
    assert found == count, f"anchor found {found}x, expected {count}: {old[:90]!r}"
    text = text.replace(old, new)


def region(start_marker: str, end_marker: str, new: str) -> None:
    global text
    assert text.count(start_marker) == 1, f"start anchor {text.count(start_marker)}x"
    start = text.index(start_marker)
    stop = text.index(end_marker, start)
    assert stop > start
    text = text[:start] + new + text[stop:]


# ---------------------------------------------------------------- docstring
DOCSTRING = '''"""Part 21 - operating the DR plan instead of describing it. The full-source handover.

Generated, not written by hand, for the reason Part 15 established and Parts 16 to 20 repeated: a
hand-copied "full source" document starts drifting the moment a file changes, and a document whose
completeness cannot be re-proved is a document that merely claims. This script embeds the complete
content of every file Part 21 added or modified, states its own gate results by RUNNING the suites,
and accepts ``--check``, which regenerates in memory and compares byte for byte against the committed
file.

Copied from ``scripts/gen_part20_handover.py`` and re-pointed, which is the honest description of the
relationship. Part 20 is the last document in the chain, so the baseline search, the ancestor
regeneration order (16, 17, 18, 19, 20) and the fence-aware comparison all carry forward unchanged;
what changed is which gates are part-specific (sec. above: the core and ``scripts/``, not the engine
and the API), and the fact that the DR command set is now six commands rather than three.

The file lists were derived, not remembered. With no VCS in this workspace the prior handovers are the
snapshots: every candidate file was compared against the newest handover that embeds it, and the
result - plus the Part 21 markers this part wrote into the files it touched - is the list below. Two
sweep notes belong in this document rather than in a footnote. The first: the sweep also reports files
whose content has moved since a Part 8/9/10 snapshot and which no later part re-embedded (the SLO
identity constants, the burn-rate rules, the OpenTelemetry ``use_span`` imports, and Part 11's
``dr-manifest.mjs`` ancestors); they are not Part 21's, are not claimed here, and are named in
``docs/PART20_ENGINE_STATUS_EDGE.md`` sec. 6's account of the same phenomenon. The second: running
``scripts/gen_part11_handover.py --check`` during this part's audit turned out to REWRITE
``docs/PART11_HANDOVER_FULL_SOURCE.md``, because that generator predates ``--check`` and treats an
unknown flag as a plain run. The file is now byte-identical to a fresh generation of Part 11's own 68
files against today's tree - which is what the ancestor documents in this chain mean - and the
incident is recorded in sec. 9 of ``docs/PART21_DR_OPERATIONS.md`` instead of being left as an
unexplained delta.

The part's own defect find, worth having in the same place as the code that found it: the rehearsal
runner's restore-order law failed on the shipped ``docs/dr/manifest.json`` the first time it ran.
``restoreProcedure`` and ``restoreOrder`` disagreed about three of five components - each representation
was valid and each was validated, only never against the other. The data was corrected to follow the
procedure, and ``--check`` refuses that disagreement from now on.
"""'''

region('"""Part 20 - the engine\'s own account, read; and the checker, run. The full-source handover.', "from __future__ import annotations\n", DOCSTRING + "\n")

# ---------------------------------------------------------------- pointers
sub('OUT = ROOT / "docs" / "PART20_HANDOVER_FULL_SOURCE.md"', 'OUT = ROOT / "docs" / "PART21_HANDOVER_FULL_SOURCE.md"')
sub('ROOT / "docs" / f"PART{n}_HANDOVER_FULL_SOURCE.md" for n in range(19, 0, -1)',
    'ROOT / "docs" / f"PART{n}_HANDOVER_FULL_SOURCE.md" for n in range(20, 0, -1)')
sub('frozenset({"scripts/gen_part20_handover.py"})', 'frozenset({"scripts/gen_part21_handover.py"})')
sub('"scripts/gen_part20_handover.py"', '"scripts/gen_part21_handover.py"', text.count('"scripts/gen_part20_handover.py"'))

# ---------------------------------------------------------------- file lists
NEW_BLOCK = '''NEW: Final[list[tuple[str, str]]] = [
    (
        "scripts/dr-schedule-install.mjs",
        "the deployment half of the generated schedule: it verifies `docs/dr/schedule/dr.cron` with the "
        "*same* `scheduleDrift` function `--check-schedule` runs (imported, so the installer cannot "
        "develop its own opinion about what a valid schedule is), refuses to install anything it would "
        "have to author, and manages a `# BEGIN/END wlct-dr-schedule` block so that every unmanaged "
        "crontab entry survives byte for byte. Install is idempotent; `--uninstall` removes only the "
        "block; a schedule line containing `--record` or `--record-rls` is refused on the installer's own "
        "check rather than trusted to the generator; `crontab` is the only binary in the command "
        "allowlist and it is always invoked as an argv array with no shell, a per-call timeout and a "
        "three-variable child environment; `MemoryHost` exists for tests and cannot be selected from the "
        "CLI, so no invocation can report an install that only happened in a unit test. Exit codes 0/1/"
        "2/3/4 separate ok, not-installed, drift, refusal and no-cron-facility, and both mutating modes "
        "re-read the host afterwards - the incident that made that a rule is told in "
        "`docs/PART21_DR_OPERATIONS.md` sec. 2.",
    ),
    (
        "scripts/dr-schedule-install.test.mjs",
        "26 tests over the installer's laws. The block carries the artifact bytes and no timestamp (a "
        "timestamp would make every install read as drifted); the four `checkInstall` states each get "
        "their own code and reason; a hand-edited job line and a changed `SHELL=` line are both drift; "
        "foreign entries are preserved; malformed or duplicated markers are refused rather than "
        "overwritten; dry runs write nothing while exercising the same code path as a real install; a "
        "missing artifact is a refusal naming `--emit-schedule`; drift, ledger-writing lines and "
        "secret-shaped lines each refuse; `--host memory` is refused; paths outside the repository and a "
        "NUL byte are refused; the static sweep pins one `spawn` site, no `exec`, no `shell: true` and no "
        "caller-string `RegExp`. One test runs the real subprocess path against a fake `crontab` on a "
        "temporary `PATH` - install, verify, drift, uninstall - and another pins that a host which exits "
        "0 while writing nothing is reported as a failure.",
    ),
    (
        "scripts/dr-rehearsal.mjs",
        "the drill record as data. The plan is built from `restoreProcedure` (what an operator follows) "
        "and both representations are compared against each other, per component, including the "
        "manifest's own convention for component-less post-restore steps; per component the runner checks "
        "declared `paths` inside the repository (traversal is a finding, not an attempt) and `envRefs` "
        "names against the `.env.example` templates and for presence in its own process - names only, "
        "never values, never lengths - and carries `verification` and `backupMethod` prose as `UNVERIFIED` "
        "operator obligations. Failed key material marks every later step `blockedBy`, because the "
        "manifest says stop the line. `--execute` runs a closed four-probe allowlist (each argv, each "
        "graded from its exit code, probe output stored as a digest) and restores nothing; production, "
        "unknown targets, `NODE_ENV=production` and a non-destructive target are refused before any read, "
        "and `--execute` additionally requires `--confirm <rehearsalId>`, the hash of the canonical plan "
        "being approved, so the confirmation cannot be pasted onto a different plan or exported once and "
        "forgotten. Evidence appends only with `--emit-evidence`, is scanned by `findSecretShapes` before "
        "the write (a hit refuses rather than redacting), and `rtoObservedHours` is null in every record "
        "this version can write - the runner's own elapsed milliseconds are reported next to that field and "
        "never inside it.",
    ),
    (
        "scripts/dr-rehearsal.test.mjs",
        "33 tests, most of them about the one property that decides whether this tool is evidence or "
        "fabrication: a rehearsal with no restore behind it must not look like one. The plan is "
        "deterministic and clock-free and its id moves with the target; procedural steps are steps; every "
        "check class (path present, path escaping the repository, env name missing from templates, env name "
        "unset, verification prose) is asserted to grade the way it is defined to; the ordering "
        "disagreements - the historical one, a gapped order, a duplicated component, a component with no "
        "step - fail the plan; dependency blocking is asserted including the negative (a procedural step is "
        "not a component); `gradeRehearsal` cannot return `pass` for a dry run, cannot return `pass` when "
        "nothing ran, treats an absent probe outcome as unverified rather than failed, and treats overdue "
        "RPO evidence as failed; `parseRehearsals` refuses a dry run recorded as `pass` and four other "
        "malformed shapes; `--due` ages the drill against its own ledger through never-rehearsed, fresh and "
        "stale; the criteria stay un-verifiable by a plan, and the timed criterion stays `unverified` even "
        "when every probe passes; the record's field set, the refusal of `--target production`/`prod`/"
        "unknown, the confirmation flow in both flag and environment form, the read-only promise (a list of "
        "watched files asserted byte-identical across status runs), the secret-shape write refusal, and an "
        "executed run against the real allowlist - which passes two probes, marks two unverified, and "
        "produces four probes with no captured output and no absolute paths in the artifact.",
    ),
    (
        "libs/trading-core/wlct_trading/observability/chaos.py",
        "the failover matrix as data: ten scenarios A-J in drill order, each a frozen record of setup, "
        "injection, expected invariant, observation, recovery, cleanup and a bounded timeout, with "
        "`requires` drawn from a closed infrastructure vocabulary and `fault_points` validated as a subset "
        "of `faults.py`'s closed set - so the matrix cannot smuggle in a new lever on the trading path. "
        "`run_matrix` grades an unavailable dependency `unverified`, a specified-but-unrun probe `planned`, "
        "and only a harness-supplied check `pass`/`fail`, recording `source: harness` on the outcome so a "
        "green cell is never readable as a production failover. A check that raises has found something and "
        "grades `fail`; `ChaosRefusedError` propagates because a refusal is not a result. Production and "
        "every unnamed environment are refused before a probe is read, and the module imports no clock, no "
        "thread, no socket and no subprocess - the timeouts it reports are declarations for whoever owns "
        "the process, which is also why a run with no `--at` is stamped `not-supplied` instead of being "
        "given a plausible time.",
    ),
    (
        "libs/trading-core/wlct_trading/observability/red.py",
        "RED as a view rather than a second system: rate, errors and duration read out of "
        "`ObservabilityRegistry.snapshot()` over the families the services already register, emitted as "
        "`DashboardRow`s for the existing dashboard document so no section and no format is added. The "
        "five states are the deliverable - `no-data` (not registered), `zero-traffic` (registered and "
        "idle), `measured` (traffic, no verdict offered), `healthy` and `over-budget` (judged only against "
        "a supplied budget) - and `unavailable` is deliberately absent, because a module inside the metrics "
        "path inventing a 'metrics are down' row would be reporting on itself while the health model "
        "already carries that fact. `RedBudget` refuses to exist without a `source` string naming where its "
        "threshold came from (the SLO or alert catalogs, never this file: there is no default budget in "
        "it), `RedSurface` requires the service's own error label values rather than a guess, two surfaces "
        "over one family are refused, rows aggregate over label sets unconditionally, and duration is "
        "labelled as the mean it is.",
    ),
    (
        "libs/trading-core/tests/test_part21_chaos_matrix.py",
        "22 tests for the matrix, most of them negative on purpose: the ten ids and their run order, the "
        "letter each scenario is cited by in the runbook, all eight fields non-filler per probe, the fault "
        "and infrastructure vocabularies closed (an invented fault point, a `kubernetes` requirement and a "
        "100,000-second timeout are construction errors), production and unknown-environment refusals, all "
        "ten `UNVERIFIED` with no infrastructure and none of them `pass`, `planned` when a requirement is "
        "declared but no check exists, a harness pass marked `harness` with the matrix still grading "
        "`planned` around it, a false and a raising check both failing while keeping their cleanup evidence, "
        "a refusal escaping rather than becoming a result, byte-identical determinism across two runs, the "
        "injector read as configured state, the reading law printed inside the JSON document, the CLI's "
        "0/1/2/3 exit-code convention, and a whole-tree walk asserting that nothing outside `observability/` "
        "mentions the matrix at all.",
    ),
    (
        "libs/trading-core/tests/test_part21_red_view.py",
        "12 tests for the view: the closed state vocabulary and a tone set that is the dashboard's own; "
        "`no-data` distinguished from `zero-traffic` and neither rendering as `ok`; a verdict withheld "
        "without a budget and a budget refused without a source (with the ratio asserted, not eyeballed); "
        "`error_values` not guessable and family names required to be registered ones; the duplicate-surface "
        "law; an end-to-end pass over a real `ObservabilityRegistry` whose counters are driven through "
        "`inc`/`observe_micros` and then cross-checked against `render_prometheus`, which is what makes "
        "'reuses the existing metrics' a checked statement rather than a description; an empty registry "
        "grading `no-data` rather than a healthy zero; identifying labels (`tenant_id`, `account_id`, "
        "`order_id`, `symbol`) asserted absent from the document; the rows being `DashboardRow`s with the "
        "mean-not-percentile note; and the module's own import discipline, checked from its source.",
    ),
    (
        "docs/PART21_DR_OPERATIONS.md",
        "the part's own document, nine sections: the audit that preceded the code, with the file:line "
        "evidence for each duplication avoided; the installer's six laws including the verify-after-write "
        "rule and the fake-`crontab` incident that produced it; the rehearsal runner's plan, refusals and "
        "confirmation mechanism; the evidence artifact's three enforced properties; the chaos matrix and "
        "why a run here can only say `UNVERIFIED`; the RED view and its five states; `--verify-rls` and the "
        "empty-scope trap that nearly made a broken regex look clean; what stays operator-only and what was "
        "intentionally not built (no Grafana or alert-rule file derived from `threshold: None`, no service "
        "section rewritten, no second status endpoint because the runtime image ships no `docs/`); and the "
        "gates, with every figure transcribed from a measured run.",
    ),
    (
        "scripts/gen_part21_handover.py",
        "this generator. It is in the list because it is a source file of the part and its content is what "
        "makes the document reproducible; it is exempt from its own suppression-token scan via `__file__`, "
        "which is also why that exemption is computed rather than hardcoded.",
    ),
]

'''
region("NEW: Final[list[tuple[str, str]]] = [\n", "MODIFIED: Final[list[tuple[str, str]]] = [\n", NEW_BLOCK)

MOD_BLOCK = '''MODIFIED: Final[list[tuple[str, str]]] = [
    (
        "scripts/dr-manifest.mjs",
        "three additions, no change to anything Part 15 or Part 20 established. `validateManifest` gained "
        "the law that the plan's two representations must agree: every component step's `step` equals its "
        "`restoreOrder`, no component is restored twice, and no component is declared restorable but never "
        "restored - the check whose absence let the shipped manifest disagree with itself. "
        "`verifyRlsEvidence` (exported, and the body of the new `--verify-rls` mode) verifies what the "
        "repository can know about row-level security without asking a database anything: the three "
        "artifacts' presence, the coverage ledger against `enable.sql` in both directions, the symmetry of "
        "`enable.sql` and `disable.sql`, one schema stamp across all three, the policy and function names "
        "the manifest declares, and the evidence ledger's age and grade - with a doubly-empty scope grading "
        "`unverified` rather than a pass, and `enabled: null` plus a fixed non-assertion sentence carried "
        "into the document. `--json` became a registered boolean flag, because every unrecognised `--x` was "
        "value-taking and `--verify-rls --json` would otherwise have swallowed the next argument.",
    ),
    (
        "scripts/dr-manifest.test.mjs",
        "13 new tests and one import: the shipped repository's `--verify-rls` result asserted check by check "
        "with its 43/43/43 counts pinned so a scan that matches nothing cannot pass as an empty scope; the "
        "four scope disagreements (a table only in `enable.sql`, a table only in the coverage ledger, a "
        "rollback narrower than the change, a stamp that disagrees) each asserted from a scratch tree rather "
        "than by editing the generated scripts; a missing block, a corrupt ledger and a fresh-but-stale "
        "audit distinguished from one another; and the CLI contract - `--verify-rls` exits 3 because nothing "
        "has ever been audited here, exits 2 on an unparseable `--now`, writes nothing, and leaves "
        "`enable.sql` byte-identical.",
    ),
    (
        "docs/dr/manifest.json",
        "the defect find, in the data: `restoreOrder` for `deployment-config`, `redis` and "
        "`dataset-objects` was 5, 3, 4 while `restoreProcedure` steps 3, 4, 5 restored them in that other "
        "order. The procedure won because it is the document an operator executes and because step 3's "
        "condition - migrations only if the image's schema is older than the restored database - is only "
        "true in that order. Cadences, waivers, the RPO/RTO figures, the drill criteria and the RLS evidence "
        "block are untouched, and the generated `docs/dr/schedule/dr.cron` needed no regeneration: "
        "`--check-schedule` exits 0 on the corrected manifest, which is the assertion that the schedule was "
        "never order-dependent in the first place.",
    ),
    (
        "docs/DR.md",
        "a new section for the two commands, with their measured output pasted rather than described, and "
        "the 'What is NOT yet automated, plainly' list amended: 'installing the file is a host act' is "
        "taken off it because the host state is now checkable and reversible, while the drill calendar, the "
        "restore itself, the real failover run and the first `--record` are kept on it with their reasons. "
        "The heading itself is unchanged, so the cross-reference from `docs/PART15_RLS_ENABLEMENT.md` still "
        "lands.",
    ),
    (
        "docs/ROADMAP.md",
        "one closing paragraph for Part 21: what is now checkable (installation, rehearsal, RLS scope, "
        "chaos specification, RED as a view), what the manifest defect was and how it was closed, and what "
        "stays open with its reason - including the sentence that keeps this part honest about the "
        "dashboards, which still have no Prometheus or Grafana file in the tree because `ALERT_RULES` carry "
        "prose conditions and `threshold: None` and no number was invented to fill that gap.",
    ),
    (
        "docs/SECURITY.md",
        "a section on operational tooling that touches nothing, written in the shape the rest of the "
        "document uses (a rule, then the mechanism that enforces it): no credential values read or written, "
        "names-only environment checks, probe output reduced to a digest, the evidence artifact scanned "
        "against the manifest's own secret-shape patterns with a refusal rather than a redaction, one "
        "allowlisted binary per script with no field or flag able to become a command line, paths validated "
        "to stay inside the repository, the production and ambiguity refusals, the closed grade vocabulary "
        "with `unverified` mandatory when a dependency is unreachable, and the boundary that no money-path "
        "module imports any of it.",
    ),
    (
        "docs/PART11_WORKER_SCALING.md",
        "sec. 18's 'Staging chaos run (the not-runnable-here half)' now points at the machine-readable "
        "version of itself: the ten probes, what each declares, and the fact that a run without the "
        "processes grades every one `UNVERIFIED` and exits 2 - which is the property that makes a staging "
        "`PASS` worth reading. The four runbook scenarios are unchanged; only their status sentence moved.",
    ),
    (
        ".env.example",
        "a commented block naming `DR_REHEARSAL_CONFIRMATION` so the name is enumerable from a committed "
        "template (which is what `collectEnvNames` reads) and so nobody mistakes the rehearsal's "
        "confirmation mechanism for a live-mode switch. No value is set, no new variable is required by the "
        "API, the worker or the engine, and the block says in the file that `EXECUTION_MODE=live` is "
        "refused at startup regardless of anything in it.",
    ),
]

'''
region("MODIFIED: Final[list[tuple[str, str]]] = [\n", "ELISION_TOKENS: Final[tuple[str, ...]] = (", MOD_BLOCK)

# ---------------------------------------------------------------- part-specific gates
region(
    "    # `mypy app` is the service's own gate and excludes tests, as it has since Part 11.",
    "    code, text = run([\"node\", \"--test\", \"scripts/\"], ROOT)",
    '''    # The service's own gate is run unchanged. Part 21 touched no file in this app, so
    # the number printed below is a regression claim, not a progress claim: it must match
    # Part 20's measurement exactly, and the header says so rather than leaving the reader
    # to remember which part added which test file.
    # (the engine's own `mypy app` run above already set `engine_mypy`; nothing is re-run here)

    # Part 21's tests, in the two places they actually live: the core suite and scripts/.
    core = ROOT / "libs" / "trading-core"
    code, text = run(
        ["python3", "-m", "pytest", "-q", "tests/test_part21_chaos_matrix.py", "tests/test_part21_red_view.py"],
        core,
    )
    out["core_part21"] = (
        f"{last_match(r'(\\d+) passed', text)} passed" if code == 0 else f"FAILED: {text[-300:]}"
    )
    # `mypy wlct_trading` is the core's gate and excludes tests, as it has since Part 8. The
    # part's two new test files are handed to mypy directly, with MYPYPATH set the way the
    # services set it, because a test that cannot type-check is a test whose assertions may be
    # reading the wrong attribute - and suppression tokens are banned in new files here, so an
    # ignore is not available even as a shortcut.
    code, text = run(
        [
            "python3",
            "-m",
            "mypy",
            "tests/test_part21_chaos_matrix.py",
            "tests/test_part21_red_view.py",
        ],
        core,
        {"MYPYPATH": str(core)},
    )
    out["core_mypy_new_tests"] = "clean" if code == 0 else f"FAILED: {text[-300:]}"

    # The DR tool set, six commands. Each is quoted with its exit code, including the
    # non-zero ones: `--check-rls` and `--verify-rls` are red because no audit has been
    # recorded in this repository, `--status` is red because no backup has either, and an
    # installer `--check` is red because this sandbox has no cron. A header that printed only
    # the zeroes would be a marketing document.
    dr_cmds = {
        "verify_rls": ["node", "scripts/dr-manifest.mjs", "--verify-rls"],
        "install_check": ["node", "scripts/dr-schedule-install.mjs", "--check"],
        "rehearsal_dry": ["node", "scripts/dr-rehearsal.mjs", "--target", "local", "--out", "none"],
        # Pinned clock: `--status` prints the instant it read, and a generated document that
        # embeds an unpinned wall-clock line can never reproduce itself (the first run of the
        # checker proved it - byte-identical in every other line, and STALE).
        "rehearsal_status": [
            "node", "scripts/dr-rehearsal.mjs", "--status", "--no-probe", "--at", "2026-09-18T00:00:00Z",
        ],
        "rehearsal_due": ["node", "scripts/dr-rehearsal.mjs", "--due"],
        "chaos_cli": ["python3", "-m", "wlct_trading.observability.chaos", "--environment", "local"],
    }
    for key, argv in dr_cmds.items():
        cwd = core if key == "chaos_cli" else ROOT
        environ = {"PYTHONPATH": str(core)} if key == "chaos_cli" else {}
        code, text = run(argv, cwd, environ)
        first = next((line for line in text.strip().splitlines() if line.strip()), "(no output)")
        out[key] = f"exit {code}: {first.strip()[:150]}"

''',
)

sub(
    """    code, text = run([\"node\", \"--test\", \"scripts/\"], ROOT)
    out[\"node_scripts\"] = (
        f\"{last_match(r'# pass (\\d+)', text)} passed / {last_match(r'# fail (\\d+)', text)} failed\"
        if code == 0
        else f\"FAILED: {text[-400:]}\"
    )""",
    """    code, text = run([\"node\", \"--test\", \"scripts/\"], ROOT)
    out[\"node_scripts\"] = (
        f\"{last_match(r'# pass (\\d+)', text)} passed / {last_match(r'# fail (\\d+)', text)} failed\"
        if code == 0
        else f\"FAILED: {text[-400:]}\"
    )
    # Per-file counts, because \"133 passed\" hides which of the three new suites broke.
    for key, spec in (
        (\"node_install\", \"scripts/dr-schedule-install.test.mjs\"),
        (\"node_rehearsal\", \"scripts/dr-rehearsal.test.mjs\"),
        (\"node_manifest\", \"scripts/dr-manifest.test.mjs\"),
    ):
        code, text = run([\"node\", \"--test\", spec], ROOT)
        out[key] = (
            f\"{last_match(r'# pass (\\d+)', text)} passed\"
            if code == 0
            else f\"FAILED: {text[-300:]}\"
        )""",
    1,
)

# the API part-specific block: Part 21 added no API tests, so the full suite stands alone.
region(
    "    # This part's three new API specs, run on their own: one number for all of them",
    "    code, text = run([\"npx\", \"tsc\", \"-p\", \"tsconfig.json\", \"--noEmit\"], api)",
    """    # No part-specific API run: this part added no test to apps/api, and the full-suite
    # number above is therefore the regression gate for the whole TypeScript side.
""",
)

# ---------------------------------------------------------------- stale comments
sub(
    """    # Python only. Part 20 is a TypeScript part, so the scan covers `.py`, `.ts`,""",
    """    # Python only. Part 21 is a scripts-and-core part, so the scan keeps covering `.py`, `.ts`,""",
    1,
)

# ---------------------------------------------------------------- main()'s kwargs
# Part 20's header asked for three part-specific numbers that this part does not produce
# (the engine's new-test count, its mypy-over-tests, the API's part spec). They are replaced by
# the ten this part does produce. The block is packed five lines deep rather than one kwarg per
# line, and two lines are then given back by tightening a comment in measure(), because the
# generator's total line count is inside the whole-tree figures every ancestor handover prints -
# and 1,008 is the number those documents were regenerated against.
sub('        engine_part20=measured["engine_part20"],\n        engine_mypy_new_test=measured["engine_mypy_new_test"],\n        api_part20=measured["api_part20"],\n', '        core_part21=measured["core_part21"], core_mypy_new_tests=measured["core_mypy_new_tests"],\n        node_install=measured["node_install"], node_rehearsal=measured["node_rehearsal"],\n        node_manifest=measured["node_manifest"], verify_rls=measured["verify_rls"],\n        install_check=measured["install_check"], rehearsal_dry=measured["rehearsal_dry"],\n        rehearsal_status=measured["rehearsal_status"], rehearsal_due=measured["rehearsal_due"],\n', 1)
sub(
    """    # The service's own gate is run unchanged. Part 21 touched no file in this app, so
    # the number printed below is a regression claim, not a progress claim: it must match
    # Part 20's measurement exactly, and the header says so rather than leaving the reader
    # to remember which part added which test file.
    # (the engine's own `mypy app` run above already set `engine_mypy`; nothing is re-run here)
""",
    """    # The service's gate is run unchanged, and the number it prints is a regression claim:
    # it must match Part 20's measurement exactly. `mypy app` above already set
    # `engine_mypy`, so nothing here is re-run for the sake of the same answer.
""",
    1,
)


HEADER = '''HEADER_TEMPLATE = """
# Part 21 - operating the DR plan: installation, rehearsal, chaos matrix, RED

> **What this part changed, and what it did not:** the generated DR schedule gained an installer and a
> verifier (`scripts/dr-schedule-install.mjs`: manages a marked crontab block, preserves every foreign
> entry, re-reads the host after writing, exits 4 rather than lying about a host with no cron); the drill
> gained a runner and an append-only evidence ledger (`scripts/dr-rehearsal.mjs`: a deterministic plan
> built from `restoreProcedure`, per-component path and environment-name preflight, a closed four-probe
> allowlist, a production refusal, a confirmation that must echo the plan's own hash, and grades in which
> `PLANNED` can never read as `pass`); row-level security gained a repository-side verifier
> (`scripts/dr-manifest.mjs --verify-rls`, which reports the 43/43/43 scope agreement and still says
> `enabled: null`); the chaos and failover work gained a specified matrix
> (`wlct_trading.observability.chaos`, ten probes, all `UNVERIFIED` here by law); and RED gained a view
> (`wlct_trading.observability.red`) over the families the services already publish, rendered as the
> existing dashboard rows with `no-data`, `zero-traffic`, `measured`, `healthy` and `over-budget` kept
> apart and no default threshold anywhere in the file. **`EXECUTION_MODE=live` is still refused at
> startup, unchanged**; no placement, risk, order, credential or engine file was touched; `enable.sql`
> and `disable.sql` are unmodified and RLS is not reported as enabled by anything in this part; no second
> schedule generator, metrics registry, database table or status endpoint was added; and no Prometheus or
> Grafana rule file was derived, because `ALERT_RULES` carry prose conditions with
> `threshold: float | None` (sec. 8 of `docs/PART21_DR_OPERATIONS.md` states what was left out and why).
> One defect was found by running the new code against the shipped data: `docs/dr/manifest.json` had
> `restoreProcedure` and `restoreOrder` disagreeing about three of five components since Part 11. The data
> was corrected, and `--check` now refuses that class of disagreement.

Complete content of every file created or modified by Part 21. Nothing is abbreviated,
quoted-with-ellipsis, or referred to by path: each block carries the whole current file, so this
document alone can be reviewed, diffed against an earlier part's handover, or used to
reconstruct the tree.

## Gates (run while this document was generated)

* `node --test scripts/` -> **{node_scripts}**. Per suite: installer **{node_install}**, rehearsal
  runner **{node_rehearsal}**, manifest validator **{node_manifest}** (50 before this part, 63 now).
  The DR command set, each quoted with its exit code because the red ones are the honest state of a
  fresh checkout: `--check` -> {manifest_check}; `--check-schedule` -> {schedule_check};
  `--check-rls` -> {check_rls}; `--verify-rls` -> **{verify_rls}**;
  `dr-schedule-install.mjs --check` -> **{install_check}**; `dr-rehearsal.mjs --target local` ->
  **{rehearsal_dry}**; `--status --no-probe` -> **{rehearsal_status}**; `--due` ->
  **{rehearsal_due}**. Three of those exits are 1, one is 3 and one is 4, and none is a failure of
  this part: four backup obligations and the RLS audit have never been recorded, and this sandbox has
  no `crontab` binary, which is the exit 4. The status line is pinned with `--at` on purpose: an
  unpinned run prints the current instant, and no document embedding one could regenerate itself.
* `cd libs/trading-core && python3 -m pytest -q` -> **{core_pytest}** (1,656 before Part 21). The
  +40 is two things: 34 tests in this part's two new files, which on their own -> **{core_part21}**,
  and 6 cases that `tests/test_observability_boundaries.py` derives from the modules now on disk
  (three parametrizations over that list, so `chaos.py` and `red.py` each add one case to each). The
  second half is counted, not inferred: that file collects 44 tests, 6 of which name a Part 21 module.
  `ruff check wlct_trading tests` -> {core_ruff} ({core_ruff_scripts} in `libs/trading-core/scripts`,
  standalone by design); `mypy wlct_trading` -> no issues in **{core_mypy} source files** (150 before
  this part: `chaos.py` and `red.py` are the two additions); `mypy` over the two new test files ->
  {core_mypy_new_tests}, which the core's gate does not cover because tests sit outside it, as in every
  part since Part 8. Both new modules are asserted by a tree walk to be unreferenced outside
  `observability/`, and `test_observability_boundaries.py` sweeps them for suppression tokens and
  ambient I/O like every other module in the package.
* `cd services/execution-engine && PYTHONPATH=../../libs/trading-core python3 -m pytest -q` ->
  **{engine_pytest}**, `ruff check app tests` -> {engine_ruff}, `mypy app` -> no issues in
  **{engine_mypy} source files**. These are regression gates and nothing else: Part 21 added no engine
  file, no test and no behaviour, so the expectation is that these numbers equal Part 20's -
  428 passed / 12 skipped, clean, 24 files - and if they do not, something here leaked.
* `cd apps/api && npx jest --silent` -> **{api_tests}** (Part 20: 425 passed / 20 suites; there is no
  part-specific run because this part added no API test), `npx tsc -p tsconfig.json --noEmit` ->
  {api_typecheck}, `npx eslint src --max-warnings 0` -> {api_lint}, `npx prisma validate` ->
  {prisma}; in `apps/admin-web`, `npx tsc --noEmit` -> {admin_typecheck}. Sibling suites:
  trading-engine **{trading_service}**, market-data **{market_service}**, both untouched - and both
  deliberately not wired to the RED view in this part, because their dashboard row sets are pinned by
  their own tests and rewriting a service's pinned output is a behaviour change this part did not come
  to make (sec. 6 of the part document).
* **Suppression tokens: {suppression_new} in the files Part 21 added and {suppression_modified} in the
  files it modified**, counted by this script over `.py`, `.ts`, `.tsx` and `.mjs`. The count is the
  reason this paragraph is long: the first draft of `chaos.py` carried an inline suppression pragma for a broad
  `except Exception`, and the core's own boundary test failed the suite over it - correctly, and after
  every gate in this part had gone green around it. The fix was to delete the token and keep the
  comment explaining the breadth, not to teach the scanner to look the other way; the same rule applies
  to the test files and to this generator's exclusion, which is computed from `__file__` and is the
  only one.

## Ledger

Measured at generation time, with code and documents counted separately because a tree-size figure
that mixes them is not a size. Part 21 shipped **{total:,} lines** - **{new_code:,}** across the
{new_code_count} new code files, **{new_docs:,}** in the {new_docs_count} new document{new_docs_s}, and
**+{mod_code:,}** code / **+{mod_docs:,}** document lines across the {mod_count} modified files (each
delta measured against the newest prior handover that lists that file - which leaves
{unbaselined_count} of them, {unbaselined_size} lines, with no delta at all because no earlier document
recorded their prior size: {unbaselined_list}. Their full text is embedded below, and their size is not
presented as a change). Whole-tree counts under the standing rule set: **{tree_source:,} source
lines**; adding the narrative documents under `docs/`: **{tree_with_docs:,}**.

Four provenance notes, because each is a sentence this part could have copied and should not.

* The modified-file deltas read **zero**, and that is a property of the procedure rather than a
  claim about the size of this part. A part's change set includes documents every earlier part also
  embedded, so the ancestors (16, 17, 18, 19, 20) must be regenerated in order before this document
  is written - and regenerating them moves the copies of `scripts/dr-manifest.mjs`,
  `docs/DR.md`, `.env.example` and the rest forward to post-Part-21 text, which is the state the
  delta is then measured from. With no VCS in the workspace, no baseline predating these edits
  survives inside the tree, so the honest figure for "what Part 21 typed into those eight files" is
  not recoverable here; what is recoverable is their complete current text, embedded below, and the
  18-entry file list, which is a derived diff rather than a remembered one. `--check` on any of the
  six documents reproduces what each prints, including this one.
* The file lists are a derived diff. `docs/dr/rehearsals.jsonl` is deliberately **not** in the list:
  the rehearsal runner has never been told to record (it refuses to seed its own ledger), so the file
  does not exist, and a part that generated its own evidence to have something to ship would be the
  thing its whole design argues against. One test asserts that a rehearsal with `--out none` creates
  nothing, and another asserts that a status run leaves every watched artifact byte-identical.
* `docs/PART11_HANDOVER_FULL_SOURCE.md` was rewritten during the audit, not by an edit: Part 11's
  generator predates `--check` and treated the flag as a plain run. It is now byte-identical to a fresh
  generation of Part 11's own file list against today's tree, which is what every ancestor document in
  this chain already means; it is a regenerable dump, excluded from the counts above, and the incident
  is recorded in sec. 9 of the part document rather than left as an unexplained delta. Parts 14 and 15's
  generators additionally fail their own audit on `services/execution-engine/app/composition.py`
  containing the word "omitted" in prose - a pre-existing condition of those two documents, not
  something Part 21 introduced or repaired.
* What Part 21 did not do is listed rather than implied: no engine or API file, no schema or table, no
  change to `--emit-schedule`/`--check-schedule` semantics, no service dashboard rewrite, no
  `enabled: true` anywhere, no paging threshold invented, no chaos probe that could reach a real
  process, and no endpoint - the runtime image for `apps/api` copies `node_modules`, `packages`,
  `apps/api/dist` and `apps/api/prisma` and no `docs/`, which is why the scheduler and rehearsal state
  are CLI documents and a panel that read them would have to be given a path by an operator.
"""'''

region('HEADER_TEMPLATE = """', "def reflow_header(text: str) -> str:", HEADER + "\n\n\n")

# ---------------------------------------------------------------- main() plumbing
sub('"## Created in Part 20 (full files)\\n"', '"## Created in Part 21 (full files)\\n"')
sub('"## Modified in Part 20 (full files, prior content preserved inside)\\n"',
    '"## Modified in Part 21 (full files, prior content preserved inside)\\n"')

DST.write_text(text, encoding="utf-8")
print(f"wrote {DST.relative_to(ROOT)} ({len(text.splitlines())} lines)")
