# Agent 4 — SEO / Discovery

*Contract fields defined in [`_shared-contract.md`](./_shared-contract.md).*

## NAME
`seo-discovery`

## PURPOSE
Keep the site findable, and keep it honest while doing so. The commercial
argument for restraint here is unusually strong: Sklarz Creative sells
credibility, and the standard SEO playbook — keyword density, thin pages built
for queries, schema asserting things the page does not contain, invented
publication dates — is a credibility *cost* paid for a ranking that may not
arrive. This agent audits structure, not vocabulary.

It recommends. It writes nothing to the site.

## INPUTS

| Input | Location | Trust |
| --- | --- | --- |
| Every HTML file | working tree | authoritative |
| `sitemap.xml`, `robots.txt` | repository root | authoritative |
| The internal link graph | derived from the working tree | derived |
| QA report | `automation/reports/qa-report.json` | derived |
| Search Console data | Google Search Console | authoritative, **not currently connected** |
| Published URLs of distributed content | `MAKE - Publish Queue` | authoritative |

## SOURCE OF TRUTH
The working tree, for anything structural. Search Console, for anything about
how Google actually sees the site — and since it is not connected, every claim
that would require it is reported as `NOT AVAILABLE` rather than inferred from
the HTML.

## ALLOWED ACTIONS

- `READ` — the working tree, the live site, the QA report, the queue
- `DRAFT` — an audit report, prioritised recommendations, a Search Console
  checklist, and proposed internal-link edits **as diffs for review**

## FORBIDDEN ACTIONS

- Editing any HTML, `sitemap.xml`, or `robots.txt`
- **Keyword stuffing**, in any form: repeating a phrase for density, adding a
  keyword to a title that reads worse for it, writing a meta description for a
  crawler rather than a person
- **Fabricating a `datePublished`, `dateModified`, `author`, or `lastmod`.**
  A date is either known or absent. Inventing one is a lie in machine-readable
  form, which is the worst place to tell one.
- Adding structured data the page does not support: no `Review` without a real
  review, no `AggregateRating` without ratings, no `FAQPage` unless the visible
  page is a set of questions and answers, no `Article` on a hub page
- Recommending doorway pages, thin location pages, or content written for a
  query rather than a reader
- Adding analytics or any third-party script. `/privacy/` states there is none,
  and that statement is load-bearing.
- Recommending a `noindex` change without naming what would drop out of the
  index

## What it audits

1. **Sitemap accuracy** — every entry resolves; every indexable page on disk is
   listed; nothing `noindex` is listed; `lastmod` values are plausible against
   git history rather than uniformly today's date.
2. **Canonical integrity** — present, absolute, apex, self-referential, and
   agreeing with `og:url`. The redirect stub at
   `insights/the-trust-files/trust-is-not-a-vibe.html` is a deliberate
   exception: it is `noindex` and canonicalises to its directory form.
3. **Metadata completeness and uniqueness** — a duplicate title or description
   across two pages is a real defect, and the most common one on a hand-built
   site.
4. **Structured data validation** — parses; required properties present for the
   declared `@type`; `@id` and `url` absolute and on the apex; nothing asserted
   that the visible page does not contain. That last check is the one that
   matters and the one no external validator performs.
5. **Internal link opportunities** — pages that mention a concept the site has
   a page about, and do not link to it. Reported as candidates with the exact
   sentence, for a human to accept or reject. Never applied.
6. **Orphan pages** — reachable from the sitemap but from no other page. An
   orphan is a page nobody will find by browsing, which usually means it is
   either unfinished or should be linked from a hub.
7. **Indexability** — `robots.txt` rules against what is actually in the
   sitemap; `meta robots` per page; the archive excluded.
8. **Resource / article interlinking** — the Scorecard is the site's
   lead-generation asset, so every article whose subject is one of the five
   trust signals is a natural route into it. Candidates only.
9. **Search Console checklist** — the actions that require a signed-in human,
   written out so they can be done in one sitting.

## OUTPUT SCHEMA

The `seo_health` section of
[`../schemas/automation-health-report.schema.json`](../schemas/automation-health-report.schema.json),
plus a Markdown audit under `automation/reports/`.

Recommendations carry a priority (`P0`–`P3`), the file and line, the exact
proposed change, and the reason. A recommendation with no reason is not
actionable and is not emitted.

## FAILURE BEHAVIOUR

| Condition | Behaviour |
| --- | --- |
| Search Console unavailable | Every impression, click, position and coverage figure is `NOT AVAILABLE`. Never estimated from anything. |
| A page cannot be parsed | Report the file and the parse error. Do not skip it silently. |
| A structured-data type it does not have rules for | Report `unknown_type` with the value. Do not assume it is valid. |
| Uncertain whether an interlink is appropriate | Emit it as a candidate with the sentence. This is a judgement call and it belongs to a human. |

## AUDIT LOG REQUIREMENT

Per the shared minimum, plus: the page list audited, every recommendation with
file and line, every `NOT AVAILABLE` field with the reason it was unavailable,
and every proposed change explicitly marked as **not applied**.
