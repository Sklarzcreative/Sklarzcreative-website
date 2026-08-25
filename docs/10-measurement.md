# 10 · Measurement

> What the site can already tell you, what it cannot, and the one decision left
> — with the exact change each option needs.

---

## What you already have, with no tracker at all

Once the capture endpoint is connected ([09](./09-lead-capture.md)), the sheet
answers a surprising amount:

| Question | Answered by |
| --- | --- |
| How many people started the Scorecard? | Rows with a name and email |
| How many finished it? | Rows where `total_score` is filled in |
| **Completion rate** | Those two, divided — including anonymous finishers, which is why `reportAnonymous` is on |
| Which channel produced a lead? | `utm_source` / `utm_campaign` / `utm_content` |
| What are people actually scoring? | `total_score` and the five category columns |
| **Which trust signal is weakest across everyone?** | `weakest_signal`, counted |
| How many opted into the follow-up? | `follow_up_opt_in` |

That last one is worth pausing on. After thirty submissions you will know which
of the five signals the market is worst at — which is a genuine research finding,
publishable as an Insight, and it costs nothing to collect.

**Use UTMs on every link you post.** Without them the `utm_*` columns stay empty
and channel attribution is guesswork:

```
https://sklarzcreative.com/insights/resources/trust-first-content-scorecard/
  ?utm_source=linkedin
  &utm_medium=organic
  &utm_campaign=trust_first_scorecard
  &utm_content=launch_post
```

Change `utm_source` per platform and `utm_content` per post. Nothing else needs
to change.

## What the sheet cannot tell you

The denominator. It knows how many people *submitted*, never how many *visited*
and left. So it cannot answer:

- How many people saw the homepage this week
- Landing-page conversion rate for the Scorecard
- Which article sends the most traffic onward
- Whether LinkedIn or Instagram brings more people at all

Those need page-view analytics, which means a script on every page. That is a
real decision with a privacy cost, so it is a decision rather than a default.

## The decision, and my recommendation

**Recommended: Cloudflare Web Analytics.** Free, no cookies, no cross-site
identifiers, no consent banner required in most jurisdictions, one script tag.
It gives page views, referrers and country, and nothing that identifies a
person.

| Option | Cost | Cookies | Consent banner | Verdict |
| --- | --- | --- | --- | --- |
| **Cloudflare Web Analytics** | Free | None | Not normally required | **Recommended** |
| Plausible / Fathom | ~$9–14/mo | None | Not normally required | Good; nicer UI; costs money |
| Umami, self-hosted | Free + a host | None | Not normally required | Only if you want to run a server |
| **Google Analytics 4** | Free | Yes | **Yes** | **Not recommended — see below** |

### Why not GA4

Three reasons, in order of weight:

1. **It sets cookies and shares data with an advertising business.** That puts a
   consent banner on a site whose whole argument is restraint, and makes the
   current privacy notice false.
2. **You do not need what it does.** GA4 is built for funnel analysis across
   large sites. Here the funnel is already in a spreadsheet, with more useful
   fields than GA4 would give you.
3. **It is the only third-party script the site would load.** Right now there
   are none. That is worth something on a site selling trust.

If you want GA4 anyway — a client asks, or an agency needs it — it is your call
and it is not hard. It just needs the consent work done honestly alongside it.

### Turning Cloudflare Web Analytics on

1. Cloudflare dashboard → **Web Analytics** → add `sklarzcreative.com`.
   You do **not** need to move DNS or proxy the site through Cloudflare; the
   JS-beacon option works on any host, GitHub Pages included.
2. Copy the beacon token. It is a **public** identifier, safe in a public repo.
3. Add one line before `</body>` on each page — the same place `motion.js` sits:

   ```html
   <script defer src="https://static.cloudflareinsights.com/beacon.min.js"
           data-cf-beacon='{"token": "YOUR_TOKEN"}'></script>
   ```

4. **Edit `/privacy/` in the same commit.** It currently says, truthfully, that
   there are no analytics. Three things have to change: the "Analytics — None"
   fact, the third-party section, and the opening claim that the site has no
   analytics. This is not optional politeness; the page is a factual description
   of the implementation, and an out-of-date privacy notice is worse than none.

Ask and this can be wired up in one commit — including the privacy edit.

## What is deliberately not measured

No heatmaps, no session recording, no scroll-depth tracking, no A/B framework.
Each would add a script, a consent question, and a decision surface, in exchange
for data that would not change what to do next on a site this size.
