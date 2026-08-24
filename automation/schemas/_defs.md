# Schemas

Every agent output that another process consumes is validated against a schema
here. Prose cannot be validated, and an unvalidatable output is an
unmonitorable one.

| Schema | Produced by | Notes |
| --- | --- | --- |
| `distribution-pack.schema.json` | Content Operations | one pack per source item; one primary job per derivative |
| `publish-queue-row.schema.json` | describes `MAKE - Publish Queue` | the contract Make reads and writes |
| `lead-record.schema.json` | the capture endpoint | `null` means unknown; it never means zero |
| `automation-health-report.schema.json` | Publishing Reliability + others | the nightly operational health report |
| `weekly-performance-report.schema.json` | Content Performance | a metric without a `data_source` is invalid, by construction |
| `case-study.schema.json` | Case Study Builder | `MISSING EVIDENCE` is a first-class value |
| `qa-report.schema.json` | the QA harness | `skipped` is its own state, never folded into `pass` |

Validate anything against any of them with no install step:

```bash
node automation/lib/validate.mjs automation/schemas/<name>.schema.json <file.json>
```

## The convention that runs through all of them

`null` means **unknown**. `0` means **measured zero**. Nothing in this
directory permits a number where the value was not measured — several schemas
enforce it structurally by requiring a `data_source` or an `availability`
alongside every figure, so a fabricated metric fails validation rather than
relying on an agent's restraint.
