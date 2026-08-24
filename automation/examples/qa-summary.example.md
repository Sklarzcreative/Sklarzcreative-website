# Website QA report

**INCOMPLETE** — no errors, but 7 checks could not run — this is not a clean bill of health

| | |
| --- | --- |
| Generated | 2026-08-24T06:56:48.639Z |
| Commit | `89df998cd55f7c98cf5577597ce0dd11f8f30d94` (working tree dirty) |
| Branch | claude/overnight-automation-2026-08-24 |
| Harness | 1.0.0 |
| Suites run | static, rendered, behaviour, live |
| Routes | 16 |
| Checks | 585 |
| Passed | 539 |
| Errors | **0** |
| Warnings | 8 |
| Skipped | 7 |

> **This run is incomplete.** 7 checks could not be performed. They are listed below with the reason, and none of them is reported as passing.

## WARN (8)

- **`static.description-length`** — / · index.html
  description is 229 characters, so a search result will truncate it around 165. Not broken — but the sentence that gets cut is the one nobody reads.
  *Evidence:* `Sklarz Creative is a strategic brand, marketing and creative consultancy. We help expert-led and innovative organisations become clearer, more credible, more discoverable, and better equipped to grow. Founded by Cassandra Sklarz.`
- **`static.description-length`** — /insights/ · insights/index.html
  description is 197 characters, so a search result will truncate it around 165. Not broken — but the sentence that gets cut is the one nobody reads.
  *Evidence:* `Explore Sklarz Creative Insights: The Trust Files, articles, podcast episodes, research notes, and practical resources on brand strategy, trust, storytelling, science communication, and innovation.`
- **`static.description-length`** — /insights/podcast/ · insights/podcast/index.html
  description is 166 characters, so a search result will truncate it around 165. Not broken — but the sentence that gets cut is the one nobody reads.
  *Evidence:* `The Sklarz Creative podcast hub, beginning with The Trust Files: long-form conversations and investigations about brand trust, storytelling, evidence, and innovation.`
- **`static.description-length`** — /insights/resources/ · insights/resources/index.html
  description is 201 characters, so a search result will truncate it around 165. Not broken — but the sentence that gets cut is the one nobody reads.
  *Evidence:* `Sklarz Creative tools, scorecards, checklists, frameworks, and practical resources for clearer strategy, stronger storytelling, and more trusted brands. Includes the free Trust-First Content Scorecard.`
- **`static.description-length`** — /insights/resources/trust-first-content-scorecard/ · insights/resources/trust-first-content-scorecard/index.html
  description is 174 characters, so a search result will truncate it around 165. Not broken — but the sentence that gets cut is the one nobody reads.
  *Evidence:* `A free 40-point diagnostic. Score one real customer-facing touchpoint across clarity, consistency, credibility, connection, and conversion, and find the weakest trust signal.`
- **`static.description-length`** — /insights/the-trust-files/ · insights/the-trust-files/index.html
  description is 185 characters, so a search result will truncate it around 165. Not broken — but the sentence that gets cut is the one nobody reads.
  *Evidence:* `The Trust Files is Sklarz Creative's signature series examining how brands earn, maintain, damage, and rebuild trust through clarity, credibility, consistency, connection, and behavior.`
- **`static.description-length`** — /insights/the-trust-files/trust-is-not-a-vibe/ · insights/the-trust-files/trust-is-not-a-vibe/index.html
  description is 170 characters, so a search result will truncate it around 165. Not broken — but the sentence that gets cut is the one nobody reads.
  *Evidence:* `File 001 of The Trust Files examines what actually makes a brand trustworthy through clarity, consistency, credibility, connection, and a practical five-touchpoint audit.`
- **`static.description-length`** — /work/ · work/index.html
  description is 204 characters, so a search result will truncate it around 165. Not broken — but the sentence that gets cut is the one nobody reads.
  *Evidence:* `How Sklarz Creative engagements run — practice areas, engagement models, the Investigate, Clarify, Create, Learn method, and published work including The Trust Files and the Trust-First Content Scorecard.`

## SKIP (7)

- **`live.404-status`**
  a nonexistent path must return a real 404, not a 200
  *Reason:* a request to https://sklarzcreative.com/ returned HTTP 403 and did not contain the site's own markup, so this environment cannot see the live domain (an egress proxy or network policy is answering instead). No live check can be performed, and none is reported as passing.
- **`live.headers`**
  compression and cache headers
  *Reason:* a request to https://sklarzcreative.com/ returned HTTP 403 and did not contain the site's own markup, so this environment cannot see the live domain (an egress proxy or network policy is answering instead). No live check can be performed, and none is reported as passing.
- **`live.https-upgrade`**
  http:// must upgrade to https://
  *Reason:* a request to https://sklarzcreative.com/ returned HTTP 403 and did not contain the site's own markup, so this environment cannot see the live domain (an egress proxy or network policy is answering instead). No live check can be performed, and none is reported as passing.
- **`live.og-image-fetch`**
  the share images must be fetchable with an image content type
  *Reason:* a request to https://sklarzcreative.com/ returned HTTP 403 and did not contain the site's own markup, so this environment cannot see the live domain (an egress proxy or network policy is answering instead). No live check can be performed, and none is reported as passing.
- **`live.outbound`**
  Calendly and the social destinations must answer
  *Reason:* a request to https://sklarzcreative.com/ returned HTTP 403 and did not contain the site's own markup, so this environment cannot see the live domain (an egress proxy or network policy is answering instead). No live check can be performed, and none is reported as passing.
- **`live.sitemap-urls`**
  HTTP status of every sitemap URL
  *Reason:* a request to https://sklarzcreative.com/ returned HTTP 403 and did not contain the site's own markup, so this environment cannot see the live domain (an egress proxy or network policy is answering instead). No live check can be performed, and none is reported as passing.
- **`live.www-redirect`**
  www.sklarzcreative.com must redirect to the apex
  *Reason:* a request to https://sklarzcreative.com/ returned HTTP 403 and did not contain the site's own markup, so this environment cannot see the live domain (an egress proxy or network policy is answering instead). No live check can be performed, and none is reported as passing.

## INFO (31)

- **`behaviour.js-off-display-none`** — /insights/resources/trust-first-content-scorecard/ · js-disabled
  display:none with scripting off, treated as deliberate state rather than a stuck reveal: p.body-copy.print-only
- **`harness.fonts-blocked`**
  Google Fonts requests are aborted so that page loads are deterministic. Every rendered measurement was therefore taken with the fallback type stack, not with Playfair Display / Montserrat / Inter. Overflow and layout findings are real signals; a clean overflow result is not proof that the real typography does not overflow. Confirm typography on the live domain.
- **`rendered.image-not-requested`** — / · desktop
  http://127.0.0.1:45149/assets/graphics/trust-files-cover.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · desktop
  http://127.0.0.1:45149/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · desktop
  http://127.0.0.1:45149/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · tablet
  http://127.0.0.1:45149/assets/graphics/trust-files-cover.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · tablet
  http://127.0.0.1:45149/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · tablet
  http://127.0.0.1:45149/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · mobile
  http://127.0.0.1:45149/assets/graphics/trust-files-cover.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · mobile
  http://127.0.0.1:45149/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · mobile
  http://127.0.0.1:45149/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · desktop
  http://127.0.0.1:45149/assets/graphics/trust-files-cover.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · desktop
  http://127.0.0.1:45149/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · desktop
  http://127.0.0.1:45149/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · tablet
  http://127.0.0.1:45149/assets/graphics/trust-files-cover.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · tablet
  http://127.0.0.1:45149/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · tablet
  http://127.0.0.1:45149/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · mobile
  http://127.0.0.1:45149/assets/graphics/trust-files-cover.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · mobile
  http://127.0.0.1:45149/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · mobile
  http://127.0.0.1:45149/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · desktop
  http://127.0.0.1:45149/sklarz-creative-logo.png is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · tablet
  http://127.0.0.1:45149/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · tablet
  http://127.0.0.1:45149/sklarz-creative-logo.png is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · mobile
  http://127.0.0.1:45149/assets/graphics/trust-framework.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · mobile
  http://127.0.0.1:45149/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · mobile
  http://127.0.0.1:45149/sklarz-creative-logo.png is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · mobile
  http://127.0.0.1:45149/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`static.canonical-stub`** — /Index.html · Index.html
  redirect stub canonicalises to https://sklarzcreative.com/
- **`static.canonical-stub`** — /insights/the-trust-files/trust-is-not-a-vibe.html · insights/the-trust-files/trust-is-not-a-vibe.html
  redirect stub canonicalises to https://sklarzcreative.com/insights/the-trust-files/trust-is-not-a-vibe/
- **`static.description`** — /Index.html · Index.html
  redirect stub, no description needed
- **`static.description`** — /insights/the-trust-files/trust-is-not-a-vibe.html · insights/the-trust-files/trust-is-not-a-vibe.html
  redirect stub, no description needed
