# OA review rubric

One rubric for every figure in the book. Machine-readable source of truth:
[`pipeline/rubric.json`](../pipeline/rubric.json).

## Criteria

Scored 1–5. *Gate* is the minimum for production. *Weight* sets the score share.

| Criterion | W | Gate | The question |
|-----------|---|------|--------------|
| `scientific_plausibility` | 3 | 4 | Malformed anatomy, impossible morphology, invented structures, animal-cell features in a plant cell? |
| `concept_fidelity` | 3 | 4 | Does it teach the one idea in *Educational Purpose*, with the specified composition and panel count? |
| `label_zone_discipline` | 2 | 4 | Free of typeset scientific text, pseudo-Latin, invented axes/numbers/gene names? Clean callout zones reserved? |
| `composition_hierarchy` | 2 | 3 | One idea reads first; negative space; nothing critical cropped. |
| `readability_print` | 2 | 3 | Holds up in print at the intended page treatment. |
| `visual_system_consistency` | 2 | 3 | Restrained botanical/scientific palette; no dispensary clichés. |
| `manny_readiness` | 1 | 3 | Would you put this in front of the author? |

## Verdicts

Computed from the scores, never asserted — so two reviewers scoring the same
numbers always reach the same verdict.

- **REGENERATE** — any criterion ≤ 2, or `scientific_plausibility` ≤ 3, or
  `concept_fidelity` ≤ 2. Structurally wrong: refine the prompt, regenerate.
- **REVISE** — all ≥ 3 but a gate is unmet. Mostly right: targeted edit.
- **PASS_WITH_MINOR_NOTES** — gates met, weighted 0.75–0.85.
- **PASS** — gates met, weighted ≥ 0.85.

`scientific_plausibility` at 3 forces REGENERATE even at a high weighted score.
In a science textbook a beautiful figure that is subtly wrong is worse than an
ugly one, because it will be believed.

## Stoplight

- **GREEN** — pass, no open scientific flag. Ready for Manny.
- **YELLOW** — passed with notes, or carries an open verification flag. Usable.
- **RED** — revise, regenerate, blocked, or cycle cap reached.

## Reviewing without an API key

`review` with `provider: "manual"` writes a `.review-brief.json` next to the
draft containing the rubric, the prompt that was sent, the negative constraints,
the scientific-accuracy notes and the manual-label list. A human — or a
vision-capable model looking at the image — scores it and records the result:

```
cannabiology.py score CH01-IMG-01 \
  scientific_plausibility=4 concept_fidelity=5 label_zone_discipline=5 \
  composition_hierarchy=4 readability_print=4 visual_system_consistency=5 \
  manny_readiness=4 --summary "Grana stacking now correct." [--flag]
```

`--flag` sets the open-scientific-verification flag and forces YELLOW.
