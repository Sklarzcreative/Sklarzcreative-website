# Session memory — prompt-archive session

Durable handoff from the Claude Code session that built the prompt-memory
system, written for the **master Sklarz Creative website session**. This file
is a reference, not an authority: where it disagrees with the repository, the
repository wins.

---

## 1 · Session identity and scope

A **documentation-only** session. It created the Claude Code prompt-memory
system and performed two read-only surveys (an 18-branch reconciliation and a
session self-assessment). It wrote **no** website code, touched no assets,
changed no configuration, and deployed nothing.

It did **not** build the redesign, the Scorecard, analytics, the privacy page,
the offer pages, or Curves Ahead. It only surveyed them. Treat its knowledge of
those streams as *observation*, not authorship.

## 2 · Repository, branch, commit

- Repo `Sklarzcreative/Sklarzcreative-website` at `/home/user/Sklarzcreative-website`
- Branch `claude/sklarz-website-prompt-archive-qwy7h4`
- Commit `b481c00` ("docs: add Claude Code website prompt memory"), plus this handoff commit
- `origin/main` was `f07ec8a` when this was written; branch was 1 ahead / 11 behind
- Working tree clean throughout; no stashes, no untracked files

## 3 · Files this session created

| Path | Purpose |
| --- | --- |
| `CLAUDE.md` (root) | Always-loaded project memory. New — none existed before |
| `docs/ai-prompts/claude-code/WEBSITE_WORKFLOW.md` | Standing rules, imported by `CLAUDE.md` |
| `docs/ai-prompts/claude-code/WEBSITE_PROMPT_ARCHIVE.md` | 34 prompt entries, ~1,300 lines |
| `docs/ai-prompts/claude-code/PROMPT_INDEX.md` | Lookup table |
| `docs/README.md` | One row added, nothing removed |
| `handoff/session-memories/prompt-archive-session-memory.md` | This file |

## 4 · How the four documents work together

Deliberate layering, by cost of loading:

- **`CLAUDE.md`** — short by design (~40 lines). Loads every session. Carries only non-negotiables and a map. It imports `@docs/ai-prompts/claude-code/WEBSITE_WORKFLOW.md`.
- **`WEBSITE_WORKFLOW.md`** — the operating authority. The nine-stage sequence (inspect → understand → back up → plan → implement → test → verify → deploy → document), brand and positioning rules, rollback requirements, pre-deploy and post-deploy QA checklists, load-bearing CSS constraints, and the prompt-capture rule.
- **`WEBSITE_PROMPT_ARCHIVE.md`** — the history. Deliberately **not** imported into `CLAUDE.md`; at ~1,300 lines it would crowd out working context. Consult it on demand.
- **`PROMPT_INDEX.md`** — the index into the archive.

**Rule to keep:** `CLAUDE.md` stays short. New standing rules go in
`WEBSITE_WORKFLOW.md`. New history goes in the archive. Never inline the
archive into memory.

## 5 · Which archived prompts are exact

Of 34 entries: **1 VERBATIM, 11 PARTIAL, 22 RECONSTRUCTED.**

- **VERBATIM (P-034 only)** — the prompt that created this system, held in-session.
- **PARTIAL (P-012–P-022)** — copied from `docs/05-build-with-claude.md`, which describes them as *"the real ones, generalised."* Substance and most phrasing are original; not keystroke-exact.
- **RECONSTRUCTED (22 entries)** — rebuilt from commits, diffs and docs. **Never cite these as things Cassandra said.** Each names its evidence.

No prior Claude Code conversation was readable. The archive's opening section
states these limits; do not let a later summary quietly upgrade them.

## 6 · Source-of-truth and precedence

Documents are **not** equally authoritative:

1. Cassandra's explicit instruction — always wins
2. The repository's actual state (`git`, file contents) — beats any prose
3. `CLAUDE.md` → `WEBSITE_WORKFLOW.md` — governing rules
4. `docs/README.md` — load-bearing CSS rules and change history
5. `docs/01`–`08` — design system as built
6. `docs/09`–`13` — **intent, much of it unbuilt**; describes a funnel that does not fully exist
7. `WEBSITE_PROMPT_ARCHIVE.md` — history, partly reconstructed

## 7 · Protected assets, paths, constraints

- **Never modify `insights/**`** without explicit instruction
- **Never redraw or regenerate** `sklarz-creative-logo.png`, `cassandra-sklarz-headshot.jpg.png`, `assets/images/cassandra-sklarz-headshot.webp`, `favicon.svg`, or the four `assets/graphics/*.svg`. Optimising is allowed; reinterpreting is not
- **Never invent a signature.** `.print-sign` is left empty deliberately
- **Preserve `_original-design/**`** — the rollback path
- **Colour:** navy `#1A2F4B`, gold `#C9A84C`. No new hues. Small gold on light must use `--gold-ink` (brand gold is ~2.4:1 on white)
- **Type:** Playfair Display (display), Montserrat (labels/nav/numerals), Inter (reading). No fourth typeface
- **Writing:** never invent metrics, client logos, testimonials, results, credentials or publication dates. If a page states no date, omit the field. Positioning is a multidisciplinary strategic brand, marketing and creative consultancy — never a social-media, content-production or graphic-design execution service. Founder title: **Founder & Strategic Marketing Consultant**. AI is an operating model, never an identity
- **Load-bearing:** every page opens with a dark section; `.page-hero` cannot carry `.is-dark`; hidden animation start-states stay scoped to `html.js`; `prefers-reduced-motion` resolves reveals to their final state; `hero.js` is homepage-only

## 8 · Deployment and approval

- GitHub Pages, deploy-from-branch on `main`. **Merging to `main` is deploying**
- **Never push directly to `main`.** Work on a branch; Cassandra approves
- Never deploy a documentation-only change unless separately requested
- Review the full diff before any deploy
- Netlify does not serve the domain — do not wire anything to it
- Public repository: no credential, token or private URL in code, docs or commits

## 9 · Dangerous, stale and incompatible branches

**Unrelated history — never merge.** `agent/clarity-before-content-insight`,
`agent/insights-library`, `agent/social-media-icons` descend from root
`511c7df`; the live site descends from `df487e4`. Git joins them only with
`--allow-unrelated-histories`, and doing so reads the redesign, the Scorecard,
`/work/`, `/privacy/` and both offer pages as deletions. Extract any wanted copy
file-by-file.

**Superseded:** `agent/fix-mobile-hero-graphic`, `agent/weekly-review-business-foundation`, `automation-assets` (one PNG worth cherry-picking).

**Fully absorbed, safe to close:** `codex/ga4-consent-events-20260824`,
`launch/trust-discoverability-audit-2026-08-25`, and the three `pre-*` snapshots.

**Duplicate:** `claude/loving-wozniak-ubvqew` and
`claude/overnight-automation-2026-08-24` are the same commit `bd89ee9`.
Integrate one.

**Not website work:** `claude/cannabiology-image-pipeline-bf9500` is a Python
figure pipeline. Do not confuse it with the website.

## 10 · PR #4 risk

**PR #4 is open against `main` and would destroy the redesign.** Head
`0bbb92a` (`agent/fix-mobile-hero-graphic`) predates it; merging replaces the
redesigned `index.html` (608 lines) with a 39-line pre-redesign version,
reverting title, description, Open Graph tags and the whole page. It looks like
a one-line mobile fix. It is not. Close or explicitly reject it.

## 11 · Known outdated documentation

- **`_original-design/RESTORE.md` Option 2 is false.** It says `main` is untouched. `main` received the redesign. Working rollbacks: `_original-design/` (Option 1) or `git show 3e44ab7:<file>` (Option 3)
- `docs/09`–`13` describe capture, email, Make.com and case studies as if wired. None is live
- Any pre-23 August doc mentioning Netlify as host is stale

## 12 · Conversation context not verifiable through git

Clearly labelled as **conversation memory, not repository fact**:

- Cassandra is reconciling parallel Claude Code **and ChatGPT** work and asked for implementation and deployment to pause
- She is selecting one master session; this one is a reference session
- She referenced an **"Apps Script security patch."** I could not find it — searched every remote ref and all six PRs. `integrations/scorecard-capture.gs` is identical (`981f979`) everywhere except `overnight-automation`, whose copy is *older*, not patched. If it exists it is outside this repository. **Do not assume it was applied**
- Her stated priorities: Scorecard live but capture disabled; Edition 02 ready, 01 and 03 need her input; approval required before publishing

## 13 · What the master session should adopt permanently

1. Never push to `main`; branch and wait for approval
2. Never merge the three unrelated-history branches; close PR #4 first
3. Keep `CLAUDE.md` short; rules to `WEBSITE_WORKFLOW.md`, history to the archive
4. Archive material prompts **before** implementing, then update with outcome, files, tests, commit and deployment status
5. Label recovered prompts honestly; never upgrade RECONSTRUCTED to VERBATIM
6. Treat `docs/09`–`13` as intent, not state
7. Verify the production commit and host from evidence before any backup or rollback
8. State what could not be verified in every QA report
9. Never claim something is deployed when it was only discussed

## 14 · Remaining uncertainties

- The Apps Script security patch — not found (section 12)
- GitHub Pages settings were never read; the production branch is inferred from CNAME, deleted workflows and docs
- The live site was never fetched; "live" means "on `main`"
- Whether the duplicate `/audit/` and `/trust-discoverability-audit/` pages are intentional
- Whether GA4 `G-15GX6KDX09` is receiving data
- Prior session transcripts are unreadable, which is why 22 prompts are reconstructions
