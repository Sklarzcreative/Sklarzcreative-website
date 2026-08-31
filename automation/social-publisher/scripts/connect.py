"""Verify social credentials and auto-discover the IDs the publisher needs.

Read-only by design. This script never posts, never writes to the Google Sheet,
and never modifies .env. Run it as often as you like.

    python scripts/connect.py            # check every platform
    python scripts/connect.py bluesky    # check one platform

For each platform it answers three questions:

  1. Is the token present?
  2. Does the token actually work against the live API?
  3. What are the account IDs/URNs that .env still needs?

Point 3 is the time-saver. Values like LINKEDIN_PERSON_URN and META_IG_USER_ID
are not shown anywhere obvious in the platforms' own UIs, but every one of them
can be read back from the token itself. Paste the token, run this, copy the
lines it prints into .env.
"""

from __future__ import annotations

import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

TIMEOUT = 30

OK = "OK"
MISSING = "MISSING"
BROKEN = "BROKEN"


class Result:
    """Outcome for one platform: a status, human notes, and .env lines to copy."""

    def __init__(self, platform: str):
        self.platform = platform
        self.status = MISSING
        self.notes: list[str] = []
        self.env_lines: list[str] = []

    def note(self, text: str) -> None:
        self.notes.append(text)

    def suggest(self, key: str, value: str) -> None:
        """Record a discovered value, but only if .env does not already match."""
        if os.getenv(key, "").strip() != value:
            self.env_lines.append(f"{key}={value}")


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def _describe_http(exc: Exception) -> str:
    return f"{type(exc).__name__}: {exc}"


def _api_error(response: requests.Response) -> str:
    """Pull the human-readable message out of a platform error body."""
    try:
        payload = response.json()
    except ValueError:
        return f"HTTP {response.status_code}: {response.text[:200]}"

    for path in (("error", "message"), ("error_description",), ("message",), ("error",)):
        node = payload
        for key in path:
            if not isinstance(node, dict) or key not in node:
                node = None
                break
            node = node[key]
        if isinstance(node, str) and node:
            return f"HTTP {response.status_code}: {node}"
    return f"HTTP {response.status_code}: {str(payload)[:200]}"


def check_bluesky() -> Result:
    result = Result("Bluesky")
    handle = _env("BLUESKY_HANDLE").lstrip("@")
    password = _env("BLUESKY_APP_PASSWORD")
    pds = os.getenv("BLUESKY_PDS", "https://bsky.social").rstrip("/")

    if not handle or not password:
        result.note("Set BLUESKY_HANDLE and BLUESKY_APP_PASSWORD.")
        result.note("App password: bsky.app -> Settings -> Privacy and security")
        result.note("-> App passwords -> Add App Password. Takes about two minutes.")
        return result

    if password.count("-") != 3:
        result.note("That does not look like an app password (format: xxxx-xxxx-xxxx-xxxx).")
        result.note("Use an app password, never your real account password.")

    try:
        response = requests.post(
            f"{pds}/xrpc/com.atproto.server.createSession",
            json={"identifier": handle, "password": password},
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        result.status = BROKEN
        result.note(f"Could not reach {pds}: {_describe_http(exc)}")
        return result

    if response.status_code != 200:
        result.status = BROKEN
        result.note(_api_error(response))
        result.note("Most common cause: using the account password instead of an app password.")
        return result

    data = response.json()
    result.status = OK
    result.note(f"Authenticated as {data.get('handle', handle)} ({data.get('did', 'no did')}).")
    return result


def check_mastodon() -> Result:
    result = Result("Mastodon")
    base = _env("MASTODON_BASE_URL").rstrip("/")
    token = _env("MASTODON_ACCESS_TOKEN")

    if not base or not token:
        result.note("Set MASTODON_BASE_URL (e.g. https://mastodon.social) and MASTODON_ACCESS_TOKEN.")
        result.note("Token: your instance -> Preferences -> Development -> New application.")
        result.note("Scopes needed: write:statuses. No review process, issued instantly.")
        return result

    try:
        response = requests.get(
            f"{base}/api/v1/accounts/verify_credentials",
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        result.status = BROKEN
        result.note(f"Could not reach {base}: {_describe_http(exc)}")
        return result

    if response.status_code != 200:
        result.status = BROKEN
        result.note(_api_error(response))
        return result

    account = response.json()
    result.status = OK
    result.note(f"Authenticated as @{account.get('username', '?')} on {base}.")
    return result


def check_linkedin() -> Result:
    result = Result("LinkedIn")
    token = _env("LINKEDIN_ACCESS_TOKEN")

    if not token:
        result.note("Set LINKEDIN_ACCESS_TOKEN.")
        result.note("This is the slowest one to obtain. See the notes at the end of this run.")
        return result

    try:
        response = requests.get(
            "https://api.linkedin.com/v2/userinfo",
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        result.status = BROKEN
        result.note(f"Could not reach LinkedIn: {_describe_http(exc)}")
        return result

    if response.status_code == 401:
        result.status = BROKEN
        result.note(_api_error(response))
        result.note("The token is expired or invalid. LinkedIn tokens last 60 days.")
        return result

    if response.status_code != 200:
        result.status = BROKEN
        result.note(_api_error(response))
        result.note("If this says the scope is missing, the token lacks 'openid profile'.")
        return result

    profile = response.json()
    subject = profile.get("sub", "")
    result.status = OK
    result.note(f"Authenticated as {profile.get('name', 'unknown')}.")

    if subject:
        result.suggest("LINKEDIN_PERSON_URN", f"urn:li:person:{subject}")

    # Posting uses w_member_social, which /v2/userinfo does not exercise. Warn
    # rather than test, because the only real test is a live post.
    if not _env("LINKEDIN_PERSON_URN") and not subject:
        result.note("Could not read your person URN from this token.")
    result.note("Note: identity works. Posting also needs the 'w_member_social' scope,")
    result.note("which can only be confirmed by the controlled test post.")

    org_urn = _env("LINKEDIN_ORGANIZATION_URN")
    if not org_urn:
        result.note("LINKEDIN_ORGANIZATION_URN is unset - only needed for LinkedIn Company posts.")

    return result


def check_meta() -> Result:
    result = Result("Facebook / Instagram")
    token = _env("META_PAGE_ACCESS_TOKEN")
    version = os.getenv("META_GRAPH_VERSION", "v24.0")

    if not token:
        result.note("Set META_PAGE_ACCESS_TOKEN.")
        result.note("Get it from developers.facebook.com -> your app -> Graph API Explorer.")
        result.note("Permissions: pages_manage_posts, pages_read_engagement,")
        result.note("instagram_basic, instagram_content_publish.")
        return result

    try:
        accounts = requests.get(
            f"https://graph.facebook.com/{version}/me/accounts",
            params={"fields": "id,name,access_token", "access_token": token},
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        result.status = BROKEN
        result.note(f"Could not reach Meta Graph API: {_describe_http(exc)}")
        return result

    if accounts.status_code != 200:
        result.status = BROKEN
        result.note(_api_error(accounts))
        result.note("A short-lived token expires in about an hour. Exchange it for a")
        result.note("long-lived Page token, or this will keep breaking.")
        return result

    pages = accounts.json().get("data", [])
    if not pages:
        result.status = BROKEN
        result.note("Token works, but it manages no Pages.")
        result.note("This usually means it is a User token without Page permissions granted.")
        return result

    result.status = OK
    result.note(f"Token manages {len(pages)} Page(s):")
    for page in pages:
        result.note(f"  - {page.get('name', '?')} (id {page.get('id', '?')})")

    page = pages[0]
    page_id = page.get("id", "")
    if len(pages) > 1:
        result.note("More than one Page found; suggesting the first. Change it if that is wrong.")

    if page_id:
        result.suggest("META_PAGE_ID", page_id)
        # The Page-scoped token is the correct one for publishing, not the user token.
        page_token = page.get("access_token", "")
        if page_token and page_token != token:
            result.note("Your META_PAGE_ACCESS_TOKEN is a USER token, not a PAGE token.")
            result.note("The Page-scoped token is what the publisher should use.")
            result.suggest("META_PAGE_ACCESS_TOKEN", page_token)

        # Instagram business account hangs off the Page.
        try:
            ig = requests.get(
                f"https://graph.facebook.com/{version}/{page_id}",
                params={"fields": "instagram_business_account", "access_token": token},
                timeout=TIMEOUT,
            )
            if ig.status_code == 200:
                ig_account = ig.json().get("instagram_business_account") or {}
                ig_id = ig_account.get("id", "")
                if ig_id:
                    result.suggest("META_IG_USER_ID", ig_id)
                    result.note(f"Instagram business account found (id {ig_id}).")
                else:
                    result.note("No Instagram business account linked to this Page.")
                    result.note("Instagram posting needs a Professional account linked to the Page.")
            else:
                result.note(f"Could not read Instagram link: {_api_error(ig)}")
        except requests.RequestException as exc:
            result.note(f"Could not read Instagram link: {_describe_http(exc)}")

    _report_meta_expiry(result, token, version)
    return result


def _report_meta_expiry(result: Result, token: str, version: str) -> None:
    """Meta tokens silently expire; surface the expiry so it is not a surprise."""
    try:
        debug = requests.get(
            f"https://graph.facebook.com/{version}/debug_token",
            params={"input_token": token, "access_token": token},
            timeout=TIMEOUT,
        )
    except requests.RequestException:
        return
    if debug.status_code != 200:
        return
    data = debug.json().get("data", {})
    expires_at = data.get("expires_at")
    if expires_at == 0:
        result.note("Token does not expire. Good - that is what unattended publishing needs.")
    elif isinstance(expires_at, int) and expires_at > 0:
        from datetime import datetime, timezone as _tz

        when = datetime.fromtimestamp(expires_at, tz=_tz.utc)
        result.note(f"WARNING: this token expires {when.isoformat()}.")
        result.note("Exchange it for a long-lived Page token before going unattended.")


def check_threads() -> Result:
    result = Result("Threads")
    token = _env("THREADS_ACCESS_TOKEN")
    base = os.getenv("THREADS_API_BASE", "https://graph.threads.net/v1.0").rstrip("/")

    if not token:
        result.note("Set THREADS_ACCESS_TOKEN.")
        result.note("Threads uses its own app and token, separate from Facebook.")
        result.note("See developers.facebook.com -> Threads API.")
        return result

    try:
        response = requests.get(
            f"{base}/me",
            params={"fields": "id,username", "access_token": token},
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        result.status = BROKEN
        result.note(f"Could not reach Threads API: {_describe_http(exc)}")
        return result

    if response.status_code != 200:
        result.status = BROKEN
        result.note(_api_error(response))
        result.note("A Facebook/Instagram token will not work here; Threads needs its own.")
        return result

    data = response.json()
    result.status = OK
    result.note(f"Authenticated as @{data.get('username', '?')}.")
    user_id = data.get("id", "")
    if user_id:
        result.suggest("THREADS_USER_ID", user_id)
    return result


def check_google_sheet() -> Result:
    """The queue itself - nothing publishes without this one."""
    result = Result("Google Sheet (queue)")
    raw = _env("GOOGLE_SERVICE_ACCOUNT_JSON")

    if not raw or raw == "{}":
        result.note("Set GOOGLE_SERVICE_ACCOUNT_JSON to the full service-account key JSON.")
        result.note("This is the one credential the publisher cannot run without.")
        return result

    # Import lazily so a missing key does not require the Google libraries.
    from social_publisher.core import ConfigurationError, GoogleSheetQueue, Settings

    try:
        queue = GoogleSheetQueue(Settings.from_env())
    except ConfigurationError as exc:
        result.status = BROKEN
        result.note(str(exc))
        return result
    except Exception as exc:  # noqa: BLE001 - report any provider failure verbatim
        result.status = BROKEN
        message = _describe_http(exc)
        result.note(message)
        if "SpreadsheetNotFound" in message or "PermissionError" in message or "403" in message:
            result.note("The key is valid but cannot open the Sheet.")
            result.note("Share the Sheet with the service-account email as Editor.")
        return result

    result.status = OK
    result.note(f"Opened worksheet '{queue.settings.worksheet_name}'.")
    result.note(f"Columns found: {len(queue.headers)}.")
    return result


CHECKS = {
    "sheet": check_google_sheet,
    "linkedin": check_linkedin,
    "facebook": check_meta,
    "instagram": check_meta,
    "meta": check_meta,
    "threads": check_threads,
    "bluesky": check_bluesky,
    "mastodon": check_mastodon,
}

# Order follows the route-expansion order in GitHub issue #9.
DEFAULT_ORDER = ["sheet", "linkedin", "meta", "threads", "bluesky", "mastodon"]

SYMBOL = {OK: "[ OK ]", MISSING: "[ -- ]", BROKEN: "[FAIL]"}


def main(argv: list[str]) -> int:
    requested = [a.lower() for a in argv[1:]] or DEFAULT_ORDER

    unknown = [name for name in requested if name not in CHECKS]
    if unknown:
        print(f"Unknown platform(s): {', '.join(unknown)}")
        print(f"Choose from: {', '.join(sorted(CHECKS))}")
        return 2

    # Deduplicate while preserving order (meta/facebook/instagram share a check).
    seen: set = set()
    checks = []
    for name in requested:
        fn = CHECKS[name]
        if fn not in seen:
            seen.add(fn)
            checks.append(fn)

    print()
    print("Sklarz Creative publisher - credential check (read-only, posts nothing)")
    print("=" * 72)

    results = []
    for check in checks:
        result = check()
        results.append(result)
        print(f"\n{SYMBOL[result.status]} {result.platform}")
        for note in result.notes:
            print(f"       {note}")

    pending = [line for r in results for line in r.env_lines]
    if pending:
        print("\n" + "=" * 72)
        print("Discovered values - paste these into .env:\n")
        for line in pending:
            print(f"  {line}")

    print("\n" + "=" * 72)
    ready = [r.platform for r in results if r.status == OK]
    broken = [r.platform for r in results if r.status == BROKEN]
    todo = [r.platform for r in results if r.status == MISSING]
    print(f"Working:     {', '.join(ready) if ready else 'none yet'}")
    print(f"Needs a fix: {', '.join(broken) if broken else 'none'}")
    print(f"Not set up:  {', '.join(todo) if todo else 'none'}")
    print()
    print("Nothing was published. PUBLISHER_ENABLED and DRY_RUN were not changed.")
    print()
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
