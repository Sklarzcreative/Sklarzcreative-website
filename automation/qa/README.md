# The website QA harness

> Reads. Measures. Reports. **It cannot change the website**, and that is a
> property worth keeping: a QA tool that might rewrite your work is a tool you
> stop running on a whim, and a tool you stop running catches nothing.

Agent specification: [`../agents/website-qa.md`](../agents/website-qa.md)
Output schema: [`../schemas/qa-report.schema.json`](../schemas/qa-report.schema.json)

## Running it

```bash
cd automation
npm ci                       # once. Playwright is the only dependency.
npx playwright install chromium   # once, unless PLAYWRIGHT_BROWSERS_PATH is set

npm test                     # unit tests: consent, UTM, scoring, queue, schemas
npm run qa                   # static + rendered + behaviour
npm run qa:static            # source-level only, no browser
npm run qa:live              # also check the live domain
```

Or directly, from the repository root:

```bash
node automation/qa/run.mjs --help
```

Reports land in `automation/reports/` — `qa-report.json` (machine-readable) and
`qa-summary.md` (for a human). Both are gitignored: a report is a measurement of
a moment, not a source file. A committed example of each lives in
[`../examples/`](../examples/).

## What runs where

| Suite | Needs | Checks |
| --- | --- | --- |
| `static` | nothing | title/description/canonical uniqueness and correctness, Open Graph and Twitter completeness, **og:image dimensions read from the file header**, JSON-LD parsing and unsupported claims, `datePublished` values that do not appear in the visible text, one `<h1>`, heading order, duplicate ids, `alt` attributes, declared image dimensions vs the real file, every internal link and asset resolving on disk, `target="_blank"` + `rel="noopener"`, robots rules, sitemap ↔ disk agreement in both directions |
| `rendered` | Chromium | HTTP status, horizontal overflow at 1440/834/390 **with the widest offending element named**, accessible names on every link and button, duplicate ids in the live DOM, images that failed to load, console errors, page errors, failed requests |
| `behaviour` | Chromium | JavaScript disabled, `prefers-reduced-motion`, redirect stubs, mobile navigation (open → focus → Escape → focus returns), the skip link, **the Scorecard's arithmetic at every band boundary**, **the Scorecard failing open** |
| `live` | network to the apex | a real 404 status, `www` → apex, `http` → `https`, compression and cache headers, the share images fetchable, outbound destinations answering |

## The design rules

### Skipped is its own state

A QA tool that reports a check it could not run as a pass is **worse than no
tool**: it converts an unknown into a false reassurance, and it does it in a
document people trust. So `skipped` is a severity, it is counted separately, and
a run with skips and no failures reports its verdict as **`incomplete`** — never
`pass`.

You will see this immediately in an offline environment: `--live` reports seven
skips with the reason the network could not reach the domain, and the verdict
reads `incomplete`. That is the harness working.

### Exit codes distinguish "the site is broken" from "the tool is broken"

| Code | Meaning |
| --- | --- |
| `0` | No errors. Warnings, info and skips do not fail a build. |
| `1` | At least one `error` finding. The site has a defect. |
| `2` | The harness itself failed — it could not start a server, or it crashed. |

Conflating 1 and 2 wastes the first hour of every debugging session.

### False positives are treated as bugs in the harness

Three specific ones were found and fixed while building this, and each is worth
knowing about because each looked like a real defect:

1. **`display: none` is not a stuck reveal.** The motion system only animates
   `transform`, `opacity` and `filter`, so a reveal that failed to resolve shows
   up as an opacity or a visibility. A `display: none` is deliberate state — a
   print-only paragraph, a result block that is empty until the card is
   finished. Reporting those as failures flags correct code.
2. **The harness's own blocked requests are not the site's console errors.**
   External font requests are aborted so page loads are deterministic; Chromium
   logs each abort as a console error. Reporting that would be the harness
   accusing the site of a failure the harness caused.
3. **A lazy image far outside the viewport may never have been asked to load.**
   That is unknowable, not broken, and it is reported as `info`.

### The typography caveat, stated in every report

Google Fonts requests are aborted, because in a sandboxed environment they do
not fail fast — an egress proxy can hold them open until the navigation timeout,
which turned a 29-second suite into one that had not finished after seven
minutes.

The cost is real and the report states it every run: **rendered measurements are
taken with the fallback type stack, not with Playfair Display.** Anything that
depends on glyph widths — text wrapping, element heights, and therefore overflow
caused by a long word — is measured against the wrong face. An overflow finding
is still a real signal; a *clean* overflow result is **not** proof that the real
typography does not overflow. Confirm typography on the live domain.

### Nothing is ever posted

The fail-open check drives the real capture form, so it needs a configured
endpoint. It uses a non-routable `.invalid` host **and** aborts every request to
it at the network layer. Nothing leaves the machine, and no test row can reach a
real lead sheet.

## The two checks that matter most

Everything else here protects a metric or a page. These two protect the
commercial premise of the site.

### The Scorecard must fail open

> With the capture endpoint configured and unreachable, access to the diagnostic
> must still be granted.

A capture that fails costs Sklarz Creative a lead record. It must never cost the
visitor the tool. This is the rule that is easiest to break by accident — one
`await` in the wrong place does it — and hardest to notice, because it only
manifests when the endpoint is already failing.

The check installs an accessor for `window.TFCS_CAPTURE` rather than assigning
it, because the page's own head script assigns it and would overwrite a plain
injected value. That detail matters: without it the check silently exercised the
shipped-off default and proved nothing.

### The Scorecard's arithmetic must match the specification

The harness drives the real form at every band boundary — 0, 15/16, 23/24,
31/32, 39, 40 — plus the tie and five-way-tie cases, and compares against
[`../lib/scorecard.mjs`](../lib/scorecard.mjs).

That module is a **test oracle, not a second implementation**. If the two
disagree, the page is the truth about what visitors see and the oracle is the
truth about what was intended. Reconcile deliberately; editing the oracle to
match a page that changed by accident converts a caught bug into a silent one.

## Both were mutation-tested

A check that has never failed is a check you have no reason to believe. Each of
these was deliberately broken and the harness confirmed to catch it:

| Mutation | Caught as |
| --- | --- |
| Move `openScorecard()` inside the capture's `.then()` | `behaviour.scorecard-fails-open` |
| Shift a band threshold from 32 to 33 | `behaviour.scorecard-band` |
| Point a canonical at `www` | `static.canonical-origin`, `static.og-url-canonical` |
| Give two pages the same `<title>` | `static.title-duplicate` |
| Point `og:image` at the 1254×1254 logo | `static.og-image-aspect`, `static.og-image-declared` |

All mutations were reverted. If you change a check, break it on purpose once and
confirm it still fails.

## Adding a check

1. Put it in the suite that can answer it honestly — `static/` if the source
   answers it, `rendered/` if it needs layout, `behaviour/` if it asserts a rule,
   `live/` if it is a property of the host.
2. Give it a stable `check` identifier, so a finding can be tracked across runs.
3. Attach `evidence`. A finding without evidence cannot be triaged, and an
   untriageable finding gets ignored, which is how a suite rots.
4. Choose the severity honestly. `error` means a visitor, a crawler or a screen
   reader is affected. If you are unsure, it is a `warning`.
5. If it cannot always run, emit `skipped` **with a reason**. The report builder
   throws on a skip with no reason, on purpose — a skip with no reason is
   indistinguishable from a check nobody wrote.
6. Break it on purpose and confirm it fails.
