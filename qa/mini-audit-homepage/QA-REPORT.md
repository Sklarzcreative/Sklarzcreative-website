# Mini Audit homepage QA

**Date:** 9 September 2026

**Production source:** `main` at `a285571`

**Feature source:** PR #21, merged 4 September 2026

**Page checked:** https://sklarzcreative.com/

**Canonical offer page:** https://sklarzcreative.com/audit/

## Outcome

The already-live Mini Audit homepage section passes the factual, semantic, contrast, keyboard-focus, link, reduced-motion, no-JavaScript, and changed-scope checks performed here. The section uses existing components and required no Mini Audit-specific CSS.

One evidence limitation remains: the available cloud QA browser had a fixed effective viewport of 1363 × 936 CSS pixels and did not permit viewport resizing. A clean desktop screenshot is included. Mobile and tablet behavior was checked against the responsive CSS rules, but 375 px and 768 px screenshots could not be captured in this environment and are not represented as completed.

## Factual reconciliation

| Fact | Homepage | `audit/index.html` | Result |
| --- | --- | --- | --- |
| Standard price | $350, fixed fee, paid upfront | $350, fixed fee, paid upfront | Pass |
| Turnaround | 3–5 business days | 3–5 business days | Pass |
| Scope | Homepage or main landing page plus one primary social profile | Homepage or main landing page plus one primary social profile | Pass |
| Local rate | Five introductory Central Massachusetts founder spots at $199, subject to availability | Five introductory qualified Central Massachusetts founder spots at $199, with limited availability | Pass |

## QA checklist

| Check | Result | Evidence and notes |
| --- | --- | --- |
| Desktop visual, 1363 × 936 | Pass | `mini-audit-homepage-after-1363x936-clean.jpg`. Section reads as part of the existing editorial flow, cards align, CTA and supporting local-rate text are readable. |
| Mobile visual, approximately 375 px | Not captured | Browser viewport resizing was unavailable. Static CSS review confirms the auto-fit card grid resolves to one column and `.btn-row` becomes a full-width vertical stack below 620 px. |
| Tablet visual, 768 px | Not captured | Browser viewport resizing was unavailable. Static CSS review confirms the generic auto-fit card grid and existing 960 px responsive system govern the section; no section-specific override exists. |
| Before screenshot | Not captured | The feature had already been merged and deployed before this QA. The exact before/after markup remains preserved in PR #21. |
| Keyboard focus | Pass | The section contains one focusable element. Keyboard focus landed on “Explore the Mini Audit”; computed focus outline was 2 px solid `#7A5B10` with a 3 px offset. |
| Focus order | Pass | The sole section CTA follows the offer cards and precedes the supporting $199 text in document order. |
| Heading order | Pass | The section heading is an `h2` with `id="mini-audit-heading"`; the section references it with `aria-labelledby`. Card labels use `h3`. |
| Contrast | Pass | Values below meet WCAG AA for their intended sizes. |
| Reduced motion | Pass | No new animation was added. The existing `prefers-reduced-motion: reduce` rule forces all `[data-reveal]` content visible and removes transforms. |
| No JavaScript | Pass by source inspection | Hidden reveal states are scoped to `.js [data-reveal]`. With JavaScript off, the `.js` class is never added, so the section remains visible. The CTA is a normal anchor. |
| Link | Pass | Keyboard activation resolved to `https://sklarzcreative.com/audit/`, whose H1 is “Trust & Discoverability Mini Audit.” |
| CTA count | Pass | Exactly one link exists inside the section: “Explore the Mini Audit” to `/audit/`. No mailto or Calendly CTA appears inside it. |
| Responsive rules | Pass by source inspection | The section reuses `.shell`, `.section-head`, `.card-grid`, `.card`, `.btn-row`, and typography utilities. No `.mini-audit` CSS exists or is required. |
| Console | Pass with environment note | No page-origin warning or error was observed. The cloud browser logged its own extension metadata errors from a `chrome-extension://` URL; these are unrelated to the site. No Mini Audit-specific script or component is introduced. |
| Changed-file scope | Pass | This completion branch changes only sales-support files under `outreach/` and QA evidence under `qa/mini-audit-homepage/`. No production HTML, CSS, scripts, media, `audit/`, `insights/`, `automation/`, or `_original-design/` files are modified. |

## Contrast results

| Element | Foreground | Background | Ratio | Requirement | Result |
| --- | --- | --- | --- | --- | --- |
| Headline and price | `#1A2F4B` | `#FAF8F3` | 12.75:1 | 3:1 large / 4.5:1 normal | Pass |
| Lede and body | `#5A6675` | `#FAF8F3` | 5.51:1 | 4.5:1 | Pass |
| Eyebrow and structural labels | `#7A5B10` | `#FAF8F3` | 5.94:1 | 4.5:1 | Pass |
| CTA text | `#F2F5F9` | `#1A2F4B` | 12.37:1 | 4.5:1 | Pass |

## Acceptance criteria

- Native-feeling and consistent with the existing homepage: pass
- Understandable without reading the full audit page first: pass
- One CTA to `/audit/`: pass
- $199 Central Massachusetts rate remains supporting text: pass
- Existing homepage messaging remains intact: pass
- No unrelated production files changed by this completion branch: pass
- Keyboard, heading, contrast, reduced-motion, no-JavaScript, and link checks completed: pass
- Three requested viewport screenshots: partial, desktop captured; mobile and tablet blocked by the fixed browser viewport
