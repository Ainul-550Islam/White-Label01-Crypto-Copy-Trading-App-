#!/usr/bin/env bash
# Part 21's final sequence: reinstall the sandbox, regenerate the ancestor handover chain in
# order (16 -> 20) then Part 21's own document, prove each byte-reproducible with --check,
# refresh the generated source dump, and re-run every gate. Written to replace the per-suite
# calls that came before it, so that one dependency install serves every step (the sandbox
# drops installed packages between calls).
set -u
cd /home/user/whitelabel-copytrade || exit 1

say() { printf '\n=== %s ===\n' "$*"; }

say "deps: python"
# The literal recipe this sandbox needs. The per-service requirements files are the only ones in
# the repository (there is no root requirements.txt), asyncpg==0.29.0 has no wheel here and
# conflicts with the 0.31.0 that does, and the files carry comment lines plus relative -r/-e
# lines that cannot resolve from the root - so the pin list is filtered, the asyncpg pin is
# replaced, and the core is installed editable from its own path.
python3 -m pip install -q --disable-pip-version-check \
    $(grep -hvE '^[[:space:]]*(#|$|-|asyncpg)' services/*/requirements*.txt) asyncpg==0.31.0 pyyaml 2>&1 | tail -5
python3 -m pip install -q --disable-pip-version-check -e libs/trading-core 2>&1 | tail -3
python3 -c "import fastapi, pytest, redis, asyncpg, structlog, pydantic, yaml, sqlglot, wlct_trading; print('python deps ok')" 2>&1 | tail -1
# Abort rather than proceed: a generator that runs its gates against a half-installed
# environment would write a header full of "FAILED" strings into six documents, and those
# documents are the deliverable. Better to stop here than to spend an hour producing them wrong.
if ! python3 -c "import fastapi" > /dev/null 2>&1 || ! python3 -m pytest --version > /dev/null 2>&1; then
  echo "FATAL: python test/web deps missing, aborting before any generator runs"; exit 1
fi

say "deps: node"
# This workspace is an npm WORKSPACE: apps/api has no node_modules of its own, so the install
# belongs at the repository root (npm ci, then the packages' tsc builds, then the API's prisma
# generate through its workspace script). Running `npm ci` inside apps/api instead "succeeds" into
# the root tree while `npm run build:packages` fails there with "unknown script", which is how the
# first two runs of this chain lost the API gates. The checks look at the root's node_modules and
# at the generated client, and the run aborts if either is missing: a generator that cannot run
# jest would still happily print "UNPARSED" into a handover header, and a handover with a fake
# green is worse than no handover.
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
ls node_modules/.bin/ | grep -c . | sed 's/^/node_modules bins: /'

for n in 16 17 18 19 20 21; do
  say "generate PART${n}"
  python3 -u "scripts/gen_part${n}_handover.py" > "/home/user/gen${n}.log" 2>&1
  echo "gen ${n} exit=$? lines=$(wc -l < "docs/PART${n}_HANDOVER_FULL_SOURCE.md" 2>/dev/null)"
done

for n in 16 17 18 19 20 21; do
  say "check PART${n}"
  python3 -u "scripts/gen_part${n}_handover.py" --check > "/home/user/check${n}.log" 2>&1
  echo "check ${n} exit=$? -> $(tail -1 "/home/user/check${n}.log")"
done

say "source dump"
node scripts/generate-source-dump.mjs 2>&1 | tail -3

say "core gates"
cd libs/trading-core || exit 1
python3 -m ruff check wlct_trading tests 2>&1 | tail -2
python3 -m ruff check scripts --config 'lint.extendSelect=["E4","E7","E9","F"]' 2>&1 | tail -2
python3 -m mypy wlct_trading 2>&1 | tail -2
python3 -m pytest -q 2>&1 | tail -2
cd ../.. || exit 1

say "engine gates"
cd services/execution-engine || exit 1
export PYTHONPATH=/home/user/whitelabel-copytrade/libs/trading-core
python3 -m ruff check app tests 2>&1 | tail -2
python3 -m mypy app 2>&1 | tail -2
python3 -m pytest -q 2>&1 | tail -2
cd ../.. || exit 1

say "api gates"
cd apps/api || exit 1
npx prisma validate 2>&1 | tail -1
npx tsc -p tsconfig.json --noEmit 2>&1 | tail -2; echo "tsc exit=$?"
npx eslint src --max-warnings 0 2>&1 | tail -2; echo "eslint exit=$?"
npx jest --silent 2>&1 | tail -3
npx prettier --check 'src/**/*.ts' ../admin-web/src/lib/navigation.ts ../../scripts/dr-manifest.mjs ../../scripts/dr-manifest.test.mjs ../../scripts/dr-schedule-install.mjs ../../scripts/dr-schedule-install.test.mjs ../../scripts/dr-rehearsal.mjs ../../scripts/dr-rehearsal.test.mjs ../../docs/dr/manifest.json 2>&1 | tail -2
node --test src/ 2>&1 | grep -E "^# (tests|pass|fail)"
cd ../.. || exit 1

say "admin-web + services + compose"
(cd apps/admin-web && npx tsc --noEmit 2>&1 | tail -1; echo "admin tsc exit=$?")
(cd services/trading-engine && python3 -m pytest -q 2>&1 | tail -1)
(cd services/market-data && python3 -m pytest -q 2>&1 | tail -1)
cd services/trading-engine && python3 -m ruff check app tests 2>&1 | tail -1
cd ../market-data && python3 -m ruff check app tests 2>&1 | tail -1
cd /home/user/whitelabel-copytrade || exit 1
python3 -c "
import sys, yaml
for p in ('docker-compose.yml','docker-compose.observability.yml'):
    doc = yaml.safe_load(open(p))
    print(f'{p}: {len(doc[\"services\"])} services ->', ', '.join(doc['services']))
print('yaml ok')" 2>&1 | tail -3

say "dr command set"
node scripts/dr-manifest.mjs --check; echo "check exit=$?"
node scripts/dr-manifest.mjs --check-schedule; echo "check-schedule exit=$?"
node scripts/dr-manifest.mjs --check-rls >/dev/null 2>&1; echo "check-rls exit=$?"
node scripts/dr-manifest.mjs --verify-rls >/dev/null 2>&1; echo "verify-rls exit=$?"
node scripts/dr-schedule-install.mjs --check >/dev/null 2>&1; echo "install --check exit=$?"
node scripts/dr-rehearsal.mjs --status --no-probe >/dev/null 2>&1; echo "rehearsal --status exit=$?"
node --test scripts/ 2>&1 | grep -E "^# (tests|pass|fail)"

say "DONE"
