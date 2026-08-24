# Runbook C · Failure handling

> Error record → retry policy → alert → **no duplicate publish**.

The last clause is the one to hold on to. A retry mechanism whose worst case is
publishing twice is worse than no retry mechanism at all: a missed post is
invisible, and a duplicate post is public.

---

## The error record

One row per failed attempt, in an `ERRORS` tab of the content engine
spreadsheet. Append-only — never edited, never cleared. The value of an error
log is entirely in its history; a log someone tidies is a log that cannot show
you that this same failure happened in March.

| Field | Notes |
| --- | --- |
| `error_id` | Unique per attempt, not per row |
| `occurred_at` | ISO 8601 |
| `scenario` | e.g. `SC-03 Sklarz Scheduled Publisher` |
| `row_id`, `content_id`, `platform` | What was being published |
| `attempt_count` | Which attempt this was |
| `http_status` | Where the platform gave one |
| `error_text` | **Verbatim.** Never summarised. |
| `error_class` | `auth` · `rate_limit` · `validation` · `asset` · `network` · `platform_5xx` · `unknown` |
| `retryable` | Derived from `error_class`, per the table below |
| `resolution` | Filled in by a human, later. Blank is honest. |

## Retry policy

**What is retried is decided by the class of error, not by hope.**

| Class | Retry? | Policy |
| --- | --- | --- |
| `network` — timeout, DNS, connection reset | Yes | 3 attempts: 1 min, 5 min, 15 min |
| `platform_5xx` | Yes | 3 attempts: 1 min, 5 min, 15 min |
| `rate_limit` — 429 | Yes | Honour `Retry-After` if present, otherwise 15 min, 60 min. Max 2. |
| `auth` — 401, 403 | **No** | A retry cannot fix an expired token. Alert immediately: a human must reconnect. |
| `validation` — 400, 422 | **No** | The content is wrong. Retrying posts the same wrong content. |
| `asset` — missing or unresolvable media | **No** | Nothing to publish. |
| `unknown` | **No** | Alert. An unclassified error retried blind is how one failure becomes three. |

After the final attempt: `status = FAILED`, and the error record's `retryable`
set to false.

### The retry rule that prevents the duplicate

> **Retry the row you claimed. Never re-select from the queue.**

A retry that re-runs the selection step can pick up a row that *did* publish and
whose status write failed — and publish it again. The retry path takes the
`row_id` it already has and, before publishing, re-reads that row and stops if
`published_url` is now non-empty.

Concretely, before every publish attempt including every retry:

```
1. Re-read the row by row_id.
2. If published_url is not empty  → stop. Set status = PUBLISHED. Log
   "already published, status write had failed". This is a SUCCESS, not an error.
3. If another row shares this idempotency_key and has a published_url
                                  → stop. Set status = CANCELLED,
                                    error = "duplicate of <row_id>".
4. Otherwise publish.
```

Step 2 is the case people forget: the platform accepted the post and the write
back to the sheet failed. Everything then *looks* like a failure, and the
obvious response — retry — publishes twice.

## Alerting

| Condition | Alert | Where |
| --- | --- | --- |
| Any `auth` class error | Immediately | Email to the operator |
| 3+ failures on one platform in 24h | Immediately, once per platform per day | Email |
| Any row `PROCESSING`/`SENDING` for over 60 min | Immediately | Email |
| Any `APPROVED` row over 90 min past its time with no error | **Immediately.** This is the silent failure. | Email |
| A single `platform_5xx` that then succeeded on retry | Never | Log only |

**Alert on the silence, not only on the noise.** The incident this system has
already had was a silent failure: nothing errored, so nothing alerted, and the
queue simply stopped going out. A monitor that only fires on errors would not
have caught it, which is why the fourth row of that table is the important one.

**Deduplicate alerts.** An alert that arrives forty times is an alert that gets
filtered, and a filtered alert is worse than no alert because you believe you
have one.

## No duplicate publish — the defences, in order

1. **The claim.** `status = PROCESSING` before any platform call removes the row
   from the selection filter.
2. **The idempotency key.** `content_id` + `platform` + `scheduled_at`, checked
   against other rows before publishing.
3. **The pre-publish re-read.** Step 2 of the retry rule above, on every attempt.
4. **A small selection limit.** Five rows per run bounds how many mistakes one
   bad run can make.
5. **Duplicate-risk detection after the fact.** The reliability agent flags two
   rows sharing `content_id` + `platform` inside 72 hours — as a *risk*, because
   a deliberate repost is legitimate and only a human knows which it is.

Five overlapping defences for one failure mode is proportionate: it is the only
failure mode in this system that is both irreversible and public.

## Manual recovery

| Situation | What to do |
| --- | --- |
| A token expired | Reconnect it in Make. Then release **one** row and verify the published URL before releasing anything else. |
| A duplicate was published | Delete one on the platform. Set the losing row to `CANCELLED` with a note. Then find which defence failed and why — a duplicate means one of the five above did not hold, and that is the actual bug. |
| A row is stuck `PROCESSING` | Confirm on the platform whether it published. If yes, set `PUBLISHED` and paste the URL by hand. If no, set back to `APPROVED` and let the schedule pick it up. **Check the platform first** — this is the exact situation that produces a duplicate. |
| Errors are accumulating with no pattern | Stop the scenario. A publisher failing unpredictably is worse than a publisher that is off, because it consumes the queue while producing nothing. |
