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
window.TFCS_CAPTURE = { endpoint: '', mode: 'opaque' };
//                                ^ paste the URL here
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

| Field | Notes |
| --- | --- |
| `first_name`, `email` | Required. |
| `follow_up_opt_in` | `yes` only when the box is ticked. **Unchecked by default, and declining does not block access** — verified by test. |
| `resource`, `page` | So a second resource later is distinguishable in one sheet. |
| `dwell_ms`, `company_website` | Spam signals. |
| `timestamp` | Added server-side. |

No tracking, no analytics, no third-party scripts, no cookies. `localStorage`
holds one flag (`tfcs-access`) so a returning visitor is not asked twice.

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
