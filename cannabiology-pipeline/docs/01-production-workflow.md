# Production workflow

## Stages

`QUEUED → PROMPT_READY → GENERATED_DRAFT → OA_REVIEW_1 → REVISION_NEEDED →
REGENERATED → OA_REVIEW_2 → APPROVED_FOR_MANNY → PRESENTED_TO_MANNY →
MANNY_REVISION_REQUESTED → FINAL_APPROVED`, plus `BLOCKED`.

## The four routes

The tracker's *Current Status* column encodes how a figure must be produced.
Only one of the four routes belongs in this image pipeline. This is the single
most important rule in the project — it is what keeps invented science out of
the book.

| Route | Meaning | Where it is produced |
|-------|---------|----------------------|
| `GENERATE` | Base art an image model can legitimately produce | This pipeline |
| `VECTOR-BUILD` | Exact geometry: chemistry, karyotypes, genomics schematics | Illustrator / Canva, by hand |
| `DATA-DRIVEN` | Plots real measured values | Only from a verified dataset |
| `HOLD` | Blocked on an open author decision | Nothing is drawn yet |

A `VECTOR-BUILD` figure sent to an image model produces plausible-looking
chemistry that is wrong. Do not do it.

## Loop, per figure

1. `prompt <FIG>` — assemble prompt (+ any repair note from the last round).
2. `generate <FIG>` — draft; round counter increments.
3. `review <FIG>` — emits the review brief, or calls a vision model.
4. `score <ASSET> k=v …` — record scores; the verdict is computed, not asserted.
5. On `PASS` / `PASS_WITH_MINOR_NOTES` → `APPROVED_FOR_MANNY`, stop.
   On `REVISE` → `repair` chooses a targeted edit.
   On `REGENERATE` → `repair` refines the prompt and regenerates.
6. Max 2 repairs. Third failure sets `BLOCKED` for a human call.

Or run the batch: `run --batch 1`.

## Batch vs sequential

Batch only figures that are **independent and same-route**. Batch 1 deliberately
leads with the four visual-system test comps: they establish the book's visual
grammar, and finding a style problem on comp 1 is far cheaper than finding it on
figure 30. Do not batch a figure whose style depends on a comp that has not yet
passed review.

## Packaging cadence

Package after each meaningful batch, not at the end of the book. Manny sees
progress early, and style corrections arrive while they are still cheap.
