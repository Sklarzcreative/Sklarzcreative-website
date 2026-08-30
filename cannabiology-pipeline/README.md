# Cannabiology figure production pipeline

Takes a manuscript figure from queued to author-approved:

```
route → context → prompt → candidates → OA review → repair → vector overlay → package → human approval
```

Scientifically conservative, deterministic where it can be, privacy-safe,
resumable, and structurally unable to manufacture authoritative-looking science.

## This repository is public

It serves sklarzcreative.com. The Cannabiology manuscript, prompts, tracker
data, artwork and review packets are unpublished client IP and are **never**
committed. They live in `$CANNABIOLOGY_WORKSPACE`, an absolute path outside the
repo. Without it the pipeline **fails closed**. `.gitignore` is defence in depth
only.

What is committed is the method: the tool, the rules, the schema, the tests.

## Quickstart

```bash
export CANNABIOLOGY_WORKSPACE=$HOME/cannabiology-workspace
python3 -m cannabiology doctor --init-workspace
cd src
python3 -m cannabiology audit
python3 -m cannabiology run CH01-IMG-01 --dry-run
```

Python 3.11+ and PyYAML. RDKit is needed only to build chemistry figures.
`jsonschema` is used if present; a built-in validator covers it otherwise.

## The five guarantees

**1. Routing gate.** Every figure gets exactly one of six routes before anything
is generated. `VECTOR_BUILD`, `DATA_DRIVEN`, `HUMAN_BUILD` and `HOLD` can never
enter image generation, and `--force` does not open the gate. A route derived
rather than stated by the tracker requires `--confirm-route` from a human.

**2. Verdicts are computed, not asserted.** The reviewing model reports
findings; code decides. A model cannot approve a figure while blocking findings
remain. Fabricated data or generated scientific text is `REJECTED` outright,
because once invented values are baked into a composition, editing is not a
reliable fix.

**3. Exact structures are built, not generated.** Chemistry renders from a cited
source via RDKit, with the molecular formula cross-checked against that source;
mechanism diagrams build from a human-confirmed topology spec. A compound with
no citation, or a spec nobody confirmed, refuses to draw. See
[Building figures deterministically](docs/05-vector-build.md).

**4. Science-bearing text is vector, not pixels.** Generated base art carries no
authoritative text. Labels, leaders, panel letters, scale bars and captions are
built as SVG and composited over the art. A spelling error costs an SVG rewrite,
never a regeneration — so `VECTOR_EDIT` rounds don't count against the repair
cap.

**5. Human approval is mandatory.** The terminal automated state is
`PENDING_HUMAN_APPROVAL`. `HUMAN_APPROVED` is reachable only through
`cannabiology approve`. Silence is not approval.

## Current routing of the canonical library

Recomputed from the tracker on every run — not hard-coded.

| Route | Figures | Assets |
|---|---:|---:|
| HYBRID | 32 | 33 |
| VECTOR_BUILD | 7 | 7 |
| DATA_DRIVEN | 6 | 6 |
| HOLD | 6 | 6 |
| **Total** | **51** | **52** |

Zero figures are purely generative: every figure the project marked `GENERATE`
also carries a manual-label list, which makes it `HYBRID`. 19 of the 32 are
*derived* routes awaiting human confirmation.

## Docs

- [Architecture](docs/01-architecture.md)
- [The routing gate](docs/02-routing.md)
- [Review, verdicts and repair](docs/03-review-and-repair.md)
- [Operations](docs/04-operations.md)
- [Building figures deterministically](docs/05-vector-build.md)
- [Permanent project instructions](CLAUDE.md)
