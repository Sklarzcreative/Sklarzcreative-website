# Sklarz Creative — prompt index

Fast lookup for the Claude Code website prompt archive. Full entries, with
exact wording and notes, are in
[`WEBSITE_PROMPT_ARCHIVE.md`](./WEBSITE_PROMPT_ARCHIVE.md). Standing rules are
in [`WEBSITE_WORKFLOW.md`](./WEBSITE_WORKFLOW.md).

**Recovery status:** `V` = VERBATIM · `P` = PARTIAL · `R` = RECONSTRUCTED.
Read the ["Read this before trusting any entry"](./WEBSITE_PROMPT_ARCHIVE.md#read-this-before-trusting-any-entry)
section before citing any of these — 22 of the 34 are reconstructed from
repository evidence, not from a transcript.

**Deployment:** unless a row says otherwise, everything through P-033 is live
on `sklarzcreative.com` via GitHub Pages on `main`. Current production HEAD is
`a5be572`.

---

## Phase A · Launch readiness and post-launch QA — 9–10 August 2026

Branch: `main`.

| # | Date | Title | Category | Rec. | Commit | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P-001 | 2026-08-09 | Rebuild homepage for performance, visuals, SEO, lead gen | Homepage · SEO · Conversion | R | `fa94dbd` | Superseded by P-018 |
| P-002 | 2026-08-09 | Expand the Insights content hubs for the Trust Files launch | Content pages · Copy | R | `5992f43`…`5dd125a` | Superseded by P-020 |
| P-003 | 2026-08-09 | Fix routing and canonical URLs | Navigation · SEO | R | `6feafb4`, `6b413e9`, `df487e4`, `8c0dbf1` | In force |
| P-004 | 2026-08-09 | Produce the editorial SVG graphics | Visual design | R | `15612aa`, `9afde18`, `8206d1b`, `58e0f69` | In force |
| P-005 | 2026-08-09 | Replace the redirecting 404; add SVG favicon | UX · Metadata | R | `9ab3870`, `6c34f88` | In force |
| P-006 | 2026-08-09 | Upgrade the media kit | Service page · A11y · SEO | R | `5bb75b8` | Superseded by P-020 |
| P-007 | 2026-08-09 | Standardize metadata and social previews across hubs | Metadata · Social · SEO | R | `e4da6be`, `c171574`, `5e13cad`, `2677504`, `fb7ebd9` | In force |
| P-008 | 2026-08-09 | Run a post-launch QA audit | QA · Auditing | R | `8ca5637` | Complete |
| P-009 | 2026-08-09 | Fix every defect the QA audit found | A11y · Metadata · Schema | R | `af1e5a9`…`0b28fc5` | Complete |
| P-010 | 2026-08-09/10 | Automate QA cleanup; optimize founder headshot | QA · Perf · GitHub | R | `0640052`, `ce66f38`, `e1dec6a` | Complete |
| P-011 | 2026-08-09/10 | Verify and standardize the LinkedIn URL | Copy · Links · QA | R | `95aad77`, `3e44ab7` | Complete |

---

## Phase B · The cinematic redesign — 22 August 2026

Branch: `claude/sklarz-creative-redesign-8yd5he`, since merged to `main`.
Prompt text for this phase is preserved in `docs/05-build-with-claude.md`.

| # | Date | Title | Category | Rec. | Commit | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P-012 | 2026-08-22 | Stage 0 — Survey the site and archive it before touching anything | Audit · Backup · Rollback | P | `496b9a3` | Complete |
| P-013 | 2026-08-22 | Stage 1 — Creative direction | Brand · Positioning | P | → `c64d0a8` | Complete |
| P-014 | 2026-08-22 | Stage 2 — Experience design | UX · A11y · Responsive | P | → `c64d0a8` | Complete |
| P-015 | 2026-08-22 | Stage 3 — The design system | Code · Visual · A11y | P | → `c64d0a8` | Complete |
| P-016 | 2026-08-22 | Stage 4 — The cinematic hero | Code · Visual · Perf | P | → `c64d0a8` | Complete; refined in P-023, P-024 |
| P-017 | 2026-08-22 | Stage 5 — The motion system | Code · UX · A11y | P | → `c64d0a8` | Complete |
| P-018 | 2026-08-22 | Stage 6 — Rebuild the homepage | Homepage · Copy · Code | P | `c64d0a8` | Complete |
| P-019 | 2026-08-22 | Stage 7 — Build the verification harness | QA · Testing | P | — (tooling, uncommitted) | In use on every commit since |
| P-020 | 2026-08-22 | Stage 8 — Convert every secondary page onto the design system | Code · Schema | P | `1ea9e44` | Complete |
| P-021 | 2026-08-22 | Stage 9 — Premium audit | Audit · Visual · Copy | P | → `docs/06` | Complete |
| P-022 | 2026-08-22 | Stage 10 — Launch QA | QA · Deploy readiness | P | → `docs/07` | Complete |

---

## Phase C · Positioning, scorecard and print — 22–23 August 2026

Branch: redesign branch → `main`.

| # | Date | Title | Category | Rec. | Commit | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P-023 | 2026-08-22 | Fix the gem's blown-out highlight | Visual design · Code | R | `cb8c323` | Complete |
| P-024 | 2026-08-22 | Fix the 3D object being cut in half on phones | Responsive · Visual | R | `b0af741` | Complete |
| P-025 | 2026-08-22 | Replace estimated payload figures with measured ones | QA · Doc honesty | R | `c7c63b3` | Complete |
| P-026 | 2026-08-22 | Preserve the scorecard by merging main, not rebasing | Git · Branches · Preservation | R | `26bf7a4` | Complete |
| P-027 | 2026-08-22 | Replace "Creative with a reason" | Copy · Positioning | R | `ccc69c4` | Complete |
| P-028 | 2026-08-22 | Convert the Trust-First Content Scorecard onto the design system | Code · A11y · QA | R | `240e002` | Complete |
| P-029 | 2026-08-22 | Sharpen strategic positioning across the site | Positioning · Founder title · Schema | R | `000e1b8` | Complete |
| P-030 | 2026-08-22 | Wire the scorecard lead capture | Forms · Conversion | R | `e0801a2` | Superseded by P-031, removed in P-032 |
| P-031 | 2026-08-23 | Make the scorecard capture fail open; onto the design system | Forms · A11y · Security | R | `1aa56c8` | Complete; capture later removed |
| P-032 | 2026-08-23 | Determine the real production host; ship the scorecard open | Deployment · Forms | R | `13d49c6` | Complete |
| P-033 | 2026-08-23 | Give the printed scorecard letterhead and a signature | Visual design · Print | R | `a5be572` | Complete — current production HEAD |

---

## Phase D · Prompt memory — 23 August 2026

Branch: `claude/sklarz-website-prompt-archive-qwy7h4`.

| # | Date | Title | Category | Rec. | Commit | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P-034 | 2026-08-23 | Create the Claude Code website prompt-memory and documentation system | Documentation · Process | V | see commit for this branch | Complete · **not deployed** |

---

## Totals

| Recovery status | Count |
| --- | --- |
| `VERBATIM` | 1 |
| `PARTIAL` | 11 |
| `RECONSTRUCTED` | 22 |
| **Total** | **34** |

---

## Adding the next one

Assign `P-035`, add the row to the right phase table above, and follow the
prompt-capture rule in [`WEBSITE_WORKFLOW.md`](./WEBSITE_WORKFLOW.md#the-prompt-capture-rule):
archive the prompt **before** implementation, then update its entry with
outcome, files changed, tests performed, branch, commit SHA, deployment status
and rollback reference afterwards.
