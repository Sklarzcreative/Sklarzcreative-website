# 05 · Building It With Claude — sequential prompts

> Staged prompts for building or extending this site with Claude Code, written
> so that no stage requires you to write code yourself.
>
> **The site in this repository was built by running this sequence.** The
> prompts below are the real ones, generalised — including the verification
> steps, which are where most of the quality actually came from.

---

## How to use this

Run one stage at a time. **Do not paste the whole document at once** — each
stage depends on the previous stage's output existing on disk, and batching
them removes the inspection step that keeps the work honest.

Three instructions appear in almost every prompt. They are the load-bearing
part of this document:

1. **"Read X before you change it."** Prevents confident edits to files whose
   actual contents were assumed.
2. **"Verify it in a real browser and show me the result."** Prevents "done"
   from meaning "written".
3. **"Do not change anything that already works."** Prevents collateral
   regressions.

---

## Stage 0 · Preserve what exists

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

## Stage 1 · Creative direction

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

## Stage 2 · Experience design

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

## Stage 3 · Design system

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

## Stage 4 · The cinematic hero

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

> **Expect several rounds here.** In this build the object went through four
> distinct material passes — too large and colliding with the headline, then
> flat plastic, then blown-out white, then green-shadowed — before it read as
> gold. Screenshot every round. This is not a stage to accept on the first
> result.

## Stage 5 · Motion system

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

## Stage 6 · Build the homepage

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

## Stage 7 · Verify — the stage that matters most

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

## Stage 8 · Convert the remaining pages

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

## Stage 9 · Premium audit

```
Act as a premium agency creative director. Audit the built site and find
everything that still reads as generic, cheap, or template-generated.

Go section by section and give me exact changes — specific values, not
adjectives — for typography, spacing, hierarchy, composition, 3D materials,
lighting, motion, copy, and micro-details.

For each item state the change, the reason, and the effort. Rank by impact.
Be harsh; I would rather hear it now.
```

## Stage 10 · Launch QA

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

---

## Prompt patterns that produced the best results

| Pattern | Why it works |
| --- | --- |
| "Read X fully before writing any markup" | Stops invented class names and assumed file contents. |
| "Screenshot it and show me" | Converts "done" from *written* to *seen working*. |
| "Iterate on my feedback before moving on" | The hero needed four passes. Batching stages would have shipped the plastic-looking version. |
| "Do not invent metrics, logos, or dates" | Models fill gaps plausibly. For a trust-led brand this is the highest-stakes failure mode on the site. |
| "This is a technical constraint, not a preference" | Distinguishes rules that may be traded off from rules that may not. |
| "Explain why a non-obvious value is what it is" | Produces a codebase the next person can safely change. |
| "State what you could NOT verify" | The most valuable line in any QA report. |
| Naming the specific failure mode | "A Lambert term makes it look like plastic" prevents the exact wrong turn, where "make it look premium" does not. |
