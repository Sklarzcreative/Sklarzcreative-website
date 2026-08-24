# Sklarz Creative — sklarzcreative.com

Official website for Sklarz Creative, a strategy-led brand and marketing
consultancy helping innovative and trust-sensitive companies build credibility
through positioning, research, storytelling, content systems, and creative
direction.

**Live:** [sklarzcreative.com](https://sklarzcreative.com/)

---

## What this repository is

A static site served directly by GitHub Pages. **No build step, no framework,
no npm, no dependencies.** Editing a file and pushing is deploying.

That describes the site, and it stays true. `automation/` — the QA harness and
its tooling — has one dependency (Playwright, because driving a real browser
cannot be reimplemented) and is **not deployed**: nothing links to it, it is
disallowed in `robots.txt`, and its `node_modules` is never committed. The
shipped surface remains dependency-free.

```
index.html                  Homepage — the reference implementation
media-kit.html              Media kit
404.html                    Branded 404
insights/                   Insights hub, The Trust Files, articles, podcast,
                            research notes, resources
assets/css/sklarz.css       The entire design system, one file
assets/js/hero.js           The WebGL hero. No 3D library.
assets/js/motion.js         The motion system
assets/graphics/*.svg       Editorial diagrams
assets/images/              Optimised imagery
docs/                       Design and build documentation — start here
privacy/                    What the site collects, in plain language
integrations/               Off-host glue (the Scorecard capture endpoint)
automation/                 QA harness, schemas, agent specs, Make runbooks.
                            Not deployed. Start at automation/README.md
.github/workflows/          One workflow: read-only site QA. It deploys nothing
_original-design/           The complete pre-redesign site + rollback guide
CNAME                       Custom domain for GitHub Pages
.nojekyll                   Serve underscore-prefixed paths
```

## Deployment

| | |
| --- | --- |
| **Host** | **GitHub Pages — the only host.** Netlify is retired and serves nothing. |
| **Publishing source** | Deploy from a branch: `main`, root (`/`). No build step. The one Actions workflow is read-only QA and publishes nothing. |
| **Production branch** | `main`. Pushing to it *is* deploying — GitHub's built-in `pages build and deployment` runs and publishes in about 30 seconds. |
| **Custom domain** | `sklarzcreative.com`, set by the `CNAME` file at the repository root. |
| **Jekyll** | Disabled by `.nojekyll`, so paths beginning with `_` (such as `_original-design/`) are served rather than skipped. |
| **Rollback** | `pre-luxury-redesign-2026-08-22` — a permanent branch pinned to `e5aa3a6`, the last pre-redesign commit. See below. |

**There is exactly one deployment path.** No workflow in this repository writes
to the repository or deploys anywhere. Deploy-from-branch was chosen over a
GitHub Actions workflow because there is nothing to build: an Actions pipeline
would add a YAML file, a runner, and a class of failure, in exchange for
copying files that are already in their final form.

The single workflow, [`site-qa.yml`](./.github/workflows/site-qa.yml), is not
part of that path. It declares `permissions: contents: read` and nothing else —
it **cannot** push, comment, or deploy, and it references no secret, so it can
leak none. It reads the repository, runs the QA harness, and uploads a report.

### DNS

Verified by live lookup, both already correct — **nothing points at any other
host**:

| Record | Name | Value |
| --- | --- | --- |
| `A` | `sklarzcreative.com` | `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` |
| `CNAME` | `www` | `sklarzcreative.github.io` |

The apex is canonical. Every `<link rel="canonical">`, every `og:url` and every
`sitemap.xml` entry uses `https://sklarzcreative.com/`, and GitHub Pages
redirects `www` to the apex on its own because the custom domain is set to the
apex and the `www` CNAME exists.

Optional, not required: GitHub also publishes `AAAA` records for IPv6
(`2606:50c0:8000::153` through `…8003::153`). None are currently set, and the
site works without them.

### Privacy

[`/privacy/`](./privacy/index.html) describes exactly what the site collects.
**If the collection changes, that page changes in the same commit** — it is a
factual description of the implementation, not boilerplate.

### Lead capture

The Trust-First Content Scorecard can capture a name and email, but ships with
that **switched off** — GitHub Pages cannot process a form post, so capture
happens off-host. One line in the scorecard page turns it on once an endpoint
exists. See [`docs/09-lead-capture.md`](./docs/09-lead-capture.md) and
[`integrations/scorecard-capture.gs`](./integrations/scorecard-capture.gs).

No credential belongs in this repository. The capture endpoint is a public,
write-only URL; any real key lives in the external service's own settings.

## Checking it before you push

The site has no build step, which means nothing catches a lost canonical tag, a
second `<h1>`, a broken internal link, or a sitemap that has drifted from what
is on disk. The QA harness is that catch:

```bash
cd automation
npm ci && npx playwright install chromium   # once
npm test                                    # 80 unit tests, ~1s
npm run qa                                  # ~594 checks over every route, ~30s
```

It reads and reports; **it cannot change the website**. Two of its checks
protect the commercial premise rather than a page: that the Trust-First Content
Scorecard opens even when its capture endpoint is unreachable, and that its
arithmetic matches the specification at every band boundary. Full detail in
[`automation/qa/README.md`](./automation/qa/README.md).

The same suite runs on every pull request, on pushes that touch public-site
code, and nightly.

## Documentation

Everything behind the 2026 redesign lives in **[`docs/`](./docs/README.md)** —
creative direction, the full UX map, the 3D hero specification, the motion
system, the premium audit, and the launch QA record.

How the operation *around* the site works — the content pipeline, the agent
architecture, the lead funnel, and the Make.com runbooks — lives in
**[`automation/README.md`](./automation/README.md)**. Read that before changing
anything in `automation/`, and before instructing any AI to act on this
operation: it lists what must never be done autonomously.

## Working on it locally

There is nothing to install. Serve the folder and open it:

```bash
npx http-server -p 8099 -c-1 .
```

Open <http://127.0.0.1:8099/>. `-c-1` disables caching, which you want while
editing.

## Before you change anything

Six rules are load-bearing — break one and something visibly fails:

1. **Every page must open with a dark section** (`.hero` or `.page-hero`). The
   header is fixed and transparent at scroll-top; a light first section drops
   the navigation type below WCAG AA contrast.
2. **Small gold text on a light background must use `--gold-ink`.** Brand gold
   `#C9A84C` measures roughly 2.4:1 on white.
3. **`.page-hero` cannot carry `.is-dark`** — that class sets its own flat
   background and would erase the hero gradient. Its dark-context overrides are
   declared separately in the stylesheet. Add to that block when you add a
   component.
4. **Hidden animation start-states stay scoped to `html.js`.** Unscope them and
   a JavaScript failure renders a blank page instead of a static one.
5. **`prefers-reduced-motion` must resolve reveals to their final state**, never
   leave them hidden.
6. **Never assert anything untrue.** No invented metrics, client logos,
   testimonials, or publication dates. For a consultancy that sells
   trustworthiness, one fabricated number is a strategic error.

The palette is navy `#1A2F4B` and gold `#C9A84C`. Every other colour in the
system is derived from those two — no new hue is introduced anywhere.

## Rolling back the redesign

`main` now holds the redesign — it is what is live. The previous site is
preserved two ways:

1. **`pre-luxury-redesign-2026-08-22`**, a permanent branch pinned to `e5aa3a6`,
   the exact commit that was serving before the redesign. Do not delete it.

   ```bash
   git checkout main
   git reset --hard pre-luxury-redesign-2026-08-22
   git push --force-with-lease origin main
   ```

   Pages rebuilds in about 30 seconds.

2. **`_original-design/`**, a complete copy of every original page with its own
   inline CSS, so any single page can be recovered without reverting anything.
   See [`_original-design/RESTORE.md`](./_original-design/RESTORE.md).
