# Sklarz Creative website — project memory

The website for **sklarzcreative.com**. A static site: no build step, no
framework, no npm. Served by **GitHub Pages, deploy-from-branch on `main`** —
so merging to `main` is deploying.

## Standing workflow — read this every session

@docs/ai-prompts/claude-code/WEBSITE_WORKFLOW.md

That file is the authority on the working sequence
(inspect → understand → back up → plan → implement → test → verify → deploy →
document), the brand and positioning rules, the backup and rollback
requirements, the QA checklist, and the prompt-capture rule. Follow it.

## Where things are

| Path | What it is |
| --- | --- |
| `index.html` | The homepage — reference implementation of the design system |
| `assets/css/sklarz.css` | The entire design system. One file, no preprocessor |
| `assets/js/hero.js` | The WebGL hero. No 3D library. **Homepage only** |
| `assets/js/motion.js` | The motion system. One observer, one rAF loop |
| `docs/` | Design and build documentation — start at `docs/README.md` |
| `docs/ai-prompts/claude-code/` | Prompt archive, standing workflow, prompt index |
| `_original-design/` | Complete pre-redesign site plus rollback instructions |
| `QA_POST_LAUNCH_2026-08-09.md` | The pre-redesign QA audit |

`docs/README.md` carries the load-bearing CSS rules and the change history.
Read it before touching the design system.

## Non-negotiables

- **Brand:** navy `#1A2F4B` and gold `#C9A84C` only, no new hues. No new typefaces.
- **Positioning:** a multidisciplinary **strategic brand, marketing and creative consultancy** — never a social-media, content-production or graphic-design execution service. Founder title is **Founder & Strategic Marketing Consultant**.
- **Truth:** never invent metrics, client logos, testimonials, credentials or publication dates.
- **Assets:** do not redraw or regenerate the logo, founder headshot, favicon or editorial SVGs.
- **Backups:** determine the exact production commit and preserve a rollback path before any material redesign or deployment.
- **Secrets:** this is a public repository. Nothing private goes into code, docs or commits.
- **Deployment:** review the diff first. Never deploy a documentation-only change unless deployment is separately requested.
