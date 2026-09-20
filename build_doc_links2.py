"""Part 19 cross-links for ARCHITECTURE.md, SECURITY.md and GETTING_STARTED.md.

Every anchor is asserted to appear exactly once, so a stale anchor fails loudly instead of
silently writing the paragraph into the wrong file.
"""

import pathlib

DOCS = pathlib.Path("/home/user/whitelabel-copytrade/docs")


def patch(name: str, pairs: list[tuple[str, str]]) -> None:
    path = DOCS / name
    text = path.read_text()
    for old, new in pairs:
        count = text.count(old)
        assert count == 1, f"{name}: anchor appears {count} times: {old[:70]!r}"
        text = text.replace(old, new)
    path.write_text(text)
    print(f"{name}: {len(pairs)} edit(s) applied")


# --------------------------------------------------------------------------
# ARCHITECTURE.md - the describe()/schema law gains its third instance
# --------------------------------------------------------------------------
ARCH_OLD = """  (docs/PART18_METRICS_EXPOSITION.md).. Part 17 added"""
ARCH_NEW = """  (docs/PART18_METRICS_EXPOSITION.md). Part 17 added"""

ARCH_PART19 = """  Part 19 is the third instance of that same decision, and the one that shows why the
  rule exists: `describe()` grew `credentialFetcher` and `operatorConfirmation` beside a
  `liveEnablement` block, and because `/health/ready` spreads the wiring view verbatim to a
  caller with no token, the confirmation could only be published as `public_summary()` -
  `required`, `keyConfigured`, `recordPresent`, `expiresAtMicros` and a 12-character digest
  fingerprint. A full digest or the nonce would have made an unauthenticated probe a way to
  collect the material a signed authorisation is made of. Two consequences are pinned rather
  than remembered: `PlacementStatusView` had to grow its two fields in the same edit (its base
  model is `extra="forbid"`, so a describe() key with no schema field is a 500 on both routes,
  which is the failure this law is designed to produce - loudly, at the boundary, instead of
  quietly publishing a partial picture), and the credential fields moved to the names
  `providerSource` / `providerFetcher` IN LOG RECORDS ONLY, because `RedactionFilter` replaces
  the value of any key whose NAME is credential-shaped and a boot line that reads `[REDACTED]`
  where the mechanism name belongs explains nothing to the person it is written for (the API
  spelling is untouched; docs/PART19_LIVE_ENABLEMENT.md sec. 3 and sec. 7).
"""

patch(
    "ARCHITECTURE.md",
    [
        (ARCH_OLD, ARCH_OLD.replace("  Part 17 added", "") + "\n" + ARCH_PART19.rstrip() + "\n  Part 17 added"),
    ],
)

# --------------------------------------------------------------------------
# SECURITY.md
# --------------------------------------------------------------------------
SEC_MANAGER_OLD = (
    "| `secret-manager` | a fetcher injected in code by the service that owns the encrypted "
    "store | boot without an injected fetcher: the API, a queue job and this endpoint's own "
    "request body are all refused as places a key provider could be installed |"
)
SEC_MANAGER_NEW = (
    "| `secret-manager` | a `SecretFetcher` in front of the encrypted store - since Part 19 "
    "selectable by configuration as `EXECUTION_CREDENTIAL_FETCHER=vault-kv2` "
    "(`app/secret_fetcher.py`), or injected in code by the service that owns the store | boot "
    "without a fetcher at all: the API, a queue job and this endpoint's own request body are "
    "all refused as places a key provider could be installed, and naming a fetcher for a "
    "source that ignores it is refused as a deployment that believes it has plumbing it does "
    "not use |"
)

SEC_CACHE_OLD = """The review that consumes those credentials answers a narrower question than
"are these bytes signed correctly": whether this key may place this order type on
this symbol in this trading phase right now. A key that can withdraw is a refusal
on any runtime, and a venue that cannot be asked is a refusal on a runtime that
could transmit (docs/PART16_PLACEMENT_REVIEW.md)."""

SEC_CACHE_NEW = """The Vault fetcher keeps the same property the environment provider was built
with: there is no settings field that could hold the token. `EXECUTION_VAULT_TOKEN_ENV`
names a variable and the value is read from `os.environ` inside the module that signs
the request, so `to_public_dict()`, `model_dump()` and `repr()` of the settings object
each have nothing to leak - which is a stronger guarantee than "the view omits it", and
is tested as the absence of the field (`test_the_token_has_no_field_it_could_be_stored_in`).
What the fetcher will not do is also part of the control: it refuses an `http://` address
and a `user:pass@host` authority even over TLS, refuses a tenant, account or exchange
identifier that is not one safe path segment BEFORE any request leaves the process (the
alternative - percent-encoding it - is what would let a traversal reach another tenant's
secret), bounds the response body before parsing it and quotes no body in any refusal, and
never renders the secret map it read. A path template is validated at boot rather than
interpreted at order time, because a typo like `{tenent}` would otherwise look up a path that
does not exist and report "no secret" for every tenant until somebody notices.

The operator confirmation (Part 19) is an authorisation record, not a credential: it holds no
key material, and it is safe to store in a configuration management system - but its `digest`
is only as strong as the HMAC key that made it, so the key is env-only under the same rule as
a venue key (`EXECUTION_CONFIRMATION_KEY_ENV`, default `EXECUTION_CONFIRMATION_HMAC_KEY`,
minimum 32 characters, never a settings field). The record's own bounds are what make it an
approval rather than a standing permission: a window no wider than 90 days, a `nonce` of at
least 16 characters so a superseded ceremony is distinguishable from the live one in the audit
trail, and a scope over tenant, account, instance, exchange, symbol and order type that the
per-order review re-derives rather than trusts - approving `BTCUSDT` never authorises `SOLUSDT`.
Verification is `hmac.compare_digest` over canonical JSON (sorted keys, both because a
signature needs the byte sequence to be reproducible and because a set does not have an order),
never `==`, so a record cannot be probed one byte at a time. An expired record refuses every
order without stopping the process, because the process is still the only path that can
safely cancel and reconcile; a *missing* key or an unparseable record is a boot failure,
because that is a deployment whose configuration is wrong rather than merely old.

The review that consumes those credentials answers a narrower question than
"are these bytes signed correctly": whether this key may place this order type on
this symbol in this trading phase right now, and - since Part 19 - whether a named
operator authorised this scope inside a window the deployment can verify. A key that
can withdraw is a refusal on any runtime, and a venue that cannot be asked is a refusal
on a runtime that could transmit (docs/PART16_PLACEMENT_REVIEW.md,
docs/PART19_LIVE_ENABLEMENT.md)."""

SEC_CONTROL4_OLD = """   (Part 16, gate `PLACEMENT_ATTESTED`). There is no configuration that removes
   control 4, because a switch that lets a deployment trade without asking the
   venue whether the key may trade is the same as no review."""
SEC_CONTROL4_NEW = """   (Part 16, gate `PLACEMENT_ATTESTED`), and refuses each order a required
   operator confirmation does not cover (Part 19, `OPERATOR_CONFIRMATION_*`). There
   is no configuration that removes control 4, because a switch that lets a
   deployment trade without asking the venue whether the key may trade is the same
   as no review - which is why the confirmation is a signed, scoped, expiring record
   and not an `ALLOW_LIVE` boolean: a boolean is the same kind of object as the
   switch this control exists to make impossible."""

SEC_OPEN_OLD = """  transmission. Part 16 wired the credential source and the review, so the
  open prerequisites are now the venue attestor instance built from the
  deployment's own signed adapter, per-tenant key custody, a signed transport
  with the egress addresses allow-listed at the venue, and the durable store
  shipped in Part 13 (docs/PART13_DURABLE_STORE.md) - and they stay enforced,
  not configuration."""
SEC_OPEN_NEW = """  transmission. Part 16 wired the credential source and the review and Part 19
  closed the per-tenant key custody half of the open list with the Vault fetcher, so
  the remaining items are computed at boot from the wiring the process built rather
  than asserted in a document: `VENUE_ATTESTOR_WIRED` and `SIGNED_TRANSPORT_WIRED`
  (one absence seen twice - the gatherer is built over the live adapter this
  composition root never constructs), `DISTRIBUTED_LOCKS_WIRED` (the core ships a
  Redis lock manager; `app/composition.py:338` does not select it), and
  `DURABLE_STORE_WIRED`, whose store shipped in Part 13 (docs/PART13_DURABLE_STORE.md)
  and is selected by `EXECUTION_STORE_BACKEND=postgres`. They stay enforced, not
  configurable away, and `liveRefused` is `true` in the report of every build this
  repository ships (docs/PART19_LIVE_ENABLEMENT.md sec. 7 and sec. 8)."""

SEC_RULES_OLD = """* Exchange keys should be created trade-only, with withdrawal permission
  disabled and IP-allowlisted to the platform's egress addresses."""
SEC_RULES_NEW = """* Exchange keys should be created trade-only, with withdrawal permission
  disabled and IP-allowlisted to the platform's egress addresses.
* The confirmation HMAC key is a signing key for authorisations and is custody-graded
  as one: one per environment, injected as an environment variable, rotated by
  restarting with a fresh value (a key rotation and a record replacement are two acts,
  not one, because the record is parsed at boot and the key at verifier construction).
  Rotating it invalidates nothing that was already signed *and* recorded - the audit
  trail keeps its verdicts - which is the point of storing the digest rather than
  relying on the key to still be around to explain it."""

patch(
    "SECURITY.md",
    [
        (SEC_MANAGER_OLD, SEC_MANAGER_NEW),
        (SEC_CACHE_OLD, SEC_CACHE_NEW),
        (SEC_CONTROL4_OLD, SEC_CONTROL4_NEW),
        (SEC_OPEN_OLD, SEC_OPEN_NEW),
        (SEC_RULES_OLD, SEC_RULES_NEW),
    ],
)

# --------------------------------------------------------------------------
# GETTING_STARTED.md
# --------------------------------------------------------------------------
GS_OLD = """`docs/PART18_METRICS_EXPOSITION.md` sec. 6.1.

| Service | Address |"""
GS_NEW = """`docs/PART18_METRICS_EXPOSITION.md` sec. 6.1.

### The Part 19 knobs, and what a first deployment should leave alone

`services/execution-engine/.env.example` documents thirteen variables Part 19 added -
one fetcher selector (`EXECUTION_CREDENTIAL_FETCHER`), eight for Vault KV v2
(`EXECUTION_VAULT_ADDR`, `..._MOUNT`, `..._PATH_TEMPLATE`, `..._TOKEN_ENV`,
`..._NAMESPACE`, `..._TIMEOUT_MS`, `..._TLS_VERIFY`, `..._MAX_RESPONSE_BYTES`) and four
for the operator confirmation (`EXECUTION_REQUIRE_OPERATOR_CONFIRMATION`,
`..._OPERATOR_CONFIRMATION_JSON`, `..._OPERATOR_CONFIRMATION_FILE`,
`EXECUTION_CONFIRMATION_KEY_ENV`). Every one of them defaults to the dark side, none
of them opens the money path, and the two key variables are deliberately absent from
`docker-compose.yml` - a compose file is a place secrets get copied from, and these
values are read from the process environment of the container that needs them.

What a first deployment should actually set: nothing here. What a deployment that wants
its review to have real evidence to reason over should set: `EXECUTION_CREDENTIAL_SOURCE`
(plus a fetcher if the source is `secret-manager`), so the credential lookup can be made,
and `EXECUTION_STORE_BACKEND=postgres` once the migration has run. The confirmation is the
last item, not the first: it is a record a human signs about a specific symbol and order
type, and minting one before the review above it has real evidence produces an approval of
nothing in particular. `docs/PART19_LIVE_ENABLEMENT.md` is the operational document -
sec. 5 is the minting ceremony with the exact bytes, sec. 9 is the order to turn the pieces
on, sec. 10 is the refusal catalogue for when a boot says no.

| Service | Address |"""

patch("GETTING_STARTED.md", [(GS_OLD, GS_NEW)])
