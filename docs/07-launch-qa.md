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
- CSS ~40 KB, JS ~19 KB total, both uncompressed and un-minified
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
