# Sklarz Creative Direct Social Publisher

This subsystem replaces Make.com as the publishing execution layer while preserving the existing Google Sheet as the canonical content queue.

## Architecture

`Google Sheet (MAKE - Publish Queue) -> Python publisher -> direct platform APIs -> Sheet status bookkeeping`

Execution can happen in either of two free ways:

1. **GitHub Actions** on a 15-minute schedule.
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

The preferred local Windows configuration is **keyless service-account impersonation**. Do not weaken an organization policy that blocks long-lived service-account keys.

1. Enable Google Sheets API and IAM Service Account Credentials API in the existing Sklarz Creative Google Cloud project.
2. Create the `sklarz-social-publisher` service account.
3. Share the canonical spreadsheet with the service-account email as **Editor**.
4. Install Google Cloud CLI and authenticate the local Windows account.
5. Run `scripts/setup_google_keyless.ps1` to grant the signed-in account `Service Account Token Creator` on the publisher service account and create local Application Default Credentials using impersonation.

The Python queue adapter uses `GOOGLE_SERVICE_ACCOUNT_JSON` only when a usable JSON key is explicitly supplied. Otherwise it uses Application Default Credentials.

Canonical spreadsheet ID:

`1DQ_2ThldqZjh_rqMSh8LkzZeUFZaCr5PtRZBgmbggbk`

Worksheet:

`MAKE - Publish Queue`

## Platform credentials

The tokens stored inside Make.com are Make-managed connections and should not be assumed reusable here. Direct publishing requires credentials owned by Sklarz Creative.

### LinkedIn Personal

Required:

- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_PERSON_URN`

LinkedIn queue rows must also include a public HTTPS `Asset URL` pointing to a
JPG, PNG, or GIF. The publisher uploads that image through LinkedIn's Images API
and includes `Alt Text` from the queue when present. It will not fall back to a
text-only LinkedIn post when the asset is missing or invalid.

The LinkedIn Developer app must have **Share on LinkedIn** (`w_member_social`) and **Sign In with LinkedIn using OpenID Connect** (`openid`, `profile`, optionally `email`).

For the simplest controlled local setup, generate a member access token from LinkedIn Developer Portal's OAuth 2.0 tools with `openid profile email w_member_social`, then run:

```powershell
.\.venv\Scripts\python.exe .\scripts\setup_linkedin_personal.py
```

Paste the token only into the hidden local prompt. The helper verifies it against `https://api.linkedin.com/v2/userinfo`, derives `urn:li:person:{sub}`, and writes both values only to the ignored local `.env`. It also forces `PUBLISHER_ENABLED=false` and `DRY_RUN=true` during credential setup.

LinkedIn member access tokens are time-limited, so plan to reauthorize before expiry. Programmatic refresh tokens are not generally available to ordinary self-service Share on LinkedIn apps.

### LinkedIn Company

Required:

- `LINKEDIN_ORGANIZATION_URN`
- an access token with the organization permissions required by LinkedIn

Company-page publishing is a separate access path and should remain held until organization permissions are confirmed.

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

From the repository root, use the tested bootstrap:

```powershell
.\automation\social-publisher\START_HERE_WINDOWS.bat
```

Then configure Google keyless authentication and platform credentials one route at a time. Start in dry-run mode:

```powershell
cd automation\social-publisher
.\.venv\Scripts\python.exe -m social_publisher.main --dry-run
```

After one controlled platform test passes, set:

```text
PUBLISHER_ENABLED=true
DRY_RUN=false
```

Then run continuously:

```powershell
.\.venv\Scripts\python.exe scripts\run_loop.py
```

Use Windows Task Scheduler to start that command at boot, with the laptop configured not to sleep while plugged in.

### Linux

```bash
cd automation/social-publisher
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m social_publisher.main --dry-run
```

For continuous operation:

```bash
python scripts/run_loop.py
```

A systemd service can be added after the controlled publishing test passes.

## GitHub Actions setup

The workflow is `.github/workflows/social-publisher.yml`.

Do not enable GitHub-hosted publishing while the local laptop is the live primary runner. If GitHub Actions later becomes primary, store required credentials as repository Secrets and disable the laptop scheduler first.
