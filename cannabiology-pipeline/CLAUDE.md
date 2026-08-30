# Cannabiology pipeline — permanent instructions

These rules bind any agent or contributor working in this directory.

## Identity
- Canonical figure IDs are `CHnn-IMG-nn` and are **embedded in the manuscript,
  the QA register, the decision register and the layout specs**. Never rename
  them. Never introduce a replacement scheme such as `CBIO_C01_F001`.
- Sub-assets extend the parent ID: `CH01-IMG-02` ships as `CH01-IMG-02A` and
  `CH01-IMG-02B`. This is why 51 canonical figures require 52 production assets.
- Internal UUIDs may identify runs, candidates or log rows. They never replace a
  canonical ID.

## Privacy
- **This repository is public.** It serves sklarzcreative.com.
- All client-derived material lives in `$CANNABIOLOGY_WORKSPACE`, an absolute
  path outside the repo. Without it the pipeline fails closed.
- Never commit manuscript text, context extracts, tracker exports, prompts,
  generated images, OA reports or review packets.
- `.gitignore` is defence in depth, never the primary boundary.

## Scientific conservatism
- The **canonical tracker is the source of truth**. Never invent manuscript
  facts, values, structures, gene names, pathways or regulatory status.
- The **routing gate runs before generation** and cannot be bypassed. `--force`
  never opens it. Never downgrade `VECTOR_BUILD`, `DATA_DRIVEN`, `HUMAN_BUILD`
  or `HOLD` to a generative route because a model could make something that
  looks plausible.
- `DATA_DRIVEN` figures may never have their substantive data generated. They
  require a verified source, a provenance record and an `as_of` date.
- `VECTOR_BUILD` figures require deterministic construction. An image model may
  never supply the scientific structure.
- Scientific labels are **vector text**, applied after generation. Generated
  base art carries no authoritative text.

## Review and approval
- OA means an **actual OpenAI API review**. An agent's own opinion is never an OA
  review, and a dry-run review is synthetic and must be labelled as such.
- The model supplies findings; **code computes the verdict**. A model may never
  declare a figure approved while blocking findings remain.
- Fix labels without regenerating correct artwork. Preserve everything listed in
  the review's `preserve` array; a repair that fixes one error and damages two
  accepted elements is not an improvement.
- Stop at the generative repair cap. `VECTOR_EDIT` rounds do not count.
- **Never mark a figure `HUMAN_APPROVED` without explicit human approval.**
  Silence is not approval. The terminal automated state is
  `PENDING_HUMAN_APPROVAL`.

## Operations
- The canonical tracker is **read-only** to automation. Pipeline state lives
  separately and is reconciled back only by an explicit human-run operation.
- Never delete prior generations, prompts or OA reports. Every revision is a new
  version.
- Batch independent figures; serialise stages within a figure. Hold a
  figure-level lock for any write.
- Keep human review packets client-facing: no prompts, no OA chain, no repair
  logs, no API data.
- Never expose API secrets in code, config, logs or packets.
