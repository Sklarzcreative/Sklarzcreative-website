# Sklarz Creative Direct Social Publisher

This subsystem replaces Make.com as the publishing execution layer while preserving the existing Google Sheet as the canonical content queue.

## Architecture

`Google Sheet (MAKE - Publish Queue) -> Python publisher -> direct platform APIs -> Sheet status bookkeeping`

Execution can happen in either of two free ways:

1. **GitHub Actions** on a 15-minute schedule. This repository is public, so standard GitHub-hosted Actions are suitable for the scheduler.
2. **An always-on spare laptop** running `scripts/run_loop.py`. This is the preferred option when tighter timing and full local control matter.

Do not run both live schedulers at the same time. Pick one primary runner to avoid duplicate-publish races.

## Safety model

A row is eligible only when all of these are true:

- `Approval Gate` = `APPROVED`
- `Publish Status` = `QUEUED` or `RETRY`
- `Scheduled DateTime ET` is due
- `Published URL` is blank
- the row is not older than `MAX_BACKLOG_MINUTES`

Additional controls:

- `PUBLISHER_ENABLED=false` by default
- `DRY_RUN=true` by default
- `MAX_POSTS_PER_RUN=1` by default
- overdue backlog is skipped instead of dumped automatically
- each attempted row is changed to `PROCESSING` before an API call
- success writes `PUBLISHED`, `Published URL`, and `Published At`
- provider failures write `ERROR` and the provider response into `Last Error`
- unsupported/unapproved routes are changed to `HOLD`

## Current direct routes

Implemented:

- LinkedIn Personal
- LinkedIn Company
- Facebook Page
- Instagram professional account, image and basic Reel URL route
- Threads
- Bluesky
- Mastodon

Scaffolded but intentionally held until direct API access is completed or revalidated:

- TikTok
- YouTube
- X
- Pinterest

TikTok Direct Post requires an approved app and `video.publish` authorization; unaudited clients are restricted by TikTok. YouTube needs its own Google OAuth credentials/refresh token. X may require a paid API tier. Pinterest should remain held until its route is deliberately revalidated.

## One-time Google Sheet connection

Use a Google Cloud service account for unattended execution.

1. In the existing Sklarz Creative Google Cloud project, enable the Google Sheets API.
2. Create a service account and JSON key.
3. Share the canonical spreadsheet with the service-account email as **Editor**.
4. Store the entire JSON key as `GOOGLE_SERVICE_ACCOUNT_JSON` in the runner environment. Never commit it.

Canonical spreadsheet ID:

`1DQ_2ThldqZjh_rqMSh8LkzZeUFZaCr5PtRZBgmbggbk`

Worksheet:

`MAKE - Publish Queue`

## Platform credentials

The tokens stored inside Make.com are Make-managed connections and should not be assumed reusable here. Direct publishing requires credentials owned by Sklarz Creative.

### LinkedIn

Required:

- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_PERSON_URN`
- `LINKEDIN_ORGANIZATION_URN`

The publisher uses LinkedIn's current Posts API. Keep `LINKEDIN_VERSION` configurable so version upgrades do not require code changes.

### Facebook / Instagram

Required:

- `META_PAGE_ACCESS_TOKEN`
- `META_PAGE_ID`
- `META_IG_USER_ID`

Instagram requires a professional account connected through Meta and a publicly reachable asset URL for media posts.

### Threads

Required:

- `THREADS_ACCESS_TOKEN`
- `THREADS_USER_ID`

### Bluesky

Required:

- `BLUESKY_HANDLE`
- `BLUESKY_APP_PASSWORD`

Use an app password, not the main account password.

### Mastodon

Required:

- `MASTODON_BASE_URL`
- `MASTODON_ACCESS_TOKEN`

## Local laptop setup

### Windows

```powershell
cd automation\social-publisher
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Start in dry-run mode first:

```powershell
python -m social_publisher.main --dry-run
```

After credential tests pass, set:

```text
PUBLISHER_ENABLED=true
DRY_RUN=false
```

Then run continuously:

```powershell
python scripts\run_loop.py
```

Use Windows Task Scheduler to start that command at boot, with the laptop configured not to sleep while plugged in.

### Linux

```bash
cd automation/social-publisher
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
python -m social_publisher.main --dry-run
```

For continuous operation:

```bash
python scripts/run_loop.py
```

A systemd service can be added after the controlled publishing test passes.

## GitHub Actions setup

The workflow is `.github/workflows/social-publisher.yml`.

Required repository **Secrets** match the environment-variable names above. After all credentials are installed and a controlled post succeeds, create repository variable:

`SOCIAL_PUBLISHER_ENABLED=true`

Until that variable is present, scheduled GitHub runs will not publish.

The manual workflow supports a safe dry run and an optional exact `Publish ID`.

## Controlled cutover from Make.com

1. Keep all rows on HOLD while credentials are configured.
2. Leave Make.com exhausted/paused; do not upgrade merely for this migration.
3. Configure Google Sheet credentials.
4. Configure one platform first, preferably LinkedIn Personal.
5. Queue one controlled test row 5-10 minutes ahead.
6. Run dry-run and confirm only that exact row is eligible.
7. Turn `PUBLISHER_ENABLED=true`, `DRY_RUN=false` on the chosen runner.
8. Confirm the social post exists and the Sheet changes to `PUBLISHED`.
9. Add Facebook, Threads, LinkedIn Company, Instagram, Bluesky, and Mastodon one at a time.
10. Only after route validation, restore the normal content calendar.

## Claude Code maintenance

Claude Code can work directly in this repository to add platforms, improve tests, diagnose API failures, and change queue logic. The scheduler itself is GitHub Actions or the always-on laptop; Claude Code does not need to remain open for scheduled publishing.
