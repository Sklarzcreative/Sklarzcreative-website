# Master website handoff — Sklarz Creative

> **Canonical operating document for the single master Claude Code session.**
>
> Written 28 August 2026 on `claude/website-master-integration-2026-08-28`,
> branched from freshly fetched `origin/main` at **`f07ec8a`**. Nothing was
> merged into this branch. No website code, live page, production branch, lead
> capture, publication or deployment was changed to produce it.
>
> **Precedence.** Where this document disagrees with the repository, the
> repository wins. Where it disagrees with Cassandra, Cassandra wins.

---

## Standing facts — read before acting

| | |
| --- | --- |
| **Lead capture is DISABLED.** | `endpoint: ''` on `main`. No lead has ever been captured. It stays off until Cassandra says otherwise. |
| **The proposed v2 Apps Script patch is preserved, not approved, not deployed.** | It exists only on `backup/scorecard-hardening-2026-08-28`. |
| **The backup branch must NOT be merged as a whole.** | Relative to `main` it deletes two live pages. Extract files, never merge. |
| **The two offer pages need a canonical-page decision.** | `/audit/` and `/trust-discoverability-audit/` are both live and indexable. |
| **Edition 02 is approved but NOT published.** | Nothing has been sent to LinkedIn, Substack or the site. |
| **Editions 01 and 03 are blocked on Cassandra's answers.** | Four questions, unanswered. |
| **`main` is production. Pushing to `main` deploys.** | GitHub Pages, deploy-from-branch, ~30 seconds. No staging, no approval gate. |
| **Nothing publishes without Cassandra's approval.** | Applies to editions, offers, capture activation and any live page. |
| **Protected:** `insights/`, the approved logo, the approved headshots, `_original-design/` rollback material. | No branch in the repository modifies any of them. Verified. |
| **Cannabiology is a separate project.** | `claude/cannabiology-image-pipeline-bf9500` is a Python figure pipeline. Never merge it into this workstream. |
| **PR #4 is closed** (28 Aug, verified). | It was a 1-file, +1/−1 draft. An earlier claim in this document that it deleted `.gitignore` and `_original-design/` was **wrong** — see §15. |
| **Content-engine Sheet is not shared.** | Verified 28 Aug: owner access only, `sklarzcreative@gmail.com`. |

---

## 1 · Production baseline

| | |
| --- | --- |
| Repository | `github.com/Sklarzcreative/Sklarzcreative-website` |
| Production branch | **`main`** — verified `f07ec8a` on 28 Aug |
| Host | GitHub Pages, deploy-from-branch, root. No Actions workflow on `main`, no build step |
| Domain | `sklarzcreative.com` via `CNAME` |
| Rollback | `pre-luxury-redesign-2026-08-22` (`e5aa3a6`) · `_original-design/` · snapshots `pre-editorial-audit-2026-08-25` (`fa196c9`), `pre-audit-offer-launch-2026-08-25` (`23f2834`) |

**No CI runs against production.** `.github/` does not exist on `main`, so every
push to `main` deploys unverified.

## 2 · Chronology

| Date | Event |
| --- | --- |
| 6–10 Aug | Pre-redesign agent branches. Three descend from an unrelated root |
| 22 Aug | Luxury redesign lands. `pre-luxury-redesign-2026-08-22` pinned at `e5aa3a6` |
| 23 Aug | Netlify retired; GitHub Pages becomes sole host |
| 24 Aug | Consent-gated GA4 (`G-15GX6KDX09`) ships via PR #5. Automation control plane built (unmerged) |
| 24–25 Aug | Curves Ahead migrated from Drive; editorial system built on its own branch |
| 25 Aug | Mini Audit offer pages ship via PR #6 and follow-up commits |
| 27 Aug | Systems-engineering reconciliation written |
| 28 Aug | `backup/scorecard-hardening-2026-08-28` (`fd6e138`) created. Luxury-redesign memory written *after* it, with corrected chronology. This document written |
| 28 Aug | **PR #4 closed** (`16:20:06Z`), verified against live GitHub metadata. Content-engine Sheet verified unshared. `/audit/` approved as canonical. This document corrected |

**Chronology correction, recorded deliberately.** The systems-engineering and
prompt-archive memories both state that no Apps Script security patch existed on
any branch. **Those statements were accurate when written.** The preservation
branch appeared afterwards. They are superseded by newer repository state, not
wrong, and must not be characterised as defective.

## 3 · Branch and workstream ownership

| Branch | Head | vs `main` | Owner / workstream | Disposition |
| --- | --- | --- | --- | --- |
| `main` | `f07ec8a` | — | Production | Merge via PR only |
| `claude/editorial-agent-longform-l42j6l` | `184a17b` | 12 / 5 | Editorial, Curves Ahead, tools, privacy fix | **Merges clean — verified 0 conflicts** |
| `claude/overnight-automation-2026-08-24` | `ec57e1f` | — | Automation, QA, schemas | Conflicts on `sitemap.xml` |
| `claude/loving-wozniak-ubvqew` | `bd89ee9` | — | Duplicate of the above (older) | Integrate one only |
| `claude/sklarz-creative-redesign-8yd5he` | `f4db520` | — | Design system, Scorecard, runbooks | Docs-only, merges clean |
| `claude/sklarz-website-prompt-archive-qwy7h4` | `8fa5592` | — | `CLAUDE.md`, prompt memory | Trivial `docs/README.md` conflict |
| `backup/scorecard-hardening-2026-08-28` | `fd6e138` | 13 / 5 | Preserved v2 patch | **NEVER MERGE — see §14** |
| `claude/cannabiology-image-pipeline-bf9500` | — | — | **Not this website** | Out of scope |
| `codex/ga4-consent-events-20260824` | `523f290` | — | GA4 — squashed into `main` (PR #5 closed) | Safe to close |
| `launch/trust-discoverability-audit-2026-08-25` | `9905ca2` | — | Offer — squashed into `main` (PR #6 closed) | Safe to close |
| `agent/clarity-before-content-insight`, `agent/insights-library`, `agent/social-media-icons` | — | — | Pre-redesign | **UNRELATED HISTORY — verified no common ancestor. Never merge** |
| `agent/fix-mobile-hero-graphic` | `0bbb92a` | — | PR #4 — **CLOSED 28 Aug**, see §15 | Reference only; do not delete |
| `agent/weekly-review-business-foundation`, `automation-assets` | — | — | Superseded | Read before deleting |
| `pre-*` (three) | — | — | Restore points | **Keep permanently** |

## 4 · Deployed to production

Luxury redesign · Trust-First Content Scorecard (works with JavaScript off) ·
`/privacy/` · print/PDF output · OG cards · Netlify retirement · consent-gated
GA4 · `/audit/` and `/trust-discoverability-audit/` · `docs/01`–`13`.

## 5 · Committed but not merged

- **Editorial** (`184a17b`, 12 commits, 45 files): editorial standard v1.2, voice
  and imprint profiles, Curves Ahead source, three edition drafts, ten review
  files, `tools/{cadence.py,audit.py,browser-audit.js}`, `docs/14`, `docs/15`,
  the privacy grey-cell fix, `.claude/` agent and command.
- **Automation** (`ec57e1f`): `.github/workflows/site-qa.yml`, seven agent specs,
  seven schemas, validators, 80 tests, six Make.com runbooks.
- **Redesign** (`f4db520`): `docs/11`–`13`, `handoff/`. Documentation only.
- **Prompt archive** (`8fa5592`): `CLAUDE.md`, `WEBSITE_WORKFLOW.md`, prompt
  archive and index.

## 6 · Preserved but unapproved

`backup/scorecard-hardening-2026-08-28` (`fd6e138`) — three files, verified
present:

| File | Size |
| --- | --- |
| `docs/16-scorecard-endpoint-hardening.md` | 12,483 B |
| `integrations/scorecard-capture.v2.gs` | 22,249 B, 592 lines |
| `integrations/scorecard-capture.test.js` | 19,828 B |

v1 is byte-identical on that branch and on `main` (`53c9707962c92993…`) — the
patch is additive and diffable, not a replacement in place.

## 7 · Proposed but unimplemented

Apps Script endpoint deployment · Kit custom fields and tag · the Make.com
scenario · the email sequence in Kit · Search Console and Bing · live-device QA ·
three case studies · Media Kit PNG compression · publishing-health observation
(P1-a) · seven route verifications (P1-b) · silence alerting (P1-c).

## 8 · Website redesign

Live since 22 August. Load-bearing constraints that must survive any merge:
every page opens with a dark section · `.page-hero` never carries `.is-dark` ·
hidden animation start-states stay scoped to `html.js` ·
`prefers-reduced-motion` resolves reveals to their final state · `hero.js` is
homepage-only · navy `#1A2F4B` and gold `#C9A84C` only, small gold on light uses
`--gold-ink` · three typefaces, no fourth.

Hero material: `env()`'s sky is deliberately decoupled from `backdrop()`. **Do
not re-tie `env()` to `NAVY`** — it turns the gold green.

## 9 · Scorecard and lead capture

**Scorecard: live and working.** Twenty statements authored in HTML, so the
instrument stays complete and printable with scripting off.

**Lead capture: disabled by design.** `endpoint: ''` hides the form entirely —
the shipped default, not an unfinished state. Fail-open ordering is deliberate:
validate → open the tool → post, never awaited. A failed capture costs a lead
record, never the visitor's access. **Preserve that ordering.**

## 10 · Apps Script v1 and proposed v2

**v1** (`integrations/scorecard-capture.gs`, 187 lines, 24-column `HEADERS`) is on
`main` and **has never been deployed**.

**v2** is preserved, unapproved, undeployed.

> ### Unresolved technical claim — must not be treated as established
>
> The v2 documentation asserts that `SpreadsheetApp.getActiveSpreadsheet()`
> returns `null` in a deployed web-app context, making v1 fail silently.
>
> **This claim is UNVERIFIED in this repository and cannot be tested outside
> Apps Script.** The v2 test suite reports 23/23 passing, but against *mocks*
> that were written to model the claimed behaviour — that is not independent
> confirmation.
>
> **Do not authorise deployment of v1 or v2 on this claim alone.** Resolve it by
> deploying a throwaway test script in Apps Script and observing the result.
>
> If the claim holds, **`docs/11` step 1 does not work as written** and must be
> treated as suspended.

v2 additionally proposes formula-injection escaping, `LockService`, a body-size
cap, daily write caps, strict validation, and separate `Leads`/`Spam`/`Analytics`
tabs. Those are independent of the disputed Finding 8.

## 11 · Privacy and analytics

`/privacy/` is live and accurate. GA4 `G-15GX6KDX09` is wired in
`assets/js/motion.js`, consent-gated on `sc_analytics_consent_v1`, and disclosed
on the privacy page.

**A visible defect is live now:** the third-parties grid on `/privacy/` renders a
solid grey cell. The fix is on the editorial branch and not yet merged.

**`docs/10-measurement.md` is outdated.** It recommends Cloudflare Web Analytics,
argues against GA4, and states the site carries no third-party script. GA4
shipped 24 August. Rewrite it to record GA4 as shipped, keeping the Cloudflare
reasoning as the recorded alternative.

## 12 · Curves Ahead Editions 01–03

| Edition | State |
| --- | --- |
| **01 · AI Is Making Execution Cheap** | Full editorial pass done. Blocked on Q1 (a concrete example) and Q2 (a concession). **Not proofed.** |
| **02 · Growth Without Losing the Plot** | **APPROVED** 25 Aug. Canonical `--light-2-edited`; publication text `--proof`. **NOT PUBLISHED.** |
| **03 · Why Newsletters Are Becoming Interesting Again** | Full pass done, sources footnoted. Blocked on Q3 and Q4. **Not proofed.** |

All of it lives only on `claude/editorial-agent-longform-l42j6l`. `origin/main`
contains **zero** `editorial/` files. Questions are in
`editorial/author-questions-2026-08-25.md`.

## 13 · Offers, automation, QA, prompt memory

**Offers — a decision is required.** Both pages are live:

- `/audit/` — in the sitemap at priority 0.95, Service schema, **orphaned: the
  only `href="/audit/"` in the repository is the page's own internal anchor**
- `/trust-discoverability-audit/` — `index,follow`, canonical pointing at itself,
  **absent from the sitemap**, linked from nowhere

Two indexable pages for one offer, neither reachable by navigation.

**Automation:** complete and unmerged. `automation/` is deliberately not deployed.
Design rule to preserve: *a check that could not run is reported as skipped with
a reason, never as a pass.*

**Prompt memory:** `CLAUDE.md` exists **only** on the prompt-archive branch. Keep
it short; standing rules go to `WEBSITE_WORKFLOW.md`, history to the archive.
Of 34 archived prompts: 1 verbatim, 11 partial, 22 reconstructed — **never cite a
reconstruction as something Cassandra said.**

## 14 · Conflicts

### Mechanical

| Pair | File | Resolution |
| --- | --- | --- |
| automation → `main` | `sitemap.xml` | **Resolve toward `main`.** The branch would roll twelve `lastmod` dates back and silently delete `/audit/` from the sitemap |
| editorial ↔ automation | `robots.txt` | Keep all three disallows: `/editorial/`, `/tools/`, `/automation/` |
| editorial ↔ automation | `README.md` | Keep both sections; they append |
| three branches | `docs/README.md` | Three-way, all adding table rows. Order-dependent |

Docs numbering: `10`–`13` taken on `main`, `14`–`16` reserved by the editorial and
backup branches. **Next free number is 17.**

### Semantic — git sees nothing; these are the real risk

1. **Schema vs script drift.** `automation/schemas/lead-record.schema.json`
   claims the Apps Script `HEADERS` array implements it. It does not:
   `lead_id`/`submission_id`, `clarity_score`/`clarity` (×5),
   `email_sequence_status`/`sequence_state`. With
   `additionalProperties: false`, a real row fails validation. Reconcile the
   schema to `main`'s 24-column `HEADERS`, in one commit.
2. **Two Make.com specifications.** `automation/runbooks/make-a-scorecard-capture.md`
   uses Watch New Rows; `docs/11` uses scheduled Search Rows with a
   `sequence_state` stamp. One must be deleted, not left as an alternative.
3. **Duplicate offer pages** — §13.
4. **`Index.html` / `index.html` — RESOLVED 28 Aug: intent confirmed, file KEPT.**
   Investigated for deletion and **deliberately not deleted.** See §15b.

### The backup branch hazard — verified

```
git diff --diff-filter=D --name-only origin/main origin/backup/scorecard-hardening-2026-08-28
  audit/index.html
  trust-discoverability-audit/index.html
```

It descends from the editorial branch, which predates both offer pages.
**Merging it deletes two live pages.** Extract the three files individually.

## 15 · PR #4 — CLOSED, and a correction to this document

### Current status: CLOSED

Independently verified against live GitHub API metadata on **28 August 2026**.
PR #4 was **closed at `2026-08-28T16:20:06Z`**. It was never merged.

| Field | Live value |
| --- | --- |
| State | `closed` (never merged) |
| Draft | `true` |
| Mergeable | **`false`** (`mergeable_state: dirty`) |
| Changed files | **1** |
| Additions | **1** |
| Deletions | **1** |
| Head / base | `0bbb92a` (`agent/fix-mobile-hero-graphic`) / `3e44ab7` |

Its single change was an **obsolete mobile-hero CSS adjustment in `index.html`**,
written 10 August against a pre-redesign homepage. The redesign superseded it.

### Correction — the earlier claim in this document was WRONG

> **Superseded claim, preserved verbatim so the error is not hidden:**
>
> *"Verified against current `main`, merging it would: replace `index.html` —
> 608 lines → 39 lines, reverting the entire redesign; **delete `.gitignore`**,
> which blocks `.env`, `*.pem`, `*.key`, `credentials*`, `secrets*` from a public
> repository; **delete the whole `_original-design/` rollback archive**,
> including `RESTORE.md` and the archived headshot."*

**That claim was incorrect.** PR #4 would not have deleted `.gitignore` or
`_original-design/`, and the live metadata (1 file, +1/−1) is incompatible with
a change of that size.

**Root cause — comparing incompatible trees.** The claim came from running a
*tree diff* between two branch tips:

```
git diff --name-status origin/main 0bbb92a      # WRONG for previewing a merge
```

That reports what differs between two snapshots. It listed 52 files as `D`
simply because they exist on `main` and did not yet exist at `0bbb92a`, an
August-10 commit. A merge does not delete those files: git resolves against the
**merge base**, and where only one side changed a file, that side wins.

The correct preview uses the merge base:

```
MB=$(git merge-base origin/main 0bbb92a)        # 3e44ab7
git diff --name-status $MB 0bbb92a
  M	index.html                                   # the only change PR #4 contributes
```

**One file. Exactly matching GitHub's own count.**

**Lesson recorded for future sessions:** never preview a merge with
`git diff <branch-a> <branch-b>`. Use `git merge-base` and diff from it, or
`git merge-tree`. A tree diff against an older branch tip will always
manufacture false deletions, and the older the branch, the more alarming the
false result.

The outcome — close PR #4, do not merge it — was correct. The stated reasoning
was not.

## 15b · `Index.html` determination — kept, with reasoning

**Outcome: `Index.html` is retained.** Deletion was authorised only if the file
held no unique required functionality. It holds none by *content* — but its
redirect is its function, and that function was added deliberately.

### The exact comparison

| | `Index.html` | `index.html` |
| --- | --- | --- |
| Size | 413 B | 36,536 B |
| Lines | 0 (single line) | 609 |
| sha256 | `08d2605c197dd864…` | `3b2c3f06022742f3…` |
| `<section>` | 0 | 12 |
| `<img>` | 0 | 4 |
| `<nav>` / `<footer>` | 0 / 0 | 1 / 1 |
| JSON-LD | 0 | 1 |
| `<script>` | 1 (`location.replace('/')`) | 4 |

Token-level check — every `href`, `src`, `id` and `name` in `Index.html`
compared against `index.html`: **zero attributes unique to `Index.html`.** It
contains no markup, styling, structured data or behaviour that the real homepage
lacks.

### Why it was kept anyway

1. **It was created on purpose.** Commit **`6feafb4` — "Redirect legacy
   Index.html to canonical homepage."** It is not an accident or a stray copy.
2. **It is documented as correct.** `QA_POST_LAUNCH_2026-08-09.md`: *"Root
   homepage is a real `index.html` and legacy `Index.html` redirects to `/`."*
3. **GitHub Pages is case-sensitive.** `/Index.html` is a distinct URL from `/`.
   Deleting the file converts a working redirect into a 404 for every legacy
   inbound link, old bookmark or stale external reference pointing at the
   capitalised path.

The file is correctly built for its job: `noindex`, canonical to `/`, meta
refresh, `location.replace`, and a visible fallback link. It is the same pattern
used for the Trust Files stub and now for `/trust-discoverability-audit/`.

### References verified

No reference to the capitalised path exists in any HTML, XML, CSS, JS or text
file. `sitemap.xml` and `robots.txt`: **0 occurrences each.** The only mentions
are the QA record above and `_original-design/Index.html`, which is protected
rollback material and untouched. **All live references already use the lowercase
path.**

### If Cassandra still wants it removed

It is a one-line deletion, reversible, and the only consequence is that
`/Index.html` would serve the branded `404.html` instead of forwarding. That is
a defensible choice — but it is a choice, not a cleanup, so it is being left to
her rather than made here.

## 16 · Source-of-truth hierarchy

1. **Cassandra's explicit current instruction** — always wins
2. **Freshly verified repository state** — beats any prose
3. `CLAUDE.md` → `WEBSITE_WORKFLOW.md` (prompt-archive branch)
4. `README.md`, `docs/README.md` — load-bearing rules
5. `editorial/standards/editorial-standard.md` (v1.2) for editorial;
   `editorial/curves-ahead/00-master-handoff.md` for Curves Ahead
6. `docs/01`–`08` — the design system as built
7. `docs/09`–`13` — **intent, much of it unbuilt**
8. Session memories and `WEBSITE_PROMPT_ARCHIVE.md` — reference, partly
   reconstructed

**Known stale:** `docs/10-measurement.md` (pre-GA4) · `_original-design/RESTORE.md`
Option 2 (falsely claims `main` untouched) · any pre-23 Aug document naming
Netlify as host.

## 17 · Protected assets and deployment rules

**Never modify:** `insights/**` · `sklarz-creative-logo.png` ·
`cassandra-sklarz-headshot.jpg.png` · `assets/images/cassandra-sklarz-headshot.webp` ·
`favicon.svg` · `assets/graphics/*.svg` · `_original-design/**` · `.nojekyll`.
Optimising is allowed; reinterpreting or regenerating is not. Never invent a
signature — `.print-sign` is empty deliberately.

**Never invent** a metric, client, testimonial, result, credential or publication
date. On a consultancy positioned on checkable credibility, invented proof is
self-refuting.

**Deployment:** never push directly to `main`. Land through a pull request,
approved by Cassandra. Review the full diff first. Public repository — no
credential, token or private URL in code, docs or commits.

## 18 · Recommended integration order — a recommendation only

1. ~~Close PR #4~~ — **done, closed 28 Aug** (§15).
2. **Decide the canonical offer page** (§13). It gates sitemap and navigation work.
3. **PR the automation branch**, resolving `sitemap.xml` toward `main`. This
   installs CI first, so every later merge is verified.
4. **PR the editorial branch** — merges clean today; ships the live privacy
   defect fix. Keep all three `robots.txt` disallows and both `README.md` sections.
5. **PR the redesign branch** (docs only), then the prompt-archive branch.
6. **Resolve the schema/`HEADERS` drift** and delete one Make.com specification.
7. **Resolve Finding 8 empirically** before touching the endpoint.
8. **Extract** the three preserved files from the backup branch — never merge it.
9. **Only then** consider enabling capture, with Cassandra's approval.

## 19 · Decisions required from Cassandra

1. **Canonical offer page** — keep both, redirect one, or remove one?
3. **Approve or reject the v2 patch** — and authorise an empirical test of
   Finding 8 before any endpoint deployment.
4. **The four editorial questions** — unblocks Editions 01 and 03.
5. **Publish Edition 02?** LinkedIn + Substack same day, then the site archive.
6. **Enable lead capture?** Requires `docs/11` step 1 and her Google account.
7. **Keep or delete** the pre-redesign `agent/*` branches and the automation
   duplicate.
8. ~~Confirm the content-engine sheet's sharing~~ — **RESOLVED 28 Aug.**
   Independently verified as **not shared**: the only permission returned is
   owner access for `sklarzcreative@gmail.com`. No link sharing, no additional
   grantees. Re-check if the sheet is ever used by Make.com, which will require
   granting access to a service identity.

## 20 · Unknowns and verification limits

- **Finding 8 is unresolved** and decides whether `docs/11` step 1 is usable.
- **The live site has never been observed from this environment.** The proxy
  returns 403 for `sklarzcreative.com`. Every "live" claim here means "present on
  `origin/main`", not served bytes.
- **GitHub Pages settings were never read.** The production branch is inferred
  from `CNAME`, documentation and the absence of deploying workflows.
- Whether GA4 is actually receiving data.
- Whether `Index.html` is deliberate.
- Whether the schema naming divergence is deliberate mapping or drift.
- Whether the `agent/*` branches hold anything unique — **read before deleting**.
- Kit's plan tier — whether Sequences and Visual Automations are available.
- Real-device rendering (Safari, Firefox, iOS) and Lighthouse scores.
- Whether Drive has moved since the 24 Aug Curves Ahead migration. Nothing syncs it.

## 21 · Provenance of imported material

| Section source | Branch | Commit | File |
| --- | --- | --- | --- |
| Design system, Scorecard, hero, deployment, Kit, §8–11 detail | `origin/claude/sklarz-creative-redesign-8yd5he` | `f4db520` | `handoff/session-memories/luxury-redesign-session-memory.md` |
| Automation, QA, schemas, sitemap risk, offer findings, §14 semantics | `origin/claude/overnight-automation-2026-08-24` | `ec57e1f` | `handoff/session-memories/systems-engineering-session-memory.md` |
| Prompt memory, precedence, protected assets, PR #4, unrelated histories | `origin/claude/sklarz-website-prompt-archive-qwy7h4` | `8fa5592` | `handoff/session-memories/prompt-archive-session-memory.md` |
| Editorial, Curves Ahead, tools, privacy fix | `origin/claude/editorial-agent-longform-l42j6l` | `184a17b` | `editorial/**`, `docs/14`, `docs/15` |
| Preserved v2 patch | `origin/backup/scorecard-hardening-2026-08-28` | `fd6e138` | `docs/16`, `integrations/scorecard-capture.v2.gs`, `integrations/scorecard-capture.test.js` |
| Production baseline | `origin/main` | `f07ec8a` | repository root |

**Independently re-verified for this document, not taken on trust:** the six
branch hashes · the three memory files' existence and size · the three preserved
files' existence and size · the backup branch's two deletions · the three
unrelated-history branches having no common ancestor with `main` · both
`Index.html` and `index.html` on `main` · `/audit/` having exactly one
self-referential link · `/trust-discoverability-audit/` being `index,follow` and
absent from the sitemap · the editorial branch merging clean · PR #4's line
counts and its deletion of `.gitignore` and `_original-design/`.

**Conversation context, not repository fact:** Cassandra is reconciling parallel
Claude Code and ChatGPT work · she selected a single master session · her
approval of Edition 02's first-person restoration · her instruction to pause
implementation and deployment · Playfair Display and the Scorecard PDF confirmed
working on a real device · the olive cast reported from her phone · Netlify
retired on credit-exhaustion evidence · Kit chosen as the email platform.
