# Sklarz Creative Post-Launch QA — 2026-08-09

## Confirmed passes
- Root homepage is a real `index.html` and legacy `Index.html` redirects to `/`.
- Major Insights routes exist as directory `index.html` pages.
- File 001 has a clean canonical directory URL.
- Custom branded `404.html` exists and no longer silently redirects unknown paths.
- `CNAME` contains `sklarzcreative.com`.
- Homepage has responsive breakpoints at 920px and 620px, a mobile menu, skip link, reduced-motion handling, explicit image dimensions, and lazy loading below the fold.
- Media Kit has responsive breakpoints at 900px and 620px, skip link, explicit image dimensions, and lazy loading on lower-page graphics.
- Main brand images and SVG graphics referenced by the homepage/Media Kit exist in the repository.
- `social-share.png`, logo master, founder headshot, Trust Framework SVG, content-engine SVG, Trust Files cover SVG, and article cover SVG exist.
- `robots.txt` points to `sitemap.xml`; sitemap includes the main public content routes.

## Confirmed defects / corrections
1. **Broken favicon reference**: homepage and at least the Clarity Before Content article reference `/favicon.png`, but the repository contains `favicon.svg` and no `favicon.png`.
2. **Media Kit tablet/mobile navigation**: `.links` is hidden at `max-width:900px` without a replacement hamburger/menu, removing section navigation on tablets and phones.
3. **Small gold text contrast on light backgrounds**: brand gold `#C9A84C` is used for small eyebrow/status text on white/off-white. This is visually on-brand but does not meet WCAG AA contrast for normal-size text. Use a darker accessible gold for small text on light surfaces while retaining current gold on navy/dark surfaces and for large/decorative elements.
4. **Schema consistency**: homepage, Media Kit, Insights, Trust Files, File 001 and Clarity article have structured data, but Articles hub, Podcast hub, Research Notes and Resources should receive appropriate CollectionPage/WebPage structured data for consistency.
5. **Social-profile verification**: current homepage/Media Kit LinkedIn reference uses `https://www.linkedin.com/in/cassandra-sklarz`. Public search surfaced a Cassandra Sklarz profile at `https://www.linkedin.com/in/cassandra-sklarz-762738179`; verify the intended vanity URL before replacing the current link.
6. **Calendly consistency**: pages currently mix `https://calendly.com/sklarzcreative` and `https://calendly.com/sklarzcreative/30min`. Standardize to the intended booking destination after live destination verification.
7. **Keyboard focus styling**: skip links are visible on focus, but interactive controls across secondary pages rely largely on browser-default focus outlines. Add consistent `:focus-visible` treatment to links/buttons/menu controls.
8. **Homepage mobile menu semantics**: `aria-expanded` updates correctly, but the menu button label remains “Open navigation” when expanded. Toggle the accessible label to “Close navigation” while open.

## Image-reference crawl
### Verified present
- `/sklarz-creative-logo.png`
- `/cassandra-sklarz-headshot.jpg.png`
- `/social-share.png`
- `/assets/graphics/trust-framework.svg`
- `/assets/graphics/content-engine.svg`
- `/assets/graphics/trust-files-cover.svg`
- `/assets/graphics/article-clarity-cover.svg`
- `/favicon.svg`

### Missing
- `/favicon.png`

## Responsive review
- Homepage: desktop grid; <=920px major grids collapse; <=620px capability/process and CTA controls become single-column/full-width.
- Media Kit: layout collapses appropriately, but navigation disappears at <=900px (defect above).
- Insights: <=980px major feature/CTA grids collapse; <=620px category cards become single-column.
- Trust Files: <=850px hero/intro/CTA collapse; card/timeline grids reduce; <=620px single-column.
- File 001: <=850px framework/production grids reduce; <=620px single-column.
- Articles: <=850px featured article and cards collapse to one column.
- Podcast: <=850px hero/feature collapse and grids reduce; <=620px single-column.
- Research Notes: <=850px content grids collapse; <=620px methods become single-column.
- Resources: <=850px primary grids collapse; <=620px cards/tools become single-column.

## Performance review
### Positive implementation choices
- Static HTML/CSS; no frontend framework payload.
- Minimal inline JavaScript.
- SVG editorial graphics.
- Explicit image width/height to reduce layout shift.
- Lazy loading on below-the-fold homepage and Media Kit imagery.
- Only major third-party render dependency is Google Fonts.

### Measurement still required from a live browser/network
- Lighthouse/PageSpeed Performance score
- LCP, CLS, INP/FCP/TBT lab metrics
- transferred byte sizes for logo/headshot PNGs
- live server cache/compression headers

The audit environment could not currently resolve the newly configured public domain, so those measurements must not be represented as completed until the live endpoint is reachable from the external test runner.

## Public-host checks still requiring live HTTP verification
- `www.sklarzcreative.com` -> `sklarzcreative.com` redirect
- actual HTTP 404 status for a random nonexistent URL
- live response/redirect status of every Calendly/social destination

GitHub Pages configuration and the repository CNAME/DNS setup are consistent with GitHub’s documented automatic apex/www redirect behavior once both DNS variants are configured.