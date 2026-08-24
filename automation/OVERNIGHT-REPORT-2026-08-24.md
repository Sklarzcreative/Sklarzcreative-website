# Overnight system report — 24 August 2026

> A systems-engineering pass on the operation around sklarzcreative.com. The
> site was already in strong shape; this night went on the machinery that runs
> it, on making its rules checkable, and on writing it down so another system
> can operate it.
>
> **Nothing was merged. Nothing was deployed. `main` is untouched.**

---

## 1 · Production SHA at start

| | |
| --- | --- |
| `main` | **`6dc946b4b48210ecfcb8e7914c1414831514302c`** — "Capture the result, not just the address; add a privacy notice and real OG cards" |
| Backup branch | **`pre-luxury-redesign-2026-08-22`** at `e5aa3a63530a6f7e9bed699980a7ffaff3c5237b` — confirmed present, untouched |

Both verified unchanged at the end of the session.

## 2 · Branch used

**`claude/overnight-automation-2026-08-24`**, created from `origin/main`, pushed.
Also pushed to `claude/loving-wozniak-ubvqew` at the same commit, because the
session harness designated that name — the two are identical, review either.

No merge to `main`. No force-push to any branch that existed before tonight.

## 3 · Commits created

Eight, in reviewable units, oldest first:

| SHA | What |
| --- | --- |
| `7e2999d` | Establish the automation control plane and the agent contract |
| `6fe00ab` | Make the operational rules executable: schemas, validators, 80 tests |
| `f6d36be` | Build the website QA harness, and prove every check can fail |
| `4adb709` | Write the Make.com runbooks, and make the recovery procedure the hard part |
| `1f1649f` | Keep the content-engine spreadsheet id out of a public repository |
| `c64eb24` | Correct twelve stale sitemap dates, and add the check that keeps them honest |
| `72fb304` | Write the operator manual for whoever runs this next |
| `83fb7db` | Keep the README true after adding automation and a workflow |

`git diff --shortstat origin/main..HEAD` → **68 files changed, 10 478
insertions, 14 deletions.**

## 4 · Files created

| Area | Count | Notes |
| --- | --- | --- |
| QA harness (`automation/qa/`) | 10 files, 2 463 lines | Executable |
| Libraries (`automation/lib/`) | 5 files, 1 297 lines | Executable, tested |
| Tests (`automation/tests/`) | 6 files, 824 lines | 80 tests |
| Scripts (`automation/scripts/`) | 1 file, 135 lines | Queue reliability CLI |
| JSON Schemas | 7 | All with worked examples |
| Examples | 7 | Every one validates, asserted by a test |
| Documentation | 30 files, 4 127 lines | Architecture, 7 agent specs, 7 runbooks, operator manual |
| GitHub Actions | 1 | `.github/workflows/site-qa.yml` |

## 5 · Files changed

Only three files outside `automation/` and `.github/` were touched:

| File | Change | Why |
| --- | --- | --- |
| `robots.txt` | `Disallow: /automation/` added | New directory is source, not content |
| `sitemap.xml` | 12 `lastmod` values corrected `2026-08-22` → `2026-08-23` | They were stale; the real dates come from git |
| `README.md` | Repository tree, deployment note, dependency note, QA section, pointer to the operator manual | Three of its statements stopped being precise once a workflow and a dependency existed |

**No HTML, CSS or JavaScript on the live site was modified.** No visual change.

## 6 · Agent architecture created

Seven narrow agents rather than one autonomous one, split by **blast radius**.
Full contract: [`agents/_shared-contract.md`](./agents/_shared-contract.md).

| # | Agent | Highest verb | Real today? |
| --- | --- | --- | --- |
| 1 | Content Operations | `STAGE` | spec + schema |
| 2 | Publishing Reliability | `DRAFT` | spec + tested code |
| 3 | **Website QA** | `DRAFT` | **executable** |
| 4 | SEO / Discovery | `DRAFT` | spec + static half runs in the harness |
| 5 | Lead Funnel | `STAGE` | spec + tested consent logic |
| 6 | Content Performance | `STAGE` | spec + schema |
| 7 | Case Study Builder | `STAGE` | spec + schema + intake |

The permission ladder is the load-bearing idea: `READ` → `DRAFT` → `STAGE` →
`APPROVE` → `PUBLISH` → `DELETE`, and **no agent holds the last three.**
`APPROVE` is a human's because approval spends a named person's professional
reputation. `PUBLISH` sits with Make executing an already-approved row, because
a stuck queue is embarrassing and fixable while an agent that publishes at 3am
is not. The worst realistic outcome of any of the seven malfunctioning is a bad
draft, a wrong number in a report, or a case study marked `MISSING EVIDENCE`.

## 7 · Automation code created

| Module | What it does |
| --- | --- |
| [`qa/`](./qa/) | The QA harness. 591 checks over 16 routes in ~30s. |
| [`lib/consent.mjs`](./lib/consent.mjs) | The one consent check. Only the string `yes` passes. |
| [`lib/utm.mjs`](./lib/utm.mjs) | UTM vocabulary, builder, auditor. Refuses case drift; refuses to overwrite existing tracking. |
| [`lib/scorecard.mjs`](./lib/scorecard.mjs) | The Scorecard specification as a **test oracle** — not a second implementation. |
| [`lib/queue-audit.mjs`](./lib/queue-audit.mjs) | Publish-queue classification as pure functions. |
| [`lib/validate.mjs`](./lib/validate.mjs) | Dependency-free JSON Schema validator. Throws on keywords it does not support rather than skipping them. |
| [`scripts/audit-queue.mjs`](./scripts/audit-queue.mjs) | Runs the reliability analysis against a queue export. |

One dependency in total — Playwright, because driving a real browser cannot be
reimplemented. Everything else runs on a clean checkout with no install.

## 8 · GitHub Actions created

**`.github/workflows/site-qa.yml`** — the only workflow in the repository.

- `permissions: contents: read` and nothing else. It **cannot** push, comment,
  or deploy.
- `persist-credentials: false` on checkout.
- **References no secret**, so it can leak none.
- `pull_request`, not `pull_request_target` — a fork's code never runs with
  repository context.
- Triggers: pull requests and pushes touching public-site code, nightly at
  03:20 UTC, and manual dispatch.
- Uploads the JSON report and Markdown summary as an artifact, and writes the
  summary to the run page **even when the QA step failed** — a report only
  visible on green is useless.
- `fetch-depth: 0`, because one check needs per-file git history.

It adds no build step. GitHub Pages deploy-from-branch remains the sole
deployment path.

## 9 · Tests run

| Suite | Result |
| --- | --- |
| Unit tests (`npm test`) | **80 / 80 pass** |
| QA harness, static + rendered + behaviour | **591 checks · 552 passed · 0 errors · 8 warnings · 31 info · 0 skipped** |
| QA harness with `--live` | **7 skipped** — the environment cannot reach the live domain (see §10) |
| Schema validation | Every committed example validates; asserted by a test so they cannot rot |
| Mutation tests | **6 deliberate defects introduced, 6 caught, all reverted** |

### The mutation tests, because a check that has never failed is a check you have no reason to believe

| Mutation | Caught as |
| --- | --- |
| `openScorecard()` moved inside the capture's `.then()` — breaking fail-open | `behaviour.scorecard-fails-open` |
| Band threshold shifted 32 → 33 | `behaviour.scorecard-band` |
| A canonical pointed at `www` | `static.canonical-origin` + `static.og-url-canonical` |
| Two pages given the same `<title>` | `static.title-duplicate` |
| `og:image` pointed at the 1254×1254 logo | `static.og-image-aspect` + `static.og-image-declared` |
| A sitemap `lastmod` set to a future date | `static.sitemap-lastmod-accuracy` |

## 10 · Results — and what was NOT verified

### Verified, in this environment, on this branch

- The unit suite passes.
- The QA suite reports zero errors across all 16 routes at 1440 / 834 / 390px.
- The Scorecard's arithmetic matches the specification at every band boundary
  (0, 15/16, 23/24, 31/32, 39, 40) plus the tie and five-way-tie cases, driven
  through the real form in Chromium 141.
- **The Scorecard fails open** — with a capture endpoint configured and
  unreachable, access is still granted. Confirmed by mutation that the check
  catches the opposite.
- Every page renders with scripting disabled; no content is left invisible.
- `prefers-reduced-motion` leaves no reveal unresolved.
- The mobile menu opens, takes focus, and returns focus to the toggle on Escape.
- Every internal link and asset resolves to a file on disk.
- Every declared image dimension matches the real file header.
- The sitemap and disk agree in both directions; every `lastmod` now matches
  its page's git history.
- No credential anywhere in the working tree or in 105 commits (§11).

### NOT verified — do not treat as passing

| Item | Why | How to check |
| --- | --- | --- |
| **Everything on the live domain** | This environment's egress policy answers HTTP 403 to `sklarzcreative.com`. Confirmed against the proxy's own status endpoint. | `node automation/qa/run.mjs --live` from an unrestricted network |
| Real 404 status, `www` → apex, `http` → `https` | Same | Same, or `curl -I` |
| Share images fetchable over HTTPS | Same | Same |
| Calendly and social destinations | Same | Click each one |
| **Typography** | Google Fonts is blocked so page loads are deterministic. **Every rendered measurement was taken with the fallback type stack, not Playfair Display.** An overflow finding is a real signal; a clean overflow result is *not* proof the real typography does not overflow. | Load the site and look |
| Lighthouse / Core Web Vitals | Needs the live domain | PageSpeed Insights |
| Safari / Firefox / iOS | No browser but Chromium here | Real devices |
| Anything in Make, Google Sheets, or an email provider | No access, and nothing was touched | §13, §14 |

The `--live` run reports verdict **`incomplete`**, not `pass`, precisely because
of this. That is the harness working: a check it could not run is never reported
as a pass.

## 11 · Security findings

**No credential was found anywhere** — not in the working tree, not in any of
the 105 commits reachable from any branch. Scanned for generic high-entropy
patterns and provider-specific ones covering Google (API keys, service-account
JSON, OAuth), Make, Mailchimp, SendGrid, Postmark, ConvertKit, Resend,
MailerLite, Stripe, Twilio, Slack, AWS, GitHub tokens, OpenAI, Anthropic, JWTs,
private-key PEM blocks, and basic-auth URLs.

**One finding, which I had introduced myself earlier in the night.**

| | |
| --- | --- |
| What | The content engine's Google Sheets id, written into `architecture.md` and runbook B |
| Severity | **Low.** A Sheets id is not a credential — access is governed by the sheet's sharing settings, not by knowing its id. |
| Why it still matters | This repository is public. An id published here is permanently discoverable: it tells a reader the sheet exists, invites an access attempt, and becomes an effective access token the moment anyone sets that sheet to "anyone with the link" — a change made in a different UI by someone who will not remember this file. |
| Action taken | Removed from the current state **and** from the four commits that carried it, before the branch's first push. It has therefore never reached GitHub. No pushed history was rewritten; nothing was force-pushed. |
| Rotation needed | **No.** Nothing was exposed. |

**One thing to check on your side:** confirm that sheet's sharing is
*restricted*, not "anyone with the link". That is the setting that would have
made the id matter, and it is worth knowing either way.

GitHub's own secret scanning could not be used as an independent cross-check —
the repository does not have Advanced Security enabled. The audit above is
therefore mine alone, which is worth knowing when weighing it.

Also noted, and correct as-is: `.gitignore` already blocks `.env`, `*.pem`,
`*.key`, `credentials*` and `secrets*`, so an accidental `git add .` cannot
publish one. `window.TFCS_CAPTURE.endpoint` is still `''` — untouched.

## 12 · Website findings

**No P0 or P1 defect was found.** The site is in genuinely good technical shape,
and most of what the brief anticipated had already been fixed.

### Fixed

| Finding | Priority | Action |
| --- | --- | --- |
| Twelve sitemap `lastmod` values claimed `2026-08-22` for pages whose content last changed on the 23rd | P3 | Corrected from git history, and a check added so it stops drifting |
| `/automation/` crawlable | P3 | `robots.txt` disallow added; the harness asserts all four disallows |

### Already correct — checked, nothing to do

- **The social share images are already 1200×630** (`social-share.png` and
  `social-share-scorecard.png`, ~320 KB each), and both pages declare matching
  `og:image:width` / `og:image:height`. The square-image concern in the brief
  was resolved in the 23 August commit. The harness now reads the real file
  header and cross-checks it against `twitter:card`, so a regression here fails
  the build rather than being noticed by a platform.
- Every page has a unique title and description, a self-referential apex
  canonical, complete Open Graph and Twitter metadata, and valid JSON-LD.
- No fabricated `datePublished` anywhere — and there is now a check that a date
  asserted in structured data must appear in the page's visible text.
- `Index.html` and `trust-is-not-a-vibe.html` are deliberate `noindex` redirect
  stubs, not duplicates. Both are checked for actually redirecting.
- One `<h1>` per page, no skipped heading levels, no duplicate ids, every
  `target="_blank"` carries `rel="noopener"`, every image has an `alt`.

### Reported, not changed

| Finding | Priority | Why I did not change it |
| --- | --- | --- |
| Eight meta descriptions run 166–229 characters, so a search result truncates them | P3 | The truncated tail is crafted brand copy. Rewriting eight descriptions overnight without you is a copywriting decision dressed as a fix. Exact counts are in the QA report; the longest is the homepage at 229. |
| Seven production publishing routes have never been verified against the published-URL and failure-visibility gates | **P1** | See §16. Switching them off would be a real cost with no evidence behind it; verifying them takes minutes each and is the highest-value publishing work available. |
| `404.html` carries a self-canonical | P3 | Harmless on a `noindex` page. Not worth a commit. |

## 13 · Make.com work that still requires UI access

Nothing in this repository can edit Make. Everything below is a runbook to
follow, not a thing that has been built.

| Runbook | Status |
| --- | --- |
| [A · Scorecard capture and follow-up](./runbooks/make-a-scorecard-capture.md) | **ChatGPT owns this live.** The runbook is the contract to satisfy — do not build it twice. |
| [B · Publisher](./runbooks/make-b-publisher.md) | Documented against the existing SC-03 scenario. Two things to add if absent: the `PROCESSING` claim before any platform call, and a selection limit of 5. |
| [C · Failure handling](./runbooks/make-c-failure-handling.md) | The error record, the retry classes, and the **pre-publish re-read** that prevents the duplicate everyone hits. Also the alert on silence, which is the one that would have caught the previous incident. |
| [D · Weekly reporting](./runbooks/make-d-weekly-reporting.md) | Not built. The highest-leverage piece is a scenario that writes a queue snapshot somewhere the reliability analysis can read — without it, nothing here can notice a publishing failure. |
| [Route onboarding](./runbooks/route-onboarding.md) | Eight gates. TikTok, YouTube and Bluesky **remain off**. |

## 14 · Google / email work requiring account authorization

| Task | Needs | Blocked on |
| --- | --- | --- |
| Deploy the Apps Script capture endpoint | Google account | **ChatGPT's live workstream.** Not touched here. |
| Create the lead sheet | Google account | Same |
| Connect an email provider | Provider account + Make connection | Same |
| **Search Console** | A signed-in Google account | Nobody. [One sitting, checklist ready.](./runbooks/seo-search-console.md) Until it is done, every Search Console figure in every report is `NOT AVAILABLE` — which is the correct value, not a gap to fill with an estimate. |
| Platform analytics connections | Each platform | Nobody. Until then every metric reports `NOT AVAILABLE` with its reason, never `0`. |
| Confirm the content-engine sheet's sharing is restricted | Google account | Nobody. See §11. |

## 15 · Items deliberately NOT changed

1. **`window.TFCS_CAPTURE.endpoint`** — still `''`. ChatGPT owns activating
   capture. Not touched, not tested against a live endpoint, not enabled.
2. **No credential, connection or provider was activated.** Anywhere.
3. **TikTok, YouTube and Bluesky publishing.** Not added. YouTube and TikTok
   have no video asset to publish; Bluesky's audience overlaps what is already
   covered; and seven existing routes are unverified. Adding an eighth widens
   exactly the surface that failed once already.
4. **No visual redesign.** Not one shadow, spacing value or animation. The brief
   said not to, and the QA pass found no measurable defect that would justify it.
5. **The eight long meta descriptions.** Brand copy — your call, not mine.
6. **No analytics.** `/privacy/` states there is none and that statement is
   load-bearing. Adding it is a consent decision with a privacy-page edit in the
   same commit.
7. **`main`.** Not merged to, not pushed to, not touched.
8. **`pre-luxury-redesign-2026-08-22`.** Verified present and untouched.
9. **`_original-design/`.** Untouched.
10. **No case study written.** The system for them is real and empty, because no
    evidence was supplied. Inventing one is the single thing the Case Study
    agent exists to prevent.

## 16 · Ranked remaining issues

### P0 — broken / security / data loss
**None.**

### P1 — lead generation or publishing reliability

| | Issue | Recommended action |
| --- | --- | --- |
| P1-a | **Nothing can observe publishing health.** Reading the queue needs a Google credential, which must not live in a public repository. Every publishing figure in the health report is `null` — honest, and it means an automated run cannot notice a failure. | Have a Make scenario write a queue snapshot somewhere an authorised run can read, or run `audit-queue.mjs` against a weekly export. Runbook D. |
| P1-b | **Seven production routes are unverified** against gate 4 (a published URL is captured) and gate 7 (a failure is visible). An unverified route is where the last incident lived. | Two checks per route, minutes each: confirm a recent `published_url` exists and opens, and confirm a deliberately broken attempt produces an alert. |
| P1-c | **No alert on silence.** The previous incident produced no error, so an error-only monitor would not have caught it. | Runbook C's fourth alert row: any `APPROVED` row 90 minutes past its time with no error. |

### P2 — growth / measurement

| | Issue | Recommended action |
| --- | --- | --- |
| P2-a | Search Console not connected — nothing is known about how the site is actually found | [One signed-in sitting](./runbooks/seo-search-console.md) |
| P2-b | No platform analytics connections; every metric is `NOT AVAILABLE` | Start with LinkedIn, which does most of the work for this positioning |
| P2-c | Site traffic is unknowable by design | A real decision to make deliberately, with a `/privacy/` edit, or not at all |
| P2-d | No case study exists | Fill in [the intake](./examples/case-study.intake.md). **Anonymous is the recommended default** — anonymised-but-true ships today and beats named-but-embellished. |

### P3 — polish

| | Issue |
| --- | --- |
| P3-a | Eight meta descriptions truncate in search results (166–229 chars) |
| P3-b | Live-domain checks unverified from here — one `--live` run from an unrestricted network closes this |
| P3-c | Typography never actually seen; confirm Playfair Display renders live |
| P3-d | `404.html` self-canonical, harmless |

## 17 · Reviewing this tomorrow

```bash
git fetch origin
git checkout claude/overnight-automation-2026-08-24

# Confirm production and the backup are untouched
git rev-parse origin/main                              # 6dc946b… unchanged
git rev-parse origin/pre-luxury-redesign-2026-08-22    # e5aa3a6… unchanged

# What changed on the live site — three files, no HTML/CSS/JS
git diff origin/main..HEAD -- robots.txt sitemap.xml README.md

# Everything else is additive
git diff --stat origin/main..HEAD

# Run it yourself
cd automation
npm ci && npx playwright install chromium
npm test          # expect 80/80
npm run qa        # expect 0 errors, 8 warnings
npm run qa:live   # from an unrestricted network — this is the gap I could not close
```

Then read, in this order:

1. [`automation/README.md`](./README.md) — the operator manual. Its two most
   important sections are "Things an AI must never do autonomously" and "What is
   real today, and what is a document".
2. [`automation/architecture.md`](./architecture.md) — both pipelines and the
   ownership table.
3. [`automation/agents/_shared-contract.md`](./agents/_shared-contract.md) — the
   permission ladder.
4. [`automation/runbooks/incident-recovery.md`](./runbooks/incident-recovery.md)
   — worth reading **before** you ever need it.

### Recommended merge order

The commits are independent enough to cherry-pick, but this order minimises
review risk:

| Order | Commits | Risk | Note |
| --- | --- | --- | --- |
| 1 | `c64eb24` (sitemap + robots + the lastmod check) | **Touches the live site.** Lowest risk of the three site changes and the only one with a user-visible effect (a crawler-visible one). | Review the sitemap diff — it is 12 date changes |
| 2 | `83fb7db` (README) | Documentation only | |
| 3 | `7e2999d`, `6fe00ab`, `4adb709`, `1f1649f`, `72fb304` (all of `automation/`) | **Cannot affect the live site.** Not deployed, not linked, disallowed in `robots.txt`. | Merge whenever |
| 4 | `f6d36be` (the QA harness + workflow) | Adds a workflow that will start running on every PR | Merge last so you see it run once on the merge PR before it becomes routine |

If you want the smallest possible first merge: **just `c64eb24`.** It is three
files, it fixes a real inaccuracy, and it stands alone.

## 18 · For ChatGPT, before continuing the Scorecard implementation

**Nothing was activated. The live path is exactly as you left it.**

- `window.TFCS_CAPTURE.endpoint` is still `''`. No endpoint, no credential, no
  provider connection was created, changed or tested against.
- The scorecard page's HTML and JavaScript are **byte-identical to `main`**.
  Two mutations were applied during testing and both were reverted; `git diff
  origin/main..HEAD -- insights/` is empty.

**Five things here are useful to you:**

1. **[`lib/consent.mjs`](./lib/consent.mjs) is the consent contract.** Only the
   exact string `yes`, trimmed and case-insensitive, is consent. `true`,
   `"TRUE"`, `1`, `"y"`, `"on"` are all **no** — a boolean means some system
   converted the value on the person's behalf, and the fix for that is the
   writer, not a wider reader. Match these semantics in the Make filter **and**
   in the provider's own audience rules. Two independent checks is not theatre:
   if one is edited by mistake, the other still refuses.
2. **[`schemas/lead-record.schema.json`](./schemas/lead-record.schema.json) is
   the field contract.** If the live sheet's headers differ, change **the schema
   and the Apps Script `HEADERS` array together, in one commit**, so they cannot
   drift. Two field rules that are cheap to get wrong and expensive to have
   wrong:
   - `total_score: null` means the card was never finished. `0` means someone
     scored zero on twenty statements. Merging them puts a fictional average in
     every report thereafter.
   - `discovery_call_clicked: null` means we were not watching. `false` asserts
     we watched and they did not click.
3. **[Runbook A](./runbooks/make-a-scorecard-capture.md) is the scenario,
   module by module** — trigger, the consent filter, the re-read, the provider
   mapping, the status stamp, the idempotency key, and the manual recovery for
   the two cases that matter (someone enrolled who declined; someone who
   consented and was not enrolled).
4. **The timing fact to design around:** the row is created *before* the scores
   exist. Day 0 can only be generic. Day 2 is the first message that can name
   the weakest signal, and it must **re-read the row** rather than trust the
   trigger's values — and it needs a real fallback for an empty
   `weakest_signal`, because some rows never get scores and that is normal.
5. **The fail-open guarantee is now enforced by a test that fails the build.**
   `behaviour.scorecard-fails-open` drives the real form with the endpoint
   unreachable and asserts access is still granted. It was mutation-tested, so
   it genuinely catches the regression. **If you change the capture ordering,
   run `npm run qa` before pushing** — if that check fails, the change has cost
   a visitor the tool in exchange for a lead record, which is the one trade this
   design refuses.

**One request:** when the endpoint goes live, add nothing about it to this
repository except the endpoint URL in that one config line. Not the spreadsheet
id, not the deployment id, not a provider key. The reasoning is written up in
[`architecture.md`](./architecture.md#why-the-spreadsheet-id-is-not-in-this-repository).

---

## The one-paragraph version

The site did not need redesigning and was not redesigned. What it needed was a
way to know when it breaks, and the operation around it needed writing down. So:
a QA harness that runs 591 checks in thirty seconds and whose two most important
assertions protect the commercial premise rather than a page — that the Scorecard
opens even when its capture fails, and that its arithmetic is what it claims.
Eighty tests around the rules that matter most, including the one that stops
someone who ticked nothing from getting an email. Seven agents, none of which can
publish, approve, send or delete. Runbooks for the parts that need a UI, with the
publishing-recovery procedure written to talk an operator out of the bulk release
that would turn an outage into an incident. And an operator manual that says
plainly which of it executes and which of it is a document — because a
specification described as running software is the most damaging documentation
there is.
