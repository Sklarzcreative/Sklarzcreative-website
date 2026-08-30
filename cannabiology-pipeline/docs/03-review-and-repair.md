# OA review, verdicts and repair

## The reviewer gets context

A reviewer given only an image judges *plausibility*, not manuscript accuracy.
Every review brief carries the manuscript excerpt around the figure's anchor,
the figure's brief, the educational purpose, the negative constraints, the
scientific-accuracy notes, the manual-label list, and — on a repair round — the
prior review and the `preserve` array.

## Findings in, verdict out

The model reports **findings**. `verdict.compute()` decides. Rules:

| Condition | Verdict |
|---|---|
| Fabricated data / generated scientific text / implied precision (MAJOR+) | `REJECTED` |
| Reviewer flags a human decision | `HUMAN_CONFIRMATION_REQUIRED` |
| Repair cap reached with issues open | `REJECTED` |
| Any blocker | `REQUIRES_CORRECTION` |
| Science-category MAJOR | `SCIENTIFIC_VERIFICATION_REQUIRED` |
| Majors over threshold, or preserve damage | `REQUIRES_CORRECTION` |
| Non-generative route | `HUMAN_CONFIRMATION_REQUIRED` |
| Otherwise | `PRODUCTION_READY_BASE_ART` |

Fabrication is `REJECTED`, not `REQUIRES_CORRECTION`: once invented data is
baked into a composition, editing it is not a reliable fix.

Review output is validated against `schemas/oa_review.schema.json` before it can
alter state. Invalid output changes nothing.

## Four repairs

| Action | When | Consumes a generative round? |
|---|---|---|
| `VECTOR_EDIT` | Every finding lives in the overlay — spelling, placement, leaders, legends | **No** |
| `IMAGE_EDIT` | Base art largely correct, local correction needed | Yes |
| `REGENERATE` | Structure or teaching idea wrong; editing less reliable than rebuilding | Yes |
| `HUMAN_CONFIRMATION` | Ambiguous intent, competing valid options, cap reached | Stops automation |

## The preserve contract

Every repair prompt restates what must not change. After a repair the reviewer
checks both whether the issue was fixed **and** whether preserved elements were
damaged (`PRESERVE_DAMAGE`), which blocks approval on its own.
