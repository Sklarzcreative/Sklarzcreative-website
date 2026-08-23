# 08 · Scorecard Capture & Delivery

> How the Trust-First Content Scorecard captures a lead, why access never
> depends on that capture succeeding, and exactly where an email-marketing
> provider connects when one is authenticated.
>
> Implementation: `insights/resources/trust-first-content-scorecard/index.html`
> (form markup + inline capture script) and section 16b of
> `assets/css/sklarz.css` (form components).

---

## 1. The rule the whole design follows

> **The visitor gets the tool. The capture is a courtesy.**

Access to the scorecard does not depend on a form round-trip, a redirect, an
email arriving, an email provider existing, or JavaScript running. Each of
those is a thing that can fail, and every one of them fails on the visitor's
side of the transaction — they would have handed over an address and got
nothing.

So the flow is ordered deliberately:

```
submit → validate locally → open the scorecard → POST the capture in the background
```

The POST is last, it is not awaited, and its failure is reported as
information ("nothing was saved") rather than as an obstacle. The scorecard is
already open by then.

This also means the gate is not a paywall and is not pretended to be one. On a
static site the markup is public; a hard gate would be theatre. What the form
buys is a signal about whether the tool is worth developing, which is the
honest reason it exists and the reason given on the page.

## 2. The three paths through the page

| Path | What happens | Where the lead goes |
| --- | --- | --- |
| **JavaScript on** (the normal case) | Inline `<head>` script decides the gate before first paint. On submit, the form is validated in-page, the scorecard is revealed, and the body is POSTed to Netlify with `fetch`. | Netlify Forms → `trust-first-scorecard` |
| **JavaScript off** | Neither gate rule applies (both are scoped to `html.js`), so the ask *and* the full scorecard render. The form posts natively; Netlify handles it and redirects to the `action`. | Netlify Forms → `trust-first-scorecard` |
| **Returning visitor** | `localStorage['tfcs-access']` opens the scorecard with no second ask. | Nothing — already captured |

The `?access=1` query parameter is the no-JavaScript redirect target and a
shareable direct link. It is not a secret and is not treated as one.

### Failure behaviour

Every branch fails open. The `<head>` script's gate decision is wrapped in
`try/catch` and the `catch` **adds** the open class rather than withholding it:
if the URL or `localStorage` cannot be read, the visitor gets the tool.

With scripting unavailable the twenty statements are still real `<fieldset>`s
with real radio inputs, so the instrument can be completed on screen, scored by
hand against the four bands printed on the page, and printed as a worksheet.
Only the live total is lost, and a `<noscript>` block says exactly that.

**This is why the statements are authored in HTML rather than generated in
JavaScript.** The previous implementation built all twenty from a JS array,
which meant a scripting failure produced an empty container.

## 3. Netlify Forms contract

Form name: **`trust-first-scorecard`**

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `first-name` | text | yes | `autocomplete="given-name"` |
| `email` | email | yes | `autocomplete="email"` |
| `follow-up-opt-in` | checkbox, value `yes` | **no** | Unchecked by default. Present in the payload only when ticked. |
| `resource` | hidden | — | Constant `Trust-First Content Scorecard`, so a second resource later is distinguishable in one form. |
| `form-name` | hidden | — | Required by the scripted POST; ignored on the plain-HTML path. |
| `company-website` | honeypot | — | Declared via `netlify-honeypot`. Off-screen, `aria-hidden`, `tabindex="-1"`. |

Netlify detects forms at **build time** by parsing the deployed HTML, so the
form must stay in the static markup. It must never be moved into a script.

### Verifying detection after deploy

1. Deploy the branch.
2. Netlify → Project → **Forms**. `trust-first-scorecard` should be listed.
   If it is not, the build did not see the form — check that the page was
   included in the publish directory.
3. Submit the form on the deployed URL.
4. Confirm the submission appears under that form with all fields, and that
   `follow-up-opt-in` is present only when the box was ticked.

Until step 4 has actually happened on a deployed build, the capture is
**unverified**. Local testing cannot confirm it: there is no Netlify in front
of a local static server, so the background POST simply fails and the page
reports that it failed — which is itself the behaviour worth testing locally.

## 4. Email provider — the integration point

**Nothing is connected today.** There is no provider account verified, no form
ID, no API key, and no autoresponder. The three-part follow-up series exists as
copy and nothing more. The page does not claim otherwise: the checkbox label
describes what would be sent, and the button reveals the scorecard rather than
promising an email.

### Where it goes

Server-side, in a Netlify Function subscribed to the form event:

```
netlify/functions/submission-created.js
```

Netlify invokes that filename automatically on every successful form
submission. It receives the payload and runs with access to the project's
environment variables.

```js
// netlify/functions/submission-created.js  — TO BE ADDED
export default async (req) => {
  const { payload } = await req.json();
  if (payload.form_name !== 'trust-first-scorecard') return;

  // The consent gate. Anything other than an explicit 'yes' enrols nobody.
  if (payload.data['follow-up-opt-in'] !== 'yes') return;

  await fetch(PROVIDER_SUBSCRIBE_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${process.env.EMAIL_PROVIDER_API_KEY}`,
    },
    body: JSON.stringify({
      email: payload.data.email,
      first_name: payload.data['first-name'],
    }),
  });
};
```

### The four rules that apply to it

1. **The credential comes from `process.env`**, set in Netlify →
   Site configuration → Environment variables. Never from a file in this
   repository — the repository is public.
2. **No provider identifier of any kind goes in front-end code.** Not a form
   ID, not a publishable key, not an account subdomain. A public repo publishes
   whatever the browser can see.
3. **`follow-up-opt-in !== 'yes'` enrols nobody.** The lead is already captured
   in Netlify Forms; enrolling someone who declined is the single outcome this
   checkbox exists to prevent.
4. **This function must never gate access.** It runs after the submission, on
   Netlify's infrastructure, entirely out of the visitor's path. If it throws,
   the visitor is unaffected and has already used the scorecard.

### What must not be done instead

- ❌ Replacing the Netlify form with an embedded provider form. That moves the
  capture off-site, drops the design system, and re-introduces the dependency
  the whole flow was built to avoid.
- ❌ Calling a provider API from the page with a "public" key. Public keys are
  still abusable, and the network tab shows the endpoint to anyone.
- ❌ Making the reveal wait on a provider response.

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
| `.form-hp` | Netlify honeypot. Off-screen rather than `display:none`, because a bot that skips hidden inputs would skip the trap too. |
| `.form-note` | Small print under a control. |
| `.notice` | A short standing message with a gold left rule. Not a toast. |
| `.score-low` | The named weakest signal. `:empty` collapses it. |
| `.print-lean` | Body opt-in: drops the footer and the CTA band when printing. For pages meant to be printed as a document. |

The gate itself is three CSS rules, all scoped to `html.js` so that a scripting
failure hides nothing.
