# 08 · Printed Output

> The Trust-First Content Scorecard is designed to be filled in, filed, or
> handed to a client. This is how it behaves on paper.
>
> Implementation: `assets/css/sklarz.css` §16b (the instrument) and §17b (the
> stationery), plus the `.print-masthead` / `.print-colophon` markup in
> `insights/resources/trust-first-content-scorecard/index.html`.
>
> Lead capture used to be documented here. It now lives in
> [09 · Lead Capture](./09-lead-capture.md).

---

## Behaviour by condition

| Condition | What the visitor gets |
| --- | --- |
| Normal | The full diagnostic with a live total, category subtotals, result band and named weakest signal. |
| **JavaScript off** | All twenty statements as real `<fieldset>`s with working radios, the four bands printed on the page, and a `<noscript>` note explaining that only the running total is missing. |
| Print / Save as PDF | Navigation, footer, CTA band and the print button drop. Statements, subtotals and the result print black, with the chosen score inked solid. The sheet carries its own letterhead and colophon. |

**The statements are authored in HTML, not generated in JavaScript.** That is
what makes the middle row true. An earlier implementation built all twenty from
a JS array, so a scripting failure produced an empty container.

### The printed sheet is a document, not a screenshot

A completed scorecard gets filed, forwarded, or handed to a client. It arrives
with no header, no navigation and no address bar, so it has to say who produced
it and where it came from on its own.

Two print-only components in `sklarz.css` §17b do that:

| Component | What it puts on paper |
| --- | --- |
| `.print-masthead` | Letterhead: the wordmark, the practice line, and a navy rule. First thing on page one. |
| `.print-colophon` | A navy rule, then the signature block — *Cassandra Sklarz*, Founder & Strategic Marketing Consultant — with the document title, its URL, the discovery-call link and the copyright line opposite. `break-inside: avoid`, because a signature split across a page break is worse than a short last page. |

Three decisions in there are print decisions rather than screen ones:

1. **Structure is drawn with borders and type, never backgrounds.** Browsers
   drop background colours when printing but honour border and text colour.
2. **The wordmark's gold half uses `--gold-ink`, not `--gold`.** Brand gold sits
   around 65% luminance and turns to pale grey on a monochrome printer.
   `--gold-ink` is the token that exists for exactly this problem.
3. **Site-relative links print their full host.** `a[href^="/"]::after`
   prepends `sklarzcreative.com`, because `(/insights/…)` on paper has no
   address bar to resolve against. Absolute hrefs already carry their host and
   are left alone.

The signature is **typographic** — the name set in italic Playfair, which is
the signature voice the site already uses in the founder section. It is not a
facsimile of a handwritten signature, and one should not be invented. If a real
signature mark is wanted, supply it as a transparent PNG or SVG and it can
replace the `<b>` in `.print-sign`.

The vertical rhythm also collapses in print: `--space-section` drops from up to
12.5rem to 2.25rem and `.page-hero` loses the padding that exists to clear the
fixed header. On screen that generosity is the design; on paper it was blank
sheets. It saves a page on the scorecard and costs nothing elsewhere.

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

## Reusable components

All in `assets/css/sklarz.css`. There is no page-specific `<style>` block
anywhere on the page.

| Component | What it is |
| --- | --- |
| `.form-grid` / `.form-wide` | Auto-fitting form row grid; `.form-wide` spans it. |
| `.field` / `.field-msg` | A labelled control and its error message. |
| `.field.is-invalid` | Invalid state. **The palette has no red**, and an error signalled by colour alone fails AA regardless — so the border doubles in weight via an inset shadow (no layout shift) and the *identification* is the message text. |
| `.consent` | Checkbox-and-explanation row. Uses `accent-color: var(--gold)`. Excluded from the uppercase `.field > label` treatment, because it carries a sentence rather than a name. |
| `.form-hp` | Spam-trap honeypot, off-screen rather than `display:none`. |
| `.form-note` | Small print under a control. |
| `.notice` | A short standing message with a gold left rule. Not a toast. |
| `.score-low` | The named weakest signal. `:empty` collapses it. |
| `.print-lean` | Body opt-in: drops the footer and the CTA band when printing. |
| `.print-masthead` / `.print-colophon` | Print stationery — see above. |
