# 11 · Turning it on

> Five things left, and every one of them needs an account only you have.
> This is the runbook. Do them in order — each unblocks the next.
>
> **Total: about 75 minutes.** The first two are twelve of those minutes and
> they light up the whole funnel, so do them even if you stop there.

---

## The honest summary of where things stand

Eleven items were raised in the last review. Six are already built and tested,
one is a deliberate omission, and four need you. Here is the whole board:

| # | Item | State |
| --- | --- | --- |
| 1 | Lead capture off | **Built, tested, switched off by design.** Step 1 below. |
| 2 | Capture the *result*, not just the email | ✅ **Already built.** `reportResults: true`. See below. |
| 3 | Email automation | Scenario designed (step 4 below), copy written ([12](./12-email-sequence.md)). Needs your accounts. |
| 4 | Reposition the Day 0 email | ✅ **Done** — rewritten from scratch in [12](./12-email-sequence.md). |
| 5 | Privacy notice | ✅ **Built.** `/privacy/` is live and linked from the footer of all 14 pages. |
| 6 | Measurement | ✅ UTMs built and captured. Analytics decision documented in [10](./10-measurement.md). |
| 7 | Result conversion block | ✅ **Built.** Weakest signal, a specific next move, Book a Call, Email me my result. |
| 8 | Case studies | Intake questions and the template are ready in [13](./13-case-studies.md). Needs your material. |
| 9 | Social sharing image | ✅ **Done.** 1200×630 at 318 KB, plus a Scorecard-specific card. |
| 10 | Search visibility | Step 5 below. Needs your Google account. |
| 11 | Post-launch live QA | Step 6 below. Needs your devices. |

### On #2, because it is worth being precise about

The review was right that capturing an email without the score would be the
wrong architecture — and that is exactly why it is not what got built. The
capture creates a row when someone gives their name; if they go on to finish the
twenty statements, **the five category scores, the total, the band and the
weakest signal are written back onto that same row**, matched by a submission
id. One row per person, scores and all.

It is verified end to end: the result POST carries the same `submission_id`, no
email, fires exactly once, and never blocks the tool. So Email 2 can name the
weakest signal because the sheet knows it.

---

## Step 1 — Deploy the capture endpoint (5 minutes)

This is the only thing standing between the Scorecard and a working funnel.

1. Create a Google Sheet. Name it **Sklarz Creative — Scorecard leads**.
2. **Extensions → Apps Script.** Delete the placeholder `myFunction` stub.
3. Paste the entire contents of [`integrations/scorecard-capture.gs`](../integrations/scorecard-capture.gs).
   Save (the disk icon, or ⌘S).
4. **Deploy → New deployment.** Click the gear beside "Select type" and choose
   **Web app**.
   - **Description:** anything. `scorecard capture v1`.
   - **Execute as:** `Me`
   - **Who has access:** `Anyone` ← this one matters, see the note below.
5. **Deploy.** Google will ask you to authorise it. Because it is your own
   unpublished script, you will get a "Google hasn't verified this app" screen:
   **Advanced → Go to Sklarz Creative — Scorecard leads (unsafe)**. That warning
   is about unverified *third-party* apps; this one is yours, in your account,
   and it is the normal path for a personal Apps Script.
6. Copy the **Web app URL**. It ends in `/exec`. Send it to me, or do step 2
   yourself.

**Why "Anyone" is not a security hole.** Visitors are not signed in to Google,
so anything stricter rejects every real submission. The URL is a *write-only*
endpoint: it accepts a POST and returns `{"ok":true}`. It cannot be used to read
the sheet, enumerate rows, or reach anything else in your account. It is not a
credential, which is why it is safe to put in public HTML — and why no actual
key ever goes near the front end.

## Step 2 — Paste it in (2 minutes)

One line, in
`insights/resources/trust-first-content-scorecard/index.html`:

```js
window.TFCS_CAPTURE = {
  endpoint: 'https://script.google.com/macros/s/AKfy…/exec',   // ← paste here
  mode: 'opaque',
  reportResults: true,
  reportAnonymous: true
};
```

Leave `mode` as `'opaque'`. Apps Script sends no CORS headers, so the browser
must be told not to expect a readable reply. Commit, push to `main`, and it is
live in about thirty seconds.

The moment `endpoint` is non-empty the form appears. While it is empty the form
is hidden and every visitor gets the Scorecard immediately — which is the
current live behaviour, and the reason the site has never asked for an email it
could not record.

## Step 3 — Verify it, then delete your test (2 minutes)

1. Open `/insights/resources/trust-first-content-scorecard/` in a **private
   window** (a normal one may already hold an access flag).
2. Enter a real name and email. Tick the consent box.
3. Confirm the Scorecard opens **immediately** — it should not wait on the
   network.
4. Check the sheet: one row, with the header row auto-created.
5. Answer all twenty statements. Watch the same row gain `total_score`, the five
   categories, `weakest_signal`, `band`, `completed_at`.
6. **Delete that row** so your own test never enters the email sequence.

If nothing arrives: the row is missing but the tool still opened, which is the
design working as intended. Check the `/exec` URL is exact and that "Who has
access" is `Anyone`. Redeploying creates a *new* URL unless you choose **Manage
deployments → edit → Version: New version**, so prefer editing the existing
deployment over making a second one.

---

## Step 4 — Make.com → the email platform (20 minutes)

Do steps 1–3 first. There is nothing for Make to watch until rows exist.

**Pick the email platform first.** Any of MailerLite, Kit (ConvertKit), or
Brevo will do this on a free tier. The one requirement is **custom fields** —
you need somewhere to store `weakest_signal` and `total_score`, or Email 2
cannot be personalised and the whole sequence collapses into a generic
newsletter. Create these fields before touching Make:

| Field | Type |
| --- | --- |
| `first_name` | text |
| `weakest_signal` | text |
| `total_score` | number |
| `band` | text |

### The scenario

**Trigger:** Google Sheets → **Search Rows**, on a **schedule every 15 minutes**.

Not "Watch New Rows". A new row is created the moment someone gives their email
— *before* they have finished the statements. Watching new rows would fire with
every score column still empty, which is precisely the failure the review was
worried about. A scheduled search that filters on a filled-in score waits for
the person to actually finish.

**Filter** — all four must hold:

```
follow_up_opt_in   =  yes
spam_reason        is empty
sequence_state     is empty
total_score        is not empty
```

**Action 1:** email platform → *Create/Update Subscriber*. Map `email`,
`first_name`, `weakest_signal`, `total_score`, `band`. Add tag
`trust-first-scorecard`.

**Action 2:** Google Sheets → *Update a Row*. Set `sequence_state` to `queued`.

That second action is not optional. Without it the filter matches the same row
on the next run and the person gets Day 0 every fifteen minutes forever.

**Then let the email platform own the timing.** Do not build the 0/2/5 day delays
in Make. Every platform has a native automation triggered by a tag, it handles
unsubscribes and bounces for you, and it is the thing legally required to carry a
working unsubscribe link. Make's only job is to move one record across, once.

### Optional refinement, once it is running

People who give an email and never finish the statements are excluded by
`total_score is not empty` — they consented and hear nothing. If you want to
reach them, add a second scenario with `total_score is empty` and
`timestamp` older than 24 hours, stamping `sequence_state` as
`queued-unfinished`, pointing at a shorter two-email version. Worth doing later.
Not worth delaying the launch for.

---

## Step 5 — Search Console and Bing (15 minutes)

1. **[search.google.com/search-console](https://search.google.com/search-console)
   → Add property → Domain** (not URL prefix). A domain property covers
   `sklarzcreative.com`, `www.`, http and https in one go.
2. Google gives you a TXT record. Add it at your DNS provider — the same place
   the apex A records and the `www` CNAME live. **Do not remove or change those.**
   Verification usually completes within minutes, sometimes an hour.
3. **Sitemaps → Add a new sitemap →** `sitemap.xml`.
4. **URL Inspection → Request indexing** for these six, one at a time:
   - `https://sklarzcreative.com/`
   - `https://sklarzcreative.com/work/`
   - `https://sklarzcreative.com/insights/`
   - `https://sklarzcreative.com/insights/resources/trust-first-content-scorecard/`
   - `https://sklarzcreative.com/insights/the-trust-files/`
   - `https://sklarzcreative.com/insights/clarity-before-content/`
5. **[bing.com/webmasters](https://www.bing.com/webmasters)** → *Import from
   Google Search Console*. Thirty seconds, and it carries the sitemap across.
6. Check **Pages** and **Sitemaps** again after a week. Expect a handful of
   "Discovered – currently not indexed" at first; that is normal for a new
   domain and not a defect.

Nothing about the site needs to change for this. `robots.txt`, `sitemap.xml`,
canonicals and the structured-data graph are already in place and clean.

---

## Step 6 — Live device QA (20 minutes)

Everything here needs a real device or a real browser engine. Chromium under a
software rasteriser is all this environment has, so these are genuinely yours to
run. Work down it and note anything that looks wrong.

| Check | Where | Looking for |
| --- | --- | --- |
| Playfair Display renders | any device | ✅ already confirmed on your phone |
| iPhone Safari | your phone | Hero draws; nothing clipped; nav overlay traps focus |
| Android Chrome | any Android | Hero frame rate — if it stutters, tell me and I will drop the ray count |
| Desktop Safari | Mac | `backdrop-filter` on the sticky nav; `text-wrap: balance` on headlines |
| Firefox | any | Same two, plus `aspect-ratio` on the cards |
| `www` → apex | type `www.sklarzcreative.com` | Redirects to `sklarzcreative.com`, no certificate warning |
| Real 404 | `sklarzcreative.com/nope` | The styled 404, not GitHub's default |
| Calendly | every **Book a Call** button | Opens your 30-minute booking page |
| Social profiles | footer icons | Each lands on the right account |
| Link preview | paste the homepage URL into a LinkedIn draft | Landscape card, not a cropped square. Then the Scorecard URL. |
| Lighthouse | Chrome DevTools → Lighthouse → Mobile | Performance and Accessibility. Send me the numbers. |
| Core Web Vitals | Search Console, after a week | Needs real traffic first |

Two of those are worth flagging in advance. **Link previews are cached** by
LinkedIn and Facebook — if you shared the site before the image was replaced,
use LinkedIn's Post Inspector or Facebook's Sharing Debugger to force a refetch,
or you will see the old square card and think it did not work. And **Lighthouse
Performance on mobile will not be perfect** because of the WebGL hero; if it
lands above 80 I would leave it alone.

---

## What is still mine after all of this

- Three case studies, once you send the material — [13](./13-case-studies.md).
- Compressing the four 1.5 MB PNG masters in the Media Kit.
- Whatever step 6 turns up.
