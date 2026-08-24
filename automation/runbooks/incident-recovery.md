# Incident recovery

> The one procedure that must not be improvised.

This system has already had a publishing-reliability incident. The lesson worth
keeping is not "watch the queue more carefully" — it is that **the recovery is
more dangerous than the failure**. The failure costs some silence. The recovery,
done wrong, costs a flood of out-of-date posts under a founder's name, which is
public, irreversible, and reads as a system nobody is running.

So this document exists to be followed at 8am by someone who wants to fix it
fast, and its main job is to talk that person out of clicking "run all".

---

## The rule

> **Never release a backlog in bulk.**
>
> Controlled test → verify the route → release current content → decide, item by
> item, what stale content is still worth posting.

### Why, in one paragraph each

**Releasing into a route that is still broken** produces nothing, and destroys
the diagnosis: you now have forty rows in unknown states and no way to tell
which failed because of the original fault and which failed because of something
you did.

**Releasing into a route that has just been fixed** works — that is the problem.
Forty posts land at once. Anyone following sees a burst of content that is
visibly out of date, and the impression is not "they had an outage", it is "they
are not paying attention". For a consultancy that sells content systems, that is
the worst possible failure to have publicly.

**Most of a backlog is not worth publishing.** A backlog is evidence that a
system stopped, not inventory waiting to go out. Content written for a moment
that has passed does not become valuable by being late.

---

## Step 0 · Stop the publisher

Before diagnosing anything. Turn the scenario off.

A publisher failing unpredictably is worse than a publisher that is off: it
consumes the queue while producing nothing, and it keeps changing the state you
are trying to read.

## Step 1 · Take a snapshot

Export the `MAKE - Publish Queue` tab, or duplicate it, before touching a single
row. Every step below changes state, and without a snapshot there is no
before-picture to compare against.

Then run the reliability analysis against the snapshot:

```bash
node automation/scripts/audit-queue.mjs queue-snapshot.json
```

This gives you the counts, the per-route health, and — importantly — the
recommendation, which is always the controlled-release sequence and never a bulk
release.

## Step 2 · Classify what you are looking at

| What you see | What it means | Priority |
| --- | --- | --- |
| `APPROVED`, past its time, **no error**, no URL | **The silent failure.** The publisher did not run, or ran and said nothing. | P1 — this is the actual incident |
| `APPROVED` or `FAILED` **with** an error | The publisher tried and failed. Loud, therefore already half-diagnosed. | P1, but read the error first |
| `PROCESSING` / `SENDING` / `RETRY`, stale | A run died mid-flight. | P1 |
| `PUBLISHED`, no `published_url` | Unverifiable. It may have published. | P1 — check the platform by hand |
| `HOLD` | **A human decided this waits. NOT PART OF THE INCIDENT.** | Leave it alone |

**Do not touch the `HOLD` rows.** They are the easiest thing to sweep up in a
bulk fix and the most embarrassing to publish: something was deliberately
withheld, and now it is out.

## Step 3 · Find the cause before publishing anything

The reliability analysis clusters failures by platform. Read that first:

- **Failures on one platform, one error text** → a connection. Almost always an
  expired token. Reconnect it.
- **Failures across every platform, starting at one timestamp** → the scenario,
  the schedule, or Make itself. Check the execution history for the gap.
- **No failures at all, just overdue rows** → the scenario did not run. Check
  whether it is enabled, whether the schedule is what you think it is, and
  whether the operations quota was exhausted.
- **`PUBLISHED` with no URL** → the route cannot return a permalink, or the
  status is being stamped before the platform confirms. Fix the stamp, not the
  row.

**Publishing before you know the cause is how a one-hour incident becomes a
two-day one.**

## Step 4 · The controlled test — one item

1. Pick **one** row. Prefer the **least time-sensitive** content you have: an
   evergreen post, not the one tied to a date. If the test goes wrong you want
   the mistake to be boring.
2. Publish it through the **normal route** — a single-row run, or by hand
   through the same scenario. Not through the platform's own UI: posting
   manually proves nothing about the route.
3. Verify **both**:
   - a `published_url` was written to the row, **and**
   - the post is **visible on the platform**. Open it. Look at it.

The second is not optional. The URL is not the proof; the post is. A route can
return a plausible URL for a post that was rejected, and a status write can
succeed for a publish that did not.

**If the test fails, go back to step 3.** Do not try a second item to see
whether it was a one-off. It was not.

## Step 5 · Release current content only

Once one item is verified, release the content that is **still timely** — the
pieces whose moment has not passed.

A handful. Watch each one land. Then stop and look at the queue again.

## Step 6 · Decide, item by item, about the rest

For every remaining overdue row, one question:

> **If this had never been written, would I write it today?**

If no — set it to `CANCELLED` with a note. That is not waste; it is the correct
disposition of content whose moment has gone, and it takes ten seconds.

If yes — reschedule it into the normal calendar, spaced normally. Not all at
once, and not "catching up". There is nothing to catch up to.

Most rows will be a no. That is the expected outcome, and it is the step people
skip because deleting written work feels like waste. Publishing it late is the
more expensive option.

## Step 7 · Close the loop

- [ ] Write down the cause, in the `ERRORS` tab or a note on the queue
- [ ] Fix whatever made the failure **silent** — an alert that did not fire, a
      status that was not written, a monitor that only watched for errors
- [ ] If a route was involved, re-check gates 4 and 7 of
      [route onboarding](./route-onboarding.md): does it capture a published
      URL, and is its failure visible?
- [ ] Re-enable the publisher
- [ ] Run the reliability analysis again and confirm it is quiet

The most important line is the second one. **The incident was not that a publish
failed — publishes fail. The incident was that nobody knew for long enough to
build a backlog.** Fixing the publish without fixing the silence buys you the
same incident again.

---

## What an agent may do during an incident

| | |
| --- | --- |
| **May** | Read the queue. Classify rows. Identify the cause. Produce the report. Recommend the controlled sequence. |
| **May not** | Write to any row. Re-release anything. Re-run a scenario. Change a `HOLD`. Recommend a bulk release. |

If an agent's output ever contains "publish everything overdue", the output is
wrong and the run should be discarded. That string is asserted against in
[`tests/queue-audit.test.mjs`](../tests/queue-audit.test.mjs) precisely so it
cannot arrive by accident.
