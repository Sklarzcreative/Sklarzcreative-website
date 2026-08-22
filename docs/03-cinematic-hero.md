# 03 · The Cinematic Hero — "The Signal Prism"

> Complete specification of the homepage hero. Implementation:
> [`/assets/js/hero.js`](../assets/js/hero.js).

---

## 1. The concept

**One object. One light. One idea.**

A faceted gold monolith turns slowly in a navy void, wrapped by a single thin
orbital ring. Light rakes across its facets. Fine dust drifts through the beam.

It reads as something **cut** — precise, singular, deliberately made. Which is
the argument the page is making in words at the same moment: *clarity is the
first act of trust.* Clarity is what you get when someone removes everything
that isn't the point. The object is that sentence in a material.

The ring supplies the second half of the trust idea: a single element that
keeps returning on the same path. **Consistency, orbiting clarity.**

### Why not the obvious options

| Rejected | Why |
| --- | --- |
| Floating particle field | Every AI-generated agency site in 2024–26 has one. |
| Rotating abstract blob / gradient sphere | Says nothing. Reads as a shader demo. |
| Morphing typography | Fights the headline for the same job. |
| Product mockups on floating devices | She sells judgement, not screens. |
| Literal prism splitting a rainbow | Introduces every hue in the spectrum — the exact opposite of a two-colour brand kit. |

The monolith wins because it is **specific, ownable, and on-palette by
construction** — a gold object needs no colour that isn't already the brand.

## 2. Why no 3D library

Built as a raymarched signed-distance-field scene in a **single fragment
shader**, with no Three.js, no Babylon, no loader.

| | Three.js route | This route |
| --- | --- | --- |
| Transfer | ~600 KB+ | **~11 KB** of `hero.js`, no dependency |
| Geometry | Load or generate a mesh | An SDF: exact, resolution-independent, no file |
| Material | Fight a `MeshPhysicalMaterial` preset toward the brand gold | Author the BRDF directly against `#C9A84C` |
| Facet count | Baked into the mesh | One line of code |
| Failure mode | Library must parse and boot before anything renders | Compile-or-bail in a few ms |

For a hero that needs **exactly one object**, a library is all cost and no
benefit. And hand-authoring the material is the only way to get anisotropic
brushed gold that matches the swatch rather than a generic chrome preset.

## 3. Geometry

```glsl
vec3 s = q;  s.y *= 0.54;
float shard = sdOctahedron(s, 1.0) * 0.54;               // tapered silhouette
shard = max(shard, (abs(q.x) + abs(q.z)) * 0.7071 - 0.96); // 45° corner cuts
shard = max(shard, abs(q.x) - 0.92);                      // side planes
shard = max(shard, abs(q.z) - 0.92);
shard = max(shard, abs(q.y) - 1.46);                      // flat caps
```

An octahedron stretched on Y, then cut by four 45° vertical planes into an
eight-sided girdle, then capped flat top and bottom. **Roughly fourteen
faces.**

The facet count is the whole point. The first version was a plain octahedron —
eight faces, of which two dominated at any camera angle, and it rendered as a
flat diamond sticker. Cutting the corners breaks one key light into *separate*
highlights, which is what reads as a cut gem rather than a shape.

The `* 0.54` on the distance is a correctness detail: after a non-uniform
squash the SDF is no longer a true distance field, so it is scaled by the
smallest axis factor to stay a safe **underestimate**. Marching slightly
slower is the price of never punching through a surface.

The ring is `sdTorus(r, vec2(1.34, 0.017))`, tilted 1.24 rad off the monolith
axis and counter-rotating at 1.6× the object's rate.

## 4. Material — polished gold

The single most important lesson from building this:

> **Metals have almost no diffuse albedo. Nearly everything you see on gold is
> reflected environment.**

An intermediate version added a Lambert key term (`GOLD * CHAMP * kd * 1.25`).
Every facet immediately lit to a similar value and the gem read as **matte
plastic** — pale, flat, butter-coloured. Deleting that one term and letting
reflection carry the form is what turned it into metal.

```glsl
float fs = pow(1.0 - max(dot(n, v), 0.0), 5.0);
vec3 F = mix(GOLD, vec3(1.0), fs);          // Schlick-tinted reflection
m  = F * spec * 1.3 * occ;                  // reflected environment
m += GOLD * 0.06 * occ;                     // ambient floor
m += CHAMP * pow(max(dot(n, hv), 0.0), mix(230.0, 24.0, rough)) * 2.1;
m += mix(NAVY, GOLD, 0.5) * fd * 0.26 * occ;  // warm bounce
m += CHAMP * pow(rd2, 3.0) * 0.16;            // rim
m += CHAMP * fres * 0.42;                     // fresnel edge
m += CHAMP * pow(streak, 6.0) * 0.20;         // seam sparkle
```

Three material problems and their fixes, in the order they appeared:

1. **Flat and plastic** → removed the diffuse term; reflection carries form.
2. **Green-black shadows.** Multiplying the gold albedo straight into a navy
   reflection lands on **olive**. Fixed with a Schlick tint that blends toward
   white at grazing angles, plus a small gold-tinted ambient instead of a navy
   one.
3. **Jade overall cast.** With a purely navy environment, gold's shadow side
   still trended teal. Fixed by making the environment's **lower hemisphere
   warm bronze** (`vec3(0.085, 0.056, 0.030)`) — which is physically what
   happens to real gold, since it absorbs blue heavily and bounces warm light
   into its own shadows.

**Anisotropy:** roughness is modulated by value noise sampled along
`atan(n.z, n.x)` and `p.y * 26.0`, so highlights smear vertically the way
turned or brushed metal does. Roughness range 0.11–0.35 drives the specular
exponent between 230 and 24.

The ring is **not** shaded as metal. A filament that thin mostly reflects the
navy sky and rendered grey. It is treated as dim emissive gold
(`GOLD * 0.62 + CHAMP * fres * 0.45`) so it stays on-brand at every angle,
while remaining a supporting line rather than a bright white hoop.

## 5. Lighting

A three-point rig, but the key lives **inside the environment function** so
the metal genuinely mirrors it — that reflection *is* the highlight.

| Light | Direction | Colour | Role |
| --- | --- | --- | --- |
| **Key** | `(0.52, 0.60, −0.60)` | champagne ×3.4, `pow 15` | Defines the form. Broad and warm. |
| **Fill** | `(−0.72, −0.20, 0.36)` | navy↔gold mix ×0.26 | Rescues the darkest facets only. |
| **Rim** | `(−0.30, 0.42, 0.85)` | champagne ×0.16 | Separates silhouette from void. |
| **Bounce** | `(−0.62, −0.34, 0.32)` | gold ×0.34 | Warm floor light. |

Plus **4-tap ambient occlusion** along the normal, which is what gives the
facet seams weight.

The backdrop carries a warm bloom at `uv(0.26, 0.14)` that the monolith
**occludes** — the cheapest possible way to read a light source as being
*behind* an object.

## 6. Camera

- Ray origin at `−(7.6 + scroll·1.9 + (1−intro)·1.1)` on Z; focal 1.52.
- Landscape: object centred at `uv(0.42, 0.10)` — the right half, clear of the
  headline column. Portrait: `uv(0.04, −0.62)`, well below the copy.
- **Cursor moves the camera, not the object** — the ray is rotated ±0.075 rad
  (X) and ±0.055 rad (Y), damped at 0.055/frame. That lag is the whole trick:
  it reads as a head movement rather than as a widget responding to input.
- Scroll dollies back 1.9 units, rotates the object 0.22 rad, dims the scene
  55%, and fades the dust 60%.

## 7. Atmosphere

- **Dust:** three parallax layers of hashed grid points at different scales
  and drift rates. Tuned down twice — the first pass read as a *starfield*,
  which is a different and much cheaper effect. Now `step(0.945, …)` with a
  0.038 radius: sparse, fine, barely there.
- **Film grain:** a CSS layer over the canvas, generated in-browser from an
  SVG `feTurbulence` data URI, so it costs **zero requests**. Opacity 0.032 —
  above about 4% it reads as noise rather than as stock.
- **Vignette:** radial plus a left-side gradient, focusing the eye on the
  headline. Plus an ACES-approximation tonemap, gamma 2.2, and a ±1/255 hash
  **dither** — without which a navy gradient this dark bands visibly on 8-bit
  displays.

## 8. Performance

| Guard | Behaviour |
| --- | --- |
| Render scale | 0.9 of CSS px on desktop, 0.72 on weak hardware |
| DPR cap | 1.6 desktop / 1.25 weak — a retina hero at DPR 3 is 9× the pixels for no visible gain |
| March budget | 82 steps desktop, 46 on weak hardware |
| Weak-hardware test | `hardwareConcurrency <= 4` or `pointer: coarse` |
| Frame watchdog | Averages 70 frames; if mean > 27ms, steps scale to 0.62 → 0.5 → gives up |
| Offscreen | `IntersectionObserver` stops the loop when the hero leaves view |
| Tab hidden | `visibilitychange` stops the loop |
| Context lost | Handled; canvas hides and restores cleanly |

The degradation ladder matters more than peak quality. A hero that stutters is
worse than a hero that is slightly softer, and a **static gradient hero is
still a good hero** — which is why giving up entirely is an acceptable
terminal state.

## 9. Failure and accessibility

Layer order: WebGL canvas → CSS gradient fallback beneath it → vignette →
grain → content.

- **The fallback ships in the HTML.** `.hero-stage` carries a three-layer
  navy/gold gradient, and the canvas fades in over it at `opacity 0 → 1`. The
  hero is never empty, not for a single frame.
- **No WebGL, or a shader compile failure:** the function returns early, the
  canvas never gains `.is-ready`, and the gradient simply stays. No error, no
  layout shift, no blank rectangle.
- **`prefers-reduced-motion`:** draws exactly **one** fully-lit frame and
  starts no loop at all.
- The canvas is inside `aria-hidden="true"` and carries no content — it is
  decoration, and the headline never depends on it.
- Frame zero is painted *before* the canvas is revealed, so there is no flash
  of an unpainted buffer.

## 10. Headline and CTA

```
Clarity is
the first act
of trust.          ← italic, champagne
```

Three lines, authored as explicit `.line > .line-i` pairs. **No JavaScript
measures or splits the text** — a measuring splitter mis-splits at some
viewport width eventually, and clips the result. Each line's clip is released
once it has played, so later reflow can never crop the headline.

The display ceiling is capped at 96px rather than "as large as fits", because
the headline must hold three unbroken lines beside the object *and* survive a
wider fallback serif before Playfair loads.

- **Primary CTA:** "Book a Discovery Call" — solid brand gold, with a single
  slow specular sheen sweep on hover.
- **Secondary:** "See the Approach" — ghost, hairline border, scrolls into the
  argument for visitors who need convincing first.

The pairing is deliberate: one path for the ready, one for the sceptical.
