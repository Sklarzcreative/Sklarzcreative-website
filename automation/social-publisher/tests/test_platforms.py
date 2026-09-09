from __future__ import annotations

from dataclasses import dataclass

import pytest

from social_publisher.core import ConfigurationError, QueueRow
from social_publisher import platforms


@dataclass
class FakeResponse:
    status_code: int
    payload: dict | None = None
    content: bytes = b""
    headers: dict | None = None
    text: str = ""

    def __post_init__(self):
        self.headers = self.headers or {}

    def json(self):
        return self.payload or {}


def linkedin_row(asset_url: str = "https://assets.example.com/post.png") -> QueueRow:
    return QueueRow(
        2,
        {
            "Publish ID": "LI-1",
            "Platform": "LinkedIn Personal",
            "Copy": "Post copy",
            "Title": "Post title",
            "Alt Text": "Accessible description",
            "Asset URL": asset_url,
        },
    )


def test_linkedin_requires_image(monkeypatch):
    monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "secret")
    with pytest.raises(ConfigurationError, match="requires Asset URL"):
        platforms.publish_linkedin(linkedin_row(""), "urn:li:person:123")


def test_linkedin_uploads_image_and_attaches_alt_text(monkeypatch):
    calls = []
    monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "secret")

    def fake_get(url, **kwargs):
        calls.append(("get", url, kwargs))
        if url.startswith("https://api.linkedin.com/rest/images/"):
            return FakeResponse(200, {"status": "AVAILABLE"})
        return FakeResponse(
            200,
            content=b"png-bytes",
            headers={"Content-Type": "image/png"},
        )

    def fake_post(url, **kwargs):
        calls.append(("post", url, kwargs))
        if "initializeUpload" in url:
            return FakeResponse(
                200,
                {"value": {"uploadUrl": "https://upload.example.com/image", "image": "urn:li:image:abc"}},
            )
        return FakeResponse(201, headers={"x-restli-id": "urn:li:share:456"})

    def fake_put(url, **kwargs):
        calls.append(("put", url, kwargs))
        return FakeResponse(201)

    monkeypatch.setattr(platforms.requests, "get", fake_get)
    monkeypatch.setattr(platforms.requests, "post", fake_post)
    monkeypatch.setattr(platforms.requests, "put", fake_put)

    result = platforms.publish_linkedin(
        linkedin_row(), "urn:li:person:123"
    )

    assert result == "https://www.linkedin.com/feed/update/urn:li:share:456"
    post_call = [call for call in calls if call[0] == "post" and call[1].endswith("/rest/posts")][0]
    assert post_call[2]["json"]["content"]["media"] == {
        "id": "urn:li:image:abc",
        "altText": "Accessible description",
    }
    put_call = [call for call in calls if call[0] == "put"][0]
    assert put_call[2]["data"] == b"png-bytes"


def test_linkedin_rejects_non_image_asset(monkeypatch):
    monkeypatch.setattr(
        platforms.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(
            200, content=b"not-image", headers={"Content-Type": "text/html"}
        ),
    )
    with pytest.raises(ConfigurationError, match="JPG, PNG, or GIF"):
        platforms.upload_linkedin_image(
            asset_url="https://example.com/page",
            owner_urn="urn:li:person:123",
            token="secret",
            version="202608",
        )


def test_linkedin_status_poll_allows_write_only_member_token(monkeypatch):
    monkeypatch.setattr(
        platforms.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(403),
    )
    platforms._wait_for_linkedin_image("urn:li:image:abc", "secret", "202608")


@pytest.mark.parametrize(
    "configured",
    ["@sklarz.bsky.social", "sklarz.bsky.social", "  @sklarz.bsky.social  "],
)
def test_bluesky_handle_accepts_the_displayed_at_prefix(monkeypatch, configured):
    """Bluesky displays @handle, but createSession needs the bare form.

    The @ is what gets copied off the profile page. Left in place it fails
    authentication and also corrupts the post URL written back to the Sheet.
    """
    calls = []

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        if "createSession" in url:
            return FakeResponse(200, {"accessJwt": "jwt", "did": "did:plc:abc"})
        return FakeResponse(200, {"uri": "at://did:plc:abc/app.bsky.feed.post/rkey123"})

    monkeypatch.setenv("BLUESKY_HANDLE", configured)
    monkeypatch.setenv("BLUESKY_APP_PASSWORD", "aaaa-bbbb-cccc-dddd")
    monkeypatch.setattr(platforms.requests, "post", fake_post)

    published_url = platforms.publish_bluesky(
        QueueRow(2, {"Publish ID": "BS-1", "Platform": "Bluesky", "Copy": "Hello"})
    )

    session_body = calls[0][1]["json"]
    assert session_body["identifier"] == "sklarz.bsky.social"
    assert published_url == "https://bsky.app/profile/sklarz.bsky.social/post/rkey123"


def test_bluesky_posts_the_copy_verbatim(monkeypatch):
    """The record text must be exactly the Copy cell, with no decoration."""

    def fake_post(url, **kwargs):
        if "createSession" in url:
            return FakeResponse(200, {"accessJwt": "jwt", "did": "did:plc:abc"})
        assert kwargs["json"]["record"]["text"] == "Exact copy from the Sheet."
        assert kwargs["json"]["collection"] == "app.bsky.feed.post"
        return FakeResponse(200, {"uri": "at://did:plc:abc/app.bsky.feed.post/r1"})

    monkeypatch.setenv("BLUESKY_HANDLE", "sklarz.bsky.social")
    monkeypatch.setenv("BLUESKY_APP_PASSWORD", "aaaa-bbbb-cccc-dddd")
    monkeypatch.setattr(platforms.requests, "post", fake_post)

    platforms.publish_bluesky(
        QueueRow(2, {"Publish ID": "BS-2", "Platform": "Bluesky", "Copy": "Exact copy from the Sheet."})
    )
