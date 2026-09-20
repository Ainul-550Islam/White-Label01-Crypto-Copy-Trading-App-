# Part 19 implementation map (internal, outside the repo so it moves no count)

Audit method: grep + read, this session, of `libs/trading-core/wlct_trading/execution/`
(`credentials.py`, `placement_review.py`, `placement_attestor.py`, `engine.py`, `config.py`,
`__init__.py`), `services/execution-engine/app/` (`credentials.py`, `placement.py`,
`composition.py`, `config.py`, `schemas.py`, `routers/internal.py`, `observability.py`),
and the parts' tests.

## Already complete — reuse, do not rebuild

| Requested by the brief | Where it already lives |
| --- | --- |
| credential provider selection, deterministic, unknown fails closed | `app/config.py` `EXECUTION_CREDENTIAL_SOURCE: Literal["none","environment","secret-manager"]` (a `Literal` IS the fail-closed unknown-provider refusal) + `app/credentials.py::build_credential_provider` + core `NullCredentialProvider` / `EnvironmentCredentialProvider` / `SecretManagerCredentialProvider` / `CachingCredentialProvider` |
| missing credential fails closed | `NullCredentialProvider.resolve` raises `CredentialNotFound`; production refuses `environment` (`app/config.py:354`) |
| no live/paper credential mixing | env names are venue-prefixed (`credential_env_names`, `WLCT_BINANCE_API_KEY`); paper path constructs no provider at all |
| credential exists / usable / belongs to the configured exchange | `ExchangeCredentials.assert_safe`, `CredentialProvider.default_exchange`, `LocalPlacementAttestor`'s `_credential_reader` partial bound to the configured `ExchangeId` |
| permission attestation, read-only cannot trade, withdrawal NOT required | `ReviewCode.NO_SPOT_TRADE_PERMISSION`, `NO_READ_PERMISSION`, `WITHDRAW_ENABLED` (a key that CAN withdraw is the refusal), `PlacementFacts.withdrawal_permitted/read_permitted/key_permission_granted`, `no_known_withdrawal_path` claim |
| key rotation / expiry | `KEY_TOO_OLD`, `KEY_EXPIRED`, `TRADING_AUTHORITY_EXPIRED`, `PlacementReviewPolicy.max_key_age_days`, `MAX/MIN_KEY_AGE_DAYS`, `key_created_at_millis`, `trading_authority_expires_at_millis` |
| symbol filter review, normalization, disabled/malformed | `SYMBOL_UNATTACHED`, `SYMBOL_NOT_TRADING`, `ORDER_TYPE_UNSUPPORTED`, `TIF_UNSUPPORTED`, `PlacementReviewRequest._NORMALISED`, `wlct_trading.exchanges.symbols`, `SymbolFacts` |
| account capability | `ACCOUNT_TRADING_DISABLED` (`canTrade`), `ACCOUNT_TYPE_UNEXPECTED` |
| typed per-order verdict, deterministic reasons | `PlacementVerdict` (allowed, ordered findings, `codes`, `blocking_codes`, `retryable`, `verdict_id` over canonical JSON, three attested claims) |
| order-scoped, not startup-flag-scoped | `PlacementReviewRequest(tenant, account, symbol, order_type, time_in_force)` and `PlacementReviewer.review(request)` per `submit()` |
| integration into the execution flow | gate 11 of 11 in `ExecutionSafety`, `PLACEMENT_REVIEW_BLOCKED`, verdict fields ride the `SUBMITTED` event payload, `_record_placement_review` counters + `placement_review` latency stage |
| live startup refusal | `app/composition.py:253` raises `ExecutionUnavailable` before anything is built |
| metrics/logging | `wlct_trading/observability/metrics.py` + the service hub (Part 18), whose counter families are derived from `ExecutionCounters` fields |

## Genuine gaps this part fills

G1 **`secret-manager` has no fetcher.** `app/credentials.py:227` refuses it: the core
    defines `SecretFetcher` and deliberately does not implement one. Ships
    `app/secret_fetcher.py::VaultKvSecretFetcher` — real KV v2 HTTP over the existing
    `httpx` dependency (no new deps), env-only token, path template keyed by
    tenant/account/exchange, `ResolvedSecret` (permissions + expiry) out, secret never
    logged/serialised, every failure normalised to `CredentialNotFound` naming the type
    only. `EXECUTION_CREDENTIAL_FETCHER: Literal["none","vault-kv2"]` selects it;
    `secret-manager` + `none` stays a boot refusal, now narrower (it names the fetcher,
    not the whole provider).

G2 **No operator confirmation as a typed artifact.** Today the only operator signal is
    the `EXECUTION_LIVE_TRADING_CONFIRMED` boolean (`ExecutionSettings.live_trading_confirmed`).
    Ships core `execution/live_confirmation.py`: `LiveOperatorConfirmation` (scoped to
    deployment instance + tenant + account + exchange + symbol set + order-type set, with
    issue/expiry windows and a nonce), `ConfirmationState` (ABSENT / MALFORMED /
    UNVERIFIED / EXPIRED / NOT_YET_VALID / SCOPE_MISMATCH / VALID), HMAC-SHA256 over
    canonical JSON with an env-only key, and `ConfirmationVerifier.assess(...)` used per
    order. Five new `ReviewCode`s in the OPERATOR-CONFIRMATION area; the policy flag
    `require_operator_confirmation` defaults False so no existing verdict changes, and a
    reviewer asked to require one without a verifier refuses (fail-closed, not permissive).

G3 **No refusal-category vocabulary.** The brief's `LIVE_*` reasons map onto codes that
    already exist, so nothing is renamed; what is missing is the *category* axis for §11/§12.
    Ships `ReviewArea` + `area_of(code)` in `placement_review.py` as the single mapping,
    completeness-pinned by a test; six new `ExecutionCounters` fields
    (`placement_review_*_blocks`) that Part 18's derived families publish with no
    exporter change; `PlacementVerdict.blocking_areas` for callers.

G4 **The live refusal is prose, and it had already rotted.** `composition.py:258-267`
    asserts which pieces exist. Ships core `execution/live_enablement.py`:
    `LivePrerequisite` + `LiveEnablementInputs` + `evaluate_live_enablement` returning a
    deterministic report (missing in declaration order, `reason_codes()` in the
    `LIVE_*` shape, `render_refusal()`), so the boot message and `/status` are computed
    from the wiring rather than from a sentence a later part has to remember to edit.
    `SIGNED_TRANSPORT_WIRED` is structurally unsatisfiable in this build (the runtime
    never constructs a live adapter), so the report can never come back empty and
    `EXECUTION_MODE=live` keeps refusing — now with the missing prerequisites named.

## Explicitly out of this part
No signed live transport, no live adapter construction, no notional ceiling in the
confirmation (the review request carries no notional — stated as a limit, not built as a
half- abstraction), no `ALLOW_LIVE` boolean anywhere, no new metric plane, no table.
