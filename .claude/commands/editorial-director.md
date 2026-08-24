---
description: Run the Editorial Director on a draft (Light Edit, Full Editorial Pass, or Final Proof)
argument-hint: <draft path or article name> [mode] [imprint]
---

Run the **Editorial Director** on the draft identified by: `$ARGUMENTS`

Read `.claude/agents/editorial-director.md` and follow it exactly, which means
reading `editorial/standards/editorial-standard.md` in full before you edit
anything.

## Resolving the arguments

`$ARGUMENTS` is written the way a person talks, not as a strict flag list.
Extract three things from it:

**The draft.** A path, a filename, or an article title. If it is a title rather
than a path, look in `editorial/drafts/` first, then search the repository. If
the draft is not in `editorial/drafts/` but exists elsewhere (an `insights/`
page, a file the user just added), copy it into `editorial/drafts/<slug>.md`
first — converting HTML to clean Markdown if needed — so the original is
preserved before any editing begins.

**The mode.** Match on intent, not exact words:

| Say | Mode |
| --- | --- |
| "full editorial pass", "full pass", "the works", "edit this properly" | **Full Editorial Pass** |
| "light edit", "light pass", "tidy", "clean up" | **Light Edit** |
| "final proof", "proof", "last check before publishing" | **Final Proof** |

If no mode is expressed, **ask which one** — do not default silently. The one
exception: if the piece is Curves Ahead and the request is plainly a first
review, Full Editorial Pass is the imprint default; say that you are assuming
it.

**The imprint.** "Curves Ahead" or "Sklarz Creative Insights". If unstated,
infer from the draft's location or subject, and state the assumption in the
report.

## What to return

All five parts of §11 — verdict, scorecard, key editorial notes, clean edited
version, change summary — written to the two files named in §12, with the
verdict, the scorecard and both file paths summarised in your reply.

**Do not overwrite the draft. Do not edit any file under `insights/`. Do not
publish anything.**

## Examples

```
/editorial-director editorial/drafts/execution-is-cheap.md full editorial pass
/editorial-director "AI Is Making Execution Cheap" — Curves Ahead, full pass
/editorial-director editorial/drafts/execution-is-cheap.md final proof
```
