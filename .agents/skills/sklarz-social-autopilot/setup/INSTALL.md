# Install and use

## Recommendation for Cass

Use Codex as the engineering home because the existing Buffer MCP authentication was verified in that workspace. Upload this ZIP in the same Codex workspace/thread. It can unpack and read the root SKILL.md immediately. Uploading to a regular chat supplies reference files; it does not automatically install a persistent skill or grant scheduled-task access.

Claude Code can use the same pack for editing, drafting and engineering. A Claude subscription does not transfer Codex OAuth or connector access. Neither installation creates a second weekly autopilot. Keep the existing ChatGPT task as the recurrence owner.

## Persistent project installation

First inspect AGENTS.md/project instructions and the current repository checkout. Reuse the intended existing checkout; do not overwrite unrelated local changes. Extract the ZIP, then copy its complete `sklarz-social-autopilot` folder, including all policies/config/brands/subskills:

- Codex project skill: `<repo>/.agents/skills/sklarz-social-autopilot/`
- Claude Code project skill: `<repo>/.claude/skills/sklarz-social-autopilot/`

The root SKILL.md has name/description frontmatter for discovery. Supporting workflows use GUIDE.md filenames, so only the root SKILL.md is a discovery entry point. They are referenced instructions, not separately installed scheduled agents. Check the installed client's skill discovery behavior; restart/reload if needed. If discovery is unavailable, explicitly instruct the agent to read the root file. Do not claim installation merely because a ZIP was attached.

Keep one canonical copy/version in the existing repository. If using both clients, point their project instructions at that copy or synchronize a reviewable copy of the same version into the second client's skill directory. Do not maintain divergent policies. Do not commit credential stores, .env files, OAuth callbacks or local runtime receipts containing secrets.

## Copy/paste handoff after attaching the ZIP

“Use this v0.2.1 Sklarz Social Autopilot pack. Read its root SKILL.md and install the complete folder in this client's project skill directory in the existing Sklarzcreative-website checkout, preserving local changes. Confirm the installed path and whether skill discovery works. Preserve the existing task 6abbf3fa6f5481919b69ed1ac1cbeaa6. Do not create another recurrence, activate Python/Make, change routes or schedule posts merely to test installation. Verify required provider access with harmless reads in this environment; report unavailable access without requesting secret values. Do not assume interactive access proves unattended execution.”

## Validation and authentication

Validate JSON, route uniqueness and referenced files before using. Confirm the exact Metricool brand and Buffer organization/channels via existing authenticated tools. Use native OAuth connection flows only if access is actually missing; do not request keys in chat. Do not copy Codex credentials into Claude.

An installation check is read-only. It does not alter queues, release HOLDs or authorize a live publisher test. For an actual scheduling request, follow the runbook and standing authorization.

## Weekly task and the launch error

This pack cannot repair `404: Action not found` returned before the task run-now action executes. Diagnose the task service separately. A successful launch still needs an actual execution result showing its provider read. Until then unattended Buffer access is unverified. Never add another recurring service to conceal that missing connection.

Installing in Codex or Claude Code does not attach these files to an existing ChatGPT task. Its saved prompt already has current operating safeguards. Only update that existing task when needed and through supported tools; no second weekly task. All scheduled-task access must be verified in that task's runtime.
