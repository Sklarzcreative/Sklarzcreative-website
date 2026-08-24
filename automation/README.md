# Sklarz Creative — automation

> **Read this first.** It is written for whoever operates this next: a future
> ChatGPT, Claude or Codex session, a contractor, an employee, or Cassandra
> Sklarz six months from now having forgotten the details.
>
> The goal is that a competent system can run this operation without
> reconstructing it from old conversations.

---

## What this is, in five lines

- **The website** is hand-authored HTML on GitHub Pages. Pushing to `main` is
  deploying. There is no build step and adding one would be a mistake.
- **The content operation** lives in a Google Sheet and Make.com scenarios.
  Neither is in this repository, and nothing here can edit them.
- **`automation/`** holds the QA harness (real, executable), the schemas and
  validators (real, tested), the agent specifications (documents), and the
  runbooks for the parts that need a UI.
- **No credential is anywhere in this repository**, and none may be added.
- **No agent can publish, approve, send or delete anything.** That is the
  design, not a gap.

## Where to start, by task

| You want to… | Read |
| --- | --- |
| Understand how the whole thing fits together | [`architecture.md`](./architecture.md) |
| Know what an agent may and may not do | [`agents/_shared-contract.md`](./agents/_shared-contract.md) |
| Check the website is not broken | [`qa/README.md`](./qa/README.md) — then run it |
| Build or fix a Make scenario | [`runbooks/`](./runbooks/) |
| Recover from a publishing failure | [`runbooks/incident-recovery.md`](./runbooks/incident-recovery.md) — **before touching the queue** |
| Turn on the Scorecard follow-up | [`agents/lead-funnel.md`](./agents/lead-funnel.md) + [`runbooks/make-a-scorecard-capture.md`](./runbooks/make-a-scorecard-capture.md) |
| Tag a link | [`utm-convention.md`](./utm-convention.md) |
| Add a platform route | [`runbooks/route-onboarding.md`](./runbooks/route-onboarding.md) |
| Write a case study | [`examples/case-study.intake.md`](./examples/case-study.intake.md) |

## Run it

```bash
cd automation
npm ci                              # Playwright. The only dependency.
npx playwright install chromium     # once

npm test                            # 80 unit tests, no browser, ~1s
npm run qa                          # 578 checks over 16 routes, ~30s
npm run qa:live                      # adds live-domain checks
```

```bash
# From the repository root
node automation/lib/validate.mjs <schema.json> <file.json>   # validate anything
node automation/lib/utm.mjs vocab                            # the UTM vocabulary
node automation/lib/utm.mjs audit "<url>"                    # check a link
node automation/scripts/audit-queue.mjs <queue-export.json>  # publishing reliability
```

---

## Sources of truth

The full table is in [`architecture.md`](./architecture.md#sources-of-truth--who-owns-what-state).
The short version, because it is the thing most often got wrong:

| State | Sole writer |
| --- | --- |
| The website | this repository, branch `main` |
| Whether content is approved | **a human**, in `ARTICLE - Intake` |
| Queue `status`, `published_url`, `error` | **Make**, at publish time |
| Lead identity, email, consent | **the Apps Script endpoint**, from the visitor's own submission |
| `email_sequence_status` | the Make follow-up scenario (a mirror; the provider is authoritative) |
| `lead_status`, `notes` | **a human** |

If two systems can write a value, the value is untrustworthy. The fix is to
delete one writer, not to reconcile them.

## Approval gates

There are exactly two, and both are human.

1. **Content approval**, in `ARTICLE - Intake`. Everything upstream is draft.
   Everything downstream is a commitment made in public under a named person's
   professional reputation. No agent crosses it.
2. **Distribution pack review**, before a staged derivative becomes a queue row
   the publisher will act on.

An agent that believes it needs to cross a gate should output **a
recommendation naming the exact action a human should take** — never the action.

## What is automated, and what is deliberately not

| Automated | Deliberately manual | Why |
| --- | --- | --- |
| Website QA (nightly + on every PR) | — | Nothing to decide; a report is the output |
| Schema validation | — | Mechanical |
| UTM generation | — | Mechanical, and error-prone by hand |
| Publishing an **already-approved** row (Make) | Approving it | Approval spends reputation |
| Enrolling a lead who **consented** | Deciding what the sequence says | Copy is judgement |
| Detecting a publishing failure | **Recovering from one** | The recovery is more dangerous than the failure |
| — | Adding a platform route | [Eight gates](./runbooks/route-onboarding.md) |
| — | Publishing a case study | It makes claims about a real client |
| — | Deleting anything | No undo |

## Where credentials live

**Nowhere in this repository.** Not in a file, not in a comment, not redacted.
The `.gitignore` blocks `.env`, `*.pem`, `*.key`, `credentials*` and `secrets*`
so an accidental `git add .` cannot publish one.

| Credential | Lives in |
| --- | --- |
| Platform tokens (LinkedIn, Instagram, …) | Make.com's connection store |
| Google Sheets access | the Google account that owns the sheets |
| The Apps Script deployment URL | the scorecard page's one config line, **as a public write-only endpoint** — not a credential, and it is empty on this branch |
| Email provider API key | Make.com's connection store |
| Spreadsheet ids | the Make module's own configuration. [Not here, and here is why](./architecture.md#why-the-spreadsheet-id-is-not-in-this-repository) |
| Anything CI ever needs | GitHub Actions secrets. Today: **nothing**, so nothing can leak |

## Deployment

```
push to main → GitHub Pages "pages build and deployment" → live in ~30s
```

One path. No workflow in this repository deploys anything. The QA workflow
declares `permissions: contents: read` and nothing else — it cannot push,
comment, or deploy even if it tried, and it references no secret.

`automation/` is not part of the deployed surface: nothing links to it, it is
disallowed in `robots.txt`, and `node_modules` is never committed.

---

## Things an AI must never do autonomously

Not "should ask about". **Never, without a human's explicit instruction in the
moment.**

1. **Publish anything to any platform.** No post, no story, no comment, no
   test post to a real account.
2. **Send any email to any real address.** Including a test, including a
   preview, including to a lead's address to "check the merge fields".
3. **Enrol anyone whose `follow_up_opt_in` is not exactly `yes`.** Not
   "probably yes". Not blank. Not inferred from completing the Scorecard or
   clicking the call link. **Behaviour is not consent.**
4. **Set or change a consent value.** From any source other than the visitor's
   own submission.
5. **Release a publishing backlog.** Controlled release only — see
   [incident recovery](./runbooks/incident-recovery.md). If an agent's output
   contains "publish everything overdue", the output is wrong.
6. **Change a `HOLD`.** A human decided that. It is not a failure.
7. **Delete anything** — a queue row, a lead row, a post, a branch, a file that
   is not reconstructible.
8. **Push to `main`.** A push to `main` is a deployment.
9. **Force-push any branch.**
10. **Put a credential in this repository.** In any form. Including a redacted
    one that is still recognisable.
11. **Activate the Scorecard capture endpoint or any provider connection**
    without coordination. ChatGPT owns that live workstream as of 24 Aug 2026.
12. **Make Scorecard access depend on the capture succeeding.** It fails open.
    A capture failure costs a lead record; it must never cost the visitor the
    tool.
13. **Invent a number, a quote, a client name, a permission, a date or an
    outcome.** For a consultancy whose product is trustworthiness, one
    fabricated figure is a strategic error rather than a typo.
14. **Report unavailable data as `0`.** It is `null` / `unknown` /
    `NOT AVAILABLE`, with the reason. A zero is a measurement; an absence is
    not, and a report that renders absence as zero produces a confidently wrong
    decision.
15. **Add analytics or any third-party script to the site.** `/privacy/` states
    there is none, and that statement is load-bearing. It is a consent decision
    with a privacy-page edit in the same commit, not a technical convenience.
16. **Add a platform route** because a credential exists.
17. **Mark a case study publishable.** A human publishing it is what does that.
18. **Edit the website from inside the QA harness.** It reads. A QA tool that
    edits is not a QA tool.

## Recovery procedures

| Situation | Procedure |
| --- | --- |
| The site is broken | `git revert` the offending commit and push. Pages redeploys in ~30s. The full redesign rollback is on the permanent branch `pre-luxury-redesign-2026-08-22` — see the [root README](../README.md#rolling-back-the-redesign). |
| One page is broken | `_original-design/` holds a complete copy of every pre-redesign page. See [`_original-design/RESTORE.md`](../_original-design/RESTORE.md). |
| Publishing has stopped | [`runbooks/incident-recovery.md`](./runbooks/incident-recovery.md). Read it **before** touching the queue. |
| A duplicate was published | Delete one, set the losing row to `CANCELLED`, then find which of the five defences failed — see [runbook C](./runbooks/make-c-failure-handling.md). |
| Someone was emailed who declined | Unsubscribe immediately, stamp the row, then find the raw `follow_up_opt_in` value in the log. **The value is the bug, not the filter.** |
| A deletion request | A human deletes the row and the subscriber, confirms both, and records it. Never automated, never delayed. |
| CI fails | Read `automation/reports/qa-summary.md` from the run artifact. Exit 1 = the site has a defect. Exit 2 = the harness itself broke. |

## Troubleshooting the harness

| Symptom | Cause |
| --- | --- |
| `verdict: incomplete` with no errors | Checks were skipped. Read their reasons — this is deliberately not `pass`. |
| Every live check skipped | The environment cannot reach `sklarzcreative.com`. Expected in a sandbox. |
| Browser suites skipped | Chromium is not installed. `npx playwright install chromium`. |
| Exit code 2 | The harness broke, not the site. Distinct from 1 on purpose. |
| The sitemap lastmod check skipped | Shallow clone. `git fetch --unshallow`, or CI's `fetch-depth: 0`. |
| A finding you believe is wrong | Then it is a bug in the harness, and it matters more than the finding. Three such were found and fixed while building it — see [`qa/README.md`](./qa/README.md#false-positives-are-treated-as-bugs-in-the-harness). |

---

## What is real today, and what is a document

Being precise about this is the point of the section. A specification described
as if it were running software is the most damaging kind of documentation.

| | Status |
| --- | --- |
| Website QA harness | **Executable.** 578 checks, 16 routes, ~30s. Runs in CI. |
| Unit tests | **Executable.** 80 tests: consent, UTM, scoring, queue classification, every schema example. |
| Schemas and validator | **Executable.** Dependency-free. |
| UTM builder and auditor | **Executable.** |
| Queue reliability analysis | **Executable**, against an export. Cannot read the live queue — that needs a credential that must not live here. |
| Case-study intake and schema | **Real, and empty.** No case study exists, because no evidence was supplied. |
| Make scenarios | **Runbooks only.** Nothing here can edit Make. |
| Lead capture | **Built and switched off.** `window.TFCS_CAPTURE.endpoint` is `''`. ChatGPT owns switching it on. |
| Email sequence | **Not connected**, and nothing pretends it is. |
| Platform analytics | **No connections.** Every figure is `NOT AVAILABLE`, and the reports say so. |
| Search Console | **Not connected.** [Checklist](./runbooks/seo-search-console.md) needs a signed-in human. |
| Agents 1, 2, 4, 5, 6, 7 | **Specifications.** They describe how to run a capable model against real inputs; they are not daemons. |
| Agent 3 (Website QA) | **The code in [`qa/`](./qa/).** |

## Adding to this

1. **Change the schema before the implementation.** The schema is the contract;
   an implementation that drifts from it is a bug in one of the two, and it is
   cheaper to find out which at validation time.
2. **A new rule that matters gets a test.** A rule that only exists in prose
   decays silently. The tests here exist because `HOLD` must never be treated
   as a failure and only `yes` may be consent — not because coverage is a
   virtue.
3. **A new QA check gets broken on purpose once.** A check that has never
   failed is a check you have no reason to believe.
4. **A new directory gets a `robots.txt` disallow** if it is source rather than
   content. The harness asserts the four that exist, so the fifth fails the
   build rather than quietly getting crawled.
5. **Say what is real.** If something is a document, call it a document.
