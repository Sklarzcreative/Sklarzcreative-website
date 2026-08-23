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
| 08 | [Scorecard Capture & Delivery](./08-scorecard-capture.md) | How the Trust-First Content Scorecard captures a lead, why access never depends on it, and where an email provider connects later. |

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
| Access | Depended on a form POST and a Netlify redirect | Revealed locally and first; the capture POST follows and is not awaited |
| Capture | — | Netlify Forms `trust-first-scorecard`: first name, email, honeypot, and an **unchecked, optional** follow-up consent |
| Email sequence | — | Not connected, and not pretended to be. The integration point is documented in [08](./08-scorecard-capture.md) |
| Styling | A ~9 KB page-specific `<style>` block | Reconciled into `sklarz.css` §16b. The page carries no `<style>` block |
| Radio groups | Twenty groups all named "Score 0, 1, or 2" | One `<fieldset>`/`<legend>` per statement |
| Result | Total and band | Total, band, and **the weakest signal named** |

Scoring is unchanged — five categories, twenty statements, 0/1/2, bands at
32 / 24 / 16 — and is re-tested at every boundary.

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

No build step, no framework, no npm. It is a static site on GitHub Pages, and
editing a file is deploying.

## Rolling back

If you don't like the redesign, [`_original-design/RESTORE.md`](../_original-design/RESTORE.md)
documents three ways to undo it. The `main` branch is untouched and still holds
the original site exactly as it shipped.

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
