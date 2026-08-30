# Operations

## Setup

```bash
export CANNABIOLOGY_WORKSPACE=$HOME/cannabiology-workspace   # outside the repo
python3 -m cannabiology doctor --init-workspace
```

Import the canonical tracker from Drive `00 Master Control` into
`$CANNABIOLOGY_WORKSPACE/canonical/tracker_snapshot/` as
`master-figure-tracker.csv` and `prompt-library.csv`, and the manuscript sources
into `canonical/manuscript_sources/`.

Run from `cannabiology-pipeline/src` (or add it to `PYTHONPATH`).

## Commands

```bash
python3 -m cannabiology doctor [--init-workspace] [--network]
python3 -m cannabiology audit                    # 51/52 reconciliation
python3 -m cannabiology route [CH01-IMG-01]      # route + why
python3 -m cannabiology status [CH01-IMG-01]
python3 -m cannabiology run CH01-IMG-01 --dry-run
python3 -m cannabiology batch --route HYBRID --dry-run --limit 8
python3 -m cannabiology package --batch 001
python3 -m cannabiology approve CH01-IMG-01 --by "Cassandra Sklarz"
```

Flags: `--dry-run`, `--no-network`, `--confirm-route`, `--max-iterations`,
`--candidate-count`, `--model`, `--asset`, `--force`.

`--force` never bypasses `HOLD`, `DATA_DRIVEN`, `VECTOR_BUILD` or the privacy
guard.

## Going live

```bash
export OPENAI_API_KEY=sk-...
python3 -m cannabiology doctor --network      # confirm reachability
python3 -m cannabiology run CH01-IMG-01       # one figure first
```

Models are configuration (`config/pipeline.yaml`), never literals in source.

## Cost shape

Tier 1 generates 2 initial candidates; tiers 2–3 generate 1. The generative
repair cap is 4, and `VECTOR_EDIT` rounds are free. So a Tier-1 figure is
bounded at 6 image calls and typically costs 2–3.

## Tests

```bash
cd cannabiology-pipeline && python3 -m unittest discover -s tests -t tests
```

Fixtures are synthetic. No client content is used in tests.
