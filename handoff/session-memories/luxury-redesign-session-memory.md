# Session memory · Luxury redesign

> A reference session handing its knowledge to the master session. Everything
> below is verifiable in git or labelled as conversation context. Existing
> documents are linked, not repeated.

## 1 · Identity and scope

The session that built the luxury redesign, integrated the Trust-First Content
Scorecard, retired Netlify and wrote the activation runbook. Scope: design
system, homepage, secondary pages, the WebGL hero, the Scorecard, lead capture,
privacy, deployment. **Not** editorial/Curves Ahead, **not** the automation
control plane, **not** Cannabiology.

## 2 · Repository, branch, commit

- `Sklarzcreative/Sklarzcreative-website` at `/home/user/Sklarzcreative-website`
- 19 remote branches as of 28 August (was 18 the day before — the remote moves
  under this repository; re-read it, do not trust a cached count)
- Branch `claude/sklarz-creative-redesign-8yd5he`
- Head before this file: `3059e0b` — *Commit to Kit, and add the case study interview prompt*
- Working tree clean, no stash, no untracked files
- 2 ahead / 6 behind `origin/main` (`f07ec8a`)

## 3 · What this session personally implemented

- `assets/css/sklarz.css` — the design system, incl. §16b Scorecard and §17b print
- `assets/js/hero.js` — raymarched SDF hero, one fragment shader, no 3D library
- `assets/js/motion.js` — reveal/motion (GA4 was added here later, by another session)
- `index.html`, `work/`, `insights/` hubs, `media-kit.html`, `404.html`
- `privacy/index.html`; `integrations/scorecard-capture.gs` (24 columns)
- `docs/01`–`13`, `docs/og-card-template.html`, both files under `handoff/`
- `social-share.png`, `social-share-scorecard.png` at 1200×630
- Deleted two contradictory workflows that would have auto-reverted live content

## 4 · Decisions worth carrying forward

**Hero material.** Gold albedo `(0.79, 0.66, 0.30)` needs a reflected sky with
`R/G ≥ 0.84` or green wins; navy is `0.55`, and desaturating it 75% still came
out green. So `env()`'s sky is decoupled from `backdrop()`, which stays navy, and
the highlight rolloff compresses the **peak as a scalar** to preserve hue. Do not
re-tie `env()` to `NAVY`. Full reasoning: `docs/07-launch-qa.md` and the comments
in `assets/js/hero.js`.

**Scorecard fails open, always.** Validate → open the tool → post, and the POST
is never awaited. A failed capture costs a lead record, never the visitor's
access. Every error path adds `tfcs-open`.

**The 20 statements are authored in HTML**, not generated in JS, so a scripting
failure still leaves a complete printable instrument.

**Lead capture is off by design.** `endpoint: ''` hides the form entirely — the
shipped default, not an unfinished state.

**Print CSS.** Browsers drop backgrounds but honour borders and text colour.
`--gold` prints pale grey; `--gold-ink` (`#7A5B10`) survives. See `docs/08`.

**Deployment.** GitHub Pages, deploy-from-branch `main`, root, zero workflows.
**Pushing to `main` is deploying.** Netlify never served the domain and is
retired. DNS verified live: apex on all four Pages IPs, `www` → `sklarzcreative.github.io`.

## 5 · Completed and deployed

Redesign, Scorecard, `/privacy/`, print/PDF output, OG cards, Netlify retirement,
hero material fix. Last verification run: route audit **42/42 clean** at
1440/834/390, plus the Scorecard, capture, result, nav, form-a11y, print and hero
suites.

## 6 · Committed but unmerged (this branch, 2 commits)

`docs/11-turn-it-on.md` (the activation runbook), `docs/12-email-sequence.md`
(Day 0/2/5 written for Kit), `docs/13-case-studies.md` (intake),
`docs/README.md`, and both files under `handoff/`. Documentation only — no page,
stylesheet or script. Merged clean against `origin/main` in a dry run.

## 7 · Proposed, not implemented

Apps Script deployment · Kit custom fields and the `trust-first-scorecard` tag ·
the Make.com scenario · the sequence built in Kit · Search Console and Bing ·
live device QA · three case studies · compressing four ~1.5 MB Media Kit PNGs.

### The endpoint hardening — read this before deploying anything

A branch `backup/scorecard-hardening-2026-08-28` (`fd6e138`) appeared on 28
August, after the assessment I gave earlier in this session, which said no such
patch existed. **That statement is now out of date and this supersedes it.** The
patch is *proposed, not deployed*:

- `docs/16-scorecard-endpoint-hardening.md` — nine numbered findings
- `integrations/scorecard-capture.v2.gs` — proposed replacement, v1 left intact
  so the two can be diffed
- `integrations/scorecard-capture.test.js` — reported 23/23 passing

**Finding 8 is a claimed BLOCKER against the script I wrote.** It says
`SpreadsheetApp.getActiveSpreadsheet()` returns `null` in a web-app deployment,
so v1 throws and loses every submission silently. **I have not verified this
claim** — it cannot be tested outside Apps Script — but if it holds, then
**`docs/11` step 1, which I wrote and handed to the owner, would not work.**
Treat `docs/11` step 1 as suspended until this is resolved. v2 also adds a body
size cap, daily write caps, and formula-injection escaping.

**Hazard:** that branch is 13 ahead / 5 behind `main` and, relative to `main`,
**deletes `audit/index.html` and `trust-discoverability-audit/index.html`** —
both live pages — because it descends from the editorial branch, which predates
them. Do not merge it as-is.

## 8 · Conflicts

**Mechanical** (dry-run vs `origin/main`): `overnight-automation` → `sitemap.xml`;
`sklarz-website-prompt-archive` → `docs/README.md`; `agent/fix-mobile-hero-graphic`
→ `index.html`. Order-dependent: three branches contend over `docs/README.md`;
editorial × automation over `README.md` and `robots.txt`.

**Semantic — git sees nothing, and these are the real risk:**

1. `automation/schemas/lead-record.schema.json` states the Apps Script `HEADERS`
   array implements it. It does not: `lead_id` vs `submission_id`,
   `clarity_score` vs `clarity` (×5), `email_sequence_status` vs
   `sequence_state`, plus three fields the script has no column for. With
   `additionalProperties: false`, a real row fails validation. Recommendation:
   keep the script's names — it is deployed and tested — and correct the schema.
2. Two Make.com specifications. `automation/runbooks/make-a-scorecard-capture.md`
   uses **Watch New Rows** plus a re-read; `docs/11` uses **scheduled Search
   Rows** filtered on a completed score with a `sequence_state` stamp. Both spot
   the same trap — the capture row exists before the scores do. One must be
   deleted, not left as an alternative.
3. Duplicate offer: `/audit/` (in sitemap) and `/trust-discoverability-audit/`
   (not in sitemap), both live, same title.
4. `main` carries both `Index.html` (413 bytes, stub) and `index.html` (36,484
   bytes, the real homepage) — two files differing only in case.

## 9 · Source of truth, and what is stale

Authoritative: `docs/01`–`13`, `docs/README.md`, root `README.md`,
`_original-design/RESTORE.md`.

**Outdated: `docs/10-measurement.md`.** It recommends Cloudflare Web Analytics,
argues against GA4, and states the site carries no third-party script. GA4
(`G-15GX6KDX09`, consent-gated) shipped on 24 August. The document is now wrong
about the site it documents and should be rewritten to record GA4 as shipped,
keeping the Cloudflare reasoning as the recorded alternative.

`docs/09` defers to `docs/11` on the Make trigger; do not revive its earlier
Watch-New-Rows sketch. A `CLAUDE.md` exists **only** on
`claude/sklarz-website-prompt-archive-qwy7h4` — read it before it lands, it
changes how future sessions behave.

## 10 · Protected

`sklarz-creative-logo.png`, `cassandra-sklarz-headshot.jpg.png`,
`assets/images/cassandra-sklarz-headshot.webp` and the `_original-design/` copy —
**no branch modifies any of them**. `insights/` is not to be modified.
`.nojekyll` is what makes `_original-design/` serve.

## 11 · Rollback and safeguards

`pre-luxury-redesign-2026-08-22` at `e5aa3a6` is the permanent rollback point.
`_original-design/RESTORE.md` documents the procedure; its Option 2 was corrected
once, having wrongly claimed `main` was untouched.

There is **no staging environment and no approval gate** between `main` and the
live domain. Reconciliation merges belong on an integration branch, pushed to
`main` once, deliberately.

## 12 · Conversation context — not verifiable in git

Labelled as such because none of it can be checked from the repository:

- **Playfair Display renders correctly on a real device.** Owner-confirmed. It
  was never seen in the build environment — Google Fonts is blocked by the
  egress proxy, so every local screenshot fell back to Georgia.
- **The Scorecard and its PDF work live**, owner-confirmed.
- **The olive cast was reported from the owner's phone**, which is what prompted
  the material fix. That fix was verified only under SwiftShader, a *software*
  rasteriser whose colour does not match a real GPU. Final judgement belongs on a
  device.
- **Netlify was retired on evidence**: its production deploys had been "Skipped
  — account credit usage exceeded" since 9 August, and the live Scorecard route
  only ever existed in the GitHub Pages history.
- The email platform is **Kit**, chosen by the owner. Kit uses Liquid and
  namespaces fields — a bare `{{ first_name }}` renders as *nothing* rather than
  erroring, so every tag must be `{{ subscriber.* }}` with a `default:` filter.
  Whether Sequences and Visual Automations are on the owner's Kit plan is
  **unconfirmed** and must be checked before that work is built.
- An earlier push by another agent regressed accessibility work here; repaired
  by fast-forwarding and rebuilding, never by overwriting.

## 13 · What the master session must preserve

Scorecard fail-open ordering · HTML-authored statements · the
`env()`/`backdrop()` decoupling · `--gold-ink` for print · `endpoint: ''` as a
deliberate default · that pushing to `main` deploys · the rollback branch · and
that no fabricated metric, testimonial, client or outcome goes on this site. On a
consultancy positioned on checkable credibility, invented proof is
self-refuting.

## 14 · Uncertainties

Whether the v2 blocker (Finding 8) is real — unverified here, and it decides
whether `docs/11` step 1 is usable. Whether `Index.html` is deliberate. Whether the five `agent/*` branches (6–10
August, 28–78 behind) hold anything unique — read before deleting, do not assume.
Kit's plan tier. Live HTTP status of any page: this environment's proxy returns
403 for `sklarzcreative.com`, so nothing here was confirmed by fetching the live
site. Real-device rendering in Safari, Firefox and iOS, and Lighthouse scores —
all unmeasured.
