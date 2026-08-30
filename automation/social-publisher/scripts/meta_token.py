"""Turn a short-lived Facebook token into a permanent Page token.

The Graph API Explorer gives you a SHORT-LIVED USER token. It expires in about
an hour, and it is the wrong type: publishing to a Page needs a PAGE token.
Nothing in Meta's UI does this conversion, which is where most Facebook setups
stall. This script does all three steps:

    short-lived user token
      -> long-lived user token          (60 days)
      -> Page token derived from it     (does not expire)

A Page token derived from a LONG-LIVED user token has no expiry, which is what
unattended publishing needs. Derive it from a short-lived token instead and it
dies within the hour - the usual cause of "it worked yesterday".

Usage:

    python scripts/meta_token.py

Reads META_APP_ID and META_APP_SECRET from .env, then prompts for the
short-lived token. The token is entered hidden and is never written to disk,
logged, or echoed - this script only prints the values you should paste into
.env yourself.
"""

from __future__ import annotations

import os
import sys
from getpass import getpass

import requests
from dotenv import load_dotenv

load_dotenv()

TIMEOUT = 30
GRAPH_VERSION = os.getenv("META_GRAPH_VERSION", "v24.0")
GRAPH = f"https://graph.facebook.com/{GRAPH_VERSION}"


class MetaError(RuntimeError):
    pass


def _get(path: str, params: dict) -> dict:
    try:
        response = requests.get(f"{GRAPH}{path}", params=params, timeout=TIMEOUT)
    except requests.RequestException as exc:
        raise MetaError(f"Could not reach the Graph API: {exc}") from exc

    try:
        payload = response.json()
    except ValueError:
        raise MetaError(f"HTTP {response.status_code}: {response.text[:300]}") from None

    if response.status_code != 200 or "error" in payload:
        raise MetaError(explain_error(payload, response.status_code))
    return payload


def explain_error(payload: dict, status_code: int) -> str:
    """Translate a Graph API error into something actionable."""
    error = payload.get("error", {}) if isinstance(payload, dict) else {}
    message = error.get("message", f"HTTP {status_code}")
    code = error.get("code")

    hints = {
        190: "The token is expired or invalid. Generate a fresh one in the Graph API Explorer.",
        102: "The session is invalid. Generate a fresh token.",
        1: "Often a wrong App Secret. Check it against Settings -> Basic in your app.",
        200: (
            "The token lacks a required permission. In the Graph API Explorer, add: "
            "pages_show_list, pages_manage_posts, pages_read_engagement."
        ),
    }
    hint = hints.get(code)
    detail = f"{message} (code {code})" if code else message
    return f"{detail}\n       {hint}" if hint else detail


def exchange_for_long_lived_user_token(app_id: str, app_secret: str, short_token: str) -> str:
    payload = _get(
        "/oauth/access_token",
        {
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_token,
        },
    )
    token = payload.get("access_token", "")
    if not token:
        raise MetaError("Exchange succeeded but returned no access_token.")
    return token


def fetch_pages(user_token: str) -> list[dict]:
    payload = _get("/me/accounts", {"fields": "id,name,access_token", "access_token": user_token})
    return payload.get("data", [])


def fetch_instagram_id(page_id: str, token: str) -> str:
    try:
        payload = _get(
            f"/{page_id}", {"fields": "instagram_business_account", "access_token": token}
        )
    except MetaError:
        return ""
    return (payload.get("instagram_business_account") or {}).get("id", "")


def token_never_expires(token: str) -> bool | None:
    """True if permanent, False if it expires, None if it could not be checked."""
    try:
        payload = _get("/debug_token", {"input_token": token, "access_token": token})
    except MetaError:
        return None
    expires_at = payload.get("data", {}).get("expires_at")
    if expires_at == 0:
        return True
    if isinstance(expires_at, int) and expires_at > 0:
        return False
    return None


def choose_page(pages: list[dict]) -> dict:
    if len(pages) == 1:
        return pages[0]
    print("\nYou administer several Pages:\n")
    for index, page in enumerate(pages, start=1):
        print(f"  {index}. {page.get('name', '?')} (id {page.get('id', '?')})")
    while True:
        choice = input("\nWhich Page should the publisher post to? Enter a number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(pages):
            return pages[int(choice) - 1]
        print("Not a valid choice.")


def main() -> int:
    app_id = os.getenv("META_APP_ID", "").strip()
    app_secret = os.getenv("META_APP_SECRET", "").strip()

    print()
    print("Meta long-lived Page token helper")
    print("=" * 72)

    if not app_id or not app_secret:
        print("\nMissing META_APP_ID and/or META_APP_SECRET in .env.")
        print("\nFind them at developers.facebook.com -> your app -> Settings -> Basic.")
        print("Add both to .env, then run this again. They are only used to sign the")
        print("token exchange; the publisher itself never needs them.")
        return 2

    print("\nIn the Graph API Explorer (developers.facebook.com/tools/explorer):")
    print("  1. Select your app.")
    print("  2. Add permissions: pages_show_list, pages_manage_posts,")
    print("     pages_read_engagement, and for Instagram also instagram_basic")
    print("     and instagram_content_publish.")
    print("  3. Click 'Generate Access Token' and approve the dialog.")
    print("  4. Copy the token and paste it below.")
    print("\nThe paste is hidden and is never saved to disk.\n")

    short_token = getpass("Short-lived token: ").strip()
    if not short_token:
        print("\nNo token entered. Nothing to do.")
        return 2

    try:
        print("\nExchanging for a long-lived user token...")
        long_user_token = exchange_for_long_lived_user_token(app_id, app_secret, short_token)
        print("  Done.")

        print("Looking up the Pages this token administers...")
        pages = fetch_pages(long_user_token)
    except MetaError as exc:
        print(f"\nFAILED: {exc}")
        return 1

    if not pages:
        print("\nFAILED: the token works, but administers no Pages.")
        print("       Add the pages_show_list permission and regenerate the token.")
        print("       If you still see none, confirm you are a Page admin.")
        return 1

    page = choose_page(pages)
    page_id = page.get("id", "")
    page_token = page.get("access_token", "")
    page_name = page.get("name", "?")

    if not page_token:
        print(f"\nFAILED: no Page token returned for {page_name}.")
        print("       This usually means the pages_manage_posts permission was not granted.")
        return 1

    print(f"\nSelected Page: {page_name} (id {page_id})")

    permanent = token_never_expires(page_token)
    if permanent is True:
        print("Verified: this Page token does not expire.")
    elif permanent is False:
        print("WARNING: this Page token still has an expiry. The user token was")
        print("         probably not long-lived. Re-run with a freshly generated token.")
    else:
        print("Note: could not verify the expiry. Check it with scripts/connect.py.")

    ig_id = fetch_instagram_id(page_id, page_token)

    print("\n" + "=" * 72)
    print("Paste these into .env:\n")
    print(f"  META_PAGE_ID={page_id}")
    print(f"  META_PAGE_ACCESS_TOKEN={page_token}")
    if ig_id:
        print(f"  META_IG_USER_ID={ig_id}")
    print()
    if not ig_id:
        print("No Instagram business account is linked to this Page, so Instagram")
        print("posting stays unavailable. Facebook posting is unaffected.")
        print()
    print("Then verify with:  python scripts/connect.py facebook")
    print("Keep PUBLISHER_ENABLED=false and DRY_RUN=true until the controlled test.")
    print()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nCancelled. Nothing was changed.")
        sys.exit(130)
