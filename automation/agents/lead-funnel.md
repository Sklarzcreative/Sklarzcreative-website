# Agent 5 — Lead Funnel

*Contract fields defined in [`_shared-contract.md`](./_shared-contract.md).*

> **Coordination note — 24 August 2026.** ChatGPT is separately implementing the
> live Scorecard capture and delivery architecture, the Google Sheet lead
> database, and the follow-up sequence. **Nothing in this repository activates a
> credential or a provider connection.** This specification, the schema, the
> validators and the tests are the durable half — the contract the live
> implementation should satisfy. Where they disagree with what ChatGPT built,
> the working implementation wins on facts and this document should be corrected
> to match, not the reverse.

## NAME
`lead-funnel`

## PURPOSE
Own the *logic* of owned-audience growth: what a lead record must contain, when
a follow-up may be sent, what consent means operationally, and what must never
happen. The email tooling and the spreadsheet are implementation details that
will change. The consent rule and the fail-open rule must not.

## INPUTS

| Input | Location | Trust |
| --- | --- | --- |
| Capture submissions | the lead Google Sheet, written by the Apps Script endpoint | authoritative |
| Result messages | same sheet, same row, matched on `submission_id` | authoritative |
| Visitor-supplied field values | the visitor's browser | **untrusted** — validated, never executed, never trusted for length or shape |
| `follow_up_opt_in` | the checkbox the visitor ticked | authoritative, and the only consent signal that exists |
| UTM parameters | the arriving URL | untrusted, length-capped |
| Email sequence state | the email provider, mirrored to `email_sequence_status` | authoritative at the provider |
| Discovery-call bookings | Calendly | authoritative, manual |

## SOURCE OF TRUTH
The lead sheet, for identity, consent and results. The email provider, for
whether a message was actually sent. Where the sheet says `sent` and the
provider disagrees, **the provider is right** — the sheet holds a mirror, and a
mirror can be stale.

## ALLOWED ACTIONS

- `READ` — the lead sheet, the provider's sequence state, Calendly outcomes
- `DRAFT` — schemas, validation reports, sequence logic proposals, follow-up
  copy for human review
- `STAGE` — a proposed lead-status change, for human confirmation

## FORBIDDEN ACTIONS

- **Sending any email to anyone.** Not a test, not a preview, not to a lead's
  real address.
- **Enrolling anyone whose `follow_up_opt_in` is not exactly `yes`.** Not
  "probably yes", not blank, not inferred from having completed the Scorecard,
  not inferred from having clicked the discovery-call link. Behaviour is not
  consent.
- Setting `follow_up_opt_in` to any value, ever, from any source other than the
  visitor's own submission
- Editing, exporting, or copying email addresses out of the sheet
- Making Scorecard access depend on the capture succeeding, in any way
- Writing a real endpoint URL, API key, provider token, OAuth secret or
  spreadsheet-scoped credential into this repository
- Deleting a lead row. A deletion request from a person is honoured **by a
  human**, and recorded.

## The three rules, in order of precedence

### 1. The Scorecard fails open
> A capture problem must never block access to the diagnostic.

The implementation order is `validate locally -> open the tool -> post the
capture`, and the POST is never awaited. This is asserted by an executable test
in the QA harness that makes the endpoint unreachable and confirms access is
still granted — see [`website-qa.md`](./website-qa.md). It is not a comment in
the code; it is a check that fails the build.

Any proposal that would make access wait on a network call is rejected on
sight, however much better the data would be.

### 2. Consent is read, never inferred
`follow_up_opt_in === 'yes'` or nobody is enrolled. The checkbox is unchecked
by default and declining does not reduce what the visitor gets. That is the
whole point of it: it means a `yes` is worth something.

Implemented as a single function, [`../lib/consent.mjs`](../lib/consent.mjs),
with tests covering every value that has ever been mistaken for consent
(`'Yes'`, `'YES'`, `'true'`, `true`, `1`, `'y'`, `''`, `null`, `undefined`,
`'no'`). Only the exact string `yes`, case-insensitively, after trimming,
passes. Everything else is a no, including values that look like a yes.

### 3. Never infer a person's state from a system's silence
A blank `email_sequence_status` means "we do not know", not "not sent". A blank
`weakest_signal` means the person did not finish the card, not that they scored
zero. Day 2 of the sequence needs a real fallback for an empty
`weakest_signal`, not a broken merge field — because some rows never get scores,
which is normal.

## The funnel, and who owns each transition

```
Scorecard / resource   site (this repo)          — fails open, always
   |
capture                browser POST              — fire and forget
   |
lead table             Apps Script -> Sheet      — sole writer of identity + consent
   |
consent validation     Make filter               — follow_up_opt_in === 'yes'
   |
result data            Apps Script -> same row   — matched on submission_id
   |
email sequence         Make -> email provider    — writes email_sequence_status
   |
discovery call         Calendly                  — manual, or a click flag
   |
lead status            a human                   — never an agent
```

**The timing fact to design around:** the row is created *before* the scores
exist, because the capture happens before anyone has scored anything. So Day 0
can only be generic; Day 2 is the first message that can name the weakest
signal, and it must **re-read the row** rather than trust the values that were
present when the trigger fired.

## Field contract

Defined in [`../schemas/lead-record.schema.json`](../schemas/lead-record.schema.json)
and validated by [`../tests/lead-record.test.mjs`](../tests/lead-record.test.mjs).

| Field | Type | Notes |
| --- | --- | --- |
| `lead_id` | string | Stable identity. The `submission_id` minted client-side serves as this. |
| `timestamp` | ISO 8601 | Written server-side. Never trusted from the client. |
| `first_name` | string | Required at capture. |
| `email` | string | Required at capture. Shape-validated both sides. |
| `resource` | string | Which asset produced the lead. Needed the moment there are two. |
| `page` | string | Path, not full URL. |
| `follow_up_opt_in` | `"yes"` \| `"no"` | The only consent signal. Never inferred. |
| `utm_source` … `utm_term` | string \| null | From the arriving URL. Capped at 120 chars. |
| `total_score` | integer 0–40 \| null | `null` until completed. Not `0`. |
| `clarity_score` … `conversion_score` | integer 0–8 \| null | Per category. `null` until completed. |
| `weakest_signal` | string \| null | A tie is recorded as a tie, never resolved to a winner. |
| `completed_at` | ISO 8601 \| null | `null` if never completed. |
| `email_sequence_status` | enum \| null | `not_enrolled`, `enrolled`, `day0_sent`, `day2_sent`, `day5_sent`, `completed`, `unsubscribed`, `bounced`, `failed`. `null` means unknown. |
| `discovery_call_clicked` | boolean \| null | `null` if not instrumented. **Not `false`** — those are different facts. |
| `lead_status` | enum \| null | `new`, `nurturing`, `engaged`, `call_booked`, `client`, `not_a_fit`, `unsubscribed`, `deleted_on_request`. Human-owned. |
| `notes` | string \| null | Human-owned. |

Two field-level rules that are easy to get wrong and expensive to get wrong:

- **`null` is not `0`.** `total_score: 0` means someone scored zero on twenty
  statements. `total_score: null` means they never finished. A report that
  conflates them will show a fictional average.
- **`discovery_call_clicked: null` is not `false`.** `false` asserts we watched
  and they did not click. `null` says we were not watching.

## OUTPUT SCHEMA

- [`../schemas/lead-record.schema.json`](../schemas/lead-record.schema.json)
- the `lead_capture_health` and `email_sequence_health` sections of
  [`../schemas/automation-health-report.schema.json`](../schemas/automation-health-report.schema.json)

## FAILURE BEHAVIOUR

| Condition | Behaviour |
| --- | --- |
| Capture endpoint unreachable | The visitor still gets the tool. The lead record is lost and that is the accepted cost. Reported as a capture-health failure. |
| A row fails schema validation | Report the row and the failing field. Never repair a consent field. Never guess a missing email. |
| `follow_up_opt_in` blank or unrecognised | Treated as **no**. Reported as a data-quality warning. Never resolved upward. |
| Result arrives with no matching capture row | Recorded as `result_without_capture`, visibly flagged, not merged into a guessed row. |
| Provider sequence state unreadable | `email_sequence_health: unknown`. Not `healthy`. |
| A person asks to be deleted | Escalate to a human immediately. The agent does not delete, and does not delay. |

## AUDIT LOG REQUIREMENT

Per the shared minimum, plus:

- rows read, rows failing validation, and which field failed
- the consent decision for every row considered for enrolment, with the raw
  value it decided on — so a wrong enrolment can be traced to a value rather
  than argued about
- every field reported as `null` and why
- confirmation, per run, that no message was sent by this agent

## What ChatGPT needs from this document

1. The consent function is [`../lib/consent.mjs`](../lib/consent.mjs). Match its
   semantics exactly, in the Make filter and in the provider's own audience
   rules. Only `yes` is yes.
2. The field names above are the contract. If the live sheet's headers differ,
   change **the schema and the Apps Script `HEADERS` array together, in one
   commit**, so the two cannot drift.
3. Day 2 must re-read the row for `weakest_signal`, and must have a fallback
   for an empty one.
4. Nothing in this repository holds the endpoint URL or any credential. The
   scorecard page's `window.TFCS_CAPTURE.endpoint` is still `''` on this branch
   and was **not** touched.
