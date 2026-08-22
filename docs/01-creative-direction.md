# 01 · Creative Direction — "The Signal"

> The governing idea for sklarzcreative.com. Everything downstream — layout,
> type, motion, 3D, copy — resolves back to this document.

---

## 1. The strategic problem

Sklarz Creative sells **judgement**. Not deliverables, not output volume —
the ability to look at a tangle of complexity and say *this is what matters,
say it this way*. That is an expensive, senior service, and it is bought on
one signal: does this person seem like they know what they're doing?

A website is the first place that gets tested. And the previous site, while
competent and well-organised, said "capable freelancer" rather than "the
person you call when the message has to be right." The content was already
strong. The presentation was under-selling it.

The gap wasn't information. It was **conviction**.

## 2. The governing idea

> **Clarity is the first act of trust.**

Not a tagline — a thesis. It connects the existing brand line ("Building
trust. Telling stories. Growing brands.") to the operating belief already in
the work ("clarity before content"), and it makes a claim only this
consultancy would make.

It also gives the site a job: **the website must itself be the proof.** If
Sklarz Creative sells clarity, a cluttered site is a self-refuting argument.
Every decision below is downstream of that. Restraint is not a style choice
here; it is the product demonstration.

## 3. Mood

**Nocturne.** A dark, quiet, expensive room with one warm light in it.

| It is | It is not |
| --- | --- |
| A cut object on a velvet ground | A hero video of people in a meeting |
| One light source, deliberately placed | Bright, evenly-lit, optimistic SaaS |
| Silence between elements | Density as evidence of value |
| Editorial, printed, considered | Dashboard-ish, tech-ish, template-ish |
| Slow | Energetic |

Reference vocabulary: a Fincher title sequence, Aesop packaging, a Swiss
editorial spread, a jeweller's vitrine, an annual report nobody threw away.

**The single most important instruction:** when in doubt, remove it. The
luxury read comes from what isn't there.

## 4. Colour system

The brand kit is navy and gold. That constraint is absolute — **no new hue is
introduced anywhere in this system.** What is added is *range*: dark steps for
cinematic depth, warm steps so light surfaces don't read as cold default grey.

### Navy ladder

| Token | Hex | Role |
| --- | --- | --- |
| `--void` | `#050B13` | The cinematic ground. Hero, footer. Near-black, still navy. |
| `--abyss` | `#08111E` | Gradient partner to void. |
| `--deep` | `#102136` | Brand deep navy. Dark sections, cards on dark. |
| `--navy` | `#1A2F4B` | **Brand primary.** Headings on light, navy buttons. |
| `--navy-lift` | `#24405F` | Raised surfaces on dark. |

### Gold ladder

| Token | Hex | Role |
| --- | --- | --- |
| `--gold` | `#C9A84C` | **Brand accent.** Buttons, rules, 3D material, marquee. |
| `--champagne` | `#E1CA83` | Gold for text on dark. Rim light. Nav accent. |
| `--bone` | `#F1E7CE` | Large display type on dark. Pull quotes. |
| `--gold-ink` | `#7A5B10` | Gold for *small text on light*. Accessibility-driven. |

### Light and ink

| Token | Hex | Role |
| --- | --- | --- |
| `--alabaster` | `#FAF8F3` | Warm off-white. The workhorse light ground. |
| `--paper` | `#FFFFFF` | True white, for contrast against alabaster. |
| `--ink` | `#14202E` | Body text. Navy-tinted, never pure black. |
| `--ink-muted` | `#5A6675` | Secondary copy. |
| `--ink-faint` | `#666F7D` | Labels and meta. |

### Three colour decisions that do most of the work

1. **Warm off-white instead of cool grey.** The previous site used `#F7F8FA`,
   a blue-grey. Moving to `#FAF8F3` costs nothing and instantly reads as
   paper rather than as an unstyled `<div>`. This is the highest
   effort-to-payoff change in the entire system.
2. **Navy-tinted ink, never `#000`.** Pure black on white is a browser
   default. `#14202E` reads as considered, and it ties body copy to the brand.
3. **Two golds, chosen by ground.** Brand gold `#C9A84C` on white measures
   ~2.4:1 — unusable for small text, and the previous site's own QA had already
   flagged it. Rather than compromise the brand colour, the system splits the
   role: `--gold` for large/decorative use and on dark grounds, `--gold-ink`
   for small text on light. The brand stays intact *and* the site passes AA.

### Ground rhythm

Sections alternate so no two identical grounds ever touch, and so every piece
of artwork lands on a contrasting field:

```
hero (void) → marquee (gold) → dark → light → warm → dark
→ light → warm → dark → light → CTA (gold) → footer (void)
```

The gold bands are deliberate interruptions — two per page, maximum. Gold is
the loudest thing in the system, so it is rationed.

## 5. Typography

**No new typefaces.** The kit already contains three, and they were being used
for two jobs. Giving each a distinct, disciplined role is what changes the
register.

| Face | Role | Treatment |
| --- | --- | --- |
| **Playfair Display** | Display voice — h1/h2, pull quotes, stat figures | Weight 400. Tracking −0.02 to −0.035em. Leading 0.93–1.02. Italic reserved as the accent voice. |
| **Montserrat** | Structural voice — logotype, eyebrows, nav, buttons, numerals | 600/700/800. Uppercase labels at 0.24em tracking, 0.7rem. |
| **Inter** | Reading voice — body, lede, meta | 400/500. Line-height 1.75, measure capped at 64–68ch. |

### What makes it read as editorial rather than as a template

- **Tight display leading.** `line-height: 0.95` on the hero, `0.96–1.02` on
  section heads. Default-ish 1.2 leading on a 96px headline is the single
  clearest tell of an unconsidered site.
- **Negative tracking that scales with size.** Large type needs less letter
  spacing, not the same amount.
- **Enormous scale contrast.** 96px headline against 11px uppercase labels.
  Timid mid-sized headings are what makes a page feel generic.
- **`text-wrap: balance`** on every heading, `pretty` on paragraphs — no
  orphaned single words, at any viewport, without manual `<br>`s.
- **One italic phrase per screen.** "*of trust.*", "*earn confidence*". Used
  more than once per view, it stops being emphasis.
- **A gold rule before every eyebrow.** One repeated 24px detail that ties
  every section header together and signals a system rather than a page.

## 6. Imagery and 3D

### Photography

There is exactly one photograph on the site: the founder portrait. That is a
deliberate scarcity decision — a single well-treated image reads as art
direction, while a page of stock photography reads as filler. It gets a
duotone-ish grade (`saturate(.92) contrast(1.04)`) and an offset gold frame so
it is composed into the page rather than dropped onto it.

**No stock photography. Ever.** No people-in-a-meeting, no laptop-on-a-desk,
no abstract gradient blobs.

### The 3D object

One object, on one page: a faceted gold monolith with a single orbital ring,
turning slowly in a navy void. Full spec in
[`03-cinematic-hero.md`](./03-cinematic-hero.md).

Material direction: **polished gold, not chrome, not plastic.** Fourteen or so
facets so a single key light breaks into separate highlights. Anisotropic
brushed streaks along the object axis. Warm bronze shadows, not grey or green
ones. One warm key, one cool navy fill, a champagne rim.

Lighting direction: **one light, plus the room.** Key from upper-front-right,
a cool bounce from lower-left, a rim from behind. Nothing else.

### Graphics

The four existing editorial SVGs are kept and reused. They are already
on-brand, tiny (1–3 KB), and infinitely sharp. Each is now placed on a
contrasting ground and wrapped in `.plate`, which supplies an offset gold
hairline — the frame is what turns a diagram into a figure.

## 7. Motion language

Full spec in [`04-motion-language.md`](./04-motion-language.md). The direction
in one line: **motion should feel like a camera, not like a UI.**

- Slow. Cinematic reveals run 760–1200ms, not 200ms.
- Expo-out easing (`cubic-bezier(.16, 1, .3, 1)`). Never a bounce, never
  an elastic overshoot, never a spin.
- Reveals include a **blur-to-sharp** pass, so entering elements read as a
  focus pull rather than a generic fade-up.
- Parallax travel is clamped to ±90px. Nothing ever detaches from its layout.
- Every animation is decorative by construction. Remove the JavaScript and the
  site is complete and static, never blank.

## 8. Copy voice

Declarative, specific, unhedged. Short sentences. No exclamation marks, no
"we're passionate about", no "unlock", "elevate", "seamless", "cutting-edge",
"solutions", or "let's chat".

The strongest existing copy is already in this register — *"Trust is not a
slogan. It is the pattern people recognise across what a brand says, shows,
and repeatedly does."* That sentence sets the standard for everything else.

**Integrity constraint, and it is a hard one:** the site asserts nothing that
isn't true. There are no invented client logos, no fabricated metrics, no
"200+ projects delivered", no fake testimonials. Where a conversion-focused
template would put a stats band, this site puts the **four real dimensions of
the trust framework** — same visual rhythm, zero fiction. For a consultancy
whose entire product is trustworthiness, a single invented number would be a
strategic error, not just an ethical one.

## 9. Conversion architecture

One primary action — **book a discovery call** — and it is never more than one
screen away:

1. Fixed header CTA, persistent on every page.
2. Hero primary button.
3. Full-width gold CTA band before the footer on every page.
4. Footer link.

Secondary paths (Insights, The Trust Files, Media Kit) exist for visitors who
need to build confidence before booking. The Insights system *is* the proof
layer — for a trust-led practice, published thinking does the work that a
client logo wall does elsewhere.

The "Engagement models" block (Clarity Sprint / Strategy & Build / Embedded
Partner) exists to answer the question that silently blocks a booking: *what
would this even look like, and am I too small for it?*

## 10. What would break this

Guardrails for future work:

- ❌ A second accent colour. Navy and gold only.
- ❌ A fourth typeface.
- ❌ Stock photography.
- ❌ A carousel, an accordion wall, or a testimonial slider.
- ❌ Invented metrics, logos, or testimonials.
- ❌ Any animation that bounces, spins, or lasts under 200ms and draws attention.
- ❌ Two gold bands within one screen of each other.
- ❌ Reducing whitespace to "fit more above the fold".
- ❌ Small gold text on a light ground (use `--gold-ink`).
- ❌ A page that opens on a light section — the fixed header needs a dark
  ground for its own contrast.
