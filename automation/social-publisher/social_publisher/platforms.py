from __future__ import annotations

import os
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

from .core import ConfigurationError, QueueRow, UnsupportedPlatformError

TIMEOUT = 45


def publish(row: QueueRow) -> str:
    platform = row.platform.strip().lower()
    if platform == "linkedin personal":
        return publish_linkedin(row, required_env("LINKEDIN_PERSON_URN"))
    if platform == "linkedin company":
        return publish_linkedin(row, required_env("LINKEDIN_ORGANIZATION_URN"))
    if platform == "facebook":
        return publish_facebook(row)
    if platform == "instagram":
        return publish_instagram(row)
    if platform == "threads":
        return publish_threads(row)
    if platform == "bluesky":
        return publish_bluesky(row)
    if platform == "mastodon":
        return publish_mastodon(row)
    if platform in {"youtube", "tiktok", "x", "pinterest"}:
        raise UnsupportedPlatformError(
            f"{row.platform} route is scaffolded but intentionally not enabled until its direct API credentials/approval are completed."
        )
    raise UnsupportedPlatformError(f"No publisher route configured for {row.platform!r}")


def publish_linkedin(row: QueueRow, author_urn: str) -> str:
    token = required_env("LINKEDIN_ACCESS_TOKEN")
    version = os.getenv("LINKEDIN_VERSION", "202608")
    response = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers={
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": version,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        },
        json={
            "author": author_urn,
            "commentary": row.copy,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        },
        timeout=TIMEOUT,
    )
    ensure_ok(response, {200, 201})
    post_id = response.headers.get("x-restli-id") or _json_value(response, "id")
    if post_id:
        return f"https://www.linkedin.com/feed/update/{post_id}"
    return "linkedin:published"


def publish_facebook(row: QueueRow) -> str:
    page_id = required_env("META_PAGE_ID")
    token = required_env("META_PAGE_ACCESS_TOKEN")
    version = os.getenv("META_GRAPH_VERSION", "v24.0")
    base = f"https://graph.facebook.com/{version}/{page_id}"

    if row.asset_url and _looks_like_image(row.asset_url):
        response = requests.post(
            f"{base}/photos",
            data={"url": row.asset_url, "caption": row.copy, "access_token": token},
            timeout=TIMEOUT,
        )
    else:
        payload = {"message": row.copy, "access_token": token}
        if row.canonical_url:
            payload["link"] = row.canonical_url
        response = requests.post(f"{base}/feed", data=payload, timeout=TIMEOUT)

    ensure_ok(response, {200})
    post_id = _json_value(response, "post_id") or _json_value(response, "id")
    return f"https://www.facebook.com/{post_id}" if post_id else "facebook:published"


def publish_instagram(row: QueueRow) -> str:
    user_id = required_env("META_IG_USER_ID")
    token = required_env("META_PAGE_ACCESS_TOKEN")
    version = os.getenv("META_GRAPH_VERSION", "v24.0")
    if not row.asset_url:
        raise ConfigurationError("Instagram publishing requires Asset URL")

    create_payload: dict[str, str] = {"caption": row.copy, "access_token": token}
    if _looks_like_video(row.asset_url):
        create_payload.update({"media_type": "REELS", "video_url": row.asset_url})
    else:
        create_payload["image_url"] = row.asset_url

    create = requests.post(
        f"https://graph.facebook.com/{version}/{user_id}/media",
        data=create_payload,
        timeout=TIMEOUT,
    )
    ensure_ok(create, {200})
    creation_id = _json_value(create, "id")
    if not creation_id:
        raise RuntimeError("Instagram container creation returned no id")

    publish_response = requests.post(
        f"https://graph.facebook.com/{version}/{user_id}/media_publish",
        data={"creation_id": creation_id, "access_token": token},
        timeout=TIMEOUT,
    )
    ensure_ok(publish_response, {200})
    media_id = _json_value(publish_response, "id")
    return f"instagram:{media_id}" if media_id else "instagram:published"


def publish_threads(row: QueueRow) -> str:
    token = required_env("THREADS_ACCESS_TOKEN")
    user_id = required_env("THREADS_USER_ID")
    base = os.getenv("THREADS_API_BASE", "https://graph.threads.net/v1.0").rstrip("/")

    create_payload: dict[str, str] = {
        "media_type": "TEXT",
        "text": row.copy,
        "access_token": token,
    }
    create = requests.post(f"{base}/{user_id}/threads", data=create_payload, timeout=TIMEOUT)
    ensure_ok(create, {200})
    creation_id = _json_value(create, "id")
    if not creation_id:
        raise RuntimeError("Threads container creation returned no id")

    published = requests.post(
        f"{base}/{user_id}/threads_publish",
        data={"creation_id": creation_id, "access_token": token},
        timeout=TIMEOUT,
    )
    ensure_ok(published, {200})
    post_id = _json_value(published, "id")
    return f"threads:{post_id}" if post_id else "threads:published"


def publish_bluesky(row: QueueRow) -> str:
    handle = normalize_bluesky_handle(required_env("BLUESKY_HANDLE"))
    password = required_env("BLUESKY_APP_PASSWORD")
    pds = os.getenv("BLUESKY_PDS", "https://bsky.social").rstrip("/")

    session = requests.post(
        f"{pds}/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
        timeout=TIMEOUT,
    )
    ensure_ok(session, {200})
    data = session.json()
    access_jwt = data.get("accessJwt")
    did = data.get("did")
    if not access_jwt or not did:
        raise RuntimeError("Bluesky session did not return accessJwt and did")

    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    created = requests.post(
        f"{pds}/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {access_jwt}"},
        json={
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": row.copy,
                "createdAt": created_at,
            },
        },
        timeout=TIMEOUT,
    )
    ensure_ok(created, {200})
    uri = created.json().get("uri", "")
    rkey = uri.rsplit("/", 1)[-1] if uri else ""
    return f"https://bsky.app/profile/{handle}/post/{rkey}" if rkey else "bluesky:published"


def publish_mastodon(row: QueueRow) -> str:
    base = required_env("MASTODON_BASE_URL").rstrip("/")
    token = required_env("MASTODON_ACCESS_TOKEN")
    response = requests.post(
        f"{base}/api/v1/statuses",
        headers={"Authorization": f"Bearer {token}"},
        data={"status": row.copy, "visibility": "public"},
        timeout=TIMEOUT,
    )
    ensure_ok(response, {200})
    return response.json().get("url") or f"mastodon:{response.json().get('id', 'published')}"


def normalize_bluesky_handle(handle: str) -> str:
    """Accept the handle as people naturally write it.

    Bluesky shows handles as @name.bsky.social, but its API expects the bare
    form. Stripping the @ here keeps a copy-paste from the profile page working
    and keeps the post URL well-formed.
    """
    return handle.strip().lstrip("@")


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigurationError(f"Missing required environment variable: {name}")
    return value


def ensure_ok(response: requests.Response, expected: set[int]) -> None:
    if response.status_code in expected:
        return
    body = response.text[:1200]
    raise RuntimeError(f"HTTP {response.status_code}: {body}")


def _json_value(response: requests.Response, key: str) -> str:
    try:
        value = response.json().get(key, "")
    except ValueError:
        return ""
    return "" if value is None else str(value)


def _looks_like_image(url: str) -> bool:
    path = urlparse(url).path.lower()
    return path.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif"))


def _looks_like_video(url: str) -> bool:
    path = urlparse(url).path.lower()
    return path.endswith((".mp4", ".mov", ".m4v", ".webm"))
