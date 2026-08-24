# Editorial standards — changelog and revision rule

The standards in this directory are the source of truth for the Editorial
Director. They will need to change as the publications develop. This file
governs how.

---

## The revision rule

**A material change archives the previous version. It never overwrites it.**

A change is *material* if it would alter a verdict, a score, or the edited text
of a piece that had already been through the agent — a new slop pattern, a
changed mode, a moved gate, a rewritten voice rule.

A change is *editorial housekeeping* if it would not: a typo, a clearer example,
a fixed link.

### Making a material change

```bash
# 1 · Archive the current version, stamped with its version number
cp editorial/standards/editorial-standard.md \
   editorial/standards/archive/editorial-standard-v1.0.md

# 2 · Edit editorial/standards/editorial-standard.md
#     Bump the version line at the top: 1.0 → 1.1 (or 2.0 if the change
#     is large enough that old reviews are no longer comparable)

# 3 · Add a row to the log below saying what changed and why
```

Housekeeping changes are made in place and do not need an archive or a log
entry.

### Why archive rather than rely on git

Git has the history, and git is the authority. The archive exists for a
different reason: a reviewer holding a six-month-old editorial report needs to
read the standard that produced it without running a bisect. The archived file
is for humans comparing verdicts, not for recovering lost work.

---

## Which file to change

| If you want to change… | Edit |
| --- | --- |
| Modes, slop patterns, output contract, gate | `editorial-standard.md` |
| How Cassandra sounds | `voice-cassandra-sklarz.md` |
| What Curves Ahead publishes and how it is judged | `imprint-curves-ahead.md` |
| What Sklarz Creative Insights publishes | `imprint-sklarz-insights.md` |
| How the agent behaves mechanically | `.claude/agents/editorial-director.md` |
| How it is invoked | `.claude/commands/editorial-director.md` |

The agent and command files deliberately contain **no editorial rules**. They
load these documents. If you find yourself adding a standard to the agent file,
it belongs here instead — otherwise the two drift and the agent starts editing
to a standard nobody can find.

---

## Log

| Version | Date | Change | Reason |
| --- | --- | --- | --- |
| 1.0 | 2026-08-24 | Initial standard, voice profile, Curves Ahead and Sklarz Insights imprint profiles, three modes, eleven-point publication gate | First version of the system |
| 1.1 | 2026-08-24 | **`editorial-standard.md`** — replaced "award-winning" with "top professional" as the quality bar, and added an explicit prohibition on the agent describing itself or its work as accredited, award-winning or certified | The commissioning brief ([`../curves-ahead/06-editorial-director-agent-prompt.md`](../curves-ahead/06-editorial-director-agent-prompt.md)) says plainly: "Do not falsely claim the agent is literally accredited or award-winning. Use those standards as the quality bar." v1.0 was drafted before that document was available and had taken the phrasing literally. A system built to strip out unearned assertions cannot open with one about itself. |
| 1.1 | 2026-08-24 | **`imprint-curves-ahead.md`** — rebuilt from the publication's real source material: pillars, departments, the seven-step template, the content gate, the precise AI rule, the never-fabricate-a-premise rule, publication order, and the not-a-corporate-bulletin positioning | v1.0 was inferred from the brief because Curves Ahead had no content in the repo. The Drive material is now migrated to [`../curves-ahead/`](../curves-ahead/README.md) and supersedes the inference. |

---

## Open items

Things known to be unfinished, recorded so they are not mistaken for decisions:

- **Drive and the repo are now two copies of the same material.** Drive is the
  authoring surface; [`../curves-ahead/`](../curves-ahead/README.md) is what the
  agent reads. Nothing keeps them in sync automatically. When a Drive document
  changes materially, re-export it and note it here — otherwise the agent will
  quietly be editing to a stale brief.
- **Scoring calibration — first three Curves Ahead reviews, recorded as
  promised.** All three launch editions have now been through the agent, and the
  scorecard held up without adjustment. Two observations worth keeping:

  | | Words/paragraph | Words/sentence | Instances of "I" | AI-slop risk |
  | --- | --- | --- | --- | --- |
  | Edition 01 | 12.8 | 8.1 | 7 | 8 |
  | Edition 02 | 19.8 | 11.1 | 0 | 3 |
  | Edition 03 | 12.7 | 9.8 | several | 8 |

  **The fragment-stack habit is a property of one production process, not of the
  author.** Editions 01 and 03 share a paragraph length to within a tenth of a
  word; Edition 02, written through a different process, does not have the habit
  at all. This matters for how the agent frames the finding: rejoining those
  paragraphs is closer to restoring the voice than constraining it, and the
  reviews should keep saying so.

  **Credibility can fall as specificity rises.** Edition 01 scored 8 on
  credibility while making no factual claims; Edition 03 scored 6 while making
  two concrete ones without sources. That is the scorecard working correctly —
  unverified specifics cost more than honest abstraction — but it is
  counter-intuitive enough that a review should explain it whenever the two
  scores move in opposite directions.
- **Edition 02 carries a contradiction that needs an author decision.** Its
  existing pack records "removed unnecessary first-person hedging such as 'I
  think'" as a completed improvement. The voice profile treats calibrated
  hedging as a feature of the argument, and the Curves Ahead profile makes first
  person native to the publication. One of those has to give when Edition 02 is
  migrated. Flagged in
  [`../curves-ahead/02a-edition-02-publishing-repurposing-pack.md`](../curves-ahead/02a-edition-02-publishing-repurposing-pack.md);
  do not resolve it silently in either direction.
- **Edition 03 has an unmet fact-check requirement.** Its source document asks
  for current LinkedIn and Substack platform facts to be refreshed against
  official documentation before publication. Until that happens the edition
  cannot pass the gate, and the agent must not verify those claims from memory.
