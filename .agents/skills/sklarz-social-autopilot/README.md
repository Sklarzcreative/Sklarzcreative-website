# Sklarz Social Autopilot 0.2.1

Prepared October 1, 2026 from Cass's current instructions. Continues the existing system without adding a paid service or another scheduler. Start with `SKILL.md`; installation directions are in `setup/INSTALL.md`.

## Current ownership

| Destination | Authoritative publisher |
|---|---|
| Sklarz Facebook, Instagram, Threads, Pinterest | Metricool brand 6721661 |
| Sklarz TikTok, YouTube | Metricool, only with suitable approved media |
| Cassandra personal LinkedIn, Sklarzcreative X | Buffer |
| Cassandra Substack profile Notes | Buffer; professional and ordinary family Notes may share this profile |
| Full Curves Ahead / Our Family Story articles | Native Substack workflow |

The company LinkedIn page is not assigned an automatic route. Cannamatrix is out of scope. The existing Python subsystem `automation/social-publisher` in `Sklarzcreative/Sklarzcreative-website` is dormant; do not activate it. Make is legacy and must not be reactivated.

`config/publishing-routes.json` records one primary publisher per destination. It is an instruction/configuration contract, not deployed enforcement in Metricool, Buffer or the old Python code. Every caller must check it and the live queues before writing.

## Content and records

Reuse existing approved articles, the 90-Day Calendar, graphics, video and source assets. The canonical workbook remains `1DQ_2ThldqZjh_rqMSh8LkzZeUFZaCr5PtRZBgmbggbk`. Do not treat its legacy `MAKE - Publish Queue` as the execution queue for Metricool or Buffer. Preserve history and every old HOLD row. Determine each worksheet's current purpose before writing; do not migrate records or invent columns automatically.

Record run results in the existing Trello card: https://trello.com/c/33kgSmqq/19-autonomous-social-engine-sklarz-creative-our-family-story

Safe evergreen marketing is already authorized for autonomous scheduling. Sensitive and uncertain material needs Cass's review. See `policies/APPROVAL_RULES.md` for the complete boundary.

## What installation does

It makes consistent editorial and operational instructions available to Codex or Claude Code. Both can read the pack, but only the existing ChatGPT task owns the weekly recurrence. A manual session must inspect queues and coordinate before scheduling.

This archive contains no credentials, provider SDK, executable publisher or background service. Installation does not connect accounts, grant scheduled-task access, fix a task endpoint or prove any post published. Prior `Run now` attempts returned `404: Action not found` before invocation; that is separate from these skill instructions and does not establish a Buffer failure.

No Blotato, Make, paid API generation or other new subscription is required by this pack.
