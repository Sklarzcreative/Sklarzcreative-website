# Reviews — the editor's versions

Two files per pass, both written by the Editorial Director, neither of which
replaces the draft in `../drafts/`.

| File | Contents |
| --- | --- |
| `<slug>--<mode>-review.md` | Verdict, scorecard, key editorial notes, change summary |
| `<slug>--<mode>-edited.md` | The full clean edited article |

`<mode>` is `light`, `full` or `proof`.

## Passes accumulate; they do not overwrite

A second Full Editorial Pass on the same draft is written as
`<slug>--full-2-edited.md`. The first pass stays where it is.

This matters more than it looks. The standard workflow runs a piece through the
agent twice — Full Editorial Pass, then Final Proof after approval — and the
proof step is only trustworthy if you can see that it left the approved language
alone.

## Reading a review

Start with the scorecard's two columns. The gap between before and after is what
the pass actually bought. If a score barely moved, the notes should say why —
either the draft was already strong on that dimension, or the fix needs a
decision only the author can make.

Then read the notes before the edited version. They name the judgement calls,
including the ones you might reasonably reverse.

## Nothing here is published

Moving a cleared piece onto the site is a separate, human-made commit. The agent
does not write to `insights/`, and a file in this directory carries no
implication that anything is live.
