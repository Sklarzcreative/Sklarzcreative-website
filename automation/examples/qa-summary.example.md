# Website QA report

**PASS_WITH_WARNINGS** — 8 warnings

| | |
| --- | --- |
| Generated | 2026-08-24T07:08:49.252Z |
| Commit | `c64eb241384b714c6eed3f438b5a3418b1269cb3` (working tree dirty) |
| Branch | claude/overnight-automation-2026-08-24 |
| Harness | 1.0.0 |
| Suites run | static, rendered, behaviour |
| Routes | 16 |
| Checks | 594 |
| Passed | 552 |
| Errors | **0** |
| Warnings | 8 |
| Skipped | 0 |

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

## INFO (34)

- **`behaviour.js-off-display-none`** — /insights/resources/trust-first-content-scorecard/ · js-disabled
  display:none with scripting off, treated as deliberate state rather than a stuck reveal: p.body-copy.print-only
- **`harness.fonts-blocked`**
  Google Fonts requests are aborted so that page loads are deterministic. Every rendered measurement was therefore taken with the fallback type stack, not with Playfair Display / Montserrat / Inter. Overflow and layout findings are real signals; a clean overflow result is not proof that the real typography does not overflow. Confirm typography on the live domain.
- **`live.suite`**
  live-domain checks were not requested; pass --live to run them
- **`rendered.image-not-requested`** — / · desktop
  http://127.0.0.1:34523/assets/graphics/trust-files-cover.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · desktop
  http://127.0.0.1:34523/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · desktop
  http://127.0.0.1:34523/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · tablet
  http://127.0.0.1:34523/assets/graphics/trust-files-cover.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · tablet
  http://127.0.0.1:34523/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · tablet
  http://127.0.0.1:34523/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · mobile
  http://127.0.0.1:34523/assets/graphics/trust-files-cover.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · mobile
  http://127.0.0.1:34523/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — / · mobile
  http://127.0.0.1:34523/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · desktop
  http://127.0.0.1:34523/assets/graphics/trust-files-cover.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · desktop
  http://127.0.0.1:34523/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · desktop
  http://127.0.0.1:34523/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · tablet
  http://127.0.0.1:34523/assets/graphics/trust-files-cover.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · tablet
  http://127.0.0.1:34523/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · tablet
  http://127.0.0.1:34523/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · mobile
  http://127.0.0.1:34523/assets/graphics/trust-files-cover.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · mobile
  http://127.0.0.1:34523/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /Index.html · mobile
  http://127.0.0.1:34523/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · desktop
  http://127.0.0.1:34523/sklarz-creative-logo.png is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · desktop
  http://127.0.0.1:34523/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · tablet
  http://127.0.0.1:34523/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · tablet
  http://127.0.0.1:34523/sklarz-creative-logo.png is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · tablet
  http://127.0.0.1:34523/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · mobile
  http://127.0.0.1:34523/assets/graphics/trust-framework.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · mobile
  http://127.0.0.1:34523/assets/graphics/content-engine.svg is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · mobile
  http://127.0.0.1:34523/sklarz-creative-logo.png is lazy and was never requested at this viewport
- **`rendered.image-not-requested`** — /media-kit.html · mobile
  http://127.0.0.1:34523/assets/images/cassandra-sklarz-headshot.webp is lazy and was never requested at this viewport
- **`static.canonical-stub`** — /Index.html · Index.html
  redirect stub canonicalises to https://sklarzcreative.com/
- **`static.canonical-stub`** — /insights/the-trust-files/trust-is-not-a-vibe.html · insights/the-trust-files/trust-is-not-a-vibe.html
  redirect stub canonicalises to https://sklarzcreative.com/insights/the-trust-files/trust-is-not-a-vibe/
- **`static.description`** — /Index.html · Index.html
  redirect stub, no description needed
- **`static.description`** — /insights/the-trust-files/trust-is-not-a-vibe.html · insights/the-trust-files/trust-is-not-a-vibe.html
  redirect stub, no description needed
