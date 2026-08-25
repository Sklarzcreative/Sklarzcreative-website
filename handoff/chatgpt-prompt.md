# Prompt for ChatGPT Pro — turn on Sklarz Creative lead capture

Copy everything below the line into ChatGPT. Agent/browser mode if you have it;
otherwise it works as a guided walkthrough.

---

You are helping me finish the launch of **sklarzcreative.com**. I am Cassandra
Sklarz, Founder & Strategic Marketing Consultant at Sklarz Creative. The website
is already live and working — **do not redesign anything, do not suggest content
changes, and do not modify the site's code.** Your job is account configuration
only.

## What already exists (do not rebuild any of this)

- The site is live on **GitHub Pages** at `sklarzcreative.com`, deploying from
  the `main` branch of the public repo `Sklarzcreative/Sklarzcreative-website`.
  No build step, no framework.
- A free diagnostic tool, the **Trust-First Content Scorecard**, is live at
  `https://sklarzcreative.com/insights/resources/trust-first-content-scorecard/`
  — 20 statements, 5 trust signals (Clarity, Consistency, Credibility,
  Connection, Conversion), scored 0–40.
- The lead-capture front end is **already built and tested**. It is switched off
  because one config value is empty. Turning it on is task 1.
- A privacy notice is live at `/sklarzcreative.com/privacy/`.
- Email copy for the follow-up sequence is already written. You do not need to
  write it.

## Your tasks, in order

### Task 1 — Deploy the Google Apps Script capture endpoint

1. Create a new Google Sheet named **Sklarz Creative — Scorecard leads**.
2. In that sheet: **Extensions → Apps Script**. Delete the placeholder
   `myFunction` stub.
3. Fetch the full contents of this file and paste it in, unmodified:
   `https://raw.githubusercontent.com/Sklarzcreative/Sklarzcreative-website/main/integrations/scorecard-capture.gs`
   **Do not rewrite, "improve", or reformat this script.** It is tested, and the
   column order is depended on elsewhere. Paste it exactly. Save.
4. **Deploy → New deployment.** Click the gear next to "Select type" → **Web app**.
   - Description: `scorecard capture v1`
   - **Execute as: Me**
   - **Who has access: Anyone**
5. Authorise it. You will hit a *"Google hasn't verified this app"* screen —
   this is my own script in my own account, so choose **Advanced → Go to … (unsafe)**.
6. Copy the **Web app URL**. It ends in `/exec`.

**Report this URL back to me.** It is a write-only endpoint, not a credential —
it accepts a POST and returns `{"ok":true}`, and cannot read the sheet.

### Task 2 — Confirm the round trip

I will paste the URL into the site and push. Once I confirm it is live:

1. Open the Scorecard page in a **private/incognito window**.
2. Submit a test name and email, ticking the consent box.
3. Confirm the Scorecard opens **immediately** — it must not wait on the network.
4. Confirm a row appears in the sheet, with a header row auto-created.
5. Answer all 20 statements. Confirm **that same row** gains `total_score`, the
   five category columns, `weakest_signal`, `band`, and `completed_at`.
6. **Delete the test row** so it never enters the email sequence.

If no row appears but the Scorecard still opened, that is the intended
fail-open behaviour, not a bug. Check the `/exec` URL is exact and that access
is set to `Anyone`.

### Task 3 — Build the Make.com scenario

**The email platform is Kit** (formerly ConvertKit) — the account already
exists, do not create a new one.

In Kit, create three **custom fields**, named lowercase with underscores exactly
as written: `weakest_signal` (text), `total_score` (number), `band` (text).
`first_name` is built into Kit already — do not create a duplicate. Create these
before anything else; Kit does not backfill a field that did not exist when a
subscriber was added.

Then create the tag `trust-first-scorecard`.

Also check and report back whether **Sequences and Visual Automations** are
available on my current Kit plan. Do not upgrade or purchase anything — just
tell me.

Then in Make.com:

- **Trigger:** Google Sheets → **Search Rows**, on a **schedule every 15 minutes**.
  **Do not use "Watch New Rows."** The row is created when someone submits their
  email, which is *before* they finish the statements — so Watch New Rows fires
  with every score column empty, and has no way to revisit the row once the
  scores land.
- **Filter — all four must be true:**
  - `follow_up_opt_in` = `yes`
  - `spam_reason` is empty
  - `sequence_state` is empty
  - `total_score` is **not** empty
- **Action 1:** email platform → *Create/Update Subscriber*. Map `email`,
  `first_name`, `weakest_signal`, `total_score`, `band`. Apply the tag
  `trust-first-scorecard`.
- **Action 2:** Google Sheets → *Update a Row*. Set `sequence_state` to `queued`.

Action 2 is **mandatory**. Without it the same row matches on every run and the
person receives the first email every fifteen minutes indefinitely.

Do **not** build the day 0/2/5 delays in Make. The email platform's own
tag-triggered automation handles timing, unsubscribes and bounces, and is what
legally must carry the unsubscribe link. Make's only job is to move one record
across, once.

Test with one row, confirm `sequence_state` flips to `queued`, then delete the
test data from both the sheet and the email platform.

### Task 4 — Search Console and Bing

1. [Google Search Console](https://search.google.com/search-console) → **Add
   property → Domain** (not URL prefix), for `sklarzcreative.com`.
2. It will give you a **TXT** record to add at my DNS provider.
   **⚠️ Add only the TXT record. Do not modify, remove, or "tidy" any existing
   A, AAAA, CNAME or ALIAS record** — those point the domain at GitHub Pages and
   changing them takes the site offline. If anything other than adding one TXT
   record seems necessary, stop and ask me.
3. **Sitemaps → Add a new sitemap →** `sitemap.xml`
4. **URL Inspection → Request indexing**, one at a time:
   - `https://sklarzcreative.com/`
   - `https://sklarzcreative.com/work/`
   - `https://sklarzcreative.com/insights/`
   - `https://sklarzcreative.com/insights/resources/trust-first-content-scorecard/`
   - `https://sklarzcreative.com/insights/the-trust-files/`
   - `https://sklarzcreative.com/insights/clarity-before-content/`
5. [Bing Webmaster Tools](https://www.bing.com/webmasters) → **Import from Google
   Search Console**.

"Discovered – currently not indexed" on a new domain is normal. Do not treat it
as a fault or try to fix it.

## Rules

- **Never put an API key, password, or private token into any file that ends up
  in the repository.** The repo is public. The Apps Script `/exec` URL is not a
  credential and is fine; anything else is not.
- **Do not invent data.** No sample leads, no placeholder testimonials, no
  filler rows in the sheet beyond a test you then delete.
- **Do not change the site's DNS records** other than adding the one TXT record.
- **Do not edit the repository** unless I explicitly ask. Report values back to
  me instead.
- If a step fails, tell me exactly what you saw. Do not work around it by
  changing the architecture.

## What to report back

1. The Apps Script `/exec` URL.
2. Whether the test row appeared, and whether the scores wrote back to that
   same row.
3. Which email platform you set up, and confirmation the four custom fields exist.
4. Whether the Make scenario ran and stamped `sequence_state`.
5. Search Console verification status and whether the sitemap was accepted.
6. Anything you could not complete, and why.
