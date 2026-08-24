# Search Console — the signed-in checklist

Nothing in this repository can do any of this. It all needs a signed-in Google
account, and none of it takes long. It is written out so it can be done in one
sitting rather than remembered in pieces.

**Until this is done, every Search Console figure in every report is
`NOT AVAILABLE` — and that is the correct value, not a gap to be filled with an
estimate.** There is no way to infer impressions, clicks or position from the
HTML, and a plausible-looking number would be worse than an honest absence.

---

## One-time setup

- [ ] **Verify the property.** Use a **Domain property** (`sklarzcreative.com`),
      not a URL-prefix property. A domain property covers the apex, `www`, and
      both protocols in one place — a URL-prefix property would report the apex
      and `www` separately, which is exactly the split the canonical strategy
      exists to avoid.
- [ ] Verification is a DNS TXT record. The DNS is already managed for the
      GitHub Pages A records, so this is the same place.
- [ ] **Submit the sitemap:** `https://sklarzcreative.com/sitemap.xml`
- [ ] Confirm it is read without errors, and that the URL count matches. The QA
      harness asserts the sitemap agrees with what is on disk in both
      directions, so a mismatch here means Search Console read a stale copy —
      wait for a recrawl before investigating anything else.
- [ ] **Confirm `/_original-design/` is not indexed.** `robots.txt` disallows
      it, but a disallow does not remove something already indexed. Check with a
      `site:` search; if anything from it appears, use the removal tool.
- [ ] Same check for `/docs/`, `/integrations/` and `/automation/`.
- [ ] Set the preferred domain expectation: every canonical, every `og:url` and
      every sitemap entry uses the **apex**. Confirm Search Console agrees that
      `www` redirects there.

## After any significant change

- [ ] **URL Inspection** on the changed pages. Check the *rendered* HTML, not
      just the raw source: the site's content is authored in HTML rather than
      generated, so this should match — and if it ever does not, that is worth
      knowing immediately.
- [ ] Request indexing for genuinely new pages. Not for edits; that queue is
      shared and spending it on a copy tweak is a waste.
- [ ] Check the **Coverage / Pages** report for new exclusions. The one to watch
      for is "Duplicate, Google chose a different canonical" — it means the
      canonical strategy is being overruled somewhere.

## Monthly

- [ ] **Coverage:** anything newly excluded, and why.
- [ ] **Core Web Vitals:** field data, if there is enough traffic to generate
      any. With low volume there will not be, and "not enough data" is the
      honest reading — not a pass.
- [ ] **Performance:** queries the site actually appears for. This is the only
      place that answers the question the whole SEO agent cannot: *what are
      people looking for when they find this?*
- [ ] **Mobile usability** and **manual actions**: expect empty. Confirm rather
      than assume.

## The one thing to look for first

Not rankings. **Which queries bring people to the Scorecard page**, because that
is the page with a conversion attached to it. Everything else on the site earns
attention; that page earns leads.

If the answer turns out to be branded queries only, the finding is that the
Scorecard is not being *found* — it is being *sent to*. That is a distribution
result rather than a search result, and it changes what the next piece of work
should be. Knowing which of the two is happening is worth more than any ranking
number on the dashboard.

---

## What this unlocks in the reports

Once connected, these fields stop being `NOT AVAILABLE`:

| Report | Field |
| --- | --- |
| [Automation health](../schemas/automation-health-report.schema.json) | `seo_health.impressions`, `seo_health.clicks`, `seo_health.search_console_connected` |
| [Weekly performance](../schemas/weekly-performance-report.schema.json) | the `organic_search` side of `answers.generated_traffic` |

Note what it still does **not** unlock: **how many people visited the site**.
Search Console reports impressions and clicks from Google, not visits. The site
carries no analytics by design — `/privacy/` says so, and that statement is
load-bearing. Adding analytics is a separate decision with a consent consequence
and a privacy-page edit in the same commit.
