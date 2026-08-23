# 08 · Scorecard Capture & Delivery

> Where the Trust-First Content Scorecard stands, why the lead capture is
> switched off, and exactly what has to be true before it can be switched on.
>
> Implementation: `insights/resources/trust-first-content-scorecard/index.html`
> and section 16b of `assets/css/sklarz.css`.

---

## 0. What is actually hosting this site

This matters more than anything else in this document, because it decides
whether a form can work at all.

| | |
| --- | --- |
| **Serving `sklarzcreative.com`** | **GitHub Pages**, deploy-from-branch on `main` |
| Evidence | Pages run #49 succeeded on `main @ e5aa3a6`. The `/insights/resources/trust-first-content-scorecard/` route exists on the live site, and it was introduced in `f51403f` on 22 August. |
| Netlify | A second, inert copy. **Every production deploy since 9 August reads "Skipped — account credit usage exceeded"**, including `e5aa3a6`, `d81042b` and `f51403f`. Netlify has never built any of them. |
| Cost | GitHub Pages is free and unmetered on a public repository. There is no credit ceiling to hit. |

**GitHub Pages serves static files and nothing else.** It cannot process a form
post, run a function, or hold a secret. Any capture has to happen somewhere
other than the host.

## 1. Why the capture is off

Netlify Forms works by parsing the deployed HTML at **build time** and
processing submissions at **Netlify's edge**. Neither of those exists here:
Netlify never builds, and it does not serve the domain. The same markup on
GitHub Pages posts into a static host that returns an error.

So a form on this page today would collect **nothing**, while adding a step in
front of a proof asset. That is the worst of both: no leads, and a slower
route to the thing that demonstrates the thinking.

The Scorecard therefore ships **open**. No gate, no ask, no stored access.

This is not a downgrade of the diagnostic — it is the same twenty statements,
the same scoring, the same result, the same printout. The only thing removed is
the ask in front of it.

## 2. The rule that survives regardless

> **The visitor gets the tool. The capture is a courtesy.**

This was the design rule while the gate existed, and it is the reason its
removal costs nothing. The reveal always happened locally and first; the
capture POST was fired afterwards and never awaited. A dead endpoint was
always going to cost a lead record rather than cost the visitor the tool.

Keep that ordering if the capture is ever restored:

```
open the diagnostic → then attempt the capture → report a failure as information
```

## 3. Restoring the capture

The full working implementation is preserved in **commit `1aa56c8`** — form
markup, validation, honeypot, consent checkbox, reveal logic, and the CSS
components. Restoring it is a paste plus a working endpoint.

The CSS components were deliberately **left in `assets/css/sklarz.css`** §16b:
`.form-grid`, `.field`, `.field-msg`, `.consent`, `.form-hp`, `.form-note`,
`.notice`. They are generic form components, they cost about 1.5 KB gzipped,
and any future contact form wants them. The three gate visibility rules are
retired in place, as a comment, next to them.

### What has to be true first — pick one

**Option A — move the site to Netlify and pay for builds.** Netlify Forms then
works exactly as the preserved code expects: `data-netlify="true"`,
`netlify-honeypot`, hidden `form-name`. Requires resolving the credit ceiling
*and* pointing DNS at Netlify instead of GitHub Pages. This is the heaviest
option and the only one that changes the host.

**Option B — keep GitHub Pages and post to a form provider.** A hosted
endpoint (Formspree, Basin, Getform and similar) accepts a cross-origin POST
from a static page. The endpoint id in such a URL is a **public identifier,
not a secret**, so it is safe in a public repository. Change one line:

```js
// was: fetch(location.pathname, …)
fetch('https://<provider-endpoint>', { … })
```

and drop the three `netlify-*` attributes. **Do not** put an API key, a
private token, or an account secret in this file — the repository is public
and the browser shows the request to anyone.

**Option C — leave it off.** Defensible. The Scorecard's job in the funnel is
proof of thinking, and the site's primary conversion action is *Book a
Discovery Call*, which appears four times on this page already. A gate in
front of a free diagnostic is the kind of friction the redesign brief
explicitly rules out.

### If a nurture sequence is ever wired up

Unchanged from the original plan, and still the correct shape — it just needs
a host that runs functions:

1. The consent checkbox stays **unchecked by default** and stays optional.
2. Enrolment happens **server-side**, never in the page.
3. `follow-up-opt-in !== 'yes'` enrols nobody. The lead is already captured;
   enrolling someone who declined is the one outcome the checkbox exists to
   prevent.
4. The credential comes from an environment variable on the host, never from a
   file in this repository.
5. It must never gate access. If it throws, the visitor is unaffected.

On Netlify that is `netlify/functions/submission-created.js`. On another host
it is whatever the equivalent post-submission hook is. **None of this exists
today, and the site does not claim it does.**

## 4. Failure behaviour, as shipped

| Condition | What the visitor gets |
| --- | --- |
| Normal | The full diagnostic, immediately, with a live total, category subtotals, result band and named weakest signal. |
| **JavaScript off** | All twenty statements as real `<fieldset>`s with working radios, the four bands printed on the page, and a `<noscript>` note explaining that only the running total is missing. The page prints as a worksheet. |
| Print / Save as PDF | Navigation, footer, CTA band and the print button drop. Statements, subtotals and the result print black, with the chosen score inked solid. |

**The statements are authored in HTML, not generated in JavaScript.** That is
what makes the no-JavaScript row above true. An earlier implementation built
all twenty from a JS array, so a scripting failure produced an empty
container.

## 5. Scoring

Unchanged from the original implementation, and re-tested at every boundary:

| Total | Band |
| --- | --- |
| 32–40 | Strong trust system |
| 24–31 | Solid foundation |
| 16–23 | Inconsistent signals |
| 0–15 | Rebuild the basics |

Five categories — Clarity, Consistency, Credibility, Connection, Conversion —
four statements each, scored 0 / 1 / 2, eight points per category, forty total.

Two things were added, neither of which touches the arithmetic:

1. **The weakest signal is named** once all twenty statements are answered.
   Reading it off five subtotals was work the page could do instead. A tie
   across all five is reported as a tie, not as a winner.
2. **An incomplete card claims nothing.** It reports "*n* of 20 answered" and
   withholds both the band and the weakest signal, because a partial total is
   not comparable to a complete one.

## 6. Reusable components this added

All in `assets/css/sklarz.css` §16b. There is no page-specific `<style>` block.

| Component | What it is |
| --- | --- |
| `.form-grid` / `.form-wide` | Auto-fitting form row grid; `.form-wide` spans it. |
| `.field` / `.field-msg` | A labelled control and its error message. |
| `.field.is-invalid` | Invalid state. **The palette has no red**, and an error signalled by colour alone fails AA regardless — so the border doubles in weight via an inset shadow (no layout shift) and the *identification* is the message text. |
| `.consent` | Checkbox-and-explanation row. Uses `accent-color: var(--gold)`. |
| `.form-hp` | Spam-trap honeypot. Off-screen rather than `display:none`, because a bot that skips hidden inputs would skip the trap too. |
| `.form-note` | Small print under a control. |
| `.notice` | A short standing message with a gold left rule. Not a toast. |
| `.score-low` | The named weakest signal. `:empty` collapses it. |
| `.print-lean` | Body opt-in: drops the footer and the CTA band when printing. For pages meant to be printed as a document. |

These are **retained but unused** on the live page — see §3. They are kept
because they are generic form components rather than scorecard-specific ones,
and because retaining them is what makes restoring the capture a paste rather
than a rebuild. `.notice` is used by the `<noscript>` block, so it is live.
