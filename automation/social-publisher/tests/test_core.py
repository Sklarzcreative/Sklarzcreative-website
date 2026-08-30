from datetime import datetime
from zoneinfo import ZoneInfo

from social_publisher.core import QueueRow, parse_queue_datetime


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
