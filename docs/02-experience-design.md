# 02 · Experience Design — the full journey

> Section-by-section UX/UI specification for sklarzcreative.com. Every block
> below states its **purpose**, **composition**, **3D/graphic**,
> **interaction**, and **transition into the next block**.

---

## The narrative spine

A visitor arrives not knowing whether this person is senior enough to trust
with a hard problem. The page has to answer, in order:

1. **What is this?** → hero
2. **What do you believe?** → thesis
3. **Can you prove you think rigorously?** → trust lens
4. **What can you actually do?** → capabilities
5. **How do you work?** → process
6. **Show me the thinking.** → Trust Files + Insights
7. **Who am I hiring?** → founder
8. **What would this cost me to start?** → engagement models
9. **Let's talk.** → CTA

Objection-handling order, not feature order. Every section closes one specific
doubt, and none of them are interchangeable.

---

## Global chrome

### Header

- **Purpose:** persistent identity + persistent booking action.
- **Composition:** logotype left, five nav items centre-right, gold "Book a
  Call" button hard right. 84px tall.
- **States:** transparent over the hero → frosted navy
  (`rgba(8,17,30,.78)` + 18px backdrop blur) past 40px of scroll.
- **Interaction:** hides on scroll-down past 240px, returns immediately on
  scroll-up. Long reading passages get the full viewport; the CTA is one
  upward flick away. Never hides while the mobile menu is open or near the top.
- **Nav links:** a gold underline wipes in from the left on hover
  (`scaleX(0→1)`, transform-origin left). Current page marked with
  `aria-current="page"` and a persistent half-opacity underline.

### Mobile navigation (≤960px)

- Hamburger → X, drawn as two 1.5px rules that rotate ±45° to meet. No third
  bar, because a two-line mark morphs exactly and a three-line one has to
  hide its middle.
- Opens a **full-screen navy overlay at 97% opacity with a 20px blur**, not a
  dropdown. Nav items render in Playfair Display at 1.6–2.4rem — the menu is a
  designed moment, not a utility list.
- Items stagger in at 55ms intervals via an inline `--i` index.
- Focus moves to the first link on open; Escape closes and returns focus to
  the toggle; the body scroll-locks behind it; growing past 960px force-closes.

### Footer

- Brand + italic tagline, then Explore and Connect columns, then a hairline
  and the legal row. On `--void`, so the page ends where it began.

### Custom cursor (desktop, fine pointer, motion allowed)

- A 36px gold ring, damped toward the pointer at 0.16 per frame, in
  `mix-blend-mode: difference`. Grows to 60px with a gold wash over anything
  interactive. Never replaces the system cursor's job — it accompanies it.
- Absent entirely on touch and under `prefers-reduced-motion`.

---

## 1 · Hero — "The Signal Prism"

- **Purpose:** state the thesis and demonstrate craft in the same three
  seconds. The 3D object *is* the credential.
- **Composition:** asymmetric. Type owns the left half (max 34rem), the object
  owns the right. Nothing competes for the object's half — an earlier version
  put the credential rail there and both elements lost.
- **Type:** eyebrow → three-line Playfair headline at up to 96px → 38ch lede →
  two buttons.
- **Credential rail:** a hairline strip across the base carrying Practice /
  Built for / Founder, plus an animated Scroll marker at the right. Proof
  adjacent to promise, without crowding the object.
- **3D:** faceted gold monolith + orbital ring, in a navy void with drifting
  dust and 3.2% film grain. See [`03-cinematic-hero.md`](./03-cinematic-hero.md).
- **Interaction:** cursor moves the *camera*, not the object (±0.075 rad,
  damped at 0.055/frame). Scrolling dollies the camera back and dims the scene.
- **Load choreography:** header → headline lines (95ms stagger, masked from
  below) → lede → buttons → rail. ~1.1s total.
- **Mobile:** the object drops below the copy, dims to 34%, and a hard scrim
  guarantees the type's ground. Legibility outranks spectacle.
- **Transition out:** into the gold marquee — a hard, bright cut after the
  dark. The jolt is intentional.

## 2 · Marquee

- **Purpose:** the brand's own language, in the brand's loudest colour, as a
  palate cleanser between the hero and the argument.
- **Composition:** a 44s linear gold ticker of positioning phrases separated
  by dimmed `//` glyphs.
- **Interaction:** pauses on hover.
- **Accessibility:** `aria-hidden` on the visual track, with the same phrases
  in a `.visually-hidden` paragraph so screen readers get the content once
  rather than twice.

## 3 · Thesis (dark)

- **Purpose:** stake a point of view. This is where a generic consultancy says
  "we're passionate about brands" and loses the reader.
- **Composition:** 0.8/1.2 split. Left: eyebrow + the pull quote — *"The
  strongest brands do not win attention. They earn confidence."* — in bone
  italic Playfair up to 50px with a `<cite>`. Right: the explanatory paragraph
  plus two cards (Trust-sensitive work / End-to-end thinking).
- **Why dark:** it is the emotional peak of the argument, and large italic
  bone type on navy is the most expensive-looking thing the system can do.

## 4 · Trust lens (light)

- **Purpose:** prove rigour. A framework is the cheapest possible demonstration
  of senior thinking, and this one is already the firm's own.
- **Composition:** framework SVG in a `.plate` on the left, copy on the right,
  and a 2×2 block of the four dimensions — Clarity, Consistency, Credibility,
  Connection — numbered 01–04.
- **This is where a template would put invented client metrics.** Same visual
  rhythm as a stats band; entirely factual content. It resolves to File 001,
  so the section also feeds the content system.
- **3D/graphic:** `trust-framework.svg` (dark navy artwork on a light section,
  so it reads as a framed plate), drifting at `data-parallax="0.05"`.

## 5 · Capabilities (warm)

- **Purpose:** answer "what do you do" without becoming a service-page list.
- **Composition:** six numbered cards, auto-fit to three columns, separated by
  1px hairlines rather than gaps and shadows — a single ruled table, not six
  floating boxes. The hairline grid is doing a lot of the premium work here.
- **Interaction:** on hover the top hairline wipes across, a faint gold wash
  rises from the bottom, and the text lifts 3px. **No scale transform** —
  scaling type is the fastest way to look cheap.

## 6 · Process (dark)

- **Purpose:** de-risk the engagement by making the method legible.
- **Composition:** four steps — Investigate, Clarify, Create, Learn — on a
  horizontal rail with a gold progress line.
- **Interaction:** the progress line's `scaleX` is driven by the section's own
  scroll progress. The reader's scrolling literally draws the process.
- **Mobile:** stacks to a vertical timeline.

## 7 · The Trust Files (light)

- **Purpose:** convert the signature series from "a blog category" into
  intellectual property.
- **Composition:** 50/50. Cover artwork in a `.plate` with parallax; gold
  `.tag`, 84px title, the series premise, File 001 call-out, two buttons.

## 8 · Insights (warm)

- **Purpose:** demonstrate a publishing *system* rather than a content pile —
  the section's own headline makes the claim.
- **Composition:** the `.editorial` component — one large featured story
  (image + body) beside a stacked list of three linked items, all on a shared
  hairline grid.
- **Interaction:** list rows warm to a 7% gold tint on hover. Whole rows are
  the link target, not just the text.

## 9 · Founder (dark)

- **Purpose:** the human close. Consultancy is bought from a person.
- **Composition:** 0.8/1.2. Portrait at 4:5 with an offset gold frame drawn
  via `outline-offset` — reliable at any stacking context, and it costs no
  layout. Right: bio, an italic signature quote, two ghost buttons.
- **Why dark:** a portrait on navy with a gold frame reads as a commissioned
  photograph rather than a headshot upload.

## 10 · Engagement models (light)

- **Purpose:** remove the last friction before booking — *what does working
  together actually look like, and am I too small for this?*
- **Composition:** three cards labelled by commitment level rather than number
  (Diagnostic / Project / Ongoing): Clarity Sprint, Strategy & Build,
  Embedded Partner. No prices — the goal is a conversation, and a price would
  invite self-disqualification.

## 11 · CTA band (gold)

- **Purpose:** the single conversion moment, unmissable.
- **Composition:** full-bleed brand gold. Headline and copy left, navy button
  right. A giant cropped outline circle adds depth with no asset.

---

## Secondary pages

Every non-homepage route opens with `.page-hero`: a compact dark opener
carrying breadcrumbs, eyebrow, title, and lede.

This is partly composition and partly a **hard technical constraint** — the
header is fixed and transparent at scroll-top, so a light first section would
drop the champagne nav type below AA contrast. Dark openers are not optional.

| Page | Shape |
| --- | --- |
| Insights hub | page hero → category cards → featured editorial → CTA |
| Articles / Resources / Research Notes / Podcast | page hero → item cards → CTA |
| The Trust Files | page hero → series premise → File 001 feature → what's coming → CTA |
| File 001 / Clarity Before Content | page hero → `.article-layout` (prose + sticky meta rail) → CTA |
| Media Kit | page hero → facts strip → founder bio → expertise → topics → collaboration chips → downloadable assets → contact |
| 404 | page hero + escape routes, header and footer intact |

Long-form articles use `.prose`: a 68ch measure, gold list markers, a
gold-ruled `blockquote`, and underlines at 1px with 0.22em offset. The
`.article-aside` rail sticks at 7.5rem — clear of the fixed header — and goes
static on mobile.

---

## Responsive strategy

Three breakpoints, each with a reason:

| Width | What changes |
| --- | --- |
| **≤1080px** | Process rail 4→2 columns; footer 3→2 columns. |
| **≤960px** | The structural break. Header CTA hides, hamburger appears, overlay nav activates. All two-column grids collapse. The 3D object moves behind the type, dims, and gains a scrim. Section rhythm tightens from 12.5rem to 7rem. |
| **≤620px** | Everything single-column. Buttons go full-width. Rail becomes a timeline. |

Mobile is not a shrunken desktop. Three things are genuinely re-authored: the
navigation becomes a designed full-screen moment, the 3D object changes role
from co-star to backdrop, and the hero's credential rail reflows from a 4-up
strip to a 2-up wrap.

`min-height: min(100svh, 62rem)` on the hero — `svh`, so mobile browser
chrome collapsing doesn't cause a jump, and capped so it never becomes absurd
on a tall desktop monitor.

---

## Accessibility as a design constraint

Not a retrofit — several visual decisions were *made* by it:

- The two-gold system exists because brand gold fails AA on white.
- The nav accent is champagne rather than gold because gold measured 4.21:1
  against the frosted header.
- Every page opens dark so the transparent header keeps its contrast.
- Skip link, single `h1`, no skipped heading levels, no duplicate ids.
- Focus rings: 2px, 3px offset, `--gold-ink` on light and champagne on dark.
  Never removed.
- `prefers-reduced-motion` kills the grain, cursor, curtain, marquee, parallax
  and hero loop — and resolves every reveal to its *final* state, so nothing
  is left invisible.
- Hidden reveal start-states are scoped to `html.js`, so a JavaScript failure
  yields a complete static page rather than a blank one.

Verified in headless Chromium at 1440 / 834 / 390px: zero AA contrast
failures, zero horizontal overflow, correct heading order.
