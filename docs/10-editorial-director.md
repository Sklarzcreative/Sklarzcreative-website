# 10 · The Editorial Director — the publication gate

> The final editorial review every long-form piece passes before it is
> published. Full documentation lives with the system itself, in
> **[`editorial/`](../editorial/README.md)**. This page explains what it is,
> why it exists here, and how it relates to the rest of the build.

---

## The problem it solves

This site sells judgement. The [creative direction](./01-creative-direction.md)
put it plainly: judgement is bought on a single signal — does this person seem
like they know what they're doing? — and the previous site failed that test by
being competent, because competent reads as a template.

Long-form writing fails the same test the same way. A well-organised article
with a clear structure, balanced paragraphs and no errors can still read as
though nobody in particular wrote it. For a consultancy whose product is
clarity, publishing prose that could have come from anywhere is the same
category of error as a cluttered homepage: the work refutes its own argument.

The Editorial Director is the gate against that. It reviews to the standard of a
top professional author, magazine editor, developmental editor and copy editor,
and it protects the human voice rather than sanding it off.

Those standards are the quality bar, not a credential the agent claims. The
brief that commissioned it is explicit on the point, and the reason is the same
one behind rule 6 of the root README: a system built to strip out unearned
assertions cannot open by making one about itself.

## What it is, concretely

A written standard, an agent that loads it, and one command that runs it.

| | |
| --- | --- |
| **The standard** | [`editorial/standards/editorial-standard.md`](../editorial/standards/editorial-standard.md) — the source of truth. Three modes, thirteen categories of AI-associated writing, a structural method, evidence rules, the output contract, and an eleven-point publication gate. |
| **The agent** | `.claude/agents/editorial-director.md` — mechanics only. Contains no editorial rules; it reads the standard. |
| **The command** | `.claude/commands/editorial-director.md` — `/editorial-director <draft> <mode>` |
| **The workflow** | [`editorial/README.md`](../editorial/README.md) |

The separation is the design. There is exactly one place to change what "good"
means, and no way for the agent to drift from a standard a human can read.

## The gate

```
draft
  → Editorial Director · Full Editorial Pass
    → Cassandra's review and approval
      → Editorial Director · Final Proof
        → publish
```

Approval sits in the middle deliberately. The agent does not approve its own
work, and the Final Proof step exists so that language already approved is not
rewritten a second time.

## How it fits the rest of the repository

Three of the repository's existing rules are load-bearing for this system too:

1. **Never assert anything untrue.** The standard's §4.13 and §6 make this
   absolute: the agent flags a missing anecdote, statistic or source; it never
   supplies one. An editing tool that fabricates is worse than no tool.
2. **The original is always preserved.** The same instinct behind
   [`_original-design/`](../../_original-design/RESTORE.md) applies to prose:
   drafts in `editorial/drafts/` are never modified, and the editor's version is
   written beside them, so an edit that flattened the voice can be seen and
   rejected.
3. **Restraint is the deliverable.** §14 of the standard is an explicit brake on
   its own rules. A standard with ninety rules is a filter, not an editor.

## What it does not do

It does not publish. It never writes to `insights/`, never edits a live page,
and never marks a piece published. Moving a cleared article onto the site is a
normal commit made by a human who has read it.

Nothing it produces appears on a published page, either — no page mentions the
agent, the workflow, or how the writing was produced.

## Not indexed

`editorial/` is added to the `Disallow` list in `robots.txt`, alongside `docs/`
and `integrations/`. It is working material on a static host, not content.
