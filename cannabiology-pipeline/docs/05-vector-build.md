# Building figures deterministically

Some figures cannot be generated. Their scientific content *is* exact structure:
chemistry, karyotypes, mechanism topology. For these the pipeline builds vector
artwork from a verified source rather than asking a model to draw one.

## The distinction that matters

Both of these produce clean vector output. Only one is safe:

| | Where the structure comes from | Safe for a textbook? |
|---|---|---|
| A model writes SVG | Its memory of what the molecule looks like | **No** — confidently wrong, just crisper |
| A renderer draws from a cited source | A recorded SMILES with provenance | **Yes** — exact, repeatable, checkable |

Sharper is not more correct. The pipeline only does the second.

## Chemistry

RDKit renders from the chemical source registry in your private workspace at
`canonical/chem_sources.yaml`. Two checks run before anything draws:

1. The SMILES must parse.
2. The formula RDKit computes must match the formula recorded from the source.
   A transcription slip changes the formula and is caught.

A compound with no entry, no citation, or `verified: false` **refuses to draw**.

```bash
python3 -m cannabiology fetch-chem cannabidiol --cid 644019   # needs network
# then a human checks the render against PubChem and sets verified: true
python3 -m cannabiology build CH01-IMG-03
```

`fetch-chem` always writes `verified: false`. Only a person sets it true.

## Diagram layouts

Six layouts, chosen by the spec's `layout` key (default `flow`). All share one
palette and type scale so the figures read as one system across the book.

| Layout | Shape | Required per node | Use for |
|---|---|---|---|
| `flow` | boxes and arrows in columns | `column` | pipelines, mechanisms, pathways |
| `lanes` | parallel tracks of stages | `lane`, `step` | side-by-side workflow comparison |
| `timeline` | dated events along an axis | `date` | histories, process evolution |
| `pyramid` | tiers narrowing upward | `tier` | evidence hierarchies |
| `layers` | stacked horizontal bands | `layer` | multi-omics and systems stacks |
| `hub` | centre with radiating spokes | one node with `hub: true` | convergence and network maps |

`flow` also accepts `bands` (labelled background regions) and `edges` with
optional `label` and `style: dashed`. `pyramid` and `layers` accept a `note` per
node, set beside the tier. Any node may carry `emphasis: primary`.

A layout that is missing a required field on any node refuses to build and names
the node, rather than silently placing it at position zero.

## Mechanism and concept diagrams

Topology is scientific content, so it is never inferred. Write a spec in
`canonical/diagram_specs/<FIGURE_ID>.yaml` with nodes, edges and a `source`,
confirm it against the manuscript, and set `confirmed: true`. An unconfirmed or
missing spec refuses to build.

## What this route does not do

It does not call an image model, and it does not run OA image review — there is
no generated art to second-guess. The content is exactly what the cited source
says, so a human confirms it against that source directly. Like every other
lane, it ends at `PENDING_HUMAN_APPROVAL`.
