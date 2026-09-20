"""Patch the four narrative docs with Part 19 cross-links. Idempotent-safe: each
anchor is asserted to appear exactly once before replacement."""

import pathlib

DOCS = pathlib.Path("/home/user/whitelabel-copytrade/docs")


def patch(name: str, pairs: list[tuple[str, str]]) -> None:
    path = DOCS / name
    text = path.read_text()
    for old, new in pairs:
        count = text.count(old)
        assert count == 1, f"{name}: anchor appears {count} times: {old[:80]!r}"
        text = text.replace(old, new)
    path.write_text(text)
    print(f"{name}: {len(pairs)} edit(s) applied")


ROADMARKER = (
    "plus the three Python image commands that could never start a process (an "
    "`app.main:app` target this module does not define, and a `--log-config /dev/null` that "
    "`logging.config.fileConfig` has refused since python 3.11) | docs/PART18_METRICS_EXPOSITION.md |\n"
)

ROAD_ROW = (
    "| 19 | Live enablement made AUDITABLE without being made possible: the credential "
    "provider selection given its one concrete fetcher (`VaultKvSecretFetcher` over KV v2 - "
    "https-only with `user:pass@host` refused even over TLS, mount and path template validated "
    "at boot, identifiers matched against `[A-Za-z0-9._-]{1,64}` BEFORE a request is built, the "
    "rendered path bounded at 512 characters, the response bounded at 1 KiB..4 MiB and refused "
    "without being consumed, every non-200 one refusal that keeps its status and drops its body, "
    "and no field on `Settings` that could hold the token), the operator confirmation as a typed "
    "record rather than a flag (`LiveOperatorConfirmation`: HMAC-SHA256 over sorted-key canonical "
    "JSON, a 90-day ceiling on the window expressed in milliseconds against microsecond stamps, "
    "`nonce` >= 16 so two ceremonies over one scope are not byte-equal, `symbols`/`orderTypes` "
    "scoped per axis with an empty set meaning `all-configured` and never `nothing`, "
    "`SCOPE_MISMATCH` naming which axis, and no `required` without a key), the confirmation graded "
    "per order by the existing six-group law instead of a parallel gate (`CONFIRMATION` findings on "
    "the verdict, a reviewer that refuses to be built when the policy asks and nothing was supplied, "
    "a verifier that RAISES becoming a blocking `UNVERIFIED` naming the exception type and not its "
    "message), the axis that makes the whole picture countable (`ReviewArea`, seven areas, seven "
    "derived counters taking `ExecutionCounters` to 36 ints and the exposition to 36 families with no "
    "exporter change, `blocking_areas` in declaration order so one refusal renders one list), the "
    "live-enablement report graded from the wiring this process built rather than from a settings dump "
    "(eight `LivePrerequisite`s, `LIVE_*` codes spelled from the enum so they cannot disagree, "
    "`hardBlockersPresent` naming the one absence no configuration reaches, prose for the operator and "
    "names for machines), `/status` and `/health/ready` carrying the report plus a `public_summary()` "
    "whose fingerprint is 12 hex characters because an unauthenticated route may correlate a ceremony "
    "and must not reproduce it, boot log fields renamed `provider*` because `RedactionFilter` scrubs "
    "any credential-SHAPED KEY and `[REDACTED]` where 'which fetcher did I get' belongs is a boot line "
    "nobody can debug from, and 174 tests across five files - `EXECUTION_MODE=live` STILL refused, with "
    "the refusal now printing what it was graded against | docs/PART19_LIVE_ENABLEMENT.md |\n"
)

ROAD_NARRATIVE_OLD = "are named there in order rather than implied. What remains of"
ROAD_NARRATIVE_NEW = (
    "are named there in order rather than implied. Part 19 retired the per-tenant key source and "
    "left the rest of that sentence standing, with one correction worth naming: the list is now "
    "COMPUTED from the wiring a process built instead of asserted in prose "
    "(docs/PART19_LIVE_ENABLEMENT.md sec. 7), and it reports `DISTRIBUTED_LOCKS_WIRED` as "
    "unsatisfied for a different reason than `SIGNED_TRANSPORT_WIRED` - the core already ships a "
    "Redis lock manager and `app/composition.py:338` does not select it, whereas nothing in this "
    "build could be put over a signed transport that was never constructed (the same section's note "
    "on the two kinds of absence). Two of the five items Part 19 was asked to close were already "
    "shipped by Parts 13-18, so its diff is the fetcher, the confirmation, the counting axis and "
    "the report, plus tests pinning the eight items the audit found done. What remains of"
)

patch("ROADMAP.md", [(ROADMARKER, ROADMARKER + ROAD_ROW), (ROAD_NARRATIVE_OLD, ROAD_NARRATIVE_NEW)])
