# Pre-merge QA — v0.2.1

Scope: the instruction pack and account mappings only. No live scheduling, credential changes, task execution, direct-publisher activation or Make activation is part of this QA.

## Corrected finding

Eight supporting workflow documents used the discovery filename SKILL.md without skill frontmatter. Renamed them to GUIDE.md and updated references and manifest paths. The root SKILL.md is now the only discovery entry point, with its required name and description. This removes ambiguity for recursive skill scanners; it is not a claim that the previous layout failed on every client.

## Static checks

- All JSON parses; version and manifest entry point agree with the release.
- Exactly one SKILL.md entry point and eight referenced supporting GUIDE.md files.
- All referenced pack files exist, and no stale supporting SKILL.md paths remain.
- Exactly nine unique destinations: six Metricool routes and three Buffer channels with the supplied account IDs.
- Provider ownership and the three historical post IDs are unchanged by the QA correction; the historical IDs remain read/reconcile records, not creation instructions.
- Existing task ownership, dormant Python publisher, inactive Make, old HOLD preservation, required approvals, family-photo protection and excluded Cannamatrix scope are retained.
- Each final platform derivative is graded after adaptation and media selection. Quality scores do not grant approval.
- Unknown delivery outcomes require reconciliation before retry. Current plan allowance is required before adding jobs. The registry is explicitly described as instructions, not a deployed cross-provider lock.
- The pack contains Markdown/JSON only, without executable publishing scripts, environment files, credential values or OAuth callback URLs.
- The revised ZIP passes integrity checks and matches the installed pack.

## Verification limits

Codex runtime discovery could not be completed in this workspace: the app server exits while initializing its SQLite state under the read-only `/run/codex-environment/codex-home` directory. No model or scheduled task was started. Static packaging validation is complete, but actual skill discovery must still be checked in a working Codex client. The documented fallback is to explicitly read the root SKILL.md.

Claude Code discovery was not run. Interactive Buffer access does not establish unattended-task access. The task-launch 404 remains a separate issue; merging this pack does not repair it.

GitHub check/status results must be read for the final PR commit. An empty check list is not a passing CI run. No publishing end-to-end test is needed for this instruction-only change, and none was performed.

## Assessment

Suitable for review and merge as an instruction/configuration pack after verifying the final remote diff. Do not describe the merge as activation or proof of a fully unattended social system.
