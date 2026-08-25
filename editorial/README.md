# The Editorial Director

The final editorial gate before anything long-form is published — articles,
newsletter editions, essays, thought-leadership pieces, and any substantial
written asset.

It reviews a draft to the standard of a top professional author, magazine editor,
developmental editor and copy editor, and it protects one thing above all: that
the finished piece reads as though **a specific, intelligent person deliberately
wrote it**, in Cassandra Sklarz's voice, with her ideas and her conclusions
intact.

It is not a polishing tool. Polish is the last ten percent of what it does.

---

## What it actually does

| Pass | What it looks for |
| --- | --- |
| **Structural** | Thesis, architecture, buried leads, sections that do not earn their place |
| **Developmental** | Argument strength, evidence, what is missing |
| **Line** | Sentence by sentence |
| **Humanization** | Rhythm, sentence-length variation, specificity, natural transitions |
| **Originality** | Is there a real thesis and a non-obvious insight, or is this generic internet advice? |
| **Copy** | Grammar, punctuation, citation consistency, formatting |

Alongside those, it hunts thirteen categories of AI-associated writing —
generic openings, empty transitions, the "it's not X, it's Y" reflex,
compulsive three-part lists, rhetorical-question stacking, staccato drama, fake
depth, corporate vocabulary, adjective inflation, section summaries, redundant
conclusions, artificial certainty, and invented personal experience. The full
list, with the reasoning behind each, is §4 of the standard.

### Three things it will never do

1. **Invent an anecdote, client story, statistic or source.** It flags the gap
   and leaves it for you to fill. For a consultancy that sells trustworthiness,
   this is the whole ballgame.
2. **Change your position to make the prose smoother.** If your argument is
   weak, it says so in the notes. It does not quietly swap in its own opinion.
3. **Touch your original draft.** Ever.

---

## Invoking it

```
/editorial-director editorial/drafts/execution-is-cheap.md full editorial pass
```

Or in plain language, which the command is built to parse:

> Run the Curves Ahead Editorial Director on this draft in Full Editorial Pass
> mode.

The draft can be a path, a filename, or an article title. If the piece is not
yet in `editorial/drafts/`, the command copies it there first — converting a
live HTML page into clean Markdown if that is what you pointed it at — so the
original is preserved before a word is edited.

## The three modes

| Mode | Use it when | What it does |
| --- | --- | --- |
| **Light Edit** | A draft that is structurally right | Grammar, repetition, weak wording, awkward transitions, minor AI-style phrasing. Structure preserved almost entirely. |
| **Full Editorial Pass** | A new piece. **Default for Curves Ahead.** | All six passes, in order. Will restructure if the structure is the problem. |
| **Final Proof** | After you have approved the edit | Grammar, punctuation, typos, citations, formatting only. Approved language is not rewritten. |

If you do not name a mode, it asks rather than guessing.

---

## What you get back

Five parts, every time:

**A · Editorial verdict** — one of `READY TO PUBLISH`,
`READY AFTER MINOR EDITS`, `NEEDS SUBSTANTIVE REVISION`,
`NEEDS STRONGER ORIGINAL THESIS`.

**B · Editorial scorecard** — 1–10 on originality, human voice, clarity,
authority, argument strength, specificity, flow, credibility, readability, and
AI-slop risk. Before and after, so you can see what the pass bought. AI-slop
risk is inverted: 10 is severe, 1 is clean.

**C · Key editorial notes** — five to ten real notes. Capped at ten on purpose.
No busywork, no lists of micro-edits.

**D · Clean edited version** — the full publication-ready piece, in its own
file.

**E · Change summary** — what changed and why, readable in thirty seconds.

---

## Where the files go

**The original draft and the editor's version are kept separately, always.**

That separation is the point of the whole directory layout. An editor can make a
piece technically cleaner and less interesting — tighter sentences, less
personality. You need both versions open side by side to catch that and reject
the edits that flattened your voice.

```
editorial/
  drafts/        <slug>.md                   your original. Never modified.
  reviews/       <slug>--<mode>-edited.md    the editor's version
                 <slug>--<mode>-review.md    verdict, scorecard, notes, summary
  standards/                                 what "good" means
  curves-ahead/                              the publication's source of truth
  tools/                                     measurement
```

A second pass on the same draft and mode is numbered (`--full-2-edited.md`)
rather than overwriting the first. The sequence of passes is part of the record.

The agent never writes to `insights/` and never publishes. Moving a cleared
piece onto the site is a separate commit made by a human who has read it.

---

## The publication gate

For **Curves Ahead**, the standard workflow is fixed:

```
draft
  → Editorial Director · Full Editorial Pass
    → Cassandra's review and approval
      → Editorial Director · Final Proof
        → publish
```

Approval sits in the middle by design. The agent does not approve its own work,
and Final Proof exists precisely so that approved language is not rewritten a
second time.

A Curves Ahead piece is only marked `READY TO PUBLISH` when all eleven gate
conditions hold — clear thesis, recognisably human writing, no AI filler,
reduced rhetorical repetition, responsibly framed claims, a genuine point of
view, a strong opening, a conclusion that earns its place, something beyond
generic advice, publication-ready formatting, and no unresolved editorial notes
left in the text. The full list is §13 of the standard.

---

## Where the rules live, and how to change them

| File | What it governs |
| --- | --- |
| [`standards/editorial-standard.md`](./standards/editorial-standard.md) | **The standard.** Modes, slop patterns, structural method, evidence rules, output contract, gate. |
| [`standards/voice-cassandra-sklarz.md`](./standards/voice-cassandra-sklarz.md) | The voice being protected |
| [`standards/imprint-curves-ahead.md`](./standards/imprint-curves-ahead.md) | Curves Ahead's lens and gate |
| [`standards/imprint-sklarz-insights.md`](./standards/imprint-sklarz-insights.md) | Sklarz Creative Insights |
| [`standards/CHANGELOG.md`](./standards/CHANGELOG.md) | **How to revise the standards.** Read before changing any of the above. |
| [`curves-ahead/`](./curves-ahead/README.md) | The Curves Ahead publication source of truth, migrated from Drive — handoff, launch pack, backlog, and the agent's origin brief |
| [`tools/cadence.py`](./tools/cadence.py) | Measures paragraph length, sentence length, first-person density and fragment stacks. Diagnostics, not a score. |
| `.claude/agents/editorial-director.md` | How the agent behaves mechanically |
| `.claude/commands/editorial-director.md` | How it is invoked |

The agent and command files contain **no editorial rules** — they load the
standard. That is deliberate: it means there is exactly one place to change what
"good" means, and no way for the agent to drift from a standard you can read.

A material change to a standard archives the previous version into
`standards/archive/` before editing. The rule and the reasoning are in the
changelog.

---

## Measuring the rhythm

```bash
python3 editorial/tools/cadence.py editorial/drafts/*.md
```

Most editorial findings are arguments. This one is a number, and it turned out
to be the most useful thing the first round of reviews produced:

| | Words/para | Spread | "I" | Stacks |
| --- | --- | --- | --- | --- |
| Curves Ahead 01 | 12.1 | 8.9 | 7 | 3 |
| Curves Ahead 02 | 18.7 | 11.8 | **0** | 1 |
| Curves Ahead 03 | 12.3 | 8.8 | 7 | 7 |

Editions 01 and 03 land within two-tenths of a word of each other across
completely different subjects. Edition 02, written through a different process,
does not share the habit — and contains no first person at all.

That comparison is why the tool exists. It turns "this feels choppy" into
something checkable, and it separates *how a piece was produced* from *how you
write*. The fragment-stack cadence is the former.

**Nothing here is a target.** Writing toward a paragraph-length number would
produce exactly the mechanical prose the standard exists to remove. The numbers
say where to look, not what to do.

One reason first-person density is reported alongside the rest: reducing
AI-associated constructions can strip voice as a side effect, because a writer's
tics and a writer's fingerprints are sometimes the same sentences. That happened
on the first Edition 01 pass and is recorded in the changelog.

## Editing the standard by argument, not by accretion

The most likely way this system degrades is by growing. Every disappointing edit
invites a new rule, and a standard with ninety rules is a filter, not an editor —
§14 exists to resist exactly that.

Before adding a rule, check whether the existing standard already covers the
case and the agent simply applied it badly. Usually it does. A better example
inside an existing section beats a new section almost every time.
