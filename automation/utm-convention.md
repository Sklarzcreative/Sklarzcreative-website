# The Sklarz Creative UTM convention

> One vocabulary, one builder, one validator.
> Implementation: [`lib/utm.mjs`](./lib/utm.mjs) · Tests: [`tests/utm.test.mjs`](./tests/utm.test.mjs)

## Why this is a document and not a habit

`utm_source=LinkedIn` and `utm_source=linkedin` are two different channels in
every reporting tool ever built, and nothing warns you. You simply see half the
traffic you earned, split across rows you never notice are the same row. By the
time the discrepancy matters the data is months old and unfixable — you cannot
retroactively merge two channels once the clicks have landed.

So UTMs are **generated, never typed**. That is the whole convention. Everything
below is the vocabulary the generator enforces.

## The command

```bash
node automation/lib/utm.mjs <url> <source> <medium> <campaign> [content] [term]

# Print the full vocabulary
node automation/lib/utm.mjs vocab

# Check a link somebody already made
node automation/lib/utm.mjs audit "https://sklarzcreative.com/?utm_source=LinkedIn"
```

Example:

```bash
$ node automation/lib/utm.mjs \
    https://sklarzcreative.com/insights/resources/trust-first-content-scorecard/ \
    linkedin organic_social trust_first_scorecard weakest_signal_carousel

https://sklarzcreative.com/insights/resources/trust-first-content-scorecard/?utm_campaign=trust_first_scorecard&utm_content=weakest_signal_carousel&utm_medium=organic_social&utm_source=linkedin
```

Parameters come out in alphabetical order, always. The same inputs produce a
byte-identical link, so one post cannot become two rows in a report through
nothing but key ordering.

## The shape of every value

`lower_snake_case` — letters, digits, single underscores. No capitals, no
spaces, no hyphens, no dots.

The builder **rejects** a value that breaks this rather than silently
lowercasing it. Normalising would make this one code path safe while leaving
every hand-written link elsewhere broken, and the error message is what teaches
the convention.

---

## `utm_source` — WHERE the click came from

A platform or a property. Never a campaign, never a format.

| Value | Meaning |
| --- | --- |
| `linkedin` | LinkedIn personal profile |
| `linkedin_company` | LinkedIn company page |
| `instagram` | Instagram |
| `facebook` | Facebook |
| `threads` | Threads |
| `x` | X (formerly Twitter) |
| `pinterest` | Pinterest |
| `youtube` | YouTube |
| `tiktok` | TikTok |
| `bluesky` | Bluesky |
| `newsletter` | The email newsletter |
| `email` | A one-to-one or transactional email |
| `podcast` | Podcast episode notes or description |
| `media_kit` | The media kit, when sent directly |
| `partner` | A named partner or collaborator placement |
| `qr` | A printed or on-screen QR code |
| `direct` | **Reserved.** Never apply this to a link — it is what untagged traffic becomes. The builder refuses it. |

**The two LinkedIn values are separate on purpose.** A personal profile and a
company page behave so differently for a founder-led consultancy that averaging
them hides the finding — which is usually that the personal profile does nearly
all the work.

Adding a source is legitimate. Add it to `SOURCES` in `lib/utm.mjs` with a
one-line description, so the vocabulary and the enforcement stay the same thing.

## `utm_medium` — HOW it travelled

The category of channel, not the platform.

| Value | Meaning |
| --- | --- |
| `organic_social` | An unpaid post on a social platform |
| `paid_social` | A paid placement on a social platform |
| `email` | Any email — newsletter, sequence, or one-to-one |
| `referral` | A link from someone else's property |
| `organic_search` | Unpaid search. Rarely taggable; present for completeness |
| `print` | Printed material, usually via a QR code |
| `offline` | A talk, an event, a conversation |
| `profile` | A bio or profile link rather than a post |

**Keep this list short.** Mediums are how you group sources; a medium per source
defeats the point of having the field.

## `utm_campaign` — WHY

A stable identifier for a body of work, reused across every source and every
post that belongs to it. **Stability is the entire value** — a campaign renamed
halfway through is two campaigns in the report, and neither is complete.

| Known value | Covers |
| --- | --- |
| `trust_first_scorecard` | The Scorecard as a lead asset |
| `the_trust_files` | The Trust Files essay series |
| `clarity_before_content` | The Clarity Before Content argument |
| `discovery_calls` | Directly driving discovery-call bookings |
| `site_launch_2026` | The 2026 site redesign launch |
| `media_kit` | Distribution of the media kit |
| `newsletter_growth` | Growing the owned list itself |

New campaigns are expected. The *pattern* is enforced; the list is documentation.

## `utm_content` — WHICH creative

The specific post, image, or link position, so two posts in one campaign can be
told apart.

**This is the field that answers "which post produced this lead", and it is the
one most often left blank.** A blank `utm_content` means you know the campaign
worked and you will never know which post did it. The auditor emits a warning
for a missing one rather than an error, because a campaign-level link is still
better than an untagged one — but a warning that keeps appearing is a habit
worth fixing.

Suggested shape: `<angle>_<format>` — `weakest_signal_carousel`,
`not_a_vibe_systems_angle`, `issue_014_scorecard_mention`.

## `utm_term` — paid and search only

The builder **refuses** `utm_term` on an organic social medium. There it is
noise that makes two otherwise identical links look different, which is the
same failure as case drift in a different costume.

---

## Links that already carry tracking

If a link already has `utm_*` parameters, `buildUrl` **throws** rather than
overwriting them.

```js
buildUrl('https://sklarzcreative.com/?utm_source=partner&utm_campaign=q3_review', { … })
// UtmError: base URL already carries deliberate tracking (utm_source, utm_campaign).
//           Refusing to overwrite it. Read what it is for first;
//           pass { overwrite: true } only once you know.
```

Someone may have set those parameters for a reason not visible from where you
are standing — a paid test, a partner's own reporting, a campaign roll-up. The
correct sequence is read, report, then decide. `{ overwrite: true }` exists and
is a deliberate act.

The Content Operations Agent is bound by the same rule: it records such links
under `preserved_links` in its output and leaves them alone.

## Where the parameters go once clicked

The Scorecard reads `utm_source` through `utm_term` from the arriving URL and
stores them with the capture — see
[`docs/09-lead-capture.md`](../docs/09-lead-capture.md). No cookie, no device
identifier, no third-party script: the parameters were already in the link.

Two honest limits on what that data can tell you:

1. **It only sees arrivals that converted.** It cannot report visits, because
   the site has no analytics. "Which post produced this lead" is answerable;
   "how many people read the post and left" is not.
2. **Values are capped at 120 characters** by the capture endpoint. The builder
   enforces the same cap, so a link cannot be built that would be truncated on
   arrival.

## Adding a value

1. Add it to `SOURCES` or `MEDIUMS` in [`lib/utm.mjs`](./lib/utm.mjs), with a
   description.
2. Add the row to the table above.
3. `node --test automation/tests/utm.test.mjs` — the vocabulary is tested for
   self-consistency, so a value that breaks its own convention fails there.
