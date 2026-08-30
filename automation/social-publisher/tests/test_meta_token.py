"""Tests for the Meta long-lived Page token helper.

Live Graph API calls cannot run in CI, so these cover the decision logic:
error translation, Page selection, and the guard that stops the script when
app credentials are absent.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import meta_token  # noqa: E402


@pytest.mark.parametrize(
    "code,expected_hint",
    [
        (190, "expired or invalid"),
        (200, "pages_manage_posts"),
        (1, "App Secret"),
    ],
)
def test_known_error_codes_get_actionable_hints(code, expected_hint):
    payload = {"error": {"message": "Something failed", "code": code}}
    assert expected_hint in meta_token.explain_error(payload, 400)


def test_unknown_error_code_still_reports_the_message():
    payload = {"error": {"message": "Unusual failure", "code": 9999}}
    message = meta_token.explain_error(payload, 400)
    assert "Unusual failure" in message
    assert "9999" in message


def test_error_without_code_falls_back_to_status():
    assert "HTTP 500" in meta_token.explain_error({}, 500)


def test_single_page_is_chosen_without_prompting(monkeypatch):
    """One Page must not ask the user to pick from a list of one."""
    def explode(*args, **kwargs):
        raise AssertionError("should not prompt when exactly one Page exists")

    monkeypatch.setattr("builtins.input", explode)
    page = {"id": "1", "name": "Sklarz Creative", "access_token": "t"}
    assert meta_token.choose_page([page]) is page


def test_multiple_pages_prompts_until_valid(monkeypatch, capsys):
    pages = [
        {"id": "1", "name": "Page One", "access_token": "a"},
        {"id": "2", "name": "Page Two", "access_token": "b"},
    ]
    answers = iter(["0", "banana", "2"])
    monkeypatch.setattr("builtins.input", lambda *_: next(answers))
    assert meta_token.choose_page(pages)["id"] == "2"


def test_missing_app_credentials_exits_before_prompting(monkeypatch, capsys):
    """Without app id/secret the script must not ask for a token it cannot use."""
    monkeypatch.delenv("META_APP_ID", raising=False)
    monkeypatch.delenv("META_APP_SECRET", raising=False)
    monkeypatch.setattr(
        meta_token, "getpass", lambda *_: pytest.fail("prompted without credentials")
    )
    assert meta_token.main() == 2
    assert "META_APP_ID" in capsys.readouterr().out
