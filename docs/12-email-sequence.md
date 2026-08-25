# 12 · The follow-up sequence

> Three emails, written to be pasted into whichever platform you choose.
> Day 0, Day 2, Day 5 — triggered by the `trust-first-scorecard` tag that
> Make.com applies — see step 4 of [11 · Turning it on](./11-turn-it-on.md).

---

## The one thing that had to change

An earlier draft of this sequence opened Day 0 by *delivering* the Scorecard.
That describes a flow the site no longer has. The Scorecard is delivered on the
page, the instant someone gives their name — the email arrives after they have
already used it.

So Day 0 cannot be a delivery email. It has to be the thing that makes the
result stick: a copy of what they scored, and permission to ignore four fifths
of it.

That is a better email anyway. Nobody is grateful for an attachment they already
have.

---

## What the platform needs

Four custom fields, populated by Make from the sheet:

| Field | Example |
| --- | --- |
| `first_name` | `Dana` |
| `weakest_signal` | `Credibility` |
| `total_score` | `28` |
| `band` | `Solid foundation` |

**Platform: Kit (formerly ConvertKit).** Kit uses Liquid, and every subscriber
field is namespaced under `subscriber`. A bare `{{ first_name }}`, without that
prefix, renders as nothing at all rather than erroring — which is the worst way
for this to fail, because the email still sends and simply loses the word.
The tags below are Kit's:

| Field | Merge tag |
| --- | --- |
| First name | `{{ subscriber.first_name }}` |
| Weakest signal | `{{ subscriber.weakest_signal }}` |
| Total score | `{{ subscriber.total_score }}` |
| Band | `{{ subscriber.band }}` |

**Put a fallback on every one of them.** A blank `weakest_signal` in Email 2
leaves a sentence with a hole in it:

```liquid
{{ subscriber.weakest_signal | default: "your lowest signal" }}
{{ subscriber.first_name | default: "there" }}
```

Custom field names in Kit are lowercase with underscores, and the tag has to
match the field name exactly. Create the fields **before** importing anyone —
Kit will not retroactively populate a field that did not exist at import time.

---

## Email 1 — Day 0

**Subject:** Your Trust-First score, and the one part worth acting on
**Preview text:** Your lowest signal is the only number that matters this week.

> Hi {{ subscriber.first_name | default: "there" }},
>
> You scored **{{ subscriber.total_score }} out of 40** — {{ subscriber.band }}.
>
> Your lowest signal was **{{ subscriber.weakest_signal | default: "your lowest signal" }}**.
>
> That is the number to act on, and the other four are a distraction for now.
> Trust does not average out. A reader does not experience a total; they hit the
> weakest signal and stop. Lifting the lowest category by two points will change
> more than lifting the total by six spread across all five.
>
> The interactive version is here whenever you want to re-run it — on a specific
> page, or on a competitor's:
>
> **[Re-open the Scorecard →](https://sklarzcreative.com/insights/resources/trust-first-content-scorecard/)**
>
> In two days I will send you the specific first move for
> {{ subscriber.weakest_signal | default: "your lowest signal" }}. Nothing to do until then.
>
> — Cassandra
>
> Cassandra Sklarz
> Founder & Strategic Marketing Consultant, Sklarz Creative

**Why it is shaped this way.** It gives them their number back, because most
people close the tab without writing it down. It then does the one genuinely
useful thing a diagnostic can do — tell them what to *ignore*. And it promises
the next email specifically, so Day 2 arrives as something they were expecting.

---

## Email 2 — Day 2 · the personalised one

**Subject:** {{ subscriber.weakest_signal | default: "your lowest signal" }} — where I would start
**Preview text:** One move, not a checklist.

> Hi {{ subscriber.first_name | default: "there" }},
>
> Your weakest signal was **{{ subscriber.weakest_signal | default: "your lowest signal" }}**. Here is the first place I
> would look.

Then **one** of the five blocks below, selected by `weakest_signal`. Most
platforms do this with conditional content in a single email; if yours does not,
build five near-identical emails and branch the automation on the field.

These deliberately go a step past the one-line move shown on the results page —
someone who has read that sentence should get something new here, not the same
sentence again.

### If Clarity

> Open the page a stranger is most likely to land on and read only the first
> sentence. Then answer two questions in writing: *what does this person do*,
> and *who is it for*. If you cannot answer both from that one sentence, it is
> not doing its job — and no amount of design further down the page will rescue
> it.
>
> The usual cause is that the opening line was written to sound impressive
> rather than to be understood. A useful test: read it to someone outside your
> industry. If they ask a clarifying question, the line has failed, and their
> question is usually the better opening line.

### If Consistency

> Put three touchpoints side by side on one screen — your website, your
> LinkedIn profile, and the last thing you sent a prospect. Read the first
> sentence of each in a row.
>
> Do not try to align all three. Find the one that disagrees with the other two
> and fix that one. Consistency problems are almost always a single stale
> artefact rather than a systemic drift, and hunting for a grand unified message
> is how this turns into a six-week project instead of an afternoon.

### If Credibility

> Take the single strongest claim you make anywhere and add one checkable thing
> to it — a number, a name, a date, a boundary. *Trusted by leading brands*
> becomes *worked with eleven organisations across science and publishing since
> 2019*. The second is a smaller claim and a far stronger one.
>
> If nothing checkable can be added, that is the finding. Soften the claim
> rather than dressing it up. Unsupported superlatives cost more credibility
> than a modest, specific statement ever gains.

### If Connection

> Find the first paragraph on your most important page that talks about you, and
> delete it. Replace it with the question the reader arrived carrying.
>
> Most pages open by establishing the author's authority, which is exactly
> backwards: authority is what you earn by demonstrating that you understood the
> problem first. Value before the ask, and in that order — the order is most of
> the point.

### If Conversion

> Click your own primary call to action, as a stranger would, and read what the
> destination actually says.
>
> Most conversion problems are not the button. They are the gap between what the
> button promised and what the next screen delivers — a *Book a call* that lands
> on a generic contact form, a *Download the guide* that asks for six fields.
> Fix the destination before you rewrite the button. If the destination is
> right, the button rarely needs the work.

Then close every variant the same way:

> If you would rather talk it through against your own material, that is what a
> discovery call is for — thirty minutes, no deck.
>
> **[Book a discovery call →](https://calendly.com/sklarzcreative/30min)**
>
> — Cassandra

---

## Email 3 — Day 5

**Subject:** The trust signal most people score lowest
**Preview text:** And what it says about how content actually gets judged.

> Hi {{ subscriber.first_name | default: "there" }},
>
> One thing I will say about the Scorecard: the five signals are not equally
> difficult. Credibility and Connection are consistently the hardest, and the
> reason is structural rather than a failure of effort.
>
> Clarity and Consistency can be fixed by editing. You can rewrite an opening
> line this afternoon. Credibility cannot be edited into existence — it needs
> something that happened, described specifically. And Connection asks you to
> lead with someone else's problem instead of your own competence, which cuts
> against every instinct that got most of us hired.
>
> That is why *Clarity is the first act of trust* is the practice and not a
> slogan. Clarity is the one you can start on today, and the other four get
> easier once it is settled.
>
> Two things you might find useful:
>
> **[The Trust Files →](https://sklarzcreative.com/insights/the-trust-files/)**
> Where I write about this properly.
>
> **[Clarity Before Content →](https://sklarzcreative.com/insights/clarity-before-content/)**
> The argument underneath the Scorecard.
>
> And if the {{ subscriber.weakest_signal | default: "your lowest signal" }} work turns out to be bigger than an afternoon
> — which it often does — that is worth a conversation.
>
> **[Book a discovery call →](https://calendly.com/sklarzcreative/30min)**
>
> — Cassandra

> **A note on this one.** Do not add a claim about *how many* people score
> lowest on which signal until the sheet can actually tell you. It will — that
> is what the `weakest_signal` column is for — and after thirty or forty
> completions you will have a real finding worth publishing as an Insight and
> worth citing in this email. Until then the paragraph above stands on reasoning
> rather than on a number, which is honest. A fabricated statistic in an email
> about credibility would be a bad joke at your own expense.

---

## Sequence settings

| Setting | Value | Why |
| --- | --- | --- |
| Trigger | tag `trust-first-scorecard` | Applied once by Make, per person |
| Day 0 | immediately on tag | They were just on the site |
| Day 1 | — | Leave it empty. Two emails in two days reads as a funnel. |
| Day 2 | Email 2 | Promised explicitly in Email 1 |
| Day 5 | Email 3 | Far enough out to be a note, not a nudge |
| After Day 5 | **stop** | No indefinite drip. |
| Send window | weekdays, business hours, their timezone | |
| Unsubscribe | the platform's own link, in every email | Legally required, and never hand-rolled |

**On the last two rows.** The sequence ends at Day 5 and does not roll into a
newsletter. If you later want an ongoing list, ask for that consent separately —
someone who agreed to a follow-up about their score has not agreed to a monthly
send, and treating those as the same thing is exactly the kind of small
dishonesty this whole practice is positioned against.

And use the platform's unsubscribe link, never a page on this site. The platform
has to record the opt-out to comply on your behalf; a hosted page here would
look like it worked and quietly do nothing.
