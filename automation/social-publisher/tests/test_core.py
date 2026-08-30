from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from social_publisher.core import (
    ConfigurationError,
    GoogleSheetQueue,
    QueueRow,
    Settings,
    _google_credentials,
    parse_queue_datetime,
)


def test_parse_queue_datetime_et():
    tz = ZoneInfo("America/New_York")
    parsed = parse_queue_datetime("2026-08-29 18:00", tz)
    assert parsed == datetime(2026, 8, 29, 18, 0, tzinfo=tz)


def test_queue_row_properties():
    row = QueueRow(
        row_number=2,
        values={
            "Publish ID": "SC-1",
            "Platform": "LinkedIn Personal",
            "Copy": "Hello",
            "Asset URL": "",
            "Canonical URL": "https://example.com",
            "Post Type": "Feed Post",
        },
    )
    assert row.publish_id == "SC-1"
    assert row.platform == "LinkedIn Personal"
    assert row.copy == "Hello"
    assert row.canonical_url == "https://example.com"


def _settings(service_account_json: str) -> Settings:
    return Settings(
        publisher_enabled=False,
        dry_run=True,
        timezone="America/New_York",
        max_posts_per_run=1,
        max_backlog_minutes=120,
        poll_seconds=300,
        sheet_id="sheet-id",
        worksheet_name="MAKE - Publish Queue",
        google_service_account_json=service_account_json,
    )


@pytest.mark.parametrize(
    "service_account_json",
    [
        "not json",
        '{"client_email": "a@b.iam.gserviceaccount.com"}',
    ],
)
def test_unusable_explicit_service_account_raises_configuration_error(
    service_account_json,
):
    with pytest.raises(ConfigurationError):
        _google_credentials(_settings(service_account_json))


def test_placeholder_uses_application_default_credentials(monkeypatch):
    marker = object()

    def fake_default(*, scopes):
        assert scopes == ["https://www.googleapis.com/auth/spreadsheets"]
        return marker, "project-id"

    monkeypatch.setattr("social_publisher.core.google.auth.default", fake_default)
    assert _google_credentials(_settings("{}")) is marker


def test_empty_value_uses_application_default_credentials(monkeypatch):
    marker = object()
    monkeypatch.setattr(
        "social_publisher.core.google.auth.default",
        lambda *, scopes: (marker, "project-id"),
    )
    assert _google_credentials(_settings("")) is marker
