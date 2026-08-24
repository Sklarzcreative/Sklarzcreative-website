# Runbooks

Procedures for the parts of the operation that live outside this repository —
Make.com scenarios, Google Sheets, the email provider, Search Console — plus
the recovery procedures for when one of them fails.

| Runbook | What it covers | Requires UI access |
| --- | --- | --- |
| [A · Scorecard lead capture](./make-a-scorecard-capture.md) | Sheet row → consent filter → result enrichment → email provider → status stamp | Make, Google, email provider |
| [B · Publisher](./make-b-publisher.md) | Approved queue → route → asset → publish → published URL → status | Make, every platform |
| [C · Failure handling](./make-c-failure-handling.md) | Error records, retry policy, alerting, and the idempotency that prevents a duplicate publish | Make |
| [D · Weekly reporting](./make-d-weekly-reporting.md) | Native analytics retrieval, normalisation, explicit reporting of missing data | Make, platforms |
| [Route onboarding](./route-onboarding.md) | The eight gates a platform passes before it may publish. **TikTok, YouTube and Bluesky have not passed.** | Make, the platform |
| [Incident recovery](./incident-recovery.md) | Controlled release after a publishing failure. The one procedure that must not be improvised. | Make |
| [Search Console](./seo-search-console.md) | The signed-in checklist nothing here can automate | Google |

## A note on what these documents are

**Nothing in this repository can edit a Make scenario, a Google Sheet, or an
email provider.** Pretending otherwise would be the most damaging kind of
inaccurate documentation — the kind that reads like a system and is a wish.

So these are runbooks: the exact modules, mappings, filters and error paths to
build in the UI, written so that following them produces a scenario that
behaves the way the [architecture](../architecture.md) says it does. Where a
credential is needed, the runbook names the placeholder and says where the real
value lives. **No credential appears in this repository, in any form, ever.**
