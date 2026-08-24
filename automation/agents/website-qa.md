# Agent 3 — Website QA

*Contract fields defined in [`_shared-contract.md`](./_shared-contract.md).*

**This agent is real, executable code**, not a specification awaiting an
implementation: [`../qa/`](../qa/). Everything below describes what that code
does and what it is forbidden from doing.

## NAME
`website-qa`

## PURPOSE
Verify that sklarzcreative.com stays technically healthy after every change.
The site is hand-authored HTML with no build step, which is a genuine strength
— and it means nothing catches a broken link, a lost canonical tag, a second
`<h1>`, or a sitemap that has drifted from what is on disk. This harness is
that catch. It replaces a per-release manual pass with a command.

It has no ability to change the website. It reads, measures, and reports.

## INPUTS

| Input | Location | Trust |
| --- | --- | --- |
| Every HTML file in the repository | working tree | authoritative |
| `sitemap.xml`, `robots.txt`, `CNAME` | repository root | authoritative |
| Rendered pages at three viewports | local static server + headless Chromium | derived |
| Live domain responses | `https://sklarzcreative.com` (only in `--live` mode) | authoritative, often unreachable |
| The Scorecard scoring specification | [`../lib/scorecard.mjs`](../lib/scorecard.mjs) | authoritative (test oracle) |

## SOURCE OF TRUTH
The repository working tree. The harness tests **what would deploy**, not what
is currently deployed — a green report on `main` means the next push is safe,
which is the question worth answering before a push. Live-domain facts
(redirects, headers, real 404 status) are checked separately and clearly marked,
because they are properties of GitHub Pages rather than of the code.

## ALLOWED ACTIONS

- `READ` — every file in the working tree
- `READ` — the live domain over HTTP, GET and HEAD only, in `--live` mode
- `DRAFT` — a machine-readable JSON report and a human-readable summary, written
  only under `automation/reports/`

## FORBIDDEN ACTIONS

- Editing, formatting, or "fixing" any site file. **A QA tool that edits is not
  a QA tool.** It must be safe to run on a whim, and a tool that might rewrite
  your work is not.
- Writing anywhere outside `automation/reports/`
- POSTing anything anywhere. In particular it never submits the Scorecard
  capture form, even in `--live` mode: that would put test rows in a real lead
  sheet.
- Committing, pushing, or opening a pull request
- Reporting a check as passed when it was skipped. **Skipped is its own
  state**, and it is reported as `skipped` with a reason.

## What it checks

Run `node automation/qa/run.mjs --help` for the current flag set. The check
groups, and where each lives:

### Static analysis — every HTML file, no browser
`qa/checks/static-html.mjs`

- `<title>` present, non-empty, unique across pages, within a sane length
- `meta description` present, non-empty, unique, within a sane length
- `rel=canonical` present, absolute, `https://sklarzcreative.com`, and matching
  the file's own path
- viewport, charset, `theme-color`, favicon
- Open Graph: `og:type`, `og:url`, `og:title`, `og:description`, `og:image`,
  `og:image:width`, `og:image:height`, `og:image:alt`
- **`og:image` dimensions are read from the actual PNG/JPEG header**, not
  trusted from the markup, and cross-checked against `twitter:card`: a
  `summary_large_image` card pointing at a square image is a real defect that
  every platform then crops differently
- Twitter: `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`
- `og:url` agrees with the canonical
- every `<script type="application/ld+json">` block parses as JSON, has
  `@context`, and every `url`/`@id` inside it is absolute and on the apex
- exactly one `<h1>`
- no skipped heading levels
- no duplicate `id` attributes
- every `<img>` has an `alt` attribute, and declared `width`/`height` match the
  file's real intrinsic dimensions
- every internal link and asset reference resolves to a file on disk
- every `target="_blank"` carries `rel="noopener"`
- `robots.txt` parses, points at the sitemap, and disallows the archive,
  `docs/`, `integrations/` and `automation/`
- `sitemap.xml` parses, every entry resolves to a file on disk, every
  indexable page on disk appears in it, and nothing `noindex` appears in it
- no obviously fabricated `datePublished` — a date in structured data must also
  appear in the page's visible text

### Rendered checks — headless Chromium at 1440 / 834 / 390
`qa/checks/rendered.mjs`

- HTTP status of every route
- console errors, page errors, failed requests
- no horizontal overflow (`scrollWidth > clientWidth + 1`)
- every link and button has a discernible accessible name
- duplicate ids after scripting
- exactly one `h1` after scripting
- all images loaded (`naturalWidth > 0`), with lazy off-screen images correctly
  reported as `not_requested` rather than as failures

### Behavioural checks
`qa/checks/behaviour.mjs`

- **JavaScript disabled**: the page still renders content, nothing is left
  invisible. This is load-bearing rule 4 of the root README, and it is exactly
  the kind of rule that decays silently.
- **`prefers-reduced-motion: reduce`**: no reveal left hidden
- **mobile navigation**: opens, focus enters the panel, Escape closes it and
  returns focus to the toggle
- **keyboard path**: the skip link is the first focusable element and it works
- **Scorecard calculation integrity**: drives the real form in a real browser
  and asserts the page's own arithmetic against
  [`../lib/scorecard.mjs`](../lib/scorecard.mjs) at every band boundary
  (0, 15/16, 23/24, 31/32, 40), plus the weakest-signal and tie cases
- **Scorecard fails open**: with capture configured *and the endpoint made
  unreachable*, access is still granted. This is the single most important
  behavioural assertion in the suite, because it is the one whose failure would
  be invisible until it cost a visitor the tool.

### Live-domain checks — `--live` only, network permitting
`qa/checks/live.mjs`

- HTTP status of every sitemap URL
- a nonexistent path returns a real `404`, not a `200`
- `www.sklarzcreative.com` redirects to the apex
- `http://` upgrades to `https://`
- compression and cache headers present
- `og:image` and `twitter:image` URLs resolve, with the right content type
- outbound destinations respond: Calendly, and each social profile

Every live check reports `skipped` with the reason when the network is
unavailable. **It never reports `pass` for a check it could not perform** —
that failure mode makes a QA tool worse than nothing.

## Severity, and what fails the build

| Severity | Meaning | Exit code effect |
| --- | --- | --- |
| `error` | A real defect. A visitor, a crawler, or a screen reader is affected. | Non-zero exit. Fails CI. |
| `warning` | Worth a human's attention; not a regression on its own. | Exit 0. |
| `info` | Observation, or a deliberate exception. | Exit 0. |
| `skipped` | Could not be evaluated, with a reason. | Exit 0, and counted separately in the summary so a run that skipped half the suite cannot read as clean. |

## OUTPUT SCHEMA

[`../schemas/qa-report.schema.json`](../schemas/qa-report.schema.json).
Written to `automation/reports/qa-report.json`, plus `qa-summary.md` for humans.
Uploaded as a CI artifact by
[`.github/workflows/site-qa.yml`](../../.github/workflows/site-qa.yml).

## FAILURE BEHAVIOUR

| Condition | Behaviour |
| --- | --- |
| Chromium unavailable | Static checks still run and are reported; rendered and behavioural checks are `skipped` with the reason. Exit code reflects the static findings only, and the summary states plainly that the browser suite did not run. |
| Local server cannot bind | Hard failure, non-zero exit, no report claiming anything. |
| Network unavailable in `--live` | Every live check `skipped`. Never `pass`. |
| A single check throws | That check is recorded as `error` with the exception message; the rest of the suite continues. One broken check must not hide fifty working ones. |

## AUDIT LOG REQUIREMENT

The report *is* the audit log. It records: the git SHA, the branch, the
timestamp, the harness version, the exact route list, every check with its
severity and evidence, and a count of skips. A report without a SHA is not
attributable to a state of the code, so the SHA is mandatory.
