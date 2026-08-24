# Runbook D · Weekly reporting

> Retrieve native analytics where possible → normalise → **report missing data
> explicitly** → summarise.

The third step is the one that makes this report worth reading. A weekly report
that renders "we could not read Instagram" as `0 impressions` will eventually
get a working channel killed, and nobody will ever know why.

Output contract:
[`schemas/weekly-performance-report.schema.json`](../schemas/weekly-performance-report.schema.json).
It enforces the rule structurally — a metric is valid only as
`{value, data_source}` or as `{value: "NOT AVAILABLE", reason}`, so a
number without a source cannot validate. That is deliberate: the rule is easier
to keep when breaking it produces an error.

---

## Trigger

| | |
| --- | --- |
| Module | **Scheduler** |
| Schedule | Mondays, 07:00 in the operator's timezone |
| Window | the previous Monday 00:00 to Sunday 23:59 |

Fixed windows, always. A "last 7 days" window means no two reports are
comparable and every trend is an artefact of when the job happened to run.

---

## Step 1 · What was published

| | |
| --- | --- |
| Module | **Google Sheets · Search Rows** on `MAKE - Publish Queue` |
| Filter | `published_at` within the window **AND** `published_url` is not empty |

**Both conditions.** A row marked `PUBLISHED` with no URL is unverifiable and is
not counted — including here. If it were counted, the report would show
publishing volume the reliability report simultaneously calls broken.

Carry `primary_job` through from the row. It determines which metric each post
is judged on: an `authority` post and an `engagement` post are not comparable on
the same number, and forcing them onto one is how a report produces a confident
wrong answer.

## Step 2 · Retrieve platform analytics

One route per platform. For each, record **three** things: the value, the
`data_source`, and the `retrieved_at`.

| Platform | Route today | `availability` |
| --- | --- | --- |
| LinkedIn (personal) | No API for personal-profile analytics. Signed-in export. | `manual_export` |
| LinkedIn (company) | Possible via the Pages API with an approved app | `manual_export` until connected |
| Instagram | Graph API, business account required | `manual_export` until connected |
| Facebook | Page Insights via Graph API | `manual_export` until connected |
| Threads | No stable analytics API | `not_available` |
| X | Paid API tier | `not_available` |
| Pinterest | Pinterest API | `manual_export` until connected |
| YouTube | YouTube Analytics API | `route_not_onboarded` |
| TikTok | TikTok API | `route_not_onboarded` |
| Bluesky | No analytics | `route_not_onboarded` |
| Newsletter | The email provider's API | `not_available` until a provider exists |

**`not_available` and `route_not_onboarded` are different and must stay
different.** One is a connection to fix; the other is a decision not yet taken.
Collapsing them hides which action is available.

### Where a manual export is the route

Have the scenario write the shape of the report with `availability:
"manual_export"` and empty metrics, then pause for a human to paste the export
into an `ANALYTICS - Manual` tab, keyed by platform and week. Reading it on the
next run turns a manual step into recorded data rather than a lost week.

**Do not skip the platform from the report because the export has not arrived.**
An omitted platform is indistinguishable from a forgotten one. Present it with
its availability and its reason.

## Step 3 · Funnel figures

| Figure | Source | Note |
| --- | --- | --- |
| Site traffic | — | **`NOT AVAILABLE`.** The site carries no analytics by design, and `/privacy/` says so. Do not infer it from anything. |
| Scorecard starts | lead sheet: rows created in the window | Only once capture is live |
| Scorecard completions | lead sheet: rows with `completed_at` in the window | |
| Completion rate | completions ÷ starts | `null` if either side is unknown. Never computed from a guess. |
| Leads | rows created, excluding `spam_reason` rows | |
| Leads by source | group by `utm_source` / `utm_campaign` / `utm_content` | |
| Unattributed leads | rows with no `utm_source` | A real and useful number. Do not assign these to the likeliest post. |
| Consent rate | `follow_up_opt_in = yes` ÷ total | Worth watching: a falling rate usually means the ask has drifted |
| Discovery calls | Calendly, matched by hand | |

### The limitation to restate every single week

> UTM attribution sees **only arrivals that converted**. It can answer "which
> post produced this lead". It cannot answer "how many people read the post and
> left". Anyone reading a channel comparison without that sentence in front of
> them will over-read it.

Adding analytics would answer the second question. It is a consent decision with
a `/privacy/` edit in the same commit, not a technical convenience — see
[`docs/09-lead-capture.md`](../../docs/09-lead-capture.md).

## Step 4 · Normalise

Into the schema. Rules:

1. Every number carries a `data_source` and a `retrieved_at`.
2. Every absence is `{value: "NOT AVAILABLE", reason: "…"}`.
3. **No number is ever computed across sources.** Do not add LinkedIn
   impressions to Instagram impressions: they are different measurements with
   different definitions, and the sum is a number about nothing.
4. Every recommendation carries a `confidence` and an `evidence_count`.
   `insufficient_evidence` is the default and is frequently correct.
5. A `stop` recommendation needs at least `medium` confidence. Killing a channel
   on one bad week is how a working channel gets killed.

## Step 5 · Summarise

Answer the seven questions in
[`agents/content-performance.md`](../agents/content-performance.md). Then:

- **One hypothesis for next week**, phrased so it can be wrong: *if X, then Y,
  measured by Z, decided by <date>*.
- **Last week's hypothesis, judged.** `supported` / `not_supported` /
  `inconclusive` / `not_run`. A hypothesis nobody ever judges is a ritual, not a
  method — and this is the field that makes the difference.

Write the row to `Weekly KPI Tracker`. **One scenario owns that tab**; if
anything else writes to it, the history becomes unreliable and the trend
becomes fiction.

---

## Success state

- A report object that validates against the schema
- Every platform present, with an `availability`
- Every metric either sourced or explicitly `NOT AVAILABLE`
- One hypothesis stated; last week's judged

## Error state

| Failure | Handling |
| --- | --- |
| A platform API errors | `availability: "not_available"`, `reason` = the error. **Not `0`.** |
| The lead sheet is unreachable | Every funnel figure `NOT AVAILABLE` with that reason. Do not emit a partial funnel that looks complete. |
| No posts published in the window | Report an empty window honestly. Do not widen it to find something to say. |
| Two sources disagree | Report both, name the discrepancy, recommend which to trust and why. **Never average them.** |

## Idempotency

Key: the window's start date. Re-running a week overwrites that week's row
rather than appending a second one.

## Logging

Every retrieval attempt: platform, endpoint, status, and the `retrieved_at`.
Every `NOT AVAILABLE` with its reason. The confidence and evidence count behind
each recommendation.

## Manual recovery

1. **A figure looks wrong.** Check its `data_source` first. A number with no
   source is the bug, whatever the number says.
2. **A `0` appears where a platform is not connected.** That is a rule violation,
   not a bad week. Find the module that produced it and make it emit
   `NOT AVAILABLE`.
3. **A recommendation was acted on and was wrong.** Check its `evidence_count`.
   If it was 1, the recommendation should not have carried more than `low`
   confidence, and the fix is to the confidence rule rather than to the analysis.
