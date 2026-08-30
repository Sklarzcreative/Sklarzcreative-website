# Architecture

```
route ─▶ context ─▶ prompt ─▶ candidates ─▶ OA review ─▶ repair ─┐
                                    ▲                            │
                                    └──────── (≤ cap) ───────────┘
                                                 │
                        vector overlay ─▶ composite ─▶ final OA
                                                 │
                                      PENDING_HUMAN_APPROVAL
```

Automation stops at `PENDING_HUMAN_APPROVAL`. Nothing else can approve a figure.

## Modules

| Module | Job |
|---|---|
| `workspace` | Privacy boundary. Fails closed without `CANNABIOLOGY_WORKSPACE`. |
| `canonical` | Read-only tracker load; canonical-ID validation. |
| `routing` | Six-route gate. Declarative rules, escalation-only. |
| `reconcile` | 51/52 count audit, duplicates, orphans, approved-without-artifact. |
| `context` | Deterministic manuscript extraction with source hash. |
| `prompts` | Immutable prompt versions with lineage. |
| `state` | Explicit state machine, atomic store, figure locks. |
| `verdict` | Deterministic verdict from findings. Code decides, not the model. |
| `repair` | Four-way taxonomy + preserve contract. |
| `vector` | SVG annotation layer and self-contained composite. |
| `package` | Client-facing review packet. |
| `doctor` | Environment, privacy and integrity checks. |

Judgment lives in two places only: prompt authoring and OA review. Everything
else is deterministic code, because a deterministic step that a model performs
is slower, costlier and unreproducible.

## Why state is separate from the tracker

The canonical tracker is authored by the project team and is authoritative
input. Automation never writes to it, so re-importing from Drive cannot be
clobbered by a pipeline run, and a pipeline run cannot silently rewrite the
author's source of truth.
