# Case study intake

> Fill this in **before** anything is drafted. Every blank is a question, and
> leaving one blank is a valid answer — it becomes an entry in `evidence_gaps`
> rather than a sentence somebody invented.
>
> Schema: [`../schemas/case-study.schema.json`](../schemas/case-study.schema.json)
> Agent: [`../agents/case-study-builder.md`](../agents/case-study-builder.md)

**The one rule:** if you do not know, write `MISSING EVIDENCE`. Do not write
your best guess, and do not write a hedge. "Early results were encouraging" is
a fabrication wearing a hedge, and it is worse than an admitted gap because a
reader cannot spot it.

---

## Identity and permission

| Field | Answer |
| --- | --- |
| Case id | |
| Client name | |
| **May the client be named?** (yes / no / not asked) | |
| Who granted that, and when? | |
| Where is the permission recorded? | |
| May any metric be quoted? | |
| May any quote be used, and from whom? | |
| Anonymous descriptor, if not named — e.g. "a Series A medical-device company" | |

> **`no` and `not asked` are both fine.** An anonymised case study is a complete
> case study, and it can ship today rather than after a permission conversation.
> Anonymised-but-true beats named-but-embellished. For the first two case
> studies, anonymous is the recommended default.

## 1 · Context
*What situation was the client in when they came to you?*

## 2 · Problem
*What did they say the problem was — in their words, not your diagnosis?*

## 3 · Constraints
*Budget, timeline, team, technical, political, regulatory. List them. "None
worth naming" is a legitimate answer.*

## 4 · Role
*Two lists, both needed.*

**You were responsible for:**

**You were NOT responsible for:**

> The second list is not modesty. An unbounded role reads as an inflated one,
> and a reader who has commissioned work before knows nobody does everything.

## 5 · Research / investigation
*What did you actually do to find out? Interviews, audits, competitor reads,
data pulls, customer conversations.*

## 6 · Strategic decision
**The decision:**

**The option you deliberately did NOT take:**

**Why you rejected it:**

> The rejected alternative is where the credibility lives. A case study with no
> discarded option reads as a description of the only thing anyone could have
> done — which reads as no decision at all.

## 7 · Work created
*The artefacts. Specific: "a 14-page positioning document", not "brand strategy".*

## 8 · Why those decisions were made
*The reasoning, decision by decision.*

## 9 · Observable outcome
*Something a sceptical third party could check.*

| Question | Answer |
| --- | --- |
| What is observable? | |
| How could a sceptic verify it? | |
| Was anything measured? (yes / no) | |
| If measured: the figure, verbatim, and its source | |
| Is that figure permitted to be quoted? | |

> **"The client was pleased" is not an outcome.** "The site launched on
> 3 March and the positioning document is still in use a year later" is.
> If nothing was measured, write `MISSING EVIDENCE` — and note that a case
> study with a shipped artefact and no metric is still publishable and still
> credible. A case study with an invented metric is neither.

## 10 · What was learned
*Including what you would do differently. This section is where a reader
decides you are honest.*

## 11 · Related capabilities
*Which of the site's existing capability lines this exercised. Drawn from the
site, not invented for the case study.*

## 12 · CTA
*Standard discovery-call route unless there is a reason to differ.*

---

## After filling this in

1. Anything blank becomes an `evidence_gaps` entry with a `who_can_supply`.
2. `publishable` stays `false`. **A human publishing the case study is what
   changes that** — there is no automated path from "the fields are filled in"
   to "this is on the website making claims about a real client".
3. Validate the resulting record:

```bash
node automation/lib/validate.mjs \
  automation/schemas/case-study.schema.json \
  path/to/case-study.json
```
