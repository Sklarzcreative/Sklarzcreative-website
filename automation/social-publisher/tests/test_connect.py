"""Tests for the credential-check helper.

The live API calls cannot run in CI, so these cover the pure logic: how
platform error bodies are turned into readable messages, and how discovered
values are suggested back to the user.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import connect  # noqa: E402


class FakeResponse:
    def __init__(self, status_code, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


@pytest.mark.parametrize(
    "payload,expected_fragment",
    [
        # Meta / Threads nest the message under "error".
        ({"error": {"message": "Invalid OAuth access token."}}, "Invalid OAuth access token."),
        # LinkedIn uses a flat "message".
        ({"message": "Empty oauth2 access token"}, "Empty oauth2 access token"),
        # Mastodon / OAuth2 use "error_description".
        ({"error_description": "The access token is invalid"}, "The access token is invalid"),
        # Bluesky returns a bare string error.
        ({"error": "AuthenticationRequired"}, "AuthenticationRequired"),
    ],
)
def test_api_error_extracts_platform_message(payload, expected_fragment):
    response = FakeResponse(401, payload)
    assert expected_fragment in connect._api_error(response)
    assert "401" in connect._api_error(response)


def test_api_error_survives_non_json_body():
    """An HTML error page must not crash the check."""
    response = FakeResponse(502, None, text="<html>Bad Gateway</html>")
    message = connect._api_error(response)
    assert "502" in message
    assert "Bad Gateway" in message


def test_suggest_skips_values_already_correct(monkeypatch):
    monkeypatch.setenv("META_PAGE_ID", "12345")
    result = connect.Result("Meta")
    result.suggest("META_PAGE_ID", "12345")
    assert result.env_lines == []


def test_suggest_reports_changed_value(monkeypatch):
    monkeypatch.setenv("META_PAGE_ID", "old")
    result = connect.Result("Meta")
    result.suggest("META_PAGE_ID", "new")
    assert result.env_lines == ["META_PAGE_ID=new"]


def test_unknown_platform_is_rejected(capsys):
    assert connect.main(["connect.py", "myspace"]) == 2
    assert "Unknown platform" in capsys.readouterr().out


def test_every_documented_platform_has_a_check():
    """DEFAULT_ORDER must only name checks that exist."""
    for name in connect.DEFAULT_ORDER:
        assert name in connect.CHECKS
