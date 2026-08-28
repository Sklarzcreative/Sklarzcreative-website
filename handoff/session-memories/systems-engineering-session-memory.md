# Systems engineering — session memory

Written 27 August 2026 by a specialist reference session, for the single master
website session. Everything below was verified against the repository at the
time of writing. Where it was not, it says so.

## 1 · Session identity and scope

Specialist reference session for **automation, systems engineering, QA,
schemas and cross-branch state**. Not the master session. It does not own
website content, editorial, design, or offers, and it holds no authority to
merge, deploy, or publish.

## 2 · Repository, branch, commit

- `Sklarzcreative/Sklarzcreative-website` at `/home/user/Sklarzcreative-website`
- Branch **`claude/overnight-automation-2026-08-24`**, commit **`bd89ee9`**
- Working tree clean; no stashes; no local commit missing from a remote
- **9 ahead, 8 behind `origin/main`** (`f07ec8a`, 25 Aug)
- `origin/claude/loving-wozniak-ubvqew` points at the *same* commit `bd89ee9`.
  The **local** ref of that name is a stale pointer at `6dc946b` with no
  upstream — do not check it out by name.

## 3 · Created here versus inherited

**Inherited.** All nine commits on this branch (`7e2999d` → `bd89ee9`,
24 Aug) were authored by an earlier session. No commit in the repository
carries this session's id.

**Created here.** A read-only cross-branch reconciliation analysis (branch
map, dry-run merge results, the offer-page findings in §10, the schema drift
in §11) and this file. Nothing else.

## 4 · Automation and QA architecture

`automation/` is deliberately separate from the website. The site has no
dependencies and no build step; **nothing under `automation/` is deployed** —
see `automation/package.json` and `automation/architecture.md`.

Three layers:

1. **Contract layer** — `automation/schemas/` defines the data shapes;
   `automation/agents/` defines seven agent roles bound by
   `automation/agents/_shared-contract.md`.
2. **Executable layer** — `automation/lib/` holds the rules as pure functions
   (consent, UTM, scorecard arithmetic, queue classification, validation), so
   they can be tested rather than asserted in prose.
3. **Observation layer** — `automation/qa/` drives a real browser against a
   locally served copy of the site and emits a machine-readable report.

The harness runs a local static server (`qa/lib/server.mjs`), loads Chromium
(`qa/lib/browser.mjs`), and executes four check modules — `checks/static-html.mjs`,
`checks/rendered.mjs`, `checks/behaviour.mjs`, `checks/live.mjs` — each emitting
namespaced findings (`behaviour.scorecard-fails-open`, `static.sitemap-lastmod`).
`qa/lib/report.mjs` builds `qa-report.json` and a Markdown summary. Entry point
`automation/qa/run.mjs`; flags `--static-only`, `--live`, `--out`, `--summary`.

**Design rule worth preserving:** a check that could not run is reported as
skipped with a reason, never as a pass.

## 5 · What is on the branch

- **Workflow** — `.github/workflows/site-qa.yml`. Read-only by construction:
  `permissions: contents: read`, no secrets referenced, `pull_request` not
  `pull_request_target`. It cannot push, comment, or deploy. Runs unit tests,
  then the QA suite; nightly cron at 03:20 UTC adds `--live`.
- **Seven agent specs** — `case-study-builder`, `content-operations`,
  `content-performance`, `lead-funnel`, `publishing-reliability`,
  `seo-discovery`, `website-qa`, under `automation/agents/`.
- **Seven JSON schemas** + `_defs.md` in `automation/schemas/`, with worked
  examples in `automation/examples/`.
- **Validators and libraries** — `automation/lib/{consent,utm,scorecard,queue-audit,validate}.mjs`;
  CLI `automation/scripts/audit-queue.mjs`.
- **80 tests** across six files in `automation/tests/` (9 consent, 16
  queue-audit, 21 schemas, 12 scorecard, 12 utm, 10 validate). Run with
  `npm test` in `automation/`.
- **Six Make.com runbooks** in `automation/runbooks/`: `make-a-scorecard-capture`,
  `make-b-publisher`, `make-c-failure-handling`, `make-d-weekly-reporting`,
  plus `incident-recovery`, `route-onboarding`, `seo-search-console`.
- **`automation/utm-convention.md`** and **`automation/OVERNIGHT-REPORT-2026-08-24.md`**.

## 6 · Complete but unmerged

Everything in §5. It is additive — new files in new directories — apart from
`README.md`, `robots.txt` and `sitemap.xml`. Consequence: **no CI runs against
production today**, because `.github/` does not exist on `main`. Every push to
`main` deploys unverified.

## 7 · Proposed but unimplemented

From `automation/OVERNIGHT-REPORT-2026-08-24.md` §16 (no P0 recorded):

- **P1-a** Nothing observes publishing health; every publishing figure in the
  health report is `null` because reading the queue needs a credential that
  must not live in a public repo. Runbook D.
- **P1-b** Seven production routes unverified against gate 4 (published URL
  captured) and gate 7 (failure visible).
- **P1-c** No alert on silence — the prior incident produced no error, so an
  error-only monitor would miss it. Runbook C, fourth alert row.
- **P2-a** Search Console not connected.

Account-dependent work is specified in `docs/11-turn-it-on.md`: deploy the
capture endpoint, paste the URL into the one config line, build Kit and the
Make scenarios, Search Console, live-device QA.

## 8 · Cross-branch conflict map

Established with `git merge-tree --write-tree` (computes a merge without
touching a ref, index, or working tree).

| Pair | File | Nature |
|---|---|---|
| this branch → `main` | `sitemap.xml` | **Real regression risk.** See §9. |
| `claude/sklarz-website-prompt-archive-qwy7h4` → `main` | `docs/README.md` | Trivial |
| this branch ↔ `claude/editorial-agent-longform-l42j6l` | `robots.txt`, `README.md` | Adjacent additions; both correct |
| handoff ↔ editorial ↔ archive | `docs/README.md` | Three-way, all adding table rows |

`claude/editorial-agent-longform-l42j6l`, `claude/sklarz-creative-redesign-8yd5he`
and `claude/cannabiology-image-pipeline-bf9500` merge cleanly into *today's*
`main`; each merge changes the ground for the next.

`codex/ga4-consent-events-20260824` and `launch/trust-discoverability-audit-2026-08-25`
read as "ahead" only because PRs #5/#6 were squashed; their content is
byte-identical in `main`. `claude/cannabiology-image-pipeline-bf9500` is a
Python scientific-figure pipeline with **no relationship to this website**.

## 9 · Sitemap, robots, README, CI risks

- **`sitemap.xml` — the dangerous merge.** Commit `c64eb24` rewrote all
  `lastmod` values to `2026-08-23` from git history. `main` has since moved
  them to `2026-08-25` *and added `/audit/`*. Resolving in this branch's favour
  would roll twelve dates backwards and **silently delete the offer page from
  the sitemap**. Resolve toward `main`, then re-derive with the branch's own
  freshness check.
- **`robots.txt`** — this branch adds `Disallow: /automation/`; editorial adds
  `/editorial/` and `/tools/`. All three are needed; keep all three.
- **`README.md`** — this branch +44 lines, editorial +18. Both append their own
  section. Keep both.
- **CI** — installing `.github/workflows/site-qa.yml` is the single highest-
  leverage merge, because it makes every later merge verified.

## 10 · Offer page findings

- **`/audit/` is orphaned.** Live, in the sitemap at priority 0.95, Service
  schema, $350 / $199 local rate — and **no page links to it**. The only
  `href="/audit/"` in the repository is the page's own internal anchor.
- **A duplicate is indexable.** `/trust-discoverability-audit/index.html`
  survives on `main` from PR #6: `index,follow`, canonical pointing at
  *itself*, absent from the sitemap, linked from nowhere. Two indexable pages
  for one offer.

## 11 · Schema and Apps Script inconsistency

`automation/schemas/lead-record.schema.json` states its contract must change
**together with the `HEADERS` array in `integrations/scorecard-capture.gs`, in
one commit**. That rule has already been broken:

- This branch's script (blob `2cdd2ca`) has **23** headers.
- `main`'s script (blob `981f979`, via `dd7ed9e`) has **24** — it added
  `sequence_state`, a column Make owns and the script never writes.
- The schema is only on this branch and **has no `sequence_state`**. Its
  nearest field is `email_sequence_status`.

Field naming also differs between the two artefacts (`lead_id` vs
`submission_id`; `clarity_score` vs `clarity`). Whether that mapping is
deliberate is **not established** — see §15. On merge, reconcile the schema
against `main`'s 24-column `HEADERS`, in one commit.

No Apps Script *security* patch exists anywhere in this repository, on any
branch. The file has three commits total: `9680041`, `6dc946b`, `dd7ed9e`.

## 12 · Protected paths, assets, rollback

- **Do not modify `insights/`.** No pending branch does.
- **`sklarz-creative-logo.png`** and **`cassandra-sklarz-headshot.jpg.png`** are
  approved and are modified by no branch in the repository.
- Rollback: branch `pre-luxury-redesign-2026-08-22` (`e5aa3a6`) and
  `_original-design/` with `_original-design/RESTORE.md`. Snapshot pins
  `pre-editorial-audit-2026-08-25` (`fa196c9`) and
  `pre-audit-offer-launch-2026-08-25` (`23f2834`). **Keep all three.**
- `.gitignore` blocks `.env`, `*.pem`, `*.key`, `credentials*`, `secrets*`.
  Open request to the owner: confirm the content-engine sheet's sharing is
  *restricted*, not "anyone with the link".

## 13 · Deployment restrictions

GitHub Pages, deploy-from-branch on `main`, custom domain via `CNAME`
(`sklarzcreative.com`). **Pushing to `main` is deploying.** Netlify is retired.
No workflow deploys anything. Land work through pull requests, never a direct
push to `main`. Enabling lead capture and publishing any Curves Ahead edition
require the owner's explicit approval.

## 14 · Recommended integration order — a recommendation only

1. Repoint the two stale local refs (`main`, local `…loving-wozniak-ubvqew`).
2. PR this branch, resolving `sitemap.xml` toward `main` — installs CI first.
3. PR `claude/editorial-agent-longform-l42j6l`; keep all three `robots.txt`
   disallows and both `README.md` sections.
4. PR `claude/sklarz-creative-redesign-8yd5he` (docs only).
5. Refresh, then PR `claude/sklarz-website-prompt-archive-qwy7h4`.
6. Fix the orphaned offer and the duplicate page as their own change.
7. Decide `claude/cannabiology-image-pipeline-bf9500` separately.
8. Close out legacy branches and PR #4.
9. Only then enable capture.

## 15 · Uncertainties

- **The live site was never observed.** This sandbox's proxy returns `403` on
  `CONNECT` to `sklarzcreative.com`. Every production claim here is read from
  `origin/main` and repo documentation, not served bytes. Verify with
  `npm run qa:live` from an unrestricted network.
- **A "proposed Apps Script security patch" has been referenced elsewhere but
  is not in this repository.** If it is real, it exists outside git.
- Whether the schema/`HEADERS` naming divergence in §11 is deliberate mapping
  or drift is unresolved.
- Curves Ahead and editorial state are known only by reading
  `claude/editorial-agent-longform-l42j6l`, not by doing that work.
- Document precedence is a judgement, not a repository fact; nothing declares
  a hierarchy.
- Branch state is a snapshot of 27 August 2026 and goes stale on the next push.
