# Autopilot and batch approval

Autopilot removes the per-figure interruption. It does not remove the human
gate — it drives every runnable figure to `PENDING_HUMAN_APPROVAL` and stops
there, so approval becomes one decision over a contact sheet instead of one
interruption per figure.

```bash
python3 -m cannabiology autopilot --confirm-route      # run everything runnable
python3 -m cannabiology package --batch auto           # one contact sheet
python3 -m cannabiology approve --all                  # shows what it would do
python3 -m cannabiology approve --all --yes            # records the approvals
```

`--dry-run` and `--no-network` work here too, so the whole sweep can be
rehearsed without an API key or a single credit.

## It never stops on one bad figure

A failure is recorded with its traceback and the run continues. The summary
groups skips by reason, so "nothing happened" always comes with a why:

```
14 completed, 0 failed, 38 skipped
  route HOLD is not automatable: 6
  route derived, needs --confirm-route: 19
  no confirmed build spec: 4
```

## What batch approval refuses to sweep up

`approve --all` splits pending figures into **clear** and **flagged**, and
approves only the clear ones. A figure is flagged when:

- its review was a **dry-run placeholder**, not a real OA review
- the reviewer recorded **major or minor findings**
- a repair **damaged preserved elements**
- the last verdict was not `PRODUCTION_READY_BASE_ART`
- it took **three or more generative repairs**

Flagged figures are listed with their reasons and held back. `--include-flagged`
approves them anyway; `--exclude ID,ID` holds specific figures back.

Nothing is recorded without `--yes`. The first run always just shows you the
list.

The dry-run rule matters most: a synthetic review looks structurally identical
to a real one, and without this check a full rehearsal would end with forty
figures marked approved on the strength of reviews that never happened.
