# 07 · Final Polish & Launch QA

> Final audit and launch checklist for sklarzcreative.com.
>
> **On verification honesty:** this document separates what was *measured* in a
> real browser from what *cannot* be measured until the site is on its live
> domain. The previous QA report (`QA_POST_LAUNCH_2026-08-09.md`) was careful
> about the same distinction, and it was right to be. Nothing unverifiable is
> presented here as passing.

---

## How this was verified

A headless Chromium harness rendered every page at **1440 / 834 / 390px**. For
each page it scrolled the full document so every `IntersectionObserver` reveal
fired and every lazy image decoded *before* measuring, then reported:

- WCAG contrast for every rendered text node against its **true composited
  background**
- Missing or untruthful image dimensions, and images that failed to load
- Links and buttons with no accessible name
- Skipped heading levels, duplicate ids, `h1` count
- Horizontal overflow
- Console errors, page errors, failed requests, HTTP ≥ 400

Interaction paths were driven directly: mobile menu open/close, Escape
handling, focus movement, `prefers-reduced-motion`, and JavaScript disabled.

### Two harness bugs worth knowing about

A QA tool that lies is worse than no tool. Both of these produced confident
false results before being fixed:

1. **Fixed overlays.** A fixed, transparent header overlays a section that is
   not its DOM ancestor. Walking up the tree resolves its background to
   body-white and reports every nav link as a contrast failure. The fix is to
   hit-test the real paint stack (`elementsFromPoint`) for anything inside a
   fixed subtree — **and to include the element's own background**, or a gold
   button reports its navy label against whatever sits behind it.
2. **Lazy images.** An image parked far outside the viewport may never have
   been *asked* to load. That is unknowable, not broken, and reporting it as a
   failure sends you chasing a bug that does not exist.

---

## Issues found and fixed, ranked by impact

### Critical — would have shipped broken

| # | Issue | Fix |
| --- | --- | --- |
| 1 | **`.page-hero` was not a dark context.** `.btn--ghost` inside it resolved to `--btn-fg: var(--navy)` on a near-black gradient — roughly **1.3:1**. Ghost buttons on every secondary page would have been effectively invisible. The components were individually correct and failed only in this one composition. | Added a complete `.page-hero` dark-context block restating every `.is-dark` override (buttons, accents, cards, facts, chips, quotes, focus rings). |
| 2 | **Mobile menu was not keyboard-usable.** `visibility` was in the transition list, so at progress 0 it still computed to `hidden` and the browser silently refused to focus the first link. Focus stayed on the toggle behind a full-screen overlay. | `visibility` now flips discretely on open and is delayed to the end of the fade on close. Focus lands on the first link; Escape returns it to the toggle. |
| 3 | **Hero type was unreadable on mobile.** The 3D object sits behind the headline at narrow widths and its lit facets washed out the lede and the ghost button. | Object dropped below the copy, dimmed to 34%, plus a hard gradient scrim. Legibility outranks spectacle. |

### High — accessibility failures

| # | Issue | Measured | Fix |
| --- | --- | --- | --- |
| 4 | `--ink-faint` on light grounds (labels, meta) | 3.07:1 / 2.90:1 | `#8A94A1` → `#666F7D` (4.79:1 on alabaster) |
| 5 | `--on-dark-faint` on the void footer | 3.54:1 | Alpha .42 → .62 (6.1:1 on void, 5.1:1 on deep) |
| 6 | Header brandmark accent vs. the frosted header | 4.21:1 | Brand gold → champagne. Same family, compliant. |
| 7 | Footer column labels were `h4` directly after an `h2` | — | Promoted to `h3` |

### Medium — correctness

| # | Issue | Fix |
| --- | --- | --- |
| 8 | Founder headshot declared `900×1100`; the file is **900×900**. Inherited from the previous build. | Corrected. Every raster and vector asset's real intrinsic size was then read from the file headers rather than trusted from markup. |
| 9 | `trust-framework.svg` and `content-engine.svg` declared as `1080×1080`; both are **1200×800**. | Corrected. |
| 9b | Brand logo declared `1024×1024`; the file is **1254×1254**. | Corrected. |
| 9c | `.asset-preview img` set both `width` and `height` to `auto`, which defeats the image's own `width`/`height` attributes — so a lazily-loaded Media Kit asset occupied **zero space until it decoded**, shifting layout mid-scroll. | Space is now reserved on the container (`min-height: 18rem`) instead of the image. |
| 10 | The editorial lead image forced `aspect-ratio: 16/9` with `object-fit: cover`, cropping a 3:2 diagram. | Changed to `3/2` to match the artwork. |
| 11 | The four trust dimensions animated as count-ups from zero. They are **labels, not measurements**. | Removed. Motion for its own sake is exactly what the brief rules out. |
| 12 | Four items in `auto-fit` produced a three-plus-one grid with a dead cell. | `.stats--quad` pins it to 2×2. |
| 13 | `.plate`'s offset frame used an absolutely-positioned pseudo-element at `z-index: -1`, which renders *behind the section background* in some stacking contexts and disappears. | Redrawn with `outline` + `outline-offset` — outside the box, no layout cost, unclippable. |
| 14 | Footer omitted the Threads and X profiles the old Media Kit carried. | Both restored to the shared footer. |
| 15 | Media Kit's section sub-nav was hidden below 900px with no replacement — a pre-existing defect from the previous QA. | Dropped in favour of the shared header; the section ids are kept so existing deep links still resolve. |
| 16 | Old Clarity article nav pointed at `/#about` and `/#services`, which no longer exist. | Repointed to the canonical nav. |
| 17 | `robots.txt` allowed the archived original site to be crawled as duplicate content. | `Disallow: /_original-design/` added; excluded from the sitemap. |

### Resolved during the build

The 3D object took four passes: too large and colliding with the headline →
flat matte plastic (a Lambert diffuse term was flattening every facet) →
blown-out white ring → green-black shadows (gold albedo multiplied into a navy
reflection lands on olive). Full detail in
[`03-cinematic-hero.md`](./03-cinematic-hero.md).

---

## Verified locally ✅

**Accessibility**
- Zero WCAG AA contrast failures on any page at 1440 / 834 / 390px
- Exactly one `h1` per page; no skipped heading levels; no duplicate ids
- Every link and button has a discernible accessible name
- Skip link present and functional on every page
- Focus visible on every interactive element, on both light and dark grounds
- Mobile menu: focus enters, Escape exits and restores focus, body scroll locks
- `prefers-reduced-motion`: no reveal left hidden, no line left clipped, no
  cursor ring, no curtain, no hero loop
- **JavaScript disabled: nothing invisible.** Hidden start-states are scoped to
  `html.js`, so the page renders complete and static.

**Rendering**
- No horizontal overflow at any tested width
- No console errors, page errors, or failed local requests
- WebGL hero initialises, reports `is-ready`, and survives context loss
- All images load and render at their declared dimensions
- Print stylesheet neutralises dark grounds and expands link URLs

**SEO / structure**
- `title`, `meta description`, canonical, viewport, `theme-color`, favicon on
  every page
- Valid JSON-LD on every page; `CollectionPage` added where hubs had none
- No fabricated `datePublished` — the field is present only where the previous
  page actually stated a date
- Sitemap covers every public route; `robots.txt` points at it

**Performance posture**
- Zero framework, zero npm dependency, zero build step
- Measured, un-minified: CSS 48.8 KB (**12.6 KB gzipped**), JS 32.4 KB
  (**11.5 KB gzipped**), homepage HTML 6.2 KB gzipped. Roughly **30 KB** of
  gzipped CSS + JS + HTML for the whole first load, before fonts.
- 3D hero adds no library; grain and noise are generated in-browser, costing
  no requests
- Only `transform` / `opacity` / `filter` are animated
- One rAF loop and one IntersectionObserver for the whole page, with cached
  geometry
- DPR capped, render scale below 1.0, march budget reduced on weak hardware,
  frame-time watchdog that degrades then bails
- Render loop stops when the hero is offscreen or the tab is hidden

---

## Cannot be verified until deployed ⚠️

These require the live domain and a real network. **Do not treat them as
passing.**

| Item | How to check after deploy |
| --- | --- |
| Lighthouse / PageSpeed scores | PageSpeed Insights on the live URL |
| Real LCP, CLS, INP | Field data, or Lighthouse on the live URL |
| Google Fonts render timing | Blocked by the build environment's egress proxy, so **display type has never been seen in Playfair here** — every local screenshot fell back to Georgia. Confirm the intended typography live. |
| Compression and cache headers | `curl -I` against the live domain |
| `www` → apex redirect | Load `www.sklarzcreative.com` |
| True 404 status code | `curl -I` a nonexistent path; expect `404`, not `200` |
| Calendly / social destinations | Click each one |
| Safari and Firefox rendering | Real browsers — `backdrop-filter`, `text-wrap: balance`, `aspect-ratio`, and WebGL precision all vary |
| iOS Safari `svh` behaviour | A real device, with the URL bar collapsing |
| Social share cards | Facebook Sharing Debugger, X Card Validator |

---

## Launch checklist

**Before merging**
- [ ] Read `_original-design/RESTORE.md` and confirm you are happy with the
      rollback path
- [ ] Skim the redesigned pages against the old ones in `_original-design/`
      and confirm no copy you wanted was lost
- [ ] Confirm the Calendly link is the intended destination
      (`calendly.com/sklarzcreative/30min`)
- [ ] Confirm the LinkedIn vanity URL is correct — the previous QA flagged two
      candidate profiles and this build kept the existing choice

**At deploy**
- [ ] Confirm GitHub Pages is building from the intended branch
- [ ] Confirm `CNAME` still contains `sklarzcreative.com`
- [ ] Confirm DNS covers both apex and `www`

**Immediately after deploy**
- [ ] Load the homepage on a real phone and a real desktop
- [ ] Confirm Playfair Display is actually loading (see the warning above)
- [ ] Run Lighthouse on the homepage and one article; record the numbers
- [ ] `curl -I` a nonexistent path and confirm a real `404`
- [ ] Test `www` → apex
- [ ] Click every outbound link
- [ ] Check the 3D hero on a mid-range Android — confirm it degrades, not stutters
- [ ] Check Safari desktop and iOS Safari
- [ ] Validate both social share cards
- [ ] Submit the sitemap in Search Console
- [ ] Confirm `/_original-design/` is not indexed

**First week**
- [ ] Watch Search Console for crawl errors on the changed routes
- [ ] Check whether discovery calls booked per visit moved
- [ ] Confirm no Core Web Vitals regression versus the previous build

---

---

## Second QA pass — 23 August 2026 · Scorecard capture & delivery

Re-run after the Trust-First Content Scorecard was given a lead-capture flow
and brought fully onto the design system. Same harness, same widths, plus the
scorecard in **both** states (gated and open) as separate routes.

### Two harness bugs, again

Both produced confident false passes and both are now fixed. Recording them
because the pattern is the point: *a QA tool that reports "0 issues" for a
region it never looked at is worse than no tool.*

3. **The scroll pass was fighting `scroll-behavior: smooth`.** The harness
   scrolls the document to fire every `IntersectionObserver` reveal before
   measuring. With smooth scrolling on `html`, a rapid `scrollTo` sequence
   animates instead of jumping and never reaches the bottom — so reveals below
   that point stayed at `opacity: 0`, and the contrast pass skips anything
   under 0.15 opacity as mid-transition. Fixed by forcing
   `scrollBehavior = 'auto'` for the duration of the pass.
4. **Measurement started before the reveals landed.** A reveal runs 760ms plus
   its stagger delay; the harness waited 400ms. `/work/` reported **17
   unmeasured elements** at 1440px once the harness was made to say so. Fixed
   with a settle loop that waits for every `[data-reveal]` to reach full
   opacity, and the harness now prints a loud warning if any never do.

### Issues found and fixed in this pass

| # | Severity | Issue | Fix |
| --- | --- | --- | --- |
| 18 | **Critical** | **The scorecard's twenty statements were generated in JavaScript.** A scripting failure produced an empty container — the instrument simply was not there. | The statements are authored in HTML. Scripting off leaves twenty real `<fieldset>`s with working radios, printable and scoreable by hand, plus a `<noscript>` note explaining that only the live total is missing. |
| 19 | **Critical** | **Access depended on a form round-trip.** The gate posted to Netlify and relied on the redirect to come back with `?access=1`. Any failure between the visitor and Netlify cost them the tool after they had handed over an address. | The reveal happens locally and first; the capture POST is fired afterwards and not awaited. A failed capture is reported as information, not as an obstacle. |
| 20 | **High** | **The accessible names had regressed.** All twenty radio groups were labelled `aria-label="Score 0, 1, or 2"` — identical, and naming the control rather than the question. | Restored to `<fieldset>` + `<legend>`, one distinct legend per statement. |
| 21 | **High** | **A ~9 KB page-specific `<style>` block** had grown on the scorecard, with hard-coded hexes outside the token system. | Reconciled into `sklarz.css` §16b as reusable components. The page now carries **zero** `<style>` blocks. |
| 22 | **High** | **The consent sentence rendered in uppercase 11px letter-spaced caps.** `.consent` is a `<label>` and a direct child of `.field`, so the uppercase *field-name* treatment applied to it. Caught by reading a screenshot, not by any automated check. | `.field > label:not(.consent)`, plus explicit type on `.consent`. |
| 23 | **Medium** | **`.page-hero` was never neutralised for print.** It paints its own gradient and sets white type, and browsers drop backgrounds when printing — so **every secondary page printed its own title white on white**. Pre-existing, not scorecard-specific. | Added to the print reset, along with its breadcrumb, lede and fact strip. |
| 24 | **Medium** | The skip link printed as a gold button on every page. | Added to the print `display: none` list. |
| 25 | **Medium** | The scorecard's footer had been replaced with a cut-down version using a `.foot-bottom` class that does not exist in the stylesheet, and the social row was gone. | Header and footer re-synced from the canonical markup. |
| 26 | **Medium** | The consent checkbox's clickable label was **22px tall** — under the 24px target minimum at ≥834px. | `min-height` + vertical padding on `.consent`. |
| 27 | **Medium** | The sticky result bar took **33% of a 390px viewport**. | The print button moved out of the bar (it does not need to follow the reader, and a button inside an `aria-live` region is re-announced on every score change) and the bar was tightened on phones. Now 24%. |
| 28 | **Low** | Three facts in the page-hero side rail auto-fitted to two columns and left a dead cell. | `.facts--stack`. |

### Verified locally ✅

- **0 issues** across 14 routes at 1440 / 834 / 390px — contrast, alt text,
  accessible names, heading order, duplicate ids, tap targets, horizontal
  overflow.
- **Scoring, at every boundary:** all zeroes → 0; all twos → 40; each category
  maxes at 8; the total always equals the sum of the five subtotals; the bands
  flip at exactly 32 / 24 / 16 (tested at 40, 32, 31, 24, 23, 16, 15, 0); an
  incomplete card reports "*n* of 20 answered" and claims neither a band nor a
  weakest signal.
- **Keyboard only:** arrow keys move within a score group, and every control
  has a visible focus ring on both grounds.
- **JavaScript disabled:** the page is complete content — all twenty
  statements, all sixty radios, and the band reference.
- **Print:** navigation, footer, CTA band and the print button all drop;
  the title, statements, subtotals and result print black; the chosen score
  prints as a solid inked box (forced, because browsers drop backgrounds and a
  gold fill dies on a mono printer); categories avoid page breaks.
- **Links:** 14 internal targets resolve, no dead links, no unresolved
  anchors, no 4xx.
- **Mobile nav** on all three affected routes: opens, traps focus, locks body
  scroll, closes on Escape, returns focus to the toggle.

The gate that existed at the time of this pass was also fully tested and
passed — locked by default, opening on submit and on `?access=1`, remembering a
returning visitor, failing open on every error path, with accessible validation
on all three fields and the honeypot kept out of the tab order. It is no longer
on the page; see the correction immediately below. Those results are recorded
because they are what makes commit `1aa56c8` a trustworthy restore point.

### Correction — the host, and what it did to the capture

The capture work above was built against Netlify Forms. That premise was
wrong, and the evidence arrived after it was built:

- **Netlify has skipped every production deploy since 9 August**, each marked
  *"Skipped — account credit usage exceeded"* — including `e5aa3a6`,
  `d81042b` and `f51403f`.
- **The live site is serving `e5aa3a6`.** Its
  `/insights/resources/trust-first-content-scorecard/` route only came into
  existence in `f51403f` on 22 August, a commit Netlify skipped.
- Therefore **GitHub Pages serves `sklarzcreative.com`**, consistent with
  Pages run #49 succeeding on `main @ e5aa3a6`.

GitHub Pages serves static files and nothing else — it cannot process a form
post. So the gate was removed and the Scorecard ships **open**. Full reasoning
and the restore path in [08](./08-scorecard-capture.md); the working
implementation is preserved in commit `1aa56c8`.

Issues 18–19 in the table above were fixed on their merits and still hold: the
statements are authored in HTML rather than generated, so the instrument
survives a scripting failure, and access was never allowed to depend on a
network round-trip. That second decision is why removing the capture cost
nothing — the reveal never waited on it.

**Verified after removal:** no page errors, no surviving `tfcs-open` rule (the
retired rules are inside a comment — confirmed by walking the parsed
stylesheet, not by grep), the diagnostic unconditionally visible, 20
fieldsets, 60 radios, no form element on the page, scoring still reaching
40/40 with the correct band, and the now-meaningless `?access=1` link still
landing on a working page.

### Still requires the deployed domain ⚠️

| Item | Why local testing cannot settle it |
| --- | --- |
| Real LCP / CLS / INP, Lighthouse | Needs the live URL. |
| **Playfair Display actually rendering** | Google Fonts is blocked by this environment's egress proxy, so display type has never been seen here. |
| Social share cards | `social-share.png` is still 1254×1254 square while declared `summary_large_image`, so platforms will crop it. |
| Safari / Firefox / iOS rendering | Real browsers vary on `backdrop-filter`, `text-wrap: balance`, `aspect-ratio` and WebGL precision. |
| Everything in the first pass's live-domain table | Unchanged. |

## Known accepted trade-offs

Deliberate decisions, not oversights:

1. **Four PNG masters are 1.5–1.8 MB each and all are 1254×1254**
   (`Favicon.png`, `sklarz-creative-logo.png`,
   `cassandra-sklarz-headshot.jpg.png`, `social-share.png`). No image tooling
   existed in the build environment to re-encode them, so they were left
   untouched rather than degraded. Normal page rendering uses the optimised
   43 KB WebP headshot and the SVG favicon, so **no page paints these files** —
   they are referenced only as Media Kit downloads and as the social-share
   source.

   **One of them is worth acting on before launch:** `social-share.png` is
   **square**, but it is declared as `twitter:card = summary_large_image` and
   as the `og:image`. Every major platform crops a square image to landscape
   for that card type, so the share preview is being cropped rather than
   composed. It also weighs 1.5 MB, which crawlers do fetch. Replacing it with
   a purpose-made **1200×630** image under ~200 KB is a small job with a
   visible payoff on every share.
2. **The hero is homepage-only.** Secondary pages get a static gradient. That
   is a performance and attention decision: the object is a first-impression
   device and repeating it would cheapen it.
3. **No dark-mode toggle.** The site already commits to a dark-first cinematic
   register; a light/dark switch would halve the impact of the alternating
   ground rhythm.
4. **`_original-design/` is publicly reachable.** GitHub Pages has `.nojekyll`,
   so the folder is served. It is `Disallow`ed and out of the sitemap.
   Delete it once you are confident in the redesign — `main` and the git
   history still hold everything.
