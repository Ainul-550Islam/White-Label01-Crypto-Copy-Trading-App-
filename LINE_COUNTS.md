counted under the handover generator's rule set: 870 files, 241,136 lines
reconciliation with the repo's own figures: source (docs/ excluded) = 219,180; with narrative docs = 241,136  <- docs/PART16_HANDOVER_FULL_SOURCE.md prints both

language                       files      lines  non-blank
Python                           329    123,053    107,536
TypeScript                       311     59,382     54,298
Markdown                          33     12,228     10,304
JSON                              37     11,587     11,587
Dart                              46      7,764      6,705
JavaScript (ESM)                  12      7,194      6,692
TypeScript (React)                26      5,496      5,094
Prisma schema                      1      4,248      3,421
SQL                               16      3,902      3,267
dotenv (example)                   5      1,395      1,280
no extension                       9      1,235      1,143
YAML                               8        909        859
Shell                              3        618        521
Lockfile                           1        607        607
Dockerfile                         6        437        365
Text                              12        377        367
ARB (Flutter l10n)                 2        234        234
TOML                               5        191        166
git ignore                         2         95         85
CSS                                1         88         78
other (.cron)                      1         46         40
JavaScript (CJS)                   1         27         27
docker ignore                      1         22         22
build artifact                     1          1          1
packaging marker                   1          0          0

tests beside implementation (lines):
  Python               tests  39,984   implementation   83,069
  TypeScript           tests   8,212   implementation   51,170
  TypeScript (React)   tests       0   implementation    5,496
  Dart                 tests     329   implementation    7,435

specifically asked about:
  Python          329 files   123,053 lines
  TypeScript      311 files    59,382 lines
  TypeScript (React)   26 files     5,496 lines
  JavaScript (ESM)   12 files     7,194 lines
  Dart             46 files     7,764 lines
  Rust              0 files         0 lines
  C                 0 files         0 lines
  C++               0 files         0 lines
  C/C++ header      0 files         0 lines
  Go                0 files         0 lines
  Java              0 files         0 lines
  Kotlin            0 files         0 lines
  Ruby              0 files         0 lines
  PHP               0 files         0 lines
  Swift             0 files         0 lines
  Scala             0 files         0 lines

by area (lines):
  libs/trading-core             92,570  Python 92,245, Text 234, TOML 79, no extension 12, packaging marker 0
  apps/api                      60,486  TypeScript 51,644, Prisma schema 4,248, SQL 3,828, JSON 729, JavaScript (CJS) 27, no extension 7, TOML 3
  docs                          21,956  Markdown 11,752, JSON 10,107, Text 51, other (.cron) 46
  scripts                       18,016  Python 10,237, JavaScript (ESM) 7,161, Shell 618
  services/execution-engine     15,295  Python 15,002, dotenv (example) 198, TOML 49, Text 42, JSON 4
  apps/mobile                    9,100  Dart 7,764, Lockfile 607, no extension 334, ARB (Flutter l10n) 234, YAML 81, Markdown 66, git ignore 13, JSON 1
  apps/admin-web                 6,855  TypeScript (React) 5,496, TypeScript 1,153, CSS 88, JSON 66, JavaScript (ESM) 33, dotenv (example) 15, Text 3, build artifact 1
  services/trading-engine        3,238  Python 3,143, dotenv (example) 40, TOML 30, Text 21, JSON 4
  (repo root)                    3,088  dotenv (example) 1,120, no extension 882, YAML 647, Markdown 247, JSON 88, git ignore 82, docker ignore 22
  packages/shared-types          2,990  TypeScript 2,965, JSON 25
  services/market-data           2,508  Python 2,426, TOML 30, Text 26, dotenv (example) 22, JSON 4
  packages/config                1,692  TypeScript 1,664, JSON 28
  infrastructure                 1,280  Dockerfile 437, JSON 425, YAML 181, Markdown 163, SQL 74
  packages/validation              840  TypeScript 810, JSON 30
  packages/utils                   640  TypeScript 611, JSON 29
  services/notification-service       582  TypeScript 535, JSON 47

excluded buckets (reported, not hidden):
  docs/source dump                12 files    596,292 lines
  PART*HANDOVER dump              19 files    356,192 lines
  dir:__pycache__                308 files     64,772 lines
  lockfile                         1 files     16,003 lines
  dir:dist                       128 files     10,929 lines
  dir:.mypy_cache              5,908 files      5,914 lines
  dir:.ruff_cache                  9 files      3,817 lines
  dir:.pytest_cache               21 files      2,406 lines
  dir:node_modules            46,377 files      (not read)
