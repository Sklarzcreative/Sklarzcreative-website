# 04 · Motion Language

> The unified animation system. Implementation:
> [`/assets/js/motion.js`](../assets/js/motion.js) and section 05 of
> [`/assets/css/sklarz.css`](../assets/css/sklarz.css).

---

## The governing principle

> **Motion should feel like a camera, not like a user interface.**

A camera moves slowly, with weight, and only when there is a reason to look
somewhere else. A UI animation draws attention to itself. This site does the
first thing.

Three rules that follow from that, and they are non-negotiable:

1. **Motion is a reward for scrolling, never a tax on it.** Nothing blocks
   reading, nothing must finish before content is usable.
2. **Motion is strictly additive.** Remove the JavaScript and the site is
   complete and static. It is never load-bearing.
3. **One thing moves at a time.** If two elements animate in the same 200ms
   window, they are the same gesture or one of them is wrong.

## Tokens

```css
--ease-out:  cubic-bezier(.16, 1, .3, 1);    /* expo out — reveals */
--ease-io:   cubic-bezier(.65, 0, .35, 1);   /* in-out — wipes, transforms */
--ease-soft: cubic-bezier(.25, .46, .45, .94); /* colour, opacity */

--t-micro:  180ms;   /* colour shifts, hover tints */
--t-base:   420ms;   /* hover transforms, header state, nav */
--t-reveal: 760ms;   /* scroll reveals */
--t-cinema: 1200ms;  /* headline lines, hero fade-in */
```

Four durations, three curves. **Every animation on the site uses one of
these.** A one-off duration is a bug.

**There is no bounce, no elastic, no overshoot, and no spin anywhere in the
system.** Expo-out decelerates hard into its destination, which reads as
weight. An overshoot reads as a toy.

## 1 · Page-load choreography

A fixed order, ~1.1s end to end:

| Step | Element | Delay |
| --- | --- | --- |
| 0 | Header + hero canvas fade (1200ms) | 0 |
| 1 | Eyebrow | 260ms |
| 2–4 | Headline lines 1, 2, 3 | 120 / 215 / 310ms |
| 5 | Lede | 650ms |
| 6 | Buttons | 780ms |
| 7 | Credential rail | 1040ms |

Gated on `document.fonts.ready` **with a 900ms timeout**, so display type never
reflows mid-reveal but a slow font CDN can never hold the page hostage.

### Headline line reveal

Each line sits in an `overflow: hidden` mask and slides up from
`translate3d(0, 110%, 0)` over 1200ms, staggered 95ms.

Two implementation decisions worth keeping:

- **Lines are authored explicitly** in the markup as `.line > .line-i` pairs.
  No JavaScript measures or splits the text. Any measuring splitter eventually
  mis-splits at some viewport width and clips the result.
- **The clip is released after playing** (`.line.is-done { overflow: visible }`).
  Once the animation is done the mask has no job, and leaving it in place means
  a later reflow at a different width could crop the headline.

## 2 · Scroll reveals

The default gesture for every block on the site:

```css
opacity: 0 → 1
transform: translate3d(0, 26px, 0) → none
filter: blur(6px) → blur(0)
760ms, --ease-out
```

**The blur is the detail that matters.** Opacity-plus-translate is the most
common effect on the web and reads as generic. Adding a 6px blur that resolves
to sharp makes the element read as a **focus pull** — a camera finding its
subject. Same cost, completely different register.

- Fires via a **single** `IntersectionObserver` at `threshold: 0.06`,
  `rootMargin: 0px 0px -12% 0px` — so things reveal slightly *before* they'd
  otherwise be centred, which feels responsive rather than late.
- **Each element unobserves itself on first entry.** Reveals happen once.
  Re-animating on scroll-back is a hallmark of an over-animated site.
- Grid children stagger 90ms via `data-reveal-group` / `data-reveal-index`.
- Variants: `data-reveal="fade"` (no travel), `data-reveal="right"`
  (horizontal, for figures).

## 3 · Parallax

One `requestAnimationFrame` loop for the whole page, with **cached geometry**.

```js
const p = (y + vh / 2 - mid) / (vh + height);
const shift = clamp(p * speed * vh, -90, 90);
el.style.transform = `translate3d(0, ${shift}px, 0)`;
```

- Speeds are 0.04–0.06. Subtle enough that most visitors will not consciously
  notice it, which is the intent.
- **Travel is hard-clamped to ±90px** so an element can never visually detach
  from its layout position — the most common parallax failure.
- Geometry is measured on load, on resize, and once more after `window.load`
  (late images change layout). **Never per frame.** A scroll handler that
  calls `getBoundingClientRect()` on every frame is a jank generator.
- Scroll listeners are `{ passive: true }` and only ever set a flag; all work
  happens inside the single rAF.

## 4 · The process rail

The one piece of scroll-driven motion that carries meaning rather than
atmosphere: a gold line whose `scaleX` tracks the section's own scroll
progress, 0 → 1.

The reader's scrolling literally draws the process from Investigate to Learn.
It is the only progress indicator on the site, and it earns its place because
the content it marks is itself a sequence.

## 5 · Hover and micro-interactions

| Element | Behaviour |
| --- | --- |
| **Primary button** | A single slow specular sheen sweeps across (900ms, `--ease-io`) plus a 2px lift. The sheen is the "metal" signature that ties buttons to the 3D object. |
| **Nav link** | Gold underline wipes in from the left, `scaleX(0→1)`, origin left. |
| **Arrow link** | Same underline wipe, plus the chevron slides 5px right. |
| **Card** | Top hairline wipes across (760ms), a faint gold wash rises from the bottom, text lifts 3px. **No scale.** |
| **Editorial row** | Background warms to a 7% gold tint. |
| **Chip** | Border goes gold, text goes gold-ink. |
| **Marquee** | Pauses on hover. |

**Cards never scale.** Scaling a card scales its type, which resamples the
glyphs and looks cheap at any duration. The hairline wipe achieves the same
"this is interactive" signal with none of that cost. This is the most
frequently violated rule in premium web design and the easiest to get right.

## 6 · Cursor

A 36px gold ring in `mix-blend-mode: difference`, damped toward the pointer at
0.16 per frame, widening to 60px with a 12% gold wash over anything
interactive.

Gated on `(hover: hover) and (pointer: fine)` **and** motion being allowed. It
accompanies the system cursor rather than replacing it — hiding the real
cursor to show a custom one costs usability for decoration, which is a bad
trade at any level of polish.

Its rAF loop only starts on first real pointer movement, and stops when the
tab hides.

## 7 · Page transitions

A navy curtain rises before an internal navigation (420ms, `--ease-io`) and is
gone on arrival.

The implementation is defensive, because a broken transition breaks the
**site**, not just an animation:

- The whole handler is inside `try/catch`. Any exception falls through to a
  normal browser navigation.
- Bails on: modifier keys, non-left clicks, `target`, `download`, cross-origin,
  same-page hashes, and identical URLs.
- The curtain is `pointer-events: none`, so it can never trap a click.
- `pageshow` with `persisted` clears it, so a back-button restore from cache
  doesn't land on a navy screen.
- Skipped entirely under `prefers-reduced-motion`.

## 8 · Header behaviour

- Transparent over the hero → frosted navy past 40px.
- Hides on scroll-down past 240px, returns on scroll-up, using a ±6px delta
  threshold so small jitters don't flicker it.
- Never hides while the mobile menu is open or near the top of the page.

## 9 · 3D motion

- Object rotation: `uTime * 0.075` on Y with an 0.11 rad nod. **Very slow** —
  roughly 84 seconds per revolution. A visibly spinning object looks like a
  loading state.
- Cursor moves the camera ±0.075 rad, damped at 0.055/frame. The lag is what
  makes it feel like a head movement.
- Scroll dollies the camera back and dims the scene.

## 10 · Reduced motion

`prefers-reduced-motion: reduce` is treated as a real user requirement:

- All durations collapse to 0.001ms.
- Grain, cursor ring, curtain, scroll cue, marquee and parallax are removed.
- The hero draws **one** static frame and starts no loop.
- **Critically:** every reveal resolves to its *final* state with
  `!important`, and line masks release their clip. The failure mode to avoid is
  a reduced-motion user getting an invisible page because the "animate in"
  never ran.

## 11 · Performance budget

| Rule | Why |
| --- | --- |
| Only `transform`, `opacity`, `filter` are animated | The only properties that stay off the layout/paint path |
| One rAF loop for parallax + rail + header | N loops means N chances to stall |
| One IntersectionObserver, self-unobserving | Observers are cheap; hundreds of live callbacks are not |
| `will-change` only on elements that actually animate | Blanket `will-change` costs memory and can *reduce* performance |
| Cached geometry, never per-frame layout reads | Layout thrash is the usual cause of scroll jank |
| Scroll/resize listeners are `passive` and flag-only | Keeps the scroll thread free |

## 12 · What is banned

- ❌ Bounce, elastic, or overshoot easing.
- ❌ Any element that spins continuously.
- ❌ Scale transforms on cards or type.
- ❌ Re-animating an element on scroll-back.
- ❌ Animations that block reading or delay a click.
- ❌ Scroll-jacking, or any hijacked scroll speed.
- ❌ Auto-playing carousels.
- ❌ Counting-up numbers that aren't measurements. *(An earlier build animated
  the trust framework's 01–04 labels from zero. They are labels, not metrics —
  it was motion for its own sake, and it was removed.)*
- ❌ More than two moving things in one viewport.
- ❌ Any duration outside the four tokens.
