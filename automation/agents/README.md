# Agents

Seven specialised agents, not one autonomous one. The reasoning, the permission
ladder and the ten required contract fields are in
**[`_shared-contract.md`](./_shared-contract.md) — read that first.**

| # | Agent | Deliverable | Highest verb it holds | Executable today |
| --- | --- | --- | --- | --- |
| 1 | [Content Operations](./content-operations.md) | distribution pack | `STAGE` | spec + schema |
| 2 | [Publishing Reliability](./publishing-reliability.md) | reliability report | `DRAFT` | spec + [`../lib/queue-audit.mjs`](../lib/queue-audit.mjs), tested |
| 3 | [Website QA](./website-qa.md) | QA report | `DRAFT` | **yes — [`../qa/`](../qa/)** |
| 4 | [SEO / Discovery](./seo-discovery.md) | audit + Search Console checklist | `DRAFT` | spec + the static half runs inside the QA harness |
| 5 | [Lead Funnel](./lead-funnel.md) | schema, consent logic, validation | `STAGE` | spec + [`../lib/consent.mjs`](../lib/consent.mjs), tested |
| 6 | [Content Performance](./content-performance.md) | weekly report | `STAGE` | spec + schema |
| 7 | [Case Study Builder](./case-study-builder.md) | case study or an evidence gap list | `STAGE` | spec + schema + intake template |

**No agent holds `APPROVE`, `PUBLISH` or `DELETE`.** That is not an oversight to
be corrected later; it is the design. See
[`_shared-contract.md`](./_shared-contract.md#the-two-rungs-no-agent-holds).

## Using one of these

These are specifications, not prompts. To run an agent, give a capable model:

1. [`_shared-contract.md`](./_shared-contract.md)
2. the agent's own specification
3. [`../architecture.md`](../architecture.md) — for the ownership table
4. the actual inputs its `INPUTS` section names
5. its output schema, and the instruction to validate against it before
   presenting anything

Then check the output against the schema mechanically:

```bash
node automation/lib/validate.mjs automation/schemas/<name>.schema.json <output.json>
```

An output that does not validate is not a result. Re-prompt; do not hand-patch
the JSON, because the thing that failed validation was the reasoning, not the
formatting.
