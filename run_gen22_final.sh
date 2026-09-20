#!/usr/bin/env bash
# Part 22's final sequence. Clone of run_gen21_all.sh with three additions, each because the part is
# different in kind: (1) a preflight that the generated bundle is in sync BEFORE any document is
# written, so a handover never embeds a red bundle check; (2) the ancestor chain extended to 22;
# (3) the bundle's own gates re-run AFTER the chain and after every suite, with a byte-comparison that
# `--check` writes nothing, because the part's central claim is that the committed deployment files
# equal a fresh render and that verification is cheap to repeat.
set -u
cd /home/user/whitelabel-copytrade || exit 1

say() { printf '\n=== %s ===\n' "$*"; }

BUNDLE=infrastructure/observability
TOOL=libs/trading-core/scripts/gen_observability_bundle.py

say "deps: python"
python3 -m pip install -q --disable-pip-version-check \
    $(grep -hvE '^[[:space:]]*(#|$|-|asyncpg)' services/*/requirements*.txt) asyncpg==0.31.0 pyyaml 2>&1 | tail -5
python3 -m pip install -q --disable-pip-version-check -e libs/trading-core 2>&1 | tail -3
python3 -c "import fastapi, pytest, redis, asyncpg, structlog, pydantic, yaml, sqlglot, wlct_trading; print('python deps ok')" 2>&1 | tail -1
if ! python3 -c "import fastapi" > /dev/null 2>&1 || ! python3 -m pytest --version > /dev/null 2>&1; then
  echo "FATAL: python test/web deps missing, aborting before any generator runs"; exit 1
fi

say "deps: node"
for attempt in 1 2 3; do
  npm ci 2>&1 | tail -2
  npm run build:packages 2>&1 | tail -2
  npm run prisma:generate 2>&1 | tail -2
  if [ -x node_modules/.bin/jest ] && [ -x node_modules/.bin/tsc ] && [ -d node_modules/.prisma/client ] && \
     [ -d packages/shared-types/dist ] && [ -d packages/validation/dist ]; then
    echo "node deps ok (attempt ${attempt})"; break
  fi
  echo "node deps incomplete (attempt ${attempt}), retrying"
done
if [ ! -x node_modules/.bin/jest ]; then
  echo "FATAL: workspace node toolchain missing, aborting before any generator runs"; exit 1
fi
node --version

run_and_note() {  # run_and_note LABEL MODE...  -> the command's OWN exit code, then its last line
  local label="$1"; shift
  local log=/home/user/bundle_gate.log
  python3 "$TOOL" "$@" > "$log" 2>&1
  local code=$?
  echo "${label} exit=${code} -> $(tail -1 "$log")"
  return $code
}

say "preflight: the bundle is in sync before any document is written"
run_and_note precheck --check || true
if ! python3 "$TOOL" --check > /dev/null 2>&1; then
  echo "FATAL: the committed bundle drifts from a fresh render; regenerate with --emit before writing handovers"; exit 1
fi
sha_before=$(find "$BUNDLE" -type f | sort | xargs sha256sum | sha256sum | cut -c1-16)
python3 "$TOOL" --check > /dev/null 2>&1
sha_after=$(find "$BUNDLE" -type f | sort | xargs sha256sum | sha256sum | cut -c1-16)
echo "--check wrote nothing: $([ "$sha_before" = "$sha_after" ] && echo yes || echo NO)"

for n in 16 17 18 19 20 21 22; do
  say "generate PART${n}"
  python3 -u "scripts/gen_part${n}_handover.py" > "/home/user/gen${n}.log" 2>&1
  echo "gen ${n} exit=$? lines=$(wc -l < "docs/PART${n}_HANDOVER_FULL_SOURCE.md" 2>/dev/null)"
done

say "source dump"
node scripts/generate-source-dump.mjs 2>&1 | tail -3

for n in 16 17 18 19 20 21 22; do
  say "check PART${n}"
  python3 -u "scripts/gen_part${n}_handover.py" --check > "/home/user/check${n}.log" 2>&1
  echo "check ${n} exit=$? -> $(tail -1 "/home/user/check${n}.log")"
done

say "core gates"
cd libs/trading-core || exit 1
python3 -m ruff check wlct_trading tests 2>&1 | tail -2
python3 -m mypy wlct_trading 2>&1 | tail -2
python3 -m pytest -q 2>&1 | tail -2
python3 -m ruff check scripts 2>&1 | tail -2
cd ../.. || exit 1

say "engine + services"
cd services/execution-engine || exit 1
export PYTHONPATH=/home/user/whitelabel-copytrade/libs/trading-core
python3 -m ruff check app tests 2>&1 | tail -1
python3 -m mypy app 2>&1 | tail -1
python3 -m pytest -q 2>&1 | tail -1
cd ../.. || exit 1
(cd services/trading-engine && python3 -m pytest -q 2>&1 | tail -1)
(cd services/market-data && python3 -m pytest -q 2>&1 | tail -1)

say "node + scripts gates"
(cd apps/api && npx tsc -p tsconfig.json --noEmit 2>&1 | tail -1; echo "tsc exit=$?")
(cd apps/api && npx eslint src --max-warnings 0 2>&1 | tail -1; echo "eslint exit=$?")
(cd apps/api && npx jest --silent 2>&1 | tail -2)
(cd apps/admin-web && npx tsc --noEmit 2>&1 | tail -1; echo "admin tsc exit=$?")
node --test scripts/ 2>&1 | grep -E "^# (tests|pass|fail)"
for spec in scripts/dr-schedule-install.test.mjs scripts/dr-rehearsal.test.mjs scripts/dr-manifest.test.mjs; do
  node --test "$spec" 2>&1 | grep -E "^# (pass|fail)" | sed "s|^|$(basename "$spec"): |"
done

say "dr command set"
node scripts/dr-manifest.mjs --check; echo "check exit=$?"
node scripts/dr-manifest.mjs --check-schedule; echo "check-schedule exit=$?"
node scripts/dr-manifest.mjs --check-rls >/dev/null 2>&1; echo "check-rls exit=$?"
node scripts/dr-manifest.mjs --verify-rls >/dev/null 2>&1; echo "verify-rls exit=$?"
node scripts/dr-schedule-install.mjs --check >/dev/null 2>&1; echo "install --check exit=$?"
node scripts/dr-rehearsal.mjs --status --no-probe >/dev/null 2>&1; echo "rehearsal --status exit=$?"
python3 -m wlct_trading.observability.chaos --list >/dev/null 2>&1; echo "chaos --list exit=$?"

say "bundle gates, re-run last"
run_and_note check --check
run_and_note emit --emit
run_and_note rules --rules
python3 "$TOOL" --catalog | wc -l | sed 's/^/catalog lines: /'
python3 "$TOOL" --dashboard execution-engine --from - <<'EXPO' > /home/user/bundle_dashboard.log 2>&1
# TYPE wlct_execution_orders_total counter
wlct_execution_orders_total{service="execution-engine"} 3
EXPO
echo "dashboard exit=$? -> $(sed -n '13p' /home/user/bundle_dashboard.log) / $(tail -1 /home/user/bundle_dashboard.log)"
find "$BUNDLE" -type f | sort | xargs sha256sum | sha256sum | cut -c1-16 | sed "s/^/bundle sha after every gate: /"

say "DONE"
