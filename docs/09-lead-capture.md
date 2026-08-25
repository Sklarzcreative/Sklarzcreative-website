# 09 · Lead Capture

> How the Trust-First Content Scorecard captures a name and email on a static
> site, why the diagnostic never depends on it, and the one manual step that
> switches it on.
>
> Implementation: the `TFCS_CAPTURE` declaration and the capture block in
> `insights/resources/trust-first-content-scorecard/index.html`, the form
> components in `assets/css/sklarz.css` §16b, and
> `integrations/scorecard-capture.gs`.

---

## The constraint

`sklarzcreative.com` is served by **GitHub Pages**, which serves static files
and nothing else. It cannot process a form post, run a function, or hold a
secret. So capture has to happen off-host, and the only thing that may live in
this repository is a **public, write-only endpoint URL**.

## The rule that outranks the capture

> **The visitor gets the tool. The capture is a courtesy.**

The ordering in the code is deliberate:

```
validate locally → open the diagnostic → post the capture (never awaited)
```

A capture that fails costs Sklarz Creative a lead record. It must never cost
the visitor the tool. Verified by test: with the endpoint deliberately aborted,
access is still granted and the failure is reported as information.

## Switching it on — the one manual step

The endpoint ships **empty**, which means no ask is shown at all and the
diagnostic opens immediately. That is a deliberate default: a form with nowhere
to post would collect nothing while adding a step in front of a proof asset.

To switch capture on, follow the setup comment at the top of
[`integrations/scorecard-capture.gs`](../integrations/scorecard-capture.gs) —
create a Google Sheet, paste that file into Apps Script, deploy as a web app,
and paste the `/exec` URL into one line of the scorecard page:

```js
window.TFCS_CAPTURE = {
  endpoint: '',              // ← paste the URL here
  mode: 'opaque',            // 'opaque' for Apps Script, 'cors' for a form service
  reportResults: true,       // send the finished scores back against the same submission
  reportAnonymous: false     // also report completions from visitors who never gave an email
};
```

Commit, push, and Pages redeploys. Nothing else changes. The gate appears on
its own, because the head script keys off whether that string is empty.

## Why Google Apps Script → Google Sheets

Weighed against a hosted form service (Formspree, Basin, Getform):

| | Apps Script → Sheets | Hosted form service |
| --- | --- | --- |
| Cost | Free at any volume this tool will see | Free tier, typically ~50 submissions/month |
| Who holds the leads | **Sklarz Creative's own Google account** | A third-party processor |
| Export | The sheet *is* the export | CSV download or API |
| Make.com later | Native Google Sheets connector — no-code | Webhook or connector |
| Delivery confirmation | **No** — see below | Yes |
| Setup | ~5 minutes, one script deploy | ~1 minute, paste a URL |

The deciding factor is the second row. For a consultancy whose product is
trust, not handing client contact details to an extra processor is worth the
five minutes and the loss of delivery confirmation.

### The one real trade-off

Apps Script web apps send no CORS headers. So the POST is deliberately
**fire-and-forget**: `mode: 'no-cors'` with a `text/plain` body, which avoids a
preflight the endpoint would fail. The submission lands, but the browser cannot
read the response.

That is why `mode: 'opaque'` **claims nothing about delivery**. It would be easy
to print "Saved" and be wrong. Check the sheet.

If confirmation matters more than data ownership, switch to a CORS-capable
service and set `mode: 'cors'` — the code path already exists and is tested,
and it reports a real failure when one happens.

## Privacy

Everything above is described in plain language for visitors at
[`/privacy/`](https://sklarzcreative.com/privacy/), which is linked from the
footer of every page and from the Scorecard's own consent copy. **If what is
collected changes, that page changes in the same commit.** It currently states,
accurately: no analytics, no advertising, no cookies set by the site, opt-in
unchecked by default, unsubscribe in every email, deletion on request.

## Spam protection

Three signals, all checked server-side in the Apps Script:

| Signal | Rejects |
| --- | --- |
| `company_website` honeypot | Bots that fill hidden inputs. Off-screen rather than `display:none`, because a bot skipping hidden fields would skip the trap too. |
| `dwell_ms` under 1500 | Anything submitting two fields faster than a human can type them. |
| Malformed email / empty name | Junk. |

Rejected submissions are **written to the sheet with a `spam_reason`** rather
than dropped, so a false positive is visible rather than invisible.

## What is captured

Two messages, one row. The capture creates the row; the result fills in the
score columns on that same row, matched by `submission_id`.

### On submit — `event: 'capture'`

| Field | Notes |
| --- | --- |
| `submission_id` | A UUID minted client-side, stored in `localStorage`, so the result can find its row. |
| `first_name`, `email` | Required. |
| `follow_up_opt_in` | `yes` only when the box is ticked. **Unchecked by default, and declining does not block access** — verified by test. |
| `resource`, `page` | So a second resource later is distinguishable in one sheet. |
| `utm_source` … `utm_term` | Read from the arriving URL, when present. See below. |
| `dwell_ms`, `company_website` | Spam signals. |
| `timestamp` | Added server-side. |

### On completion — `event: 'result'`

| Field | Notes |
| --- | --- |
| `total`, and the five category scores | `clarity`, `consistency`, `credibility`, `connection`, `conversion`. |
| `weakest_signal` | The single lowest category. A tie is reported as a tie, never as a winner. |
| `band` | The result band the total fell into. |
| `completed_at` | ISO timestamp. |

**This is what makes a personalised follow-up possible.** Advice about someone's
weakest signal is only useful if it knows which one it is, and the capture
happens before they have scored anything. Without the second message the sheet
would hold twenty thousand email addresses and no idea what any of them scored.

Three properties worth keeping if this is ever changed:

1. **It reports once.** Changing a score after completing does not re-post.
2. **It carries no name or email** — only the `submission_id`. The identity is
   already on the row.
3. **It is silent and never blocks.** Same fire-and-forget path as the capture.

### Anonymous completions

`reportAnonymous` is **off** by default. Someone who never submitted the form
has not agreed to anything, so nothing about them is sent — even though their
completion would be useful for a completion-rate figure.

Turning it on sends the scores with an empty `submission_id` and **no name or
email**; the Apps Script appends those as standalone rows flagged
`anonymous_result`. That buys a real completion rate at the cost of collecting
usage data from people who did not opt in. It is a judgement call, so it is a
switch rather than a default.

## Campaign attribution, without tracking

If the arriving URL carries `utm_*` parameters they are stored with the
submission:

```
/insights/resources/trust-first-content-scorecard/
  ?utm_source=linkedin&utm_medium=organic
  &utm_campaign=trust_first_scorecard&utm_content=launch_post
```

That gives per-channel attribution with **no cookie, no device identifier, no
third-party script and nothing that follows anyone between sites** — the
parameters were already in the link. It is deliberately the smallest thing that
answers "which post produced this lead".

It is not a substitute for analytics. It cannot tell you how many people
visited and did not convert. Adding GA4 or a privacy-first analytics tool is a
separate decision with its own consent implications, and the privacy notice
would need updating first.

No tracking, no analytics, no third-party scripts, no cookies. `localStorage`
holds two values — an access flag and the `submission_id` — neither of which is
sent anywhere except with a submission the visitor initiated.

## The follow-up sequence

**Not connected, and the site does not claim it is.** The checkbox describes
what would be sent; nothing subscribes anyone to anything.

When it is wired up, do it **outside the front end**: Make.com watching new
rows in the sheet, filtering `follow_up_opt_in = yes`, and calling the email
provider. The provider credential lives in Make.com's connection store.

Two rules hold whatever the tool:

1. `follow_up_opt_in !== 'yes'` enrols nobody. The lead is already captured;
   enrolling someone who declined is the one outcome the checkbox exists to
   prevent.
2. It must never gate access. It runs after the fact, off the visitor's path.

### The Make.com scenario

**Build it from step 4 of [11 · Turning it on](./11-turn-it-on.md).**
That is the authority; this section is why it is shaped the way it is.

An earlier draft of this document proposed a **Watch New Rows** trigger. That is
wrong, and the reason is worth recording so nobody rebuilds it:

- **The row is created before the scores exist.** Watching new rows fires the
  moment someone gives their email — with every score column still empty. Day 0
  could then only be generic, which throws away the one thing that makes this
  sequence worth sending.
- **Watch New Rows has no memory of a row it has already handled.** A row that
  gains scores later is not "new" again, so there is no clean way to come back
  to it.

So the trigger is a **scheduled Search Rows every fifteen minutes**, filtered on
`total_score` being filled — it waits for the person to actually finish — and
Make stamps a `sequence_state` column so the same row is never processed twice.
That column is in `HEADERS` and this script never writes to it; it exists solely
so Make has somewhere to record what it has done.

The cost of that design is that people who capture and never finish are excluded.
That is the right default — there is nothing personalised to say to them — and
[11](./11-turn-it-on.md) describes the optional second scenario for reaching them
later.

### The Day 0 email

The site delivers the Scorecard **immediately, on the page**. An email that opens
by delivering it describes a flow that no longer exists, so Day 0 is not a
delivery email — it hands back the score and says which four fifths of it to
ignore.

**The copy for all three emails now lives in
[12 · The follow-up sequence](./12-email-sequence.md)**, including the five
variants that name the reader's weakest signal.
