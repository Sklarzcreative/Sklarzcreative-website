# 06 · Making It Feel $20K+ — the premium audit

> An audit of what made the previous site read as generic, and the exact
> change made in each case. Ranked by impact per unit of effort.
>
> The previous site was **not bad**. It was competent, organised, responsive,
> accessible-ish, and fast. That is precisely the problem: competent is the
> baseline, and the baseline reads as a template. Nothing below is about
> adding more. Almost all of it is about **conviction and restraint**.

---

## The one-sentence diagnosis

> Every individual decision was defensible, and no decision was *committed*.

Type was mid-sized. Colours were the brand's, unmodulated. Spacing was
adequate. Nothing was wrong, and nothing was memorable. Premium comes from
extremes held under control: type much larger, colour much darker, whitespace
much wider, motion much slower, and far fewer elements.

---

## Tier 1 — highest impact

### 1. Display type was too small and too loosely set

**Before:** section titles `clamp(2.2rem, 4.7vw, 4.4rem)` in Montserrat 700 at
`line-height: 1.08`, tracking `−0.055em`. Headings and body were both
sans-serif, so hierarchy came only from size.

**The problem:** a 70px bold sans headline at 1.08 leading is the most common
heading treatment on the web. It has no voice.

**The change:**
- Display moves to **Playfair Display 400** — the serif was already in the
  brand kit, used only for one italic quote.
- Leading tightens to **0.93–1.02**. This is the single biggest change on the
  page. Default-ish leading on large type is the clearest tell of an
  unconsidered site.
- Tracking scales with size: `−0.032em` at hero scale, `−0.022em` at section
  scale.
- Hero ceiling **96px**, with 11px uppercase labels beside it. Extreme scale
  contrast. Timid mid-sized headings are what makes a page look generic.
- `text-wrap: balance` on all headings, `pretty` on paragraphs — no orphans at
  any viewport, no manual `<br>`s.

### 2. Light backgrounds were cold grey

**Before:** `#F7F8FA` — a blue-grey. **After:** `#FAF8F3`, a warm alabaster.

Three hex digits. It costs nothing, and it is the highest
effort-to-payoff change in the entire redesign. Cold grey reads as an
unstyled `<div>`; warm off-white reads as paper.

Same principle on ink: `#27313d` neutral grey → `#14202E` navy-tinted. Body
copy now belongs to the brand instead of sitting on top of it.

### 3. There was no dark, cinematic register

**Before:** the darkest surface was `#102136`, used for a gradient hero and one
section band. Everything else was white or grey. The site had no *depth*.

**After:** a full navy ladder down to `--void: #050B13`, and a section rhythm
that alternates dark and light so the page has a pulse:

```
void → gold → dark → light → warm → dark → light → warm → dark → light → gold → void
```

Two gold interruptions per page, maximum. Gold is the loudest element in the
system, so it is rationed.

### 4. Card grids used gaps and shadows

**Before:** `.cap` cards with `1px solid #E4E8ED` borders and an 18px gap — six
separate boxes floating on grey. Every SaaS template does this.

**After:** a **1px hairline grid**. Cards sit flush with `gap: 1px` over a
hairline-coloured parent, so the whole set reads as one ruled table.
Editorial, not app-like.

### 5. Hover states scaled and lifted

**Before:** `.btn:hover { transform: translateY(-2px) }` on everything, cards
lifting with a growing shadow.

**After, and this is a rule worth internalising:** **cards never scale.**
Scaling a card scales its type, which resamples the glyphs and looks cheap at
any duration. Instead:

- Top hairline wipes across (760ms).
- A faint gold wash rises from the bottom.
- Text lifts 3px — the content moves, the container does not.
- Buttons get a single slow specular **sheen sweep**, which ties them to the
  gold 3D object.

---

## Tier 2 — significant

### 6. The hero was a card collage

**Before:** three absolutely-positioned translucent cards over a navy
gradient, plus two decorative CSS circles. Busy, and it read as "I needed to
fill the right half."

**After:** one object. A raymarched faceted gold monolith with an orbital
ring, drifting dust, and film grain. Type owns the left half, the object owns
the right, and **nothing competes for the object's half** — an intermediate
version put the credential rail there and both elements lost.

### 7. Small gold text failed accessibility *and* looked muddy

Brand gold `#C9A84C` on white measures ~2.4:1. The previous site's own QA had
already flagged it and patched around it with `#806000`, which is a murky
olive.

**After:** the role is split cleanly — `--gold` for large and decorative use
and on dark grounds, `--gold-ink: #7A5B10` for small text on light. The brand
colour stays intact *and* AA passes. Accessibility and craft pointing the same
direction.

### 8. Figures were bare images

**Before:** `<img>` inside a padded navy box, or nothing at all.

**After:** `.plate` — a shadow plus an **offset gold hairline** drawn with
`outline` + `outline-offset`. A frame is what turns a diagram into a figure.

Implementation note worth keeping: the first attempt used an absolutely
positioned pseudo-element at `z-index: -1`, which renders *behind the section
background* in some stacking contexts and vanishes. `outline-offset` draws
outside the box, costs no layout, and cannot be clipped by a stacking context.

### 9. Buttons were generic

**Before:** `border-radius: 4px`, 14px padding, `font: 700 .88rem Montserrat`.

**After:** `border-radius: 2px` (sharper reads more precise), 52px min height,
`letter-spacing: .13em` uppercase at 0.78rem, and the sheen sweep. Small,
compounding refinements.

### 10. Section labels had no system

**Before:** `.eyebrow` at `letter-spacing: .16em`, floating alone.

**After:** `0.24em` tracking at `0.7rem`, and **always preceded by a short gold
rule** drawn as a pseudo-element. One repeated 24px detail across every
section header, which is what signals a system rather than a series of pages.

### 11. Reveals were generic fade-ups

Adding a **6px blur that resolves to sharp** costs nothing and changes the
register completely — it reads as a camera focus pull rather than a CSS
transition. Same duration, same easing, entirely different feel.

---

## Tier 3 — the details that separate good from expensive

| # | Change |
| --- | --- |
| 12 | **Film grain** at 3.2% over the hero, generated from an inline SVG turbulence data URI — zero requests. Above ~4% it reads as noise instead of stock. |
| 13 | **Dither in the shader.** ±1/255 hash noise. Without it, a navy gradient this dark bands visibly on 8-bit displays. |
| 14 | **Navy-tinted shadows** (`rgba(8,17,30,.22)`), never neutral black. Neutral shadows on a warm ground look dirty. |
| 15 | **Tabular numerals** on stacked figures so 01/02/03/04 align optically. |
| 16 | **One italic phrase per screen.** Used twice in a view, it stops being emphasis. |
| 17 | **`::selection`** styled gold-on-navy. Nobody notices it; everybody notices its absence. |
| 18 | **Hamburger as two rules**, not three, so the X morph is exact rather than hiding a middle bar. |
| 19 | **Mobile nav in Playfair at 1.6–2.4rem** on a full-screen 97% navy overlay with a 20px blur. A designed moment, not a utility dropdown. |
| 20 | **Header hides on scroll-down**, returns on scroll-up, with a ±6px threshold so jitter doesn't flicker it. |
| 21 | **Scroll cue** as a travelling gold segment inside a hairline, rather than a bouncing chevron. |
| 22 | **Marquee `//` separators** dimmed to 42%, so the phrases read and the punctuation recedes. |
| 23 | **Portrait grade** `saturate(.92) contrast(1.04)` plus the offset frame — composed into the page, not dropped onto it. |
| 24 | **`scroll-padding-top: 6.5rem`** so in-page anchors don't land under the fixed header. |
| 25 | **Rounded ring on the CTA band**, cropped by the section — depth from geometry, no asset. |

---

## Copy

The previous copy was already the strongest asset. Changes were minimal and
surgical:

- **Hero headline:** "Building Trust. Telling Stories. Growing Brands." → *"Clarity
  is the first act of trust."* The original is three nouns describing a
  service category. The replacement is a claim only this consultancy would
  make. The original line is retained as the footer tagline and in the
  marquee, where a slogan belongs.
- **Pull quote** promoted from a generic aside to the emotional peak of the
  page, on navy, at 50px: *"The strongest brands do not win attention. They
  earn confidence."*
- **Added the engagement-models block.** The most common unstated reason a
  qualified visitor doesn't book is not knowing what the engagement is or
  fearing they're too small for it. Three named entry points, no prices.

### The integrity decision

A conversion-optimised template puts a stats band after the hero: *"200+
projects · 15 years · 98% retention."* Every one of those numbers would have
been fabricated.

Instead that slot holds the **four real dimensions of the firm's own trust
framework** — Clarity, Consistency, Credibility, Connection, numbered 01–04.
Identical visual rhythm to a stats band. Zero fiction. And it doubles as a
route into File 001, so it feeds the content system too.

For a consultancy whose entire product is trustworthiness, one invented number
would be a strategic error, not merely an ethical one.

---

## What was deliberately *not* added

Restraint is the deliverable. Each of these would have made the site feel
cheaper:

- A testimonial slider (there are no testimonials to quote).
- A client logo wall (there is no permission to display client marks).
- An animated statistics counter (there are no verified statistics).
- A chat widget.
- A newsletter modal.
- A carousel of any kind.
- A second accent colour.
- Icons on every card. *(Six generic line icons make six cards look like a
  feature list. Numerals make them look like a table of contents.)*
- More sections. The homepage has eleven blocks and each closes a specific
  doubt. A twelfth would dilute, not add.
