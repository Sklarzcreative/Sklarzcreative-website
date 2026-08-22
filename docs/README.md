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
