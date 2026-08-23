# Sklarz Creative — Claude Code website prompt archive

Durable record of the material prompts that have directed work on
**sklarzcreative.com**: audits, redesign, positioning, copy, SEO, UX,
accessibility, QA, Git workflow, backups, deployment and rollback.

- **Companion documents:** [`WEBSITE_WORKFLOW.md`](./WEBSITE_WORKFLOW.md) (the standing rules) · [`PROMPT_INDEX.md`](./PROMPT_INDEX.md) (the fast lookup table)
- **Archive created:** 23 August 2026
- **Repository:** `Sklarzcreative/Sklarzcreative-website`
- **Live host:** GitHub Pages, deploy-from-branch on `main`, domain `sklarzcreative.com`

---

## Read this before trusting any entry below

This archive was assembled on 23 August 2026 from **the repository itself** —
commit messages and bodies, `docs/`, `_original-design/RESTORE.md`,
`QA_POST_LAUNCH_2026-08-09.md`, and `.github/workflows/` — plus the single
prompt given in the session that created the archive.

**I could not read any earlier Claude Code conversation.** Prior sessions are
not accessible from this one; the commit trailers prove at least one earlier
session existed (a `Claude-Session:` URL appears on the 22–23 August commits,
withheld here as `[REDACTED]` because it is a private URL), but its transcript
is gone as far as this repository is concerned. Nothing below is a transcript.

Every entry therefore carries an honest recovery status:

| Status | What it means here |
| --- | --- |
| `VERBATIM` | The exact text as given, held in the session that wrote this file. **One entry qualifies: P-034.** |
| `PARTIAL` | Real prompt wording preserved in-repo but edited. Applies to P-013…P-022, whose text is copied from `docs/05-build-with-claude.md`, a file that states of itself: *"The prompts below are the real ones, generalised."* Substance and most phrasing are original; keystroke-exact wording is not guaranteed. |
| `RECONSTRUCTED` | No original wording survives. The prompt is rebuilt from the commit, diff and documentation it produced, and is written as a **re-runnable instruction**, not as a claim about what was typed. |

**Do not cite a `RECONSTRUCTED` prompt as something the client said.** It is a
reasonable inference about what was asked, evidenced by what shipped. The
`Evidence` line on each entry names exactly what it was inferred from.

### Privacy handling

Prompts here are stored in a public source repository. Before writing, each was
checked for and stripped of passwords, API keys, access tokens, credentials,
private URLs, unrelated personal information, private client information,
private account information, and confidential material. Removals are marked
`[REDACTED]`.

Two categories were deliberately kept, because they are already public on the
live site and are load-bearing for the work: the Calendly booking URL and the
public social profile URLs. Private session URLs, account identifiers and
personal email addresses were **not** carried in.

---

## Phase A · Launch readiness and post-launch QA — 9–10 August 2026

Pre-redesign work on the original site. No prior-session wording survives, so
every Phase A entry is `RECONSTRUCTED` from its commits.

---

### P-001 · Rebuild the homepage for performance, visuals, SEO and lead generation

- **Date:** 2026-08-09 · **Sequence:** A1
- **Category:** Homepage editing · SEO · UX and conversion
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commit `fa94dbd` "Rebuild homepage for performance, visuals, SEO and lead generation"

```
Rebuild the sklarzcreative.com homepage. Improve page performance, tighten the
visual design, complete the SEO metadata, and give the page a clear
lead-generation path to a discovery call.

Keep the existing brand colours and the existing copy where it is already
working. Set explicit width and height on every image and lazy-load anything
below the fold.
```

- **Purpose:** Bring the original homepage to a launchable standard on speed, appearance, search metadata and conversion.
- **Implementation status:** Implemented and superseded — this homepage was later replaced by the cinematic redesign (P-018). The 9 August version is preserved at `_original-design/index.html`.
- **Files changed:** `index.html`
- **Branch / commit:** `main` @ `fa94dbd`
- **Deployment status:** Deployed to production (GitHub Pages, `main`)
- **Outcome and notes:** Established the pre-redesign homepage baseline that `_original-design/` later archived.

---

### P-002 · Expand the Insights content hubs for the Trust Files launch

- **Date:** 2026-08-09 · **Sequence:** A2
- **Category:** Service/content-page editing · Copy · UX and conversion
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commits `5992f43`, `60ff8fb`, `60926d7`, `559f61e`, `2bdf0bc`, `5dd125a`, `545b256`

```
Expand the Insights section for the Trust Files launch. Work through each hub
in turn — The Trust Files, Articles, Podcast, Research Notes, Resources, and
the Insights index — and for each one strengthen the visual hierarchy, give the
cards real editorial weight, state the editorial standard, and end with a
call to action.

Also enhance File 001 itself: better visual hierarchy and the launch content
in place.

Do not invent publication dates or claims that are not already true.
```

- **Purpose:** Turn thin hub pages into a credible content architecture ahead of the Trust Files launch.
- **Implementation status:** Implemented; later rebuilt onto the design system (P-020).
- **Files changed:** `insights/index.html`, `insights/the-trust-files/`, `insights/articles/`, `insights/podcast/`, `insights/research-notes/`, `insights/resources/`, File 001
- **Branch / commit:** `main` @ `5992f43`…`5dd125a`
- **Deployment status:** Deployed to production
- **Outcome and notes:** Seven separate commits, one per hub — the incremental pattern this project has used since.

---

### P-003 · Fix routing and canonical URLs across the site

- **Date:** 2026-08-09 · **Sequence:** A3
- **Category:** Navigation · SEO
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commits `6feafb4`, `6b413e9`, `df487e4`, `8c0dbf1`

```
Clean up the site's routing so every page has one canonical URL.

Redirect the legacy capital-I /Index.html to the canonical homepage. Give File
001 a clean permanent directory route and redirect the legacy URL to it. Add
robust fallback routing for all Insights pages so no in-flight link 404s. Then
update sitemap.xml to the clean canonical URLs.
```

- **Purpose:** Remove duplicate-URL and dead-link risk before search engines indexed the launch.
- **Implementation status:** Implemented; still in force.
- **Files changed:** `Index.html`, `insights/**/index.html`, `sitemap.xml`
- **Branch / commit:** `main` @ `6feafb4`, `6b413e9`, `df487e4`, `8c0dbf1`
- **Deployment status:** Deployed to production
- **Outcome and notes:** `Index.html` still exists as the legacy redirect and must not be deleted.

---

### P-004 · Produce the editorial SVG graphics

- **Date:** 2026-08-09 · **Sequence:** A4
- **Category:** Visual design
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commits `15612aa`, `9afde18`, `8206d1b`, `58e0f69`

```
Create the site's editorial graphics as SVG, in the brand navy and gold only:
the Trust Framework diagram, the content engine diagram, a cover for The Trust
Files, and a cover for the Clarity Before Content article.

SVG rather than raster so they stay sharp and stay small.
```

- **Purpose:** Give the content hubs original artwork instead of stock imagery.
- **Implementation status:** Implemented; all four still in use.
- **Files changed:** `assets/graphics/trust-framework.svg`, `content-engine.svg`, `trust-files-cover.svg`, `article-clarity-cover.svg`
- **Branch / commit:** `main` @ `15612aa`, `9afde18`, `8206d1b`, `58e0f69`
- **Deployment status:** Deployed to production
- **Outcome and notes:** Approved brand assets. Per the workflow rules, these are not to be reinterpreted or regenerated without instruction.

---

### P-005 · Replace the redirecting 404 and add an SVG favicon

- **Date:** 2026-08-09 · **Sequence:** A5
- **Category:** UX · Metadata
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commits `9ab3870`, `6c34f88`

```
The 404 page silently redirects unknown paths, which hides broken links from
me and from search engines. Replace it with a true branded 404 error page that
stays on the requested URL.

Also add a proper Sklarz Creative SVG favicon.
```

- **Purpose:** Make link rot visible and finish the brand chrome.
- **Implementation status:** Implemented; still in force.
- **Files changed:** `404.html`, `favicon.svg`
- **Branch / commit:** `main` @ `9ab3870`, `6c34f88`
- **Deployment status:** Deployed to production
- **Outcome and notes:** The real HTTP status code can only be confirmed against the live domain — see the deploy-time checks in `WEBSITE_WORKFLOW.md`.

---

### P-006 · Upgrade the media kit

- **Date:** 2026-08-09 · **Sequence:** A6
- **Category:** Service-page editing · Accessibility · SEO · Conversion
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commit `5bb75b8` "Upgrade media kit visuals, accessibility, SEO and conversion"

```
Upgrade the Media Kit page: stronger visuals, accessibility fixes, complete SEO
metadata, and a clearer conversion path.
```

- **Purpose:** Bring the media kit to the same standard as the homepage.
- **Implementation status:** Implemented; later rebuilt onto the design system (P-020).
- **Files changed:** `media-kit.html`
- **Branch / commit:** `main` @ `5bb75b8`
- **Deployment status:** Deployed to production
- **Outcome and notes:** The follow-up QA (P-008) still found the tablet/mobile nav broken on this page, fixed in P-009.

---

### P-007 · Standardize metadata and social previews across the hubs

- **Date:** 2026-08-09 · **Sequence:** A7
- **Category:** Metadata · Social previews · SEO
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commits `e4da6be`, `c171574`, `5e13cad`, `2677504`, `fb7ebd9`

```
Standardize the metadata across every Insights hub — Articles, Podcast,
Research Notes, Resources and The Trust Files. Each needs a correct title,
description, canonical URL, Open Graph and Twitter card tags pointing at the
share image, and a consistent discovery call to action.

Improve the visual structure of each hub while you are in there.
```

- **Purpose:** Make every hub share correctly on social and read consistently in search results.
- **Implementation status:** Implemented; carried through the redesign.
- **Files changed:** the five Insights hub `index.html` files
- **Branch / commit:** `main` @ `e4da6be`, `c171574`, `5e13cad`, `2677504`, `fb7ebd9`
- **Deployment status:** Deployed to production
- **Outcome and notes:** Social card rendering can only be confirmed with the live URL in the platform debuggers.

---

### P-008 · Run a post-launch QA audit

- **Date:** 2026-08-09 · **Sequence:** A8
- **Category:** QA · Auditing
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commit `8ca5637` "Add post-launch QA audit" → `QA_POST_LAUNCH_2026-08-09.md`

```
Audit the live site now that it has launched. Cover routing, responsive
behaviour, images and missing assets, accessibility, structured data, SEO,
performance, and every outbound link.

Write it up as a document in the repository. Separate confirmed passes from
confirmed defects, and be explicit about anything you could not verify rather
than presenting it as passing.
```

- **Purpose:** Establish a written, evidence-separated baseline of site health.
- **Implementation status:** Implemented — the audit document exists and its findings were then worked through in P-009.
- **Files changed:** `QA_POST_LAUNCH_2026-08-09.md`
- **Branch / commit:** `main` @ `8ca5637`
- **Deployment status:** Documentation only
- **Outcome and notes:** Found eight defects, including a broken `/favicon.png` reference, Media Kit nav disappearing under 900px, gold-on-light contrast failures, missing structured data on four hubs, and mixed Calendly URLs. The "confirmed passes vs. confirmed defects vs. cannot verify" structure became the house QA format and is repeated in `docs/07-launch-qa.md`.

---

### P-009 · Fix every defect the QA audit found

- **Date:** 2026-08-09 · **Sequence:** A9
- **Category:** Accessibility · Metadata · Structured data · QA remediation
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commits `af1e5a9`, `cdc9ce1`, `4f3aa1e`, `10ae3aa`, `7ae5df6`, `a94e35f`, `3780d8d`, `1292d36`, `039d180`, `0b28fc5`

```
Work through the defects in the QA audit, one page at a time, committing each
page separately.

Fix the accessibility contrast failures — small gold text on light backgrounds
fails WCAG AA, so introduce a darker gold token for that case and keep brand
gold on dark surfaces and for large or decorative type. Fix the favicon
reference and its MIME type. Standardize the booking link. Add the missing
CollectionPage/WebPage structured data to the hubs that lack it. Give
interactive controls a consistent :focus-visible treatment, and fix the mobile
menu's accessible label so it says Close when it is open.
```

- **Purpose:** Close out the audit findings without batching unrelated changes into one commit.
- **Implementation status:** Implemented across ten commits.
- **Files changed:** `index.html`, `media-kit.html`, all Insights hubs, File 001
- **Branch / commit:** `main` @ `af1e5a9` … `0b28fc5`
- **Deployment status:** Deployed to production
- **Outcome and notes:** The darker-gold-for-small-text rule established here survived the full redesign — it is `--gold-ink` in `assets/css/sklarz.css` and remains a load-bearing rule.

---

### P-010 · Automate the QA cleanup and optimize the founder headshot

- **Date:** 2026-08-09 to 2026-08-10 · **Sequence:** A10
- **Category:** QA · Performance · GitHub workflow
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commits `0640052`, `ce66f38`, `e1dec6a`; `.github/workflows/finish-site-qa.yml`

```
The remaining QA cleanup is the same find-and-replace across every HTML file,
so do it as a one-time GitHub Actions workflow rather than by hand.

It should: optimize the founder headshot to a 900px-wide WebP and write it to
assets/images/; repoint every page at the optimized image; correct the favicon
references and MIME type; standardize the Calendly link to the /30min
destination; and fix the remaining gold contrast token on the Clarity Before
Content article.

Commit and push the result from the workflow.
```

- **Purpose:** Apply a repetitive, mechanical cleanup consistently across every page.
- **Implementation status:** Implemented and run.
- **Files changed:** `.github/workflows/finish-site-qa.yml`, `assets/images/cassandra-sklarz-headshot.webp`, all `*.html`
- **Branch / commit:** `main` @ `0640052`, `ce66f38`, `e1dec6a`
- **Deployment status:** Deployed to production; commits authored by "Sklarz Creative Site QA"
- **Outcome and notes:** The workflow is triggered only by edits to its own file, so it is inert unless deliberately re-run. Both the large PNG master and the WebP derivative are kept — the derivative was added alongside, not in place of, the original.

---

### P-011 · Verify and standardize the LinkedIn URL

- **Date:** 2026-08-09 to 2026-08-10 · **Sequence:** A11
- **Category:** Copy · Links · QA
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commits `95aad77`, `3e44ab7`; `.github/workflows/linkedin-url.yml`; QA finding 5 in `QA_POST_LAUNCH_2026-08-09.md`

```
The QA audit flagged two candidate LinkedIn profiles and said not to change the
link until the intended one is confirmed. It is confirmed now — use the
confirmed Cassandra Sklarz profile URL everywhere the site links to LinkedIn,
and make it consistent across every page.
```

- **Purpose:** Resolve the one QA finding that had been deliberately left open pending human confirmation.
- **Implementation status:** Implemented.
- **Files changed:** all pages carrying a LinkedIn link; `.github/workflows/linkedin-url.yml`
- **Branch / commit:** `main` @ `95aad77`, `3e44ab7`
- **Deployment status:** Deployed to production
- **Outcome and notes:** A good precedent worth repeating: the audit refused to guess between two plausible profile URLs and waited for a human to confirm. `3e44ab7` is also the commit that `_original-design/` was later archived from — it is the last pre-redesign state of the site.

---

## Phase B · The cinematic redesign — 22 August 2026

The ten staged prompts below are copied from
[`docs/05-build-with-claude.md`](../../05-build-with-claude.md), which records
them as *"the real ones, generalised."* They are therefore `PARTIAL`: the
substance and most of the phrasing are original, but the text has been edited
for reuse and is not a keystroke-exact transcript. That file is the source of
truth for the prompt text; this archive adds what each one produced.

The document's own framing is worth keeping in view — three instructions recur
through the whole sequence and are described there as the load-bearing part:
*"Read X before you change it"*, *"Verify it in a real browser and show me the
result"*, and *"Do not change anything that already works."*

---

### P-012 · Stage 0 — Survey the site and archive it before touching anything

- **Date:** 2026-08-22 · **Sequence:** B0
- **Category:** Auditing · Production backup · Rollback
- **AI/tool:** Claude Code
- **Recovery status:** `PARTIAL` — text from `docs/05-build-with-claude.md` Stage 0
- **Evidence:** `docs/05-build-with-claude.md`; commit `496b9a3`; `_original-design/RESTORE.md`

```
Before changing anything, survey this repository and tell me what the site
currently is: every page, its content, the colour and type system in use, and
any build tooling.

Then archive the current site so it can be restored if I dislike the redesign:
copy every page into _original-design/ and write a RESTORE.md explaining at
least two ways to roll back. Each archived page must keep its own inline CSS
so it renders standalone regardless of what the redesign does to shared
stylesheets. Add a robots.txt rule so the archive is not indexed as duplicate
content. Commit that on its own before touching any live file.

Do not start redesigning yet. Show me the survey first.
```

- **Purpose:** Guarantee rollback capability before a material redesign, and force inspection before editing.
- **Implementation status:** Implemented.
- **Files changed:** `_original-design/**` (complete site copy), `_original-design/RESTORE.md`, `robots.txt`
- **Branch / commit:** `claude/sklarz-creative-redesign-8yd5he` @ `496b9a3`, archiving the state at `3e44ab7`
- **Deployment status:** Deployed to production as part of the redesign merge
- **Outcome and notes:** The single most important prompt in the archive — it is the reason a rollback path exists at all. Note that `RESTORE.md` Option 2 ("the `main` branch has not been touched") **is now stale**: `main` has since received the redesign and is at `a5be572`. Rollback today is via `_original-design/` (Option 1) or `git show 3e44ab7:index.html` (Option 3). See `WEBSITE_WORKFLOW.md`.

---

### P-013 · Stage 1 — Creative direction

- **Date:** 2026-08-22 · **Sequence:** B1
- **Category:** Brand · Positioning · Creative direction
- **AI/tool:** Claude Code
- **Recovery status:** `PARTIAL` — text from `docs/05-build-with-claude.md` Stage 1
- **Evidence:** `docs/05-build-with-claude.md`; `docs/01-creative-direction.md`

```
Act as an award-winning digital creative director. My brand kit is navy
#1A2F4B and gold #C9A84C — that constraint is absolute, no new hues.

Write a creative direction document for this site covering: the strategic
problem, one governing idea, mood, a full colour system derived only from
navy and gold, typography roles for the typefaces already in the kit,
imagery and 3D direction, motion direction, copy voice, and conversion
architecture. End with a list of things that would break the system.

Constraints:
- Do not add a typeface. Assign distinct roles to the ones already in use.
- Every colour must derive from navy or gold.
- The site must assert nothing untrue: no invented metrics, client logos, or
  testimonials. If you need a visual rhythm where stats would normally go,
  find something factual in the existing content to put there instead.

Write the document to docs/. Do not write any code yet.
```

- **Purpose:** Fix the creative strategy in writing before any code existed.
- **Implementation status:** Implemented.
- **Files changed:** `docs/01-creative-direction.md`
- **Branch / commit:** redesign branch, folded into `c64d0a8`
- **Deployment status:** Documentation; the system it defines is deployed
- **Outcome and notes:** Produced the governing idea **"Clarity is the first act of trust"** and the two-constant colour discipline. The "assert nothing untrue" constraint became a permanent brand rule and is still enforced.

---

### P-014 · Stage 2 — Experience design

- **Date:** 2026-08-22 · **Sequence:** B2
- **Category:** UX · Navigation · Mobile responsiveness · Accessibility
- **AI/tool:** Claude Code
- **Recovery status:** `PARTIAL` — text from `docs/05-build-with-claude.md` Stage 2
- **Evidence:** `docs/05-build-with-claude.md`; `docs/02-experience-design.md`

```
Act as a luxury UX/UI designer. Using the creative direction in docs/, map
the complete experience.

For every section of the homepage define: its purpose (what specific visitor
doubt it closes), composition, any 3D or graphic element, interactions, and
the transition into the next section. Order the sections by objection-handling
sequence, not by feature list.

Then map: global header and footer, mobile navigation, every secondary page
shape, the responsive strategy with a stated reason for each breakpoint, and
accessibility as a design constraint rather than a retrofit.

Write it to docs/. Still no code.
```

- **Purpose:** Define the page architecture as objection-handling rather than as a feature list.
- **Implementation status:** Implemented.
- **Files changed:** `docs/02-experience-design.md`
- **Branch / commit:** redesign branch, folded into `c64d0a8`
- **Deployment status:** Documentation; the structure it defines is deployed
- **Outcome and notes:** "Accessibility as a design constraint rather than a retrofit" is why the redesign shipped with zero WCAG AA findings instead of an accessibility cleanup pass afterwards.

---

### P-015 · Stage 3 — The design system

- **Date:** 2026-08-22 · **Sequence:** B3
- **Category:** Code · Visual design · Accessibility
- **AI/tool:** Claude Code
- **Recovery status:** `PARTIAL` — text from `docs/05-build-with-claude.md` Stage 3
- **Evidence:** `docs/05-build-with-claude.md`; `assets/css/sklarz.css`

```
Now build the design system as a single stylesheet at assets/css/sklarz.css.
No framework, no preprocessor, no build step — this is a static GitHub Pages
site.

Include: CSS custom properties for the full colour ladder, fluid type scale,
spacing rhythm, motion tokens (no more than four durations and three easing
curves), then components for buttons, header, nav, hero, cards, editorial
grids, figures, footer, and long-form prose.

Requirements:
- Small gold text must never sit on a light background — brand gold fails
  WCAG AA there. Provide a separate darker gold token for that case and
  document why it exists.
- Light surfaces must be warm off-white, not blue-grey. Body ink must be
  navy-tinted, never pure black.
- Every hidden animation start-state must be scoped under html.js, so that
  if JavaScript fails the page renders complete and static rather than blank.
- A full prefers-reduced-motion block that resolves reveals to their FINAL
  state. A reduced-motion user must never get an invisible page.
- A print stylesheet.

Comment the reasoning behind any non-obvious value.
```

- **Purpose:** One stylesheet, no build step, with the accessibility and graceful-degradation rules baked in rather than added later.
- **Implementation status:** Implemented; measured at 12.6 KB gzipped.
- **Files changed:** `assets/css/sklarz.css`
- **Branch / commit:** redesign branch, folded into `c64d0a8`
- **Deployment status:** Deployed to production
- **Outcome and notes:** Carries forward the `--gold-ink` rule first established in P-009. The `html.js` scoping rule and the reduced-motion rule are both listed as load-bearing in `docs/README.md` — break either and a page can render blank.

---

### P-016 · Stage 4 — The cinematic hero

- **Date:** 2026-08-22 · **Sequence:** B4
- **Category:** Code · Visual design · Performance
- **AI/tool:** Claude Code
- **Recovery status:** `PARTIAL` — text from `docs/05-build-with-claude.md` Stage 4
- **Evidence:** `docs/05-build-with-claude.md`; `docs/03-cinematic-hero.md`; `assets/js/hero.js`

```
Act as an elite 3D web designer. Build the homepage hero: one memorable
object, in brand gold, in a navy void.

Use raw WebGL with a raymarched signed-distance-field scene in a single
fragment shader. Do NOT add Three.js or any 3D library — the hero needs
exactly one object, and a library would add hundreds of kilobytes while
making the material harder to match to the brand swatch.

Define the object, its material, a three-point light rig, camera, depth,
particles, cursor interaction, and scroll behaviour.

Material requirement, and this is the one that decides whether it looks
expensive: shade it as real metal. Polished metal has almost no diffuse
albedo — reflection carries the form. If you add a Lambert diffuse term every
facet lights to a similar value and it reads as matte plastic.

Guards, all required:
- No WebGL or a shader compile failure must leave a CSS gradient hero in
  place, with no error and no layout shift. The fallback ships in the HTML.
- prefers-reduced-motion draws one static frame and starts no loop.
- Stop the render loop when the hero leaves the viewport or the tab hides.
- Watch frame times and step resolution down before giving up entirely.
- Cap device pixel ratio. A raymarched hero at DPR 3 is 9x the pixels for no
  visible gain.

Then render it in headless Chromium and show me a screenshot. Iterate on my
feedback about the look before moving on.
```

- **Purpose:** One unforgettable object, at library-free weight, that degrades to a gradient rather than to a blank box.
- **Implementation status:** Implemented; refined again in P-023 and P-024.
- **Files changed:** `assets/js/hero.js`, `docs/03-cinematic-hero.md`, `index.html` (fallback markup)
- **Branch / commit:** redesign branch, folded into `c64d0a8`
- **Deployment status:** Deployed to production
- **Outcome and notes:** `docs/05` records that the object took **four material passes** — too large and colliding with the headline, then flat plastic, then blown-out white, then green-shadowed — before it read as gold. Naming the specific failure mode ("a Lambert term makes it look like plastic") is recorded there as more effective than asking for "premium".

---

### P-017 · Stage 5 — The motion system

- **Date:** 2026-08-22 · **Sequence:** B5
- **Category:** Code · UX · Performance · Accessibility
- **AI/tool:** Claude Code
- **Recovery status:** `PARTIAL` — text from `docs/05-build-with-claude.md` Stage 5
- **Evidence:** `docs/05-build-with-claude.md`; `docs/04-motion-language.md`; `assets/js/motion.js`

```
Act as a luxury motion-design director. Build a unified animation system at
assets/js/motion.js covering page-load choreography, scroll reveals,
parallax, the process rail progress line, hover states, cursor, page
transitions, and header behaviour.

Architecture requirements:
- ONE IntersectionObserver for all reveals, and each element unobserves
  itself after firing. Reveals happen once; do not re-animate on scroll-back.
- ONE requestAnimationFrame loop for parallax, rail progress, and header
  state. Cache all geometry; never read layout inside the loop.
- Scroll and resize listeners must be passive and only set a flag.
- Animate only transform, opacity, and filter.

Design requirements:
- Reveals include a blur-to-sharp pass so they read as a camera focus pull
  rather than a generic fade-up.
- No bounce, no elastic, no overshoot, no spinning, no scale transforms on
  cards or type.
- Clamp parallax travel so nothing detaches from its layout position.
- Page transitions must be wrapped so that any failure falls through to a
  normal navigation, and the overlay must never be able to trap a click.
- Author headline lines explicitly in the markup rather than splitting text
  in JavaScript, and release the overflow clip once a line has played so a
  later reflow cannot crop it.
```

- **Purpose:** One motion system with a stated banned list, rather than per-page animation.
- **Implementation status:** Implemented; measured at 11.5 KB gzipped.
- **Files changed:** `assets/js/motion.js`, `docs/04-motion-language.md`
- **Branch / commit:** redesign branch, folded into `c64d0a8`
- **Deployment status:** Deployed to production
- **Outcome and notes:** "The overlay must never be able to trap a click" and the fall-through-to-normal-navigation rule are both failure-mode instructions, not aesthetic ones — the pattern this project repeatedly gets value from.

---

### P-018 · Stage 6 — Rebuild the homepage

- **Date:** 2026-08-22 · **Sequence:** B6
- **Category:** Homepage editing · Copy · Code
- **AI/tool:** Claude Code
- **Recovery status:** `PARTIAL` — text from `docs/05-build-with-claude.md` Stage 6
- **Evidence:** `docs/05-build-with-claude.md`; commit `c64d0a8`

```
Rebuild index.html on the design system and motion system. Follow the section
map in docs/ exactly, in order.

Keep every existing outbound URL unchanged: the Calendly link, the mailto,
all social profiles. Preserve the existing copy where it is already good —
tighten wording, but do not invent claims, metrics, or credentials.

Set truthful width and height on every image; check each file's real
intrinsic dimensions rather than trusting the previous markup. Alternate
section grounds so no two identical backgrounds touch, and place each graphic
on a ground that contrasts with the artwork's own background.

Then screenshot it at 1440px and 390px and show me both.
```

- **Purpose:** The reference implementation of the design system.
- **Implementation status:** Implemented.
- **Files changed:** `index.html`, plus fixes to `assets/css/sklarz.css` and `assets/js/motion.js`
- **Branch / commit:** `c64d0a8` "Rebuild homepage on a cinematic navy-and-gold design system"
- **Deployment status:** Deployed to production
- **Outcome and notes:** Verifying caught real defects the build had not noticed: muted and faint ink tokens failing AA at 3.07:1 and 2.90:1, the header brandmark at 4.21:1, a footer heading jumping h2→h4, and the headshot being 900×900 rather than the declared 900×1100. "Check the file's real intrinsic dimensions rather than trusting the markup" earned its place.

---

### P-019 · Stage 7 — Build the verification harness

- **Date:** 2026-08-22 · **Sequence:** B7
- **Category:** QA · Testing · Accessibility
- **AI/tool:** Claude Code
- **Recovery status:** `PARTIAL` — text from `docs/05-build-with-claude.md` Stage 7
- **Evidence:** `docs/05-build-with-claude.md`; `docs/07-launch-qa.md`

```
Write a headless Chromium harness that, for each page and at 1440 / 834 /
390px:

1. Scrolls the whole page so every IntersectionObserver reveal fires, and
   waits for lazy images to decode, BEFORE measuring anything.
2. Computes the WCAG contrast ratio of every rendered text node against its
   true composited background, and flags anything under 4.5:1 (or 3:1 for
   large or bold text).
3. Reports: missing or untruthful image dimensions, images that failed to
   load, links and buttons with no accessible name, skipped heading levels,
   duplicate ids, and any horizontal overflow.
4. Captures a screenshot of every section at full resolution.

Two things the harness must get right or it will lie to you:
- A fixed transparent header overlays a section that is not its DOM ancestor.
  Walking up the tree resolves its background to body-white and reports false
  contrast failures. Hit-test the real paint stack for anything inside a
  fixed subtree, and include the element's own background.
- A lazily-loaded image parked far outside the viewport may never have been
  asked to load. That is unknowable, not broken — do not report it as a
  failure.

Run it, fix every real finding, and re-run until it is clean. Show me the
before and after counts.
```

- **Purpose:** Replace opinion-based QA with measurement, and make "done" mean "measured clean".
- **Implementation status:** Implemented and used on every commit since.
- **Files changed:** harness scripts (not committed to the repository); findings recorded in `docs/07-launch-qa.md`
- **Branch / commit:** redesign branch
- **Deployment status:** Tooling only
- **Outcome and notes:** Described in `docs/05` as the stage that matters most, and the numbers bear it out — every subsequent commit body reports a route-by-width pass count. Note the standing warning: **a QA tool that lies is worse than no tool.** Two harness bugs were later found that had been reporting passes for regions they never measured (`1aa56c8`).

---

### P-020 · Stage 8 — Convert every secondary page onto the design system

- **Date:** 2026-08-22 · **Sequence:** B8
- **Category:** Code · Copy preservation · Structured data
- **AI/tool:** Claude Code
- **Recovery status:** `PARTIAL` — text from `docs/05-build-with-claude.md` Stage 8
- **Evidence:** `docs/05-build-with-claude.md`; commit `1ea9e44`

```
Convert the remaining pages onto the design system, one group at a time.

For each page: read it first, delete its inline <style> block entirely, and
rebuild it from the shared components. Preserve all copy, all URLs, and all
section ids that anything links to.

Every page must open with a dark section. The header is fixed and transparent
at scroll-top, so a light first section drops the nav type below AA contrast.
This is a technical constraint, not a preference.

Do not load the hero script on any page except the homepage.

Add the structured data any page is missing, but never invent a publication
date. If the old page did not state one, omit the field.

Then run the Stage 7 harness across every page.
```

- **Purpose:** Retire eleven separate inline stylesheets without losing copy, URLs or anchors.
- **Implementation status:** Implemented.
- **Files changed:** `media-kit.html`, `404.html`, all nine Insights pages, `assets/css/sklarz.css`
- **Branch / commit:** `1ea9e44` "Convert every secondary page onto the design system"
- **Deployment status:** Deployed to production
- **Outcome and notes:** Verified 399 internal links and anchors all resolving, zero AA failures across eleven pages at 1440 and 390px. Surfaced the `.page-hero` cannot carry `.is-dark` constraint — a ghost button in a page hero was resolving to navy on near-black at ~1.3:1, correct in isolation and broken only in that one composition. Also recovered the Threads and X profile links, which existed only on the old Media Kit and would otherwise have been silently lost.

---

### P-021 · Stage 9 — Premium audit

- **Date:** 2026-08-22 · **Sequence:** B9
- **Category:** Auditing · Visual design · Copy
- **AI/tool:** Claude Code
- **Recovery status:** `PARTIAL` — text from `docs/05-build-with-claude.md` Stage 9
- **Evidence:** `docs/05-build-with-claude.md`; `docs/06-making-it-feel-premium.md`

```
Act as a premium agency creative director. Audit the built site and find
everything that still reads as generic, cheap, or template-generated.

Go section by section and give me exact changes — specific values, not
adjectives — for typography, spacing, hierarchy, composition, 3D materials,
lighting, motion, copy, and micro-details.

For each item state the change, the reason, and the effort. Rank by impact.
Be harsh; I would rather hear it now.
```

- **Purpose:** An adversarial pass against the site's own output, demanding values rather than adjectives.
- **Implementation status:** Implemented.
- **Files changed:** `docs/06-making-it-feel-premium.md` and the fixes it drove
- **Branch / commit:** redesign branch
- **Deployment status:** Deployed to production
- **Outcome and notes:** "Specific values, not adjectives" and "be harsh" are what make this stage produce work instead of reassurance.

---

### P-022 · Stage 10 — Launch QA

- **Date:** 2026-08-22 · **Sequence:** B10
- **Category:** QA · Testing · Deployment readiness
- **AI/tool:** Claude Code
- **Recovery status:** `PARTIAL` — text from `docs/05-build-with-claude.md` Stage 10
- **Evidence:** `docs/05-build-with-claude.md`; `docs/07-launch-qa.md`

```
Act as my creative director and web QA engineer. Do a final pass over
design, typography, 3D rendering, animation, responsiveness, accessibility,
SEO, performance, browser compatibility, and conversion.

Rank every issue by impact with an exact fix for each. Verify each fix in a
real browser — do not mark anything done that you have not seen render.

Then give me a launch checklist covering what you verified locally and,
separately, what can only be verified against the live domain after deploy.
Be explicit about that split; do not present an unverifiable item as passing.
```

- **Purpose:** A ranked, verified final pass with an honest boundary around what local testing can and cannot prove.
- **Implementation status:** Implemented.
- **Files changed:** `docs/07-launch-qa.md`
- **Branch / commit:** redesign branch
- **Deployment status:** Documentation; gates deployment
- **Outcome and notes:** Produced the before-merge / at-deploy / after-deploy checklist now restated in `WEBSITE_WORKFLOW.md`. Its most valuable admission: Google Fonts is blocked by the build environment's egress proxy, so **Playfair Display has never been seen rendering locally** — every local screenshot fell back to Georgia. That is exactly the kind of item that a less honest report would have marked as passing.

---

## Phase C · Positioning, scorecard and print — 22–23 August 2026

No prior-session wording survives for this phase. Every entry is
`RECONSTRUCTED` from unusually detailed commit bodies, which in several cases
paraphrase the instruction that triggered the work.

---

### P-023 · Fix the gem's blown-out highlight

- **Date:** 2026-08-22 · **Sequence:** C1
- **Category:** Visual design · Code
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commit `cb8c323` "Stop the gem's key highlight from clipping to a mottled slab"

```
At some rotation angles the gem's highlight blows out into a flat, mottled
white slab instead of reading as sheen. Find out why and fix it without
dulling the object.
```

- **Purpose:** Remove a rotation-phase-dependent rendering artefact.
- **Implementation status:** Implemented.
- **Files changed:** `assets/js/hero.js`
- **Branch / commit:** `cb8c323`
- **Deployment status:** Deployed to production
- **Outcome and notes:** A facet mirroring the key light pushed the reflection past 1.0; tonemapping then flattened the face to near-white and exposed the material's roughness variation as blotches. Fixed with a Reinhard-style rolloff on the bright end only, so dark values stay put. Two approaches were tried and rejected first — lowering key intensity dulled everything, and normal-perturbing noise read as blotchy at any useful amplitude.

---

### P-024 · Fix the 3D object being cut in half on phones

- **Date:** 2026-08-22 · **Sequence:** C2
- **Category:** Mobile responsiveness · Visual design
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED` — the commit records the report as *"on mobile only the top half of the object showed"*, which is the repository's paraphrase, not the original wording
- **Evidence:** commit `b0af741` "Stop the 3D object being cut in half on phones"

```
On mobile only the top half of the 3D object shows. Fix it, and verify at
several real phone widths rather than one.
```

- **Purpose:** Repair the hero on the viewport class where most visitors will meet it.
- **Implementation status:** Implemented.
- **Files changed:** `assets/js/hero.js`, `assets/css/sklarz.css`, `index.html`
- **Branch / commit:** `b0af741`
- **Deployment status:** Deployed to production
- **Outcome and notes:** Two causes, and the second was the real bug: the object sat below the fold and was clipped by the hero's own edge, **and** the depth fog and ray budget were absolute world distances tuned to the landscape camera, so moving the camera back for portrait pushed the object past `t > 14.5` and past the fog's far plane. Both are now relative to camera distance. Verified at 360, 390 and 430px. The same commit gave the five footer social links real platform glyphs with 44px tap targets and `aria-label`s.

---

### P-025 · Replace estimated payload figures with measured ones

- **Date:** 2026-08-22 · **Sequence:** C3
- **Category:** QA · Documentation honesty
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commit `c7c63b3`

```
The payload sizes in the QA record were estimated before the stylesheet was
finished. Measure them and replace the estimates with the real numbers.
```

- **Purpose:** Stop an unverified figure sitting in a document that presents itself as measured.
- **Implementation status:** Implemented.
- **Files changed:** `docs/07-launch-qa.md`
- **Branch / commit:** `c7c63b3`
- **Deployment status:** Documentation only
- **Outcome and notes:** Measured 12.6 KB gzipped CSS, 11.5 KB gzipped JS, 6.2 KB gzipped homepage. Small commit, but it is the house rule applied to the project's own paperwork.

---

### P-026 · Preserve the scorecard by merging main rather than rebasing

- **Date:** 2026-08-22 · **Sequence:** C4
- **Category:** GitHub · Branches · Production commit preservation
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commit `26bf7a4` "Merge main to preserve the Trust-First Content Scorecard"

```
main has moved ahead of the redesign branch — it now has the interactive
Trust-First Content Scorecard, the Resources feature block and the sitemap
entry. Bring that work into the redesign branch without losing it.

Merge, do not rebase. Resolve the conflicts deliberately and tell me what you
chose in each one.
```

- **Purpose:** Integrate three commits of client work into an in-flight redesign branch without rewriting or dropping them.
- **Implementation status:** Implemented.
- **Files changed:** `insights/resources/index.html`, `sitemap.xml`, plus the merged scorecard page
- **Branch / commit:** `26bf7a4`, merging `f51403f`, `d81042b`, `e5aa3a6`
- **Deployment status:** Deployed to production
- **Outcome and notes:** Two conflicts resolved deliberately and documented in the commit: the Resources page kept the redesigned version with the scorecard feature block **re-authored** in the design system rather than merged as-is, and the sitemap kept the redesign's `lastmod` dates while gaining the scorecard and `/work/` routes. The scorecard page itself arrived unmodified and was converted separately in P-028 — a clean separation of "preserve" from "change".

---

### P-027 · Replace "Creative with a reason"

- **Date:** 2026-08-22 · **Sequence:** C5
- **Category:** Copy · Positioning
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED` — the commit records only that the line was *"flagged as not making sense"*
- **Evidence:** commit `ccc69c4` "Replace \"Creative with a reason\" — it does not parse"

```
"Creative with a reason" does not make sense. Replace it.
```

- **Purpose:** Remove a line that fails to communicate.
- **Implementation status:** Implemented.
- **Files changed:** `index.html`
- **Branch / commit:** `ccc69c4`
- **Deployment status:** Deployed to production
- **Outcome and notes:** Diagnosis in the commit: it uses "creative" as a noun — agency shorthand rather than plain English — and leaves two questions open, creative what and a reason for what. Replaced with **"Strategy first. Everything else answers to it."** Importantly, this commit **overturned a prior rule**: the line had been preserved under a don't-rewrite-existing-copy rule, and the commit records that as the wrong call — *"the copy belongs to the client, and a line that fails to communicate is a defect, not heritage."* The marquee dropped to five real lines rather than inventing a sixth to fill the slot, and the screen-reader copy was updated to match.

---

### P-028 · Convert the Trust-First Content Scorecard onto the design system

- **Date:** 2026-08-22 · **Sequence:** C6
- **Category:** Code · Accessibility · QA
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commit `240e002`

```
Convert the Trust-First Content Scorecard onto the design system, the same way
as the other pages — read it first, remove its inline stylesheet, rebuild from
the shared components.

The scoring model must survive exactly: five categories, twenty statements,
0/1/2, bands at 32/24/16. Verify it is unchanged rather than assuming, and
re-test at every band boundary.
```

- **Purpose:** Bring inherited client work onto the system without altering its substance.
- **Implementation status:** Implemented.
- **Files changed:** `insights/resources/trust-first-content-scorecard/index.html`, `assets/css/sklarz.css`
- **Branch / commit:** `240e002`
- **Deployment status:** Deployed to production
- **Outcome and notes:** Scoring verified **by checksum rather than by eye**. Two accessibility gains: each statement became a `fieldset` whose `legend` is the statement itself — the original gave all twenty radio groups the same accessible name, "Score 0, 1, or 2", which told a screen reader nothing — and each score option became a 44px target with a visible focus ring. One hazard found by testing rather than reading: the sticky result bar floated over the statements with no clearance, so the last statement could never be scrolled clear of it.

---

### P-029 · Sharpen strategic positioning across the site

- **Date:** 2026-08-22 · **Sequence:** C7
- **Category:** Positioning · Founder title · Copy · Structured data
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commit `000e1b8` "Sharpen strategic positioning across the site"; the positioning table in `docs/README.md`

```
The site under-sells the practice. Sharpen the positioning across every page.

Sklarz Creative is a strategic brand, marketing and creative consultancy — not
a social-media, content-production or graphic-design service. It helps
expert-led and innovative organisations become clearer, more credible, more
discoverable and better equipped to grow.

Fix the founder title. "Strategic marketing consultant, creative director,
storyteller, researcher, and founder" reads as a skills inventory rather than a
level of practice. State one senior role with the disciplines beneath it.

Rebuild the capability architecture so business development and partnerships
are a named capability rather than buried inside other cards. Add AI as an
operating model, not an identity — pair what it helps with against an explicit
column of what stays human. The site must nowhere describe itself as an AI
agency.

Add a proof layer. Invent no clients, metrics, testimonials, results or
credentials — only work that exists and is linkable.
```

- **Purpose:** Move the site from describing services to stating a level of practice.
- **Implementation status:** Implemented.
- **Files changed:** `index.html`, `media-kit.html`, new `work/index.html`, Insights pages, `assets/css/sklarz.css`, `sitemap.xml`
- **Branch / commit:** `000e1b8`
- **Deployment status:** Deployed to production
- **Outcome and notes:** The founder title became **Founder & Strategic Marketing Consultant** with a discipline line beneath — Brand Strategy · Creative Direction · Research & Intelligence · Growth & Partnerships — carried into every `jobTitle` field in the structured data. Six named capabilities, with Partnerships & Business Development promoted to its own card. New `/work/` page describing scope, role, process and output with nothing invented. Homepage gained an `@graph` of Organization, Person and WebSite with stable `@id`s so the relationship between Cassandra Sklarz and Sklarz Creative is machine-readable. `datePublished` present only where a page actually states a date. Horizontal-overflow clip declared on both `html` and `body` using `clip` rather than `hidden`, because `overflow-x` on body alone is unreliable on iOS Safari. Verified: 502 internal links resolve, sitemap matches disk exactly, zero AA/overflow/heading-order/duplicate-id/unnamed-link findings across thirteen pages at three widths.

---

### P-030 · Wire the scorecard lead capture

- **Date:** 2026-08-22 · **Sequence:** C8
- **Category:** Forms · Conversion
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED` — commit `e0801a2` has a subject line and no body, so this is inferred from its subject and from the corrective work in P-031
- **Evidence:** commit `e0801a2` "Wire Scorecard lead capture and immediate delivery"

```
Add lead capture to the Trust-First Content Scorecard, with the result
delivered immediately after the visitor submits.
```

- **Purpose:** Turn the scorecard into a lead-generation path as well as a piece of IP.
- **Implementation status:** Implemented, then substantially corrected in P-031 and removed in P-032.
- **Files changed:** `insights/resources/trust-first-content-scorecard/index.html`
- **Branch / commit:** `e0801a2`
- **Deployment status:** Deployed to production, then superseded
- **Outcome and notes:** The capture was aimed at Netlify Forms. The next two commits established that this was the wrong target — see P-031 and P-032. Recorded here as a genuine part of the history, including the part that turned out to be wrong.

---

### P-031 · Make the scorecard capture fail open and bring it onto the design system

- **Date:** 2026-08-23 · **Sequence:** C9
- **Category:** Forms · Accessibility · Code · Security
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commit `1aa56c8` "Bring the Scorecard capture onto the design system, and make it fail open"

```
Review the scorecard's lead capture before it ships. Three things are wrong
with how it is wired.

Access must not depend on the capture. Reveal the result locally and first,
then fire the POST and do not await it. A failed capture is information, not
an obstacle — the visitor gets the tool either way.

The twenty statements must be authored in HTML, not generated in JavaScript,
so a scripting failure leaves a real, printable, hand-scoreable instrument
instead of an empty container.

The page-specific style block must go into sklarz.css as reusable components.

Do not put any email-provider credential in front-end code in a public
repository. Document where the enrolment belongs instead.
```

- **Purpose:** Ensure the tool is never held hostage to the capture, and get the page onto the system.
- **Implementation status:** Implemented.
- **Files changed:** scorecard page, `assets/css/sklarz.css` (new §16b), `docs/08-scorecard-capture.md`
- **Branch / commit:** `1aa56c8`
- **Deployment status:** Deployed to production, capture later removed in P-032
- **Outcome and notes:** Established the standing rule: **the visitor gets the tool, the capture is a courtesy.** ~9 KB of inline CSS with hard-coded hexes reconciled into reusable components. The invalid state signals with border weight and a message rather than colour — the palette has no red, and colour alone would fail AA anyway. Restored the per-statement accessible names, which had regressed to twenty identical "Score 0, 1, or 2" labels. Two print bugs fixed beyond the scorecard: `.page-hero` was never neutralised for print, so every secondary page printed its title white on white. **Two harness bugs were also found and fixed — both had been reporting passes for regions they never measured.**

---

### P-032 · Determine the real production host and ship the scorecard open

- **Date:** 2026-08-23 · **Sequence:** C10
- **Category:** Deployment · Forms · Production verification
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commit `13d49c6` "Ship the Scorecard open: GitHub Pages is the host, not Netlify"

```
Before this ships, establish which platform actually serves sklarzcreative.com.
Do not assume — prove it from the deploy history and from what is live right
now.

If the capture cannot work on the real host, take it out rather than shipping
a form that collects nothing while standing in front of a proof asset.
```

- **Purpose:** Verify a deployment assumption against evidence rather than inheriting it.
- **Implementation status:** Implemented.
- **Files changed:** scorecard page, `assets/css/sklarz.css`, `docs/08-scorecard-capture.md`, `docs/README.md`
- **Branch / commit:** `13d49c6`
- **Deployment status:** Deployed to production
- **Outcome and notes:** The proof, worth preserving: **Netlify has skipped every production deploy since 9 August**, each marked "Skipped — account credit usage exceeded", including `e5aa3a6`, `d81042b` and `f51403f`. The live site was serving `e5aa3a6`, whose scorecard route only came into existence in `f51403f` — a commit Netlify skipped. So **GitHub Pages serves the domain**, matching Pages run #49 succeeding on `main` @ `e5aa3a6`. GitHub Pages cannot process a form post, run a function or hold a secret, so the gate was removed and the diagnostic ships open. The form components were kept in `sklarz.css` (~1.5 KB gzipped) so restoring capture is a paste plus an endpoint rather than a rebuild, and the three retired gate rules were left in place as a comment rather than deleted. This entry is the reason `WEBSITE_WORKFLOW.md` requires determining the exact production commit and host before acting.

---

### P-033 · Give the printed scorecard letterhead and a signature

- **Date:** 2026-08-23 · **Sequence:** C11
- **Category:** Visual design · Print · Brand
- **AI/tool:** Claude Code
- **Recovery status:** `RECONSTRUCTED`
- **Evidence:** commit `a5be572` "Give the printed scorecard letterhead and a signature"

```
A completed scorecard gets filed, forwarded or handed to a client, and the
printout currently cannot say who produced it or where it came from — no
header, no navigation, no address bar.

Give it proper stationery: a masthead on page one and a colophon closing the
sheet with the document title, its URL, the discovery-call link and the
copyright. Print-only; it must not shift the screen layout.

Tighten the print rhythm too — the screen spacing is producing blank sheets.
```

- **Purpose:** Make the printed artefact self-identifying and worth handing over.
- **Implementation status:** Implemented. **This is the current HEAD of both `main` and the working branch.**
- **Files changed:** `assets/css/sklarz.css` (§17b), scorecard page
- **Branch / commit:** `a5be572`
- **Deployment status:** Deployed to production
- **Outcome and notes:** Three choices in that CSS are print choices rather than screen ones: structure is drawn with borders and type, never backgrounds, because browsers drop background colours when printing but honour borders; the wordmark's gold half uses `--gold-ink` because brand gold sits around 65% luminance and turns pale grey on a monochrome printer; and site-relative links print their host via `a[href^="/"]::after`, because "(/insights/…)" on paper has no address bar to resolve against. **The signature is typographic, not a facsimile** — the commit states plainly that inventing somebody's signature is not the tool's to do, and leaves `.print-sign` ready for a real mark. Print rhythm collapsed through the one token driving it: the scorecard went from six pages to five with no page count getting worse elsewhere.

---

## Phase D · This archive — 23 August 2026

---

### P-034 · Create the Claude Code website prompt-memory and documentation system

- **Date:** 2026-08-23 · **Sequence:** D1
- **Category:** Documentation · Prompt memory · Process
- **AI/tool:** Claude Code
- **Recovery status:** `VERBATIM` — held in full in the session that wrote this file
- **Evidence:** the session prompt itself

```
You are working inside the Sklarz Creative website repository.
I want you to create a durable prompt-memory and documentation system specifically for all Sklarz Creative website auditing, editing, redesign, positioning, SEO, UX, QA, deployment, and rollback work.
This is a documentation and memory task only. Do not alter or deploy the production website as part of this task.
1. Inspect the repository first
Before changing anything:

* Check `git status`.
* Identify the repository root.
* Find any existing `CLAUDE.md`, `.claude/` rules, documentation folders, prompt archives, change logs, or AI instruction files.
* Preserve all existing instructions and documentation.
* Do not overwrite or delete existing material.

2. Create the Claude Code website prompt archive
Create this directory if it does not already exist:
`docs/ai-prompts/claude-code/`
Inside it create:

* `WEBSITE_PROMPT_ARCHIVE.md`
* `WEBSITE_WORKFLOW.md`
* `PROMPT_INDEX.md`

3. Recover my historical website prompts
Review everything you can legitimately access from this Claude Code conversation/session and capture every material prompt I have used concerning:

* sklarzcreative.com
* website audits or surveys
* redesigns
* brand changes
* positioning and messaging
* founder title or description changes
* homepage editing
* service-page editing
* copy changes
* UX and conversion
* SEO
* metadata
* social previews
* structured data
* navigation
* mobile responsiveness
* accessibility
* forms
* calls to action
* GitHub
* branches
* deployments
* production backups
* rollback
* production commit preservation
* QA
* testing
* post-deployment verification

Do not claim you recovered prompts you cannot actually access.
4. Preserve exact prompt wording
For every prompt you recover, add an entry to `WEBSITE_PROMPT_ARCHIVE.md` with:

* date, if known
* sequence/order if exact date is unknown
* title
* category
* AI/tool: Claude Code
* exact raw prompt
* recovery status: `VERBATIM`, `PARTIAL`, or `RECONSTRUCTED`
* purpose
* implementation status
* files changed, when known
* related branch or commit SHA, when known
* deployment status, when known
* outcome and notes

Never silently rewrite something and call it verbatim.
If only part of the original prompt is available, label it `PARTIAL`.
If you recreate a useful prompt from available context, label it `RECONSTRUCTED`.
5. Protect private information
Treat repository prompt history as potentially publishable through source control.
Before saving any raw prompt:

* remove passwords
* remove API keys
* remove access tokens
* remove credentials
* remove private URLs
* remove unrelated personal information
* remove private client information
* remove private account information
* remove confidential documents or details

Replace sensitive content with:
`[REDACTED]`
Keep the repository archive limited to website-development material that is appropriate to store in source control.
6. Create permanent website workflow memory
Create `WEBSITE_WORKFLOW.md`.
The standing Sklarz Creative website workflow is:
Inspect → understand → back up → plan → implement → test → verify → deploy → document
Include these permanent rules:

* Inspect the existing project and instructions before editing.
* Preserve the approved Sklarz Creative brand system and approved assets.
* Do not reinterpret or recreate official logo or founder assets.
* Position Sklarz Creative as a multidisciplinary strategic and creative consultancy, not merely a social-media, content-creation, or graphic-design execution service.
* Preserve rollback capability before material redesigns or deployments.
* Determine the exact production commit before creating a production backup.
* Review the Git diff before deployment.
* Test desktop and mobile.
* Verify navigation.
* Verify links.
* Verify CTAs.
* Verify forms.
* Verify images and assets.
* Verify SEO metadata.
* Verify social metadata.
* Verify favicon behavior.
* Verify responsive behavior.
* Check for obvious browser-console errors.
* Perform basic accessibility QA.
* Verify the live site after production deployment.
* Record the deployed commit SHA.
* Record the rollback branch or commit.
* Never expose secrets or private content.
* Never deploy a documentation-only prompt-memory change unless I separately request deployment.

7. Connect this to Claude Code's persistent project memory
If the repository already contains a root `CLAUDE.md`, preserve everything already there.
Add a concise import/reference for:
`@docs/ai-prompts/claude-code/WEBSITE_WORKFLOW.md`
Do not import the entire raw prompt archive into `CLAUDE.md`.
The always-loaded memory should remain concise.
If no project `CLAUDE.md` exists, create an appropriate one and import the website workflow.
Do not destroy or replace valid project instructions discovered elsewhere.
8. Build a prompt index
Create `PROMPT_INDEX.md`.
For every archived prompt, include:

* prompt number
* date
* title
* category
* recovery status
* related branch
* related commit, if known
* implementation status

Keep this file concise so I can quickly find previous prompts.
9. Add a future prompt-capture rule
From now on, material website prompts should be preserved in the archive when appropriate.
Archive prompts that materially direct:

* strategy
* positioning
* copy
* visual design
* code
* SEO
* UX
* accessibility
* QA
* deployment
* Git workflow
* backups
* rollback

Do not archive trivial conversational messages.
Before implementation, preserve the material prompt.
After implementation, update its record with:

* outcome
* files changed
* tests performed
* branch
* commit SHA
* deployment status
* rollback reference when applicable

10. Keep this setup isolated
Do not change website production code while creating this system.
When finished, show me the Git diff for the documentation and memory files only.
If the changes are clean, create a separate documentation commit:
`docs: add Claude Code website prompt memory`
Do not deploy this commit unless I explicitly tell you to deploy it.
11. Report what you recovered
When complete, tell me:

1. Which files you created or updated.
2. How many historical website prompts you recovered.
3. How many were VERBATIM.
4. How many were PARTIAL.
5. How many were RECONSTRUCTED.
6. Whether the website workflow now loads through Claude Code project memory.
7. The documentation commit SHA, if committed.
8. Which previous prompts or sessions you could not recover.

Do not say you have "memorized" something unless it has actually been stored through Claude Code's durable memory or project files.
```

- **Purpose:** Establish durable prompt memory and a standing workflow so website decisions survive the end of any single session.
- **Implementation status:** Implemented.
- **Files changed:** `docs/ai-prompts/claude-code/WEBSITE_PROMPT_ARCHIVE.md`, `WEBSITE_WORKFLOW.md`, `PROMPT_INDEX.md`; new root `CLAUDE.md`; one pointer row added to `docs/README.md`
- **Branch / commit:** `claude/sklarz-website-prompt-archive-qwy7h4`
- **Deployment status:** **Not deployed.** Documentation only, held off production pending explicit instruction, per the prompt's own rule.
- **Outcome and notes:** No production website code was changed. The recovery limits are stated at the top of this file and in the report that accompanied it.

---

## What could not be recovered

Stated plainly, because the alternative is a false impression of completeness:

1. **Every prior Claude Code conversation.** No earlier session transcript is readable from here. Commit trailers on the 22–23 August work reference a prior session URL (withheld as `[REDACTED]`, being a private URL), and that session's prompts are not recoverable through this repository. P-013…P-022 survive only because a previous session deliberately wrote them into `docs/05-build-with-claude.md` — a strong argument for this archive existing.
2. **The exact wording of everything in Phase A and Phase C.** Twenty-two entries are `RECONSTRUCTED`. The commits are unusually well written and the substance is well evidenced, but the words are not the client's.
3. **Feedback and iteration turns.** `docs/05` records that the hero needed four material passes; the rejections that drove those passes are gone. Likewise the review turns behind P-023 and P-024, and any prompt that produced no commit — rejected directions, questions, and course corrections that were absorbed into later work.
4. **Any prompt given outside Claude Code.** Nothing in this repository evidences work done in another tool, and none is claimed.
5. **Commits with no body.** `e0801a2`, `f51403f`, `d81042b`, `e5aa3a6` and the Phase A commits carry subject lines only, so P-001…P-011 and P-030 are inferred from subject, diff and downstream commentary rather than from a stated rationale.

The gap closes going forward: from now on, material prompts are archived
**before** implementation, under the capture rule in `WEBSITE_WORKFLOW.md`.
