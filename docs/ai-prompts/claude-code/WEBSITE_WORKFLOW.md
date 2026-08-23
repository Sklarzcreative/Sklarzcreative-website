# Sklarz Creative — standing website workflow

Permanent working rules for **sklarzcreative.com**. This file is imported by
the root `CLAUDE.md`, so it loads into Claude Code's project memory on every
session in this repository.

Companion documents: [`WEBSITE_PROMPT_ARCHIVE.md`](./WEBSITE_PROMPT_ARCHIVE.md) · [`PROMPT_INDEX.md`](./PROMPT_INDEX.md)

---

## The standing workflow

> **Inspect → understand → back up → plan → implement → test → verify → deploy → document**

No stage is optional, and no stage is skipped because a change looks small. The
project's own history is the argument: a one-line copy fix (P-027) turned out
to overturn a standing rule, and a lead-capture form (P-030) shipped against a
platform that had not served the site since 9 August.

| Stage | What it means here |
| --- | --- |
| **Inspect** | Read the files before changing them. Run `git status` and `git log`. Read this file, the root `CLAUDE.md`, and `docs/README.md`. |
| **Understand** | Establish what is actually true — the live host, the production commit, what a page currently says — rather than inheriting an assumption. |
| **Back up** | Preserve rollback capability before anything material. Determine the exact production commit first. |
| **Plan** | State the change and its blast radius before editing. Archive the material prompt (see the capture rule below). |
| **Implement** | Smallest change that does the job. Do not widen scope on your own. |
| **Test** | Desktop and mobile, at real widths. Measure; do not eyeball. |
| **Verify** | Separate what was measured from what cannot be measured until the site is live. Never present an unverifiable item as passing. |
| **Deploy** | Review the diff first. Merging to `main` is deploying. |
| **Document** | Record the deployed commit SHA, the rollback reference, and what was tested. Update the prompt's archive entry. |

---

## Permanent rules

### Before editing

- **Inspect the existing project and instructions before editing.** Read the file you are about to change, in full, rather than assuming its contents.
- **Preserve the approved Sklarz Creative brand system and approved assets.** Navy `#1A2F4B` and gold `#C9A84C` are absolute; no new hues. Three typefaces already in the kit, each with a distinct job — Playfair Display for display and pull-quotes, Montserrat for structural labels, nav, buttons and numerals, Inter for reading. Do not add a typeface.
- **Do not reinterpret or recreate official logo or founder assets.** The logo, the founder headshot, the favicon and the four editorial SVGs are approved artwork. Optimize or re-encode them if asked; do not redraw, restyle or regenerate them. The same applies to signatures — a typographic signature block is acceptable, a facsimile of a real person's handwriting is not yours to invent.

### Positioning

- **Sklarz Creative is a multidisciplinary strategic and creative consultancy** — strategic brand, marketing and creative — that helps expert-led and innovative organisations become clearer, more credible, more discoverable and better equipped to grow. It is **not** a social-media service, a content-production shop, or a graphic-design execution service, and must never be described as one.
- **The founder title is "Founder & Strategic Marketing Consultant"**, with the disciplines stated beneath it: Brand Strategy · Creative Direction · Research & Intelligence · Growth & Partnerships. One senior role plus disciplines reads as a level of practice; a list of six job titles reads as a skills inventory. This title must match in the visible copy and in every `jobTitle` field in the structured data.
- **The six named capabilities** are Brand Strategy; Marketing & Growth Strategy; Creative Direction & Content; Research & Intelligence; Media & Storytelling; Partnerships & Business Development.
- **AI is an operating model, not an identity.** It may be described as one component of the practice, always paired with an explicit statement of what stays human. The site never describes itself as an AI agency.
- **Assert nothing untrue.** No invented metrics, client logos, testimonials, results, credentials or publication dates. If a page does not state a date, omit the field rather than filling it. This is the highest-stakes failure mode on a trust-led brand's own website.

### Backups and rollback

- **Preserve rollback capability before material redesigns or deployments.** Archive first, in its own commit, before touching a live file.
- **Determine the exact production commit before creating a production backup.** Prove it from the deploy history and from what is actually live — do not assume the newest commit is the served one. P-032 in the archive is the worked example of getting this wrong and catching it.
- **Record the rollback branch or commit** in the commit body or the QA record, every time.

**Current rollback state, as of 23 August 2026:**

| Path | Status |
| --- | --- |
| `_original-design/` | Complete pre-redesign site, self-contained with inline CSS, archived from `3e44ab7`. Excluded in `robots.txt` and absent from `sitemap.xml`. |
| `git show 3e44ab7:<file>` | Recovers any single original file from history. |
| `git checkout main` | **No longer a rollback path.** `RESTORE.md` Option 2 says `main` is untouched; that is now stale — `main` received the redesign and is at `a5be572`. |

Fix or annotate `_original-design/RESTORE.md` before relying on it.

### Deployment

- **`sklarzcreative.com` is served by GitHub Pages, deploy-from-branch on `main`.** Merging to `main` is deploying. There is no build step, no framework and no npm.
- **A Netlify project exists but does not serve the domain.** It has skipped every production deploy since 9 August ("account credit usage exceeded"). Do not wire anything to Netlify Forms, Netlify functions or Netlify redirects on the assumption that it is live.
- **GitHub Pages serves static files only.** It cannot process a form post, run a function, or hold a secret. Any feature needing one of those needs a platform decision first, not a form.
- **Review the Git diff before deployment.** Every time, in full.
- **Never deploy a documentation-only or prompt-memory change unless deployment is separately requested.**

### Testing — before deploy

Run these and record the result. Measure rather than eyeball; the house harness
renders every page at **1440 / 834 / 390px**, scrolling each document fully so
every `IntersectionObserver` reveal fires and every lazy image decodes *before*
measuring anything.

- **Test desktop and mobile** at real widths, including narrow phones (360/390/430px), not just one breakpoint.
- **Verify navigation** — desktop nav, the mobile overlay, open/close, Escape, focus movement.
- **Verify links** — every internal link and anchor resolves; every outbound URL still points where intended.
- **Verify CTAs** — the discovery-call booking link and every conversion path.
- **Verify forms** — including the failure path. A form that cannot reach its endpoint must not stand between a visitor and the thing they came for.
- **Verify images and assets** — every file loads, and `width`/`height` match the file's **real intrinsic dimensions**, checked against the file header rather than trusted from the markup.
- **Verify SEO metadata** — title, description, canonical URL, heading order, one `h1` per page, no duplicate ids.
- **Verify social metadata** — Open Graph and Twitter card tags, pointing at an image that exists.
- **Verify structured data parses**, and that no `datePublished` was invented.
- **Verify favicon behaviour** — correct reference and correct MIME type.
- **Verify responsive behaviour** — and confirm no page scrolls horizontally at any width.
- **Check for obvious browser-console errors** — console errors, page errors, failed requests, HTTP ≥ 400.
- **Perform basic accessibility QA** — WCAG AA contrast for every text node against its *true composited background*, accessible names on every link and button, keyboard path, visible focus, 44px tap targets, `prefers-reduced-motion`, and the page rendering complete with JavaScript disabled.

Two harness traps, both of which have produced confidently false results in
this project and are documented in `docs/07-launch-qa.md`:

1. **Fixed overlays.** A fixed transparent header overlays a section that is not its DOM ancestor; walking up the tree resolves its background to body-white and reports every nav link as a false contrast failure. Hit-test the real paint stack, and include the element's own background.
2. **Lazy images.** An image parked far outside the viewport may never have been *asked* to load. That is unknowable, not broken.

**A QA tool that lies is worse than no tool.** Two harness bugs were found in
`1aa56c8` that had been reporting passes for regions they never measured. Treat
a clean report from an unverified harness as unverified.

### Verification — after deploy

Some things cannot be proven locally. Verify these against the live domain and
record the result:

- Load the homepage on a real phone and a real desktop.
- **Confirm Playfair Display is actually rendering.** The build environment's egress proxy blocks Google Fonts, so display type has never been seen in Playfair locally — every local screenshot falls back to Georgia.
- Run Lighthouse / PageSpeed on the homepage and one article; record the numbers.
- `curl -I` a nonexistent path and confirm a real `404`, not `200`.
- Test `www` → apex, and confirm DNS covers both.
- Confirm `CNAME` still contains `sklarzcreative.com`.
- Click the Calendly link and each social destination.
- Check the social share cards in the platform debuggers.
- Check Safari and Firefox — `backdrop-filter`, `text-wrap: balance`, `aspect-ratio` and WebGL precision all vary.
- Check iOS Safari `svh` behaviour on a real device, with the URL bar collapsing.
- **Record the deployed commit SHA.**

### Security and privacy

- **Never expose secrets or private content.** No credential, API key, token or private URL goes into front-end code, into documentation, or into a commit — this is a public repository.
- An email-provider enrolment or any other authenticated call belongs in a server-side function reading its credential from the environment, never in the page.
- Redact before archiving: passwords, API keys, access tokens, credentials, private URLs, unrelated personal information, private client information, private account information, confidential material. Replace with `[REDACTED]`.

### Load-bearing technical constraints

Break these and something visibly fails. Restated from `docs/README.md`:

1. **Every page must open with a dark section** (`.hero` or `.page-hero`). The header is fixed and transparent at scroll-top; a light first section drops the nav type below AA contrast. This is a technical constraint, not a preference.
2. **Small gold text on a light ground must use `--gold-ink`.** Brand gold measures ~2.4:1 on white.
3. **`.page-hero` cannot carry `.is-dark`** — it would erase the hero gradient — so its dark-context overrides are declared separately. Add to that block when you add a component.
4. **Hidden animation start-states stay scoped to `html.js`.** Unscope them and a JavaScript failure yields a blank page.
5. **`prefers-reduced-motion` must resolve reveals to their final state**, never leave them hidden.
6. **Do not load `hero.js` on any page except the homepage.**

---

## The prompt-capture rule

Material website prompts are preserved in
[`WEBSITE_PROMPT_ARCHIVE.md`](./WEBSITE_PROMPT_ARCHIVE.md) and indexed in
[`PROMPT_INDEX.md`](./PROMPT_INDEX.md).

**Archive a prompt when it materially directs** strategy, positioning, copy,
visual design, code, SEO, UX, accessibility, QA, deployment, Git workflow,
backups or rollback.

**Do not archive** trivial conversational messages — acknowledgements,
clarifying questions, "yes go ahead", or anything that produces no decision.

**Sequence:**

1. **Before implementation**, add the prompt to the archive with its exact raw wording, redacted for anything private, marked `VERBATIM`.
2. Assign the next `P-###`, add the row to `PROMPT_INDEX.md`, and mark implementation status *In progress*.
3. **After implementation**, update the entry with: outcome, files changed, tests performed, branch, commit SHA, deployment status, and the rollback reference where applicable.

**Honesty rules for the archive**, which are not negotiable:

- Never rewrite a prompt and call it `VERBATIM`.
- `PARTIAL` when only part of the original wording survives.
- `RECONSTRUCTED` when the prompt is rebuilt from context — and say what it was rebuilt from.
- Never claim to have recovered a prompt that is not actually accessible.
- Never claim something has been "memorized". Memory here means a file committed to this repository and imported through `CLAUDE.md`; nothing else persists between sessions.

---

## Working conventions that have earned their place

Drawn from what actually produced the quality in this repository, and recorded
in `docs/05-build-with-claude.md`:

| Instruction | Why it works |
| --- | --- |
| "Read X fully before changing it" | Stops confident edits to assumed file contents. |
| "Verify it in a real browser and show me" | Converts *done* from written to seen working. |
| "Do not change anything that already works" | Prevents collateral regressions. |
| "Do not invent metrics, logos, or dates" | Models fill gaps plausibly. Highest-stakes failure mode on this brand. |
| "This is a technical constraint, not a preference" | Distinguishes rules that may be traded off from rules that may not. |
| "Explain why a non-obvious value is what it is" | Produces a codebase the next person can safely change. |
| "State what you could NOT verify" | The most valuable line in any QA report. |
| Name the specific failure mode | "A Lambert term makes it look like plastic" prevents the exact wrong turn; "make it look premium" does not. |
| One concern per commit, with a real body | Every material commit here explains the reasoning, the rejected alternatives, and the QA result. That record is why this archive could be built at all. |
