# Sklarz Creative — automation architecture

> The map of the whole operation: what flows where, which system owns each
> piece of state, and where a human decision is mandatory.
>
> **Read this before changing anything in `automation/`.** Every agent
> specification in [`agents/`](./agents/) assumes the ownership table below.

---

## The two pipelines

Sklarz Creative runs two independent pipelines. They meet only at
measurement — the content pipeline produces attention, the funnel pipeline
converts it, and the performance report is the only place both are read
together. Keeping them separate is deliberate: a publishing failure must not
be able to break lead capture, and a capture failure must not be able to stop
publishing.

### Pipeline 1 — content and distribution

```
CONTENT CREATION                    human, outside any system
        |
        v
ARTICLE / CONTENT INTAKE            Sheet tab: ARTICLE - Intake
        |
        v
APPROVAL                            human gate. Nothing passes on its own.
        |
        v
DISTRIBUTION / REPURPOSING          Content Operations Agent -> distribution pack
        |
        v
PUBLISH QUEUE                       Sheet tab: MAKE - Publish Queue
        |
        v
MAKE                                Scenario: SC-03 Sklarz Scheduled Publisher
        |
        v
PLATFORM ROUTES                     LinkedIn Personal / LinkedIn Company /
        |                           Instagram / Facebook / Threads / X / Pinterest
        v
PUBLISHED URL / STATUS              written back onto the queue row by Make
        |
        v
ANALYTICS                           native platform data, retrieved weekly
        |
        v
LEARNING / NEXT CONTENT             Content Performance Agent -> weekly report
        |
        +-------> back to CONTENT CREATION
```

**The approval gate is the load-bearing part.** Everything upstream of it is
draft. Everything downstream is a commitment made in public under Cassandra
Sklarz's name. No agent may move an item across it.

### Pipeline 2 — visitor to client

```
WEBSITE VISITOR                     sklarzcreative.com (GitHub Pages)
        |
        v
RESOURCE / SCORECARD                /insights/resources/trust-first-content-scorecard/
        |
        v
LEAD CAPTURE                        browser POST, fire-and-forget, never awaited
        |
        v
LEAD DATABASE                       Google Sheet, written by the Apps Script
        |                           endpoint (integrations/scorecard-capture.gs)
        v
CONSENT FILTER                      follow_up_opt_in === 'yes' — and nothing else
        |
        v
FOLLOW-UP                           Make.com -> email provider
        |
        v
DISCOVERY CALL                      Calendly (calendly.com/sklarzcreative/30min)
        |
        v
CRM / LEAD STATUS                   lead_status column on the lead row
```

**Two rules govern this pipeline and outrank every other consideration:**

1. **The Scorecard fails open.** A capture problem must never cost the visitor
   the diagnostic. The code order is `validate locally -> open the tool ->
   post the capture`, and the POST is never awaited. See
   [`docs/09-lead-capture.md`](../docs/09-lead-capture.md).
2. **Consent is never inferred.** `follow_up_opt_in !== 'yes'` enrols nobody,
   ever, by any route, including a manual export. The lead is still captured;
   the follow-up is what consent gates.

---

## Sources of truth — who owns what state

Every row in this table has exactly one owner. If two systems can both write a
value, the value is untrustworthy, and the fix is to delete one of the writers
rather than to reconcile them.

| State | Owner (sole writer) | Readers | Never written by |
| --- | --- | --- | --- |
| Website HTML/CSS/JS | this repository, branch `main` | GitHub Pages | any agent, any Make scenario |
| Live site content | `main` (push = deploy) | visitors | Make, Apps Script |
| Content ideas / long-form drafts | `ARTICLE - Intake` tab | Content Ops Agent | Make |
| Approval state of a content item | **a human**, in `ARTICLE - Intake` | everything downstream | every agent |
| Distribution pack (per-platform derivatives) | Content Ops Agent, as a staged artefact | human reviewer | Make |
| Queue row: platform, copy, asset, scheduled time | `MAKE - Publish Queue` tab | Make publisher | agents may propose, not write |
| Queue row: `status`, `published_url`, `error` | **Make**, at publish time | reliability agent, performance agent | any agent, any human edit while a run is live |
| Editorial calendar | `90-Day Calendar` tab | humans, Content Ops Agent | Make |
| Weekly KPIs | `Weekly KPI Tracker` tab | Content Performance Agent | Make (report-only writes are acceptable if a single scenario owns the tab) |
| Newsletter issues | `NEWSLETTER - Issues` tab | humans | Make publisher |
| Lead identity: name, email, consent | the **Apps Script endpoint**, from the visitor's own submission | Make follow-up scenario | any agent; never hand-edited to add consent |
| Lead result: scores, band, weakest signal | the **Apps Script endpoint**, from the `result` message | follow-up scenario, performance agent | any agent |
| `email_sequence_status` | the Make follow-up scenario | humans | the website |
| `lead_status`, `notes` | **a human** | performance agent | Make, any agent |
| Platform credentials | Make.com connection store, Google account, GitHub secrets | nothing reads them out | **this repository, under any circumstance** |
| Site QA verdict | the QA harness in [`qa/`](./qa/), per run | humans, CI | nothing — a report is immutable once written |

### The duplication that is already avoided, and must stay avoided

- **Scorecard scoring exists twice by necessity** — once in the browser
  (`insights/resources/trust-first-content-scorecard/index.html`) and once in
  [`lib/scorecard.mjs`](./lib/scorecard.mjs), which exists *only* so the QA
  harness can assert the page agrees with the specification. `lib/scorecard.mjs`
  is not a second implementation to be shipped; it is a test oracle. If the two
  ever disagree, the page is right about what visitors see and the harness is
  right about what was intended — reconcile deliberately, do not silently
  edit the oracle to match.
- **UTM strings are generated, never typed.** [`lib/utm.mjs`](./lib/utm.mjs) is
  the only place a `utm_*` value is composed. A hand-typed UTM is a silent
  attribution loss, and it is not detectable after the fact.
- **The lead sheet header order lives in the Apps Script**, not in this
  repository. [`schemas/lead-record.schema.json`](./schemas/lead-record.schema.json)
  describes the *contract*; `integrations/scorecard-capture.gs` `HEADERS`
  implements it. Change the schema first, then the script, in that order,
  in one commit.

---

## Where each thing physically lives

| Thing | Where | Who can change it |
| --- | --- | --- |
| Website | this repo, `main` | anyone with push access; deploy is automatic |
| QA harness | this repo, `automation/qa/` | anyone; runs in CI with read-only permissions |
| Agent specifications | this repo, `automation/agents/` | anyone; they are documents, not code |
| Schemas and validators | this repo, `automation/schemas/`, `automation/lib/` | anyone |
| Content engine spreadsheet | Google Sheets, ID `<SPREADSHEET_ID — not recorded in this public repository>` | Google account holder |
| Lead sheet | a separate Google Sheet, created at capture setup | Google account holder |
| Capture endpoint | Apps Script web app bound to the lead sheet | Google account holder |
| Publisher and follow-up scenarios | Make.com | Make account holder |
| Email sequence copy | the email provider | provider account holder |
| Every credential | Make connections / Google account / GitHub Actions secrets | **not this repository** |

---

## Deployment model

There is exactly **one** deployment path, and this work does not add another.

```
push to main  ->  GitHub Pages "pages build and deployment"  ->  live in ~30s
```

GitHub Pages, deploy-from-branch, `main`, root. No build step. No workflow in
this repository deploys anything, and the QA workflow added in
[`.github/workflows/site-qa.yml`](../.github/workflows/site-qa.yml) declares
`permissions: contents: read` — it cannot write to the repository even if it
tried. See the [root README](../README.md#deployment).

`automation/` is **not part of the deployed surface**. It is excluded from
`robots.txt`, has no page linking to it, and its `node_modules` is never
committed. A visitor who guesses the path gets Markdown and JSON, which is
harmless but pointless, so it is disallowed for crawlers alongside `docs/` and
`integrations/`.

---

## The permission model, in one line each

Every agent is bound to a verb ladder. The rungs are not interchangeable, and
no agent holds all of them. Full definitions in
[`agents/_shared-contract.md`](./agents/_shared-contract.md).

| Verb | Means | Who may |
| --- | --- | --- |
| `READ` | observe state, change nothing | every agent |
| `DRAFT` | produce a proposal that lives nowhere authoritative | Content Ops, Case Study, SEO |
| `STAGE` | write into a holding area that nothing acts on | Content Ops, Case Study |
| `APPROVE` | move an item past a gate | **a human. No exceptions.** |
| `PUBLISH` | cause something to become public or to be sent | **Make, executing an already-approved row.** No agent. |
| `DELETE` | destroy state | **a human.** No agent, ever. |

The reason `PUBLISH` sits with Make and not with an agent: Make executes a row
a human approved, and its failure mode is a stuck queue. An agent that can
publish has a failure mode of a hundred posts at 3am under the founder's name,
and that is not recoverable by any technical means.

---

## Failure posture

This system has already had one publishing-reliability incident. The design
consequence is a standing rule:

> **Reliability outranks reach. A route that works beats a route that exists.**

Concretely:

- A backlog is **never** released in bulk. The recovery order is
  `controlled single-item test -> verify the route wrote a published URL ->
  release current content -> decide item by item what stale content is still
  worth posting`. See [`runbooks/incident-recovery.md`](./runbooks/incident-recovery.md).
- A new platform route is not production-ready because credentials exist. It
  passes [`runbooks/route-onboarding.md`](./runbooks/route-onboarding.md) or it
  stays off. TikTok, YouTube and Bluesky are **off** and have not been
  onboarded.
- Missing data is reported as `null` / `"unknown"` / `NOT AVAILABLE`. It is
  never reported as `0`. A zero is a measurement; a null is an absence, and
  confusing them produces confident wrong decisions.

---

## What this architecture deliberately does not do

- **No CMS.** The site is hand-authored HTML and that is a feature: no build,
  no dependency, no supply chain, no version drift.
- **No build pipeline for the website.** Suggested repeatedly, correct never.
  There is nothing to compile.
- **No analytics on the site.** `/privacy/` states there is none, and that
  statement is load-bearing. Adding analytics is a decision with a consent
  consequence and a privacy-page edit, not a technical convenience.
- **No agent with write access to the live site.** The QA harness reads.
- **No autonomous publishing.** See the permission ladder.
