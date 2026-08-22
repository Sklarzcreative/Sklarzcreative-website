# Sklarz Creative — sklarzcreative.com

Official website for Sklarz Creative, a strategy-led brand and marketing
consultancy helping innovative and trust-sensitive companies build credibility
through positioning, research, storytelling, content systems, and creative
direction.

**Live:** [sklarzcreative.com](https://sklarzcreative.com/)

---

## What this repository is

A static site served directly by GitHub Pages. **No build step, no framework,
no npm, no dependencies.** Editing a file and pushing is deploying.

```
index.html                  Homepage — the reference implementation
media-kit.html              Media kit
404.html                    Branded 404
insights/                   Insights hub, The Trust Files, articles, podcast,
                            research notes, resources
assets/css/sklarz.css       The entire design system, one file
assets/js/hero.js           The WebGL hero. No 3D library.
assets/js/motion.js         The motion system
assets/graphics/*.svg       Editorial diagrams
assets/images/              Optimised imagery
docs/                       Design and build documentation — start here
_original-design/           The complete pre-redesign site + rollback guide
```

## Documentation

Everything behind the 2026 redesign lives in **[`docs/`](./docs/README.md)** —
creative direction, the full UX map, the 3D hero specification, the motion
system, the premium audit, and the launch QA record.

## Working on it locally

There is nothing to install. Serve the folder and open it:

```bash
npx http-server -p 8099 -c-1 .
```

Open <http://127.0.0.1:8099/>. `-c-1` disables caching, which you want while
editing.

## Before you change anything

Six rules are load-bearing — break one and something visibly fails:

1. **Every page must open with a dark section** (`.hero` or `.page-hero`). The
   header is fixed and transparent at scroll-top; a light first section drops
   the navigation type below WCAG AA contrast.
2. **Small gold text on a light background must use `--gold-ink`.** Brand gold
   `#C9A84C` measures roughly 2.4:1 on white.
3. **`.page-hero` cannot carry `.is-dark`** — that class sets its own flat
   background and would erase the hero gradient. Its dark-context overrides are
   declared separately in the stylesheet. Add to that block when you add a
   component.
4. **Hidden animation start-states stay scoped to `html.js`.** Unscope them and
   a JavaScript failure renders a blank page instead of a static one.
5. **`prefers-reduced-motion` must resolve reveals to their final state**, never
   leave them hidden.
6. **Never assert anything untrue.** No invented metrics, client logos,
   testimonials, or publication dates. For a consultancy that sells
   trustworthiness, one fabricated number is a strategic error.

The palette is navy `#1A2F4B` and gold `#C9A84C`. Every other colour in the
system is derived from those two — no new hue is introduced anywhere.

## Rolling back the redesign

The previous site is preserved in full. See
[`_original-design/RESTORE.md`](./_original-design/RESTORE.md) for three ways to
undo it. The `main` branch is untouched and still holds the original exactly as
it shipped.
