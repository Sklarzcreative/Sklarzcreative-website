# Runbook A · Scorecard lead capture and follow-up

> Google Sheet new row → validate consent → enrich with the result → email
> provider → stamp the status.
>
> **Coordination, 24 August 2026:** ChatGPT is implementing this live. Treat
> this document as the contract to satisfy, not as an instruction to build it
> twice. If the live scenario differs, the live scenario wins on facts and this
> document should be corrected.

**Prerequisite:** capture is switched on — an Apps Script web app deployed from
[`integrations/scorecard-capture.gs`](../../integrations/scorecard-capture.gs)
and its `/exec` URL pasted into `window.TFCS_CAPTURE.endpoint`. Until then this
scenario has nothing to watch. As of this branch the endpoint is still `''`.

---

## Trigger

| | |
| --- | --- |
| Module | **Google Sheets · Watch New Rows** |
| Spreadsheet | the lead sheet created at capture setup |
| Sheet | the first tab (the Apps Script writes to `getSheets()[0]`) |
| Table contains headers | **Yes** — row 1 is the header the script writes and freezes |
| Limit | 20 |
| Schedule | every 15 minutes |

**Why not a webhook.** A webhook would fire the instant a capture landed, which
sounds better and is worse: the row is created *before* the visitor has scored
anything, so the interesting half of the row does not exist yet. A poll every
fifteen minutes costs nothing and arrives when there is something to read.

### The timing fact that shapes everything downstream

```
t+0s     capture lands   → name, email, consent, utm_*     (scores are EMPTY)
t+2-15m  result lands    → the five scores, band, weakest_signal, completed_at
         …or never       → the visitor left. This is normal and common.
```

So: **Day 0 can only be generic. Day 2 is the first message that can name the
weakest signal, and it must re-read the row rather than trust the trigger's
values.** A row that still has no `weakest_signal` at Day 2 needs a fallback,
not a broken merge field.

---

## Step 1 · Consent filter — the load-bearing module

| | |
| --- | --- |
| Module | **Filter** (on the route out of the trigger) |
| Label | `follow_up_opt_in is exactly yes` |
| Condition | `{{trigger.follow_up_opt_in}}` · **Text: Equal to (case insensitive)** · `yes` |

**Use an exact equality, not "contains", not "exists", not a truthiness check.**
The semantics must match
[`automation/lib/consent.mjs`](../lib/consent.mjs): only `yes` is yes.
`TRUE`, `1`, `y`, `on` and a blank are all **no**. Every accidental-enrolment
story is the same story — the check was written inline, twice, slightly
differently, and the person who ticked nothing got the email.

Add a second filter on the same route:

| | |
| --- | --- |
| Label | `not spam` |
| Condition | `{{trigger.spam_reason}}` · **Text: Equal to** · *(empty)* |

Spam-flagged rows are written to the sheet rather than dropped, so a false
positive is visible. They must not be enrolled — a honeypot hit is not a person.

> **The rows this filter stops are still leads.** They are captured, they are in
> the sheet, and they got the tool. Consent gates the follow-up, not the record.

---

## Step 2 · Enrich — read the row again

| | |
| --- | --- |
| Module | **Google Sheets · Search Rows** |
| Filter | `submission_id` equals `{{trigger.submission_id}}` |
| Limit | 1 |

Every message after Day 0 reads its merge values **from this module, not from
the trigger**. The trigger's snapshot was taken before the scores existed.

Then a **Set Variables** module to make the fallbacks explicit rather than
implicit in a template:

| Variable | Value |
| --- | --- |
| `weakest` | `{{ifempty(search.weakest_signal; "")}}` |
| `has_result` | `{{if(ifempty(search.total_score; "") = ""; false; true)}}` |
| `total` | `{{ifempty(search.total_score; "")}}` |

**Never default `total` to `0`.** An empty total means the card was not
finished; a zero means someone scored zero on twenty statements. Merging them
produces a fictional average in every report thereafter, and an email that
tells a real person they scored nothing.

---

## Step 3 · Email provider — add subscriber

| | |
| --- | --- |
| Module | *the provider's* **Add/Update Subscriber** |
| Connection | created once in Make's connection store |
| Credential | **lives in Make, never here.** Referenced in this document only as `<EMAIL_PROVIDER_API_KEY>` |

| Provider field | Source |
| --- | --- |
| email | `{{search.email}}` |
| first_name | `{{search.first_name}}` |
| tag / list | `scorecard` |
| custom: `resource` | `{{search.resource}}` |
| custom: `utm_source` | `{{search.utm_source}}` |
| custom: `utm_campaign` | `{{search.utm_campaign}}` |
| custom: `weakest_signal` | `{{weakest}}` |
| custom: `total_score` | `{{total}}` |
| custom: `submission_id` | `{{search.submission_id}}` |

**Set the provider's own double-opt-in / consent field from
`follow_up_opt_in`, not from the fact that the row reached this module.** Two
independent consent checks are not redundancy theatre: if this filter is ever
edited by mistake, the provider still refuses.

### Sequence timing

| Day | May reference the weakest signal? | Content |
| --- | --- | --- |
| 0 | **No** — the scores usually do not exist yet | Acknowledge use, point back to the interactive version, one general next move |
| 2 | Yes, when `has_result` is true | Name the weakest signal and its one concrete next move. When false: the general version, and an invitation to finish the card |
| 5 | Yes, same condition | The discovery-call route |

**Day 0 must not open by delivering the Scorecard.** The site delivers it
immediately, on the page. An email that opens "here is your scorecard" describes
a flow that no longer exists, and the reader notices.

---

## Step 4 · Stamp the status

| | |
| --- | --- |
| Module | **Google Sheets · Update a Row** |
| Row | from the Search Rows module |
| Field | `email_sequence_status` ← `enrolled` |

Then one update per send, driven by the provider's own webhook or a scheduled
reconciliation: `day0_sent`, `day2_sent`, `day5_sent`, `completed`,
`unsubscribed`, `bounced`, `failed`.

**The sheet holds a mirror; the provider is authoritative.** Where they
disagree, the provider is right. That is why the column exists at all — so a
human can see the state without signing in — and why nothing is ever concluded
from it alone.

---

## Success state

- `email_sequence_status` on the row is not empty
- the subscriber exists at the provider with a `submission_id`
- no row with `follow_up_opt_in ≠ yes` has a status other than `not_enrolled`

That last line is the one to check. It is the assertion the whole scenario
exists to keep true, and it is checkable with one filtered view of the sheet.

## Error state

| Failure | Handling |
| --- | --- |
| Provider API 4xx | Do **not** retry a 4xx — it is a rejected request, not a transient one. Write `email_sequence_status = failed`, and let runbook C alert. |
| Provider API 5xx / timeout | Retry per [runbook C](./make-c-failure-handling.md): 3 attempts, exponential, then `failed`. |
| Sheet unreachable | Make retries the scenario. The row stays unstamped, which is recoverable; a wrongly stamped row is not. |
| Duplicate email at the provider | Update rather than create. Someone taking the Scorecard twice is a returning visitor, not a second person. |
| A row appears twice in the sheet | The trigger's Watch New Rows will not re-read a row, but a manual re-run can. Guard with the idempotency check in runbook C, keyed on `submission_id`. |

## Idempotency

**Key: `submission_id`.** Before enrolling, the Search Rows module has already
found the row; if `email_sequence_status` is already non-empty, exit the route.
A second enrolment is not harmless — it can restart a sequence someone already
finished, which reads as a system that has lost track of them.

## Logging

Per execution: `submission_id`, the raw `follow_up_opt_in` value the filter
decided on, the consent verdict, the provider's response code, and the value
written to `email_sequence_status`.

**Log the raw consent value, not just the verdict.** A wrong enrolment must be
traceable to a value rather than argued about six weeks later.

## Manual recovery

1. **Someone was enrolled who should not have been.** Unsubscribe them at the
   provider immediately. Set `lead_status = unsubscribed` and
   `email_sequence_status = unsubscribed`. Then find the row's raw
   `follow_up_opt_in` value in the log and fix whatever produced it — the value
   is the bug, not the filter.
2. **Someone consented and was not enrolled.** Add them at the provider by
   hand, stamp the row, and check whether the filter is comparing against a
   value the sheet no longer writes.
3. **The sequence fired with an empty weakest signal.** Confirm Day 2 reads from
   Search Rows rather than the trigger, and that the fallback copy exists.
4. **A deletion request.** Delete the row, delete the subscriber, confirm both.
   Record that it was done and when. This is a human action, never automated.
