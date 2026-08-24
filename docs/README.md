# Sklarz Creative — design and build documentation

Everything behind the 2026 redesign of sklarzcreative.com: the creative
thinking, the experience design, the technical specification, and the QA
record.

## The documents

| # | Document | What it covers |
| --- | --- | --- |
| 01 | [Creative Direction](./01-creative-direction.md) | The governing idea, mood, colour system, typography, imagery, 3D and copy direction. **Start here.** |
| 02 | [Experience Design](./02-experience-design.md) | Section-by-section UX/UI map, global chrome, secondary pages, responsive strategy. |
| 03 | [The Cinematic Hero](./03-cinematic-hero.md) | Full spec of the 3D hero: geometry, material, lighting, camera, performance, fallbacks. |
| 04 | [Motion Language](./04-motion-language.md) | The unified animation system, its tokens, and what is banned. |
| 05 | [Building It With Claude](./05-build-with-claude.md) | The staged prompts that produced this build, for extending it without writing code. |
| 06 | [Making It Feel $20K+](./06-making-it-feel-premium.md) | Audit of what read as generic before, and the exact change made in each case. |
| 07 | [Final Polish & Launch QA](./07-launch-qa.md) | Every issue found and fixed, what was verified locally, what needs the live domain, and the launch checklist. |
| 08 | [Printed Output](./08-scorecard-capture.md) | How the Scorecard behaves on paper: letterhead, signature block, inked scores, and the print rhythm. |
| 09 | [Lead Capture](./09-lead-capture.md) | How the Scorecard captures a name and email on a static host, why the diagnostic never depends on it, and the one step that switches it on. |
| 10 | [Measurement](./10-measurement.md) | What the capture sheet already tells you, what it cannot, and the analytics decision — with a recommendation. |
| 11 | [Turning it on](./11-turn-it-on.md) | **The runbook.** The five things left, each needing an account only the owner has, in the order that unblocks them. |
| 12 | [The follow-up sequence](./12-email-sequence.md) | Day 0 / 2 / 5, written to paste in — including the five variants that name the reader's weakest signal. |
| 13 | [Case studies](./13-case-studies.md) | The intake questions, the structure, and what happens once the material arrives. |

## Update — 22 August 2026 · strategic positioning pass

The documents above describe the design system, which is unchanged. The
positioning on top of it was sharpened after the first build:

| | Before | After |
| --- | --- | --- |
| Founder title | "strategic marketing consultant, creative director, storyteller, researcher, and founder" | **Founder & Strategic Marketing Consultant**, with a discipline line beneath: Brand Strategy · Creative Direction · Research & Intelligence · Growth & Partnerships |
| Company | "brand and marketing consultancy" | **Strategic brand, marketing and creative consultancy** |
| Promise | "turn complex ideas into positioning, stories and content" | "helps expert-led and innovative organisations become **clearer, more credible, more discoverable, and better equipped to grow**" |
| Capabilities | Brand · Marketing · Content & Social · Creative Direction · Podcast & Media · Research | Brand Strategy · Marketing & Growth Strategy · Creative Direction & Content · Research & Intelligence · Media & Storytelling · **Partnerships & Business Development** |
| AI | absent | An "AI-enabled strategy & systems" section framing it as one component of the practice, with an explicit human-judgement column. Never positioned as an AI agency. |
| Proof | none | A `/work/` page and a homepage Selected Work block, describing scope, role and output — no invented clients, metrics or testimonials |

The reason the founder title changed: a six-item list of job titles reads as a
skills inventory. Stating one senior role and then the disciplines underneath it
reads as a level of practice.

## Update — 23 August 2026 · Scorecard capture & delivery

The Trust-First Content Scorecard became a lead-generation path as well as a
piece of IP. What changed, and the rule it all follows:

> **The visitor gets the tool. The capture is a courtesy.**

| | Before | After |
| --- | --- | --- |
| Statements | Generated in JavaScript | Authored in HTML — scripting off leaves a complete, printable instrument |
| Access | Depended on a form POST and a host-side redirect | Revealed locally and first; the capture POST follows and is never awaited |
| Capture | — | Built, tested, and shipping **switched off** until an endpoint exists. GitHub Pages cannot process a form post, so capture happens off-host — see [09](./09-lead-capture.md) |
| Email sequence | — | Not connected, and not pretended to be |
| Styling | A ~9 KB page-specific `<style>` block | Reconciled into `sklarz.css` §16b. The page carries no `<style>` block |
| Radio groups | Twenty groups all named "Score 0, 1, or 2" | One `<fieldset>`/`<legend>` per statement |
| Result | Total and band | Total, band, and **the weakest signal named** |
| Printout | A styled web page | A document — letterhead, signature block, source URL, and a vertical rhythm sized for paper rather than for a fixed header |

Scoring is unchanged — five categories, twenty statements, 0/1/2, bands at
32 / 24 / 16 — and is re-tested at every boundary.

## Update — 23 August 2026 · measurement and consent

Netlify retired; GitHub Pages is the sole host. Then the Scorecard was made
measurable rather than merely usable:

| | Before | After |
| --- | --- | --- |
| Capture | Netlify Forms | Off-host endpoint, one config line, ships switched off |
| What is recorded | Name, email, consent | Plus the five category scores, the total, the band and **the weakest signal** — written onto the same row when the card is completed |
| Attribution | — | `utm_*` parameters carried with the submission. No cookie, no tracker, no third-party script |
| After completion | A total and a band | A named weakest signal and **one concrete next move for that signal**, then the discovery-call route |
| Privacy | No notice | [`/privacy/`](../privacy/index.html), linked from every footer, describing the actual implementation |
| Social cards | One 1254×1254 square, 1.5 MB, cropped by every platform | Purpose-built 1200×630 cards — one general, one Scorecard-specific — at ~318 KB |

The reason the result is captured separately: the capture happens *before* anyone
has scored anything, so a follow-up that promises advice on your weakest signal
would have no idea which one it was.

## The one-paragraph version

Sklarz Creative sells judgement, and judgement is bought on a single signal:
does this person seem like they know what they're doing? The previous site was
competent — and competent reads as a template. The redesign commits: **"Clarity
is the first act of trust"** as the governing idea, a cinematic navy-and-gold
register built strictly from the two brand constants, three existing typefaces
given three distinct jobs, and one unforgettable 3D object. The site has to
*be* the proof: if the product is clarity, a cluttered site refutes its own
argument. Restraint is the deliverable.

## The code

| Path | What it is |
| --- | --- |
| `assets/css/sklarz.css` | The entire design system. One file, no preprocessor. |
| `assets/js/hero.js` | The WebGL hero. No 3D library. |
| `assets/js/motion.js` | The motion system. One observer, one rAF loop. |
| `index.html` | The homepage — the reference implementation of the system. |
| `_original-design/` | The complete pre-redesign site, plus rollback instructions. |

No build step, no framework, no npm. It is a static site on **GitHub Pages**,
deploy-from-branch on `main` — so pushing to `main` is deploying, and it is free
and unmetered on a public repository. **GitHub Pages is the only host.** No
workflow in the repository writes to it or deploys anywhere else.

## Rolling back

`main` holds the redesign — it is what is live. The previous site is preserved
on the permanent branch `pre-luxury-redesign-2026-08-22` (pinned to `e5aa3a6`)
and, page by page, in [`_original-design/`](../_original-design/RESTORE.md).
Rollback steps are in the [root README](../README.md#rolling-back-the-redesign).

## Rules that are load-bearing

Break these and something visibly fails:

1. **Every page must open with a dark section** (`.hero` or `.page-hero`). The
   header is fixed and transparent at scroll-top; a light first section drops
   the nav type below AA contrast.
2. **Small gold text on a light ground must use `--gold-ink`.** Brand gold
   measures ~2.4:1 on white.
3. **`.page-hero` cannot carry `.is-dark`** (it would erase the hero gradient),
   so its dark-context overrides are declared separately. Add to that block
   when you add a component.
4. **Hidden animation start-states stay scoped to `html.js`.** Unscope them and
   a JavaScript failure yields a blank page.
5. **`prefers-reduced-motion` must resolve reveals to their final state**, never
   leave them hidden.
6. **Never assert anything untrue** — no invented metrics, client logos,
   testimonials, or publication dates.
