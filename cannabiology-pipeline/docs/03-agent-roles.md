# Agent roles and handoffs

Six agents, each with one job and one output. Every agent is a subcommand of
`pipeline/cannabiology.py`, so a handoff is a file on disk plus a stage change
in `production-state.json` — not a conversation that has to be re-explained.

| # | Agent | Command | Consumes | Produces |
|---|-------|---------|----------|----------|
| 1 | Figure Tracker | `queue`, `status` | canonical tracker CSV | ranked queue, route, batch, live stage |
| 2 | Figure Prompt | `prompt <FIG>` | prompt library + last repair note | the exact string sent to the generator |
| 3 | Image Generation | `generate <FIG>` | prompt | draft PNG (or dry-run payload) + round number |
| 4 | OA Review | `review <FIG>`, `score <ASSET> k=v` | draft + rubric | scores, findings, verdict, stoplight |
| 5 | Repair | `repair <FIG>` | latest verdict | edit / regenerate decision + correction note |
| 6 | Packaging | `package --batch N` | approved assets | Manny review packet (HTML + CSV) |

## Why state lives outside the tracker

The recovered Drive CSVs are treated as **read-only**. All mutable production
state is written to `00-master-control/production-state.json`. Re-importing the
canonical tracker from Drive therefore can never be clobbered by pipeline
activity, and pipeline activity can never silently rewrite the author's tracker.

## Handoff rules

- Agent 2 always folds the previous round's repair note into the prompt, so a
  correction cannot be lost between rounds.
- Agent 4 never edits the prompt, and Agent 5 never scores. Keeping judgement
  and repair separate is what stops the loop from rationalising a weak draft.
- Agent 5 enforces the cycle cap. On the third failure it sets `BLOCKED` and
  stops, rather than burning credits on a figure that needs a human decision.

## Escalate to a human when

- Cycle cap (2 repairs) is reached.
- A figure's route is `HOLD` — an open author decision blocks it.
- A figure's route is `DATA-DRIVEN` and no verified dataset has been supplied.
- OA review raises `open_scientific_flag` — the art is fine but a claim needs
  the author or a source before it can carry a caption.
