# Part 20 audit — the operational tail's one missing edge

Audit-first record for the part, with the file:line evidence each claim was taken from.
Nothing here is a plan of intent; every line is a fact checked against the tree after Part 19.

## The finding

The execution engine is the only service in the platform whose operational posture nobody reads.

1. It publishes a typed posture document: `services/execution-engine/app/routers/internal.py:50`
   (`GET /internal/v1/status`), schema `StatusResponse` in `app/schemas.py`, 20 fields, every one
   of them camelCased through `_to_camel`, model config `extra="forbid"`.
2. It has no metrics-to-Redis mirror, no background loop, no Redis client at all: grep for
   `redis|REDIS` in `services/execution-engine/app/*.py` returns nothing, and the lifespan
   (`app/main.py:55-97`) starts no task. This is by design, not an omission: Part 18 chose
   scrape-time-only instruments, and `OBS_PUBLISHER_SERVICES`
   (`packages/config/src/constants.ts:155-158`) lists only `market-data` and `trading-engine`,
   the two services that publish `wlct:trading:ops:health:<service>`
   (`services/market-data/app/observability.py:384-412`, `services/trading-engine/app/observability.py:592`).
3. The single reader of that document is the worker's client,
   `apps/api/src/modules/worker/engine-internal.client.ts:155-186`. It hand-picks 9 of the 20
   keys (`instanceId, mode, dryRun, adapter, store, storeDurable, storeBackend, locksDistributed,
   commands`) and reads each with `body.X ?? ''` / `?? []` / `=== true`.
   The 11 it drops: `credentialSource`, `credentialFetcher`, `operatorConfirmation`,
   `liveEnablement`, `placement`, `incidents`, `metricsConfigured`, `retentionEnabled`,
   `retentionEventDays`, `enablementMaxAgeDays`, `simulated`.
4. Nobody else reads it. `getStatus` has exactly one caller, `apps/api/src/worker.ts:69`, once, at
   startup, for the compatibility gate. The comment at `engine-internal.client.ts:116-117` calls the
   10 s cache "only for the periodic health view" — there is no periodic health view; nothing
   consumes the cache after startup. So the phrase describes a view that was never built.
5. The operator's execution panel is built from other people's data:
   `apps/api/src/modules/observability/observability.service.ts:156` (`executionPanel`) shows
   the readiness gate `execution_adapter` — whose evidence comes from the TRADING engine
   (`services/trading-engine/app/observability.py:670`), the open-incident count, and a 24 h order
   status mix. None of it is what the execution engine says about itself.

Consequence, stated plainly: eleven facts the platform spends Parts 13-19 computing — whether a
credential reader exists, whether an operator confirmation is wired, what the live-enablement
grading came back as, whether the process is instrumented at all, whether its incident sink is
durable — are published and then dropped on the floor at the only boundary that reads them.

## What is NOT the gap (rejected, with the reason)

* Publishing the engine to the Redis health mirror. It would need a Redis client in a service
  that deliberately has none, plus a background task the process does not otherwise run, in
  order to copy facts the process already answers on request. That is a second copy of a truth,
  which is the failure mode this platform has refused since Part 8. The reader goes to the author.
* A worker-side placement gate keyed on `placement.requiresVenueAttestation` /
  `policy.requireOperatorConfirmation`. Rejected because it makes things worse: the ack law
  (`engine-internal.client.ts:130-146`) says a business rejection counts as DONE so that the
  durable order record and its refusal reason survive. Refusing before forwarding instead would
  turn a recorded, tenant-visible refusal into a queue retry with no record.
* Enabling the engine's readiness gates via `ops_readiness_mirror`
  (`libs/trading-core/wlct_trading/redis_keys.py:355-362`, "an execution worker can later publish
  its own gates"). That seam stays unclimbed by choice: it would let a displayed fact start
  blocking trading, i.e. a silent behaviour change in the money path. It is named here so the
  next reader finds the decision instead of re-deriving it.
* Time-series retention behind the exposition, RED dashboards beyond the panel, the chaos matrix
  against real infrastructure, and the `--record-rls` staging audit: all four need a deployment,
  not a commit. They stay open, with their wording preserved in
  `docs/ROADMAP.md:198-221`, so the deliberate non-absorption is not mistaken for oversight.

## The one code-able piece of the operational tail

`docs/ROADMAP.md:221` still carries: "the backup item is deployment-side WIRING of that command into a
scheduler — the ledger refuses to fake its own seed data, so the first real `--record` is the first
real backup evidence." The checking mechanism exists (`node scripts/dr-manifest.mjs --due`,
`scripts/dr-manifest.mjs:693` mode list, cadences in `docs/dr/manifest.json`); what does not exist
is the schedule itself, so `--due` runs only when a human remembers it. Emitting it from the
manifest is the fix, and the artifact must be generated rather than hand-written because a
hand-written cron is a copy of the cadence table that can disagree with it.

Law the emitter has to keep: it may emit a job that CHECKS and a job that reports, never a job that
writes ledger evidence, because `--record` without an outcome is exactly the faked seed data the
ledger refuses to contain.

## Part 20 = three changes

1. **Strict, complete status mirror** in `apps/api/src/modules/worker/engine-internal.client.ts`:
   all 20 keys typed; the keys the Python model declares REQUIRED refuse a missing or mis-typed
   value with a terminal `EngineCallError` naming the key (a contract violation must not be
   defaulted into a decision), and the keys the Python model declares with a DEFAULT keep their
   documented meaning ("an engine too old to answer"), which is the same convention
   `StatusResponse` sets for `storeBackend` at `app/schemas.py`.
   Behaviour change, deliberate and stated: a mis-shaped `/status` reply now fails the worker's
   startup gate instead of proceeding on defaults.
2. **The operator's edge**: `executionPanel` gains an ENGINE section rendered by the same parser
   through one new read service, `unverified` (never `ok`) when the engine did not answer, with the
   age of the answer shown. No new engine fields, no new endpoints, no admin-web change (the
   console renders `overview`, `trading-readiness`, `alerts`, `incidents` —
   `apps/admin-web/src/app/(console)/observability/page.tsx:146-149` — and the panel sections are
   the documented API-side ops surface, as in Parts 9 and 18).
3. **`--emit-schedule` / `--check-schedule`** in `scripts/dr-manifest.mjs`, writing
   `docs/dr/schedule/dr.cron` from the manifest cadences, with a drift gate in the same style as
   `--check`, refusals for components with no cadence, and no ledger-writing job emitted.

Plus the law that keeps the hole from coming back: a parity spec that parses `StatusResponse` out
of the engine's `app/schemas.py` (precedent: the Python-source scan at
`apps/api/src/modules/datasets/datasets-safety.spec.ts:228` and the live catalog scan described in
`apps/api/src/modules/observability/alert.constants.ts:4-8`) and asserts the TS mirror covers every
field and reproduces every default. The engine already pins `describe()` against the schema
(`app/schemas.py` PlacementStatusView docstring: "the counterpart test in the service suite asserts
the two key sets agree"); this closes the third side of the triangle.

## What actually shipped, and what the running of it found

The three changes above shipped, plus a fourth that this map could not have planned because it
only appears when the composition is executed rather than reasoned about.

1. `/internal/v1/status` is now reachable by its only caller. `app/security.py` splits into two
   scopes over one law (`_authenticate`, `_tenant_or_none`, `_request_id`,
   `TENANT_REQUIRED_CODE`, `require_internal_auth` unchanged in behaviour, new
   `require_internal_auth_readonly`); `app/routers/internal.py` uses the read scope on that one
   route, and `tests/test_part20_status_read.py` (19 tests) pins: tenantless 200 with exactly the
   20 contract keys, byte-identical to the tenant-bearing answer, 401 for every token failure
   BEFORE any tenant branch, 400 for a malformed-but-present tenant, the command scope's refusal
   sentence to the byte, the exemption to one route by walking `app.routes`, `TENANT_HEADER_REQUIRED`
   on every tenantless command route by HTTP sweep, and `/health/ready` staying a superset of
   `/status`. Measured on a booted engine, before: `400 TENANT_HEADER_REQUIRED` -> the worker's
   `assertEngineCompatible()` classed it retryable -> "execution engine gate failed" -> exit 1.
2. The mirror, the parity law and the panel shipped as planned (331/253/254/316/395-line files,
   16 + 5 + 18 tests). The two claims this map left unverified are now verified: the contract spec
   does pin `instanceId: null` as a refusal (`engine-status-contract.spec.ts:98-104`), and the API's
   port in the reference compose is `${API_PORT:-4000}:4000` - not 3001 - while the engine and the
   worker publish no host port at all, which is why `GETTING_STARTED` documents an engine dev-run
   curl on 8093 and describes the panel route instead of inventing a curl for it.
3. The schedule shipped (`docs/dr/schedule/dr.cron`, 3 job lines, waivers as comments, `--record`
   never emitted) with 13 script tests and `--manifest` as the only new knob.
4. `docker-compose.yml`: `EXECUTION_ENGINE_URL` / `EXECUTION_ENGINE_TOKEN` added to `api:` (the
   worker already had them), because `.env.example:966`'s loopback URL aims the API container at
   itself and the engine's token is documented under the name the engine validates, not the name
   the client reads. Validated by parsing the file and reading back the resolved environment
   (`docker` CLI is absent from this sandbox, so `docker compose config` was not run).

Final gates: engine 428 passed / 12 skipped, ruff clean, mypy 24 files clean, the new test file
mypy-clean when handed to mypy directly; API 425 passed / 20 suites, tsc 0, eslint clean, admin
tsc 0; `node --test scripts/` 65/65; `--check-schedule` exit 0; `--check` exit 0; `--due` exit 1
with 4 obligations DUE; core 1656, ruff green, mypy 150 files; siblings 43 and 19. Handovers 16,
17, 18, 19 and 20 all print `OK: ... byte-identical to a fresh generation`; the source dump is
byte-reproducible across two runs (11 sections, 844 files, 546,626 lines) and has no `--check`
mode, which is stated instead of invented.

The ordering rule the chain taught, recorded so the next part starts with it: a part's new files
move the whole-tree counts quoted inside every earlier handover, so the ancestors are regenerated
AFTER the new files exist and BEFORE any `--check` is believed - the first chain reported
`STALE: PART16 ... (22,828 generated lines vs 22,828 committed)`, equal counts with different
content, which is what a stale number looks like.

## The gap-fix pass, after the handover shipped

Auditing what the part left behind found four things, three of them documents that were still
actively wrong, and all four are now closed:

* `docs/DR.md`'s section "What is NOT yet automated, plainly" still claimed the `--due` scheduler
  as remaining work and Part 15's `--check-rls` as "still unwired" - both false after Part 20, in
  the document a reader trusts most for exactly this question. Rewritten; the *heading* is kept
  because `docs/PART15_RLS_ENABLEMENT.md` links to it by name.
* `docs/PART15_RLS_ENABLEMENT.md`'s own "It does not schedule" bullet got a "SUPERSEDED BY PART
  20" note in the style Parts 11 and 13 use ("RESOLVED IN PART 13", "SUPERSEDES THE CAPABILITY,
  NOT THE LAW"), so the historical claim and the current state are both readable.
* `.env.example` called the pair "optional for the API", which is true but no longer complete: the
  panel is the second consumer, absence means `unconfigured` rather than failure, and the file's
  own `127.0.0.1` URL is what compose overrides per service. No variable added; `collectEnvNames`
  reads `KEY=` lines, so prose is safe to change there and a new name would not have been.
* The compose comment cited `worker:`'s token translation by line number and `.env.example:966`;
  Part 20's own insertion had already made the first citation wrong the day it was written. Both
  are now by name, and the reason is recorded in the comment so nobody re-adds a number.

Plus one test the compose comment was leaning on but nothing owned: `engine-posture.service.spec.ts`
now pins `createEnginePostureClient` with BOTH names absent (the reference deployment minus the
env), where a naive reader might expect a thrown TypeError - `RegExp.test(undefined)` coerces to
the string "undefined", which is not an http(s) URL, so the answer is `null` and the panel says
`unconfigured`. That promise is now tested rather than reasoned.

Handover grew to 27 files (9 new + 18 modified), 12,061 lines; all five handovers re-checked byte
identical; api jest 425 passed / 20 suites, tsc and eslint clean; engine 428 passed / 12 skipped,
ruff clean, mypy clean; core 1656; siblings 43 and 19; `node --test scripts/` 65/65; the two
manifest gates still exit 0. LINE_COUNTS.md refreshed to 846 files / 227,961 lines (206,982
source), reconciled with what the generators print, and its four tables - language, tests vs
implementation, area, excluded buckets - are now filled in from the census output instead of being
left as bare headers.
