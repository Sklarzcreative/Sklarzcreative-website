# Route onboarding

> The eight gates a platform passes before it may publish.
>
> **Status as of 24 August 2026: TikTok, YouTube and Bluesky are OFF and have
> not been onboarded.** They were deliberately not added tonight.

## Why a checklist rather than just adding the route

A credential existing is not a route working. The difference between the two is
where the last publishing incident lived, and it is invisible until the moment a
post is due — which is the worst moment to discover it.

Every gate below exists because skipping it produces a specific failure that is
hard to see and public when it appears:

| Skipped gate | The failure it lets through |
| --- | --- |
| Authentication | Posts fail silently at 8am with an expired token nobody checked |
| Text-only test | A template error posts malformed copy publicly |
| Media test | A media-required platform publishes without its image, or fails and looks like a network problem |
| Published-URL capture | Everything reports green and nothing can be verified |
| Queue status update | The row stays `APPROVED` and gets published twice |
| Duplicate prevention | A retry posts twice, publicly, irreversibly |
| Failure visibility | A dead route is indistinguishable from an empty queue |
| Rollback | An incident becomes a panic |

---

## The eight gates

Onboarding is complete when all eight are recorded, with dates and evidence, in
the [record](#the-record) below. **Seven of eight is not onboarded.**

### 1 · Authentication is valid and its expiry is known

- [ ] Connection created in Make and it authorises successfully
- [ ] The account is the intended one — the company page, not a personal profile
- [ ] **The token's expiry or refresh behaviour is written down.** "It works
      today" is the state every expired token was in once.
- [ ] Where a token expires on a fixed schedule, a calendar reminder exists
      before that date

### 2 · Text-only test, where the platform allows it

- [ ] One real post, from a real queue row, through the real scenario
- [ ] It appears on the platform, correctly formatted
- [ ] Line breaks, links and any special characters survive
- [ ] Deleted afterwards if it was not content worth keeping

Manually posting through the platform's own UI proves nothing about the route.
The test has to go through the scenario.

### 3 · Media test

- [ ] One post with the media the platform requires
- [ ] The asset arrives at full quality and is not re-cropped unexpectedly
- [ ] Alt text arrives, where the platform accepts it
- [ ] The aspect ratio the platform actually wants is recorded here

### 4 · Published URL is captured

- [ ] The platform's response contains a permalink, and the scenario writes it
      to `published_url`
- [ ] The URL, pasted into a browser, opens the post

**If the platform cannot return a permalink, say so here explicitly and record
what is written instead.** Do not leave the field empty and stamp
`PUBLISHED` — the reliability agent treats that as a critical finding
permanently, which is the correct incentive.

### 5 · Queue status is updated

- [ ] `status` becomes `PUBLISHED` on success
- [ ] `published_at` and `updated_at` are written
- [ ] `status` becomes `FAILED` with the platform's **verbatim** error on failure
- [ ] `attempt_count` increments

### 6 · Duplicates are prevented

- [ ] `idempotency_key` is written when the row is created
- [ ] The row is claimed (`PROCESSING`) before any platform call
- [ ] The pre-publish re-read is in place — see
      [runbook C](./make-c-failure-handling.md#the-retry-rule-that-prevents-the-duplicate)
- [ ] **Tested:** the same row was deliberately run twice and published once

That last box is the only one that proves the other three. Test it.

### 7 · Failure is visible

- [ ] A deliberately broken attempt (revoke the token for a moment) produces an
      error record
- [ ] It produces an alert
- [ ] **A route that stops working produces a visible signal, not silence.**
      Confirm the route appears as `degraded` or `failing` in the reliability
      report rather than as `unknown` indefinitely

### 8 · Rollback is documented

- [ ] How to delete a post on this platform, written down
- [ ] Whether deletion is possible at all, and how quickly
- [ ] How to disable this route alone without stopping the publisher
- [ ] What happens to queued rows while the route is disabled

---

## The record

| Platform | Onboarded | 1 auth | 2 text | 3 media | 4 URL | 5 status | 6 dupes | 7 visible | 8 rollback |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LinkedIn personal | in production, pre-dates this checklist | — | — | — | — | — | — | — | — |
| LinkedIn company | in production, pre-dates this checklist | — | — | — | — | — | — | — | — |
| Instagram | in production, pre-dates this checklist | — | — | — | — | — | — | — | — |
| Facebook | in production, pre-dates this checklist | — | — | — | — | — | — | — | — |
| Threads | in production, pre-dates this checklist | — | — | — | — | — | — | — | — |
| X | in production, pre-dates this checklist | — | — | — | — | — | — | — | — |
| Pinterest | in production, pre-dates this checklist | — | — | — | — | — | — | — | — |
| **TikTok** | **NO** | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| **YouTube** | **NO** | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| **Bluesky** | **NO** | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

### The seven that pre-date the checklist

They are in production and this document does not retroactively switch them
off — doing so would be a change with real cost and no evidence behind it.

But **an unverified production route is a known unknown**, and the honest
position is to say so rather than to backfill ticks nobody earned. The cheapest
way to close the gap is gate 4 and gate 7 for each: confirm a recent
`published_url` exists and opens, and confirm a broken attempt is visible. Those
two answer the questions that actually matter, and each takes minutes.

**The reliability report will show any of these as `unknown` rather than
`healthy` until a verified publish appears in its window.** That is the intended
behaviour: an absence of evidence is not evidence of health.

---

## On the three that are off

**Recommendation: onboard at most one, and only if there is content that
genuinely belongs there.**

The temptation is to add all three because the queue already has content and
three more routes look like three times the reach. It is not:

- **YouTube and TikTok need video.** No video asset exists for the current
  content. A route with nothing to publish is a maintenance cost with no return,
  and a route that publishes a repurposed static image to a video platform
  performs worse than not posting.
- **Bluesky is cheap to onboard** — text-only, an open API, a real permalink —
  and its audience overlaps heavily with X and LinkedIn for this positioning.
  Low cost, low incremental reach.
- **Seven routes are already unverified against gates 4 and 7.** Adding an
  eighth before closing that gap increases the surface that can fail silently,
  which is the specific failure this system has already paid for once.

The highest-value publishing work available is not a new route. It is verifying
the seven that exist.
