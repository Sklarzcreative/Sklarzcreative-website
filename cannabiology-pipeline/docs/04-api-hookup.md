# API hookup

**Status as authored (2026-08-27): no image-generation API was reachable from
the build environment** — no key was present and outbound calls to image
endpoints were blocked. The pipeline therefore ships with `provider: "dry-run"`
and has been exercised end to end in that mode. Nothing below has been run
against a live image API; these are the exact hookups required.

## What works today, with no key

- `queue`, `status` — full tracker and routing
- `prompt` — final production prompts
- `generate` in dry-run — writes the exact request payload that would be sent
- `review` in manual mode — emits the review brief
- `score`, `repair`, `package` — the whole review, repair and packaging loop

So the only missing piece is the call that returns pixels.

## Turning generation on

```bash
cp pipeline/config.example.json pipeline/config.json   # config.json is gitignored
export OPENAI_API_KEY=sk-...
```

```json
{ "image_generation": { "provider": "openai",
    "openai": { "model": "gpt-image-1", "size": "1536x1024", "quality": "high" } } }
```

Gemini is wired the same way (`provider: "gemini"`, `GEMINI_API_KEY`). Both
adapters use `urllib` only — no SDK to install. Verify with one figure before
running a batch:

```bash
python3 pipeline/cannabiology.py generate CH01-IMG-01
```

Egress to `api.openai.com` / `generativelanguage.googleapis.com` must be open.

## Turning automated OA review on

```json
{ "oa_review": { "provider": "anthropic",
    "anthropic": { "model": "claude-opus-4-5" } } }
```

with `ANTHROPIC_API_KEY` set. The adapter sends the image plus the review brief
and parses a strict JSON verdict. `score_to_verdict()` recomputes the verdict
from the returned scores, so a model that returns generous prose alongside weak
numbers still gets the arithmetic verdict.

Manual review remains the recommended default for the first batch: a human
should see the first comps of a new visual system.

## Cost control

Dry-run first. Each `generate` is one image per asset per round; the cycle cap
of 2 bounds a figure at 3 images. Batch 1 is 9 assets, so ≤ 27 images worst case,
typically ~12.
