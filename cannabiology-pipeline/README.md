# Cannabiology figure production pipeline

A six-agent pipeline that takes a manuscript figure from queued to
author-approved: rank → prompt → generate → review → repair → package.

Built 2026-08-27 on top of existing work. It does not restart the project —
it recovers the canonical tracker, prompt library, QA rules and decision
register already produced in Drive and drives them.

## Important: this repository is public

`sklarzcreative.com` is served from this repo. The Cannabiology manuscript,
figure prompts, tracker data, generated artwork and review packets are
unpublished client IP and are **not** committed. They live in `client-data/`,
which is gitignored, and canonically in Google Drive.

What is committed here is the *method*: the tool, the rubric, the workflow.

## Quickstart

```bash
cd cannabiology-pipeline/pipeline
python3 cannabiology.py queue --route GENERATE   # what to produce, in order
python3 cannabiology.py run --batch 1            # generate → review → package
python3 cannabiology.py status --batch 1         # live state
```

Client data must be present. Re-import from Drive if `client-data/` is empty —
see [`docs/04-api-hookup.md`](docs/04-api-hookup.md).

Python 3, standard library only. No dependencies to install.

## Honest status

**No image-generation API is reachable from the environment this was built in.**
No key was present and outbound calls to image endpoints were blocked. The
pipeline ships in `dry-run` mode, where `generate` writes the exact request
payload it would send instead of returning pixels.

Everything except the call that returns pixels runs today: ranking, routing,
prompt assembly, the review rubric and verdict engine, the repair decision
logic, the cycle cap, and packet generation. All of it has been exercised end
to end. Adding a key in `config.json` turns generation on with no code change.

## The routing rule

The tracker's *Current Status* column encodes **how** each figure must be made.
Only `GENERATE` figures belong in this pipeline:

| Route | Count | Produced by |
|-------|-------|-------------|
| `GENERATE` | 13 | this pipeline |
| `VECTOR-BUILD` | 6 | Illustrator / Canva, by hand |
| `DATA-DRIVEN` | 3 | only from a verified dataset |
| `HOLD` | 6 | blocked on an open author decision |
| unrouted (Ch 5–8) | 23 | route not yet assigned |

Sending a `VECTOR-BUILD` figure to an image model yields plausible-looking
chemistry that is wrong. The queue enforces this separation.

## Docs

- [Production workflow](docs/01-production-workflow.md)
- [OA review rubric](docs/02-oa-review-rubric.md)
- [Agent roles and handoffs](docs/03-agent-roles.md)
- [API hookup](docs/04-api-hookup.md)
- [Folder structure and file naming](docs/05-file-naming.md)
