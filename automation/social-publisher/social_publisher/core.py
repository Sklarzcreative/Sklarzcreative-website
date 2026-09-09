from __future__ import annotations

import json
import logging
import os
import socket
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable
from zoneinfo import ZoneInfo

import google.auth
import gspread
from dotenv import load_dotenv
from google.auth.exceptions import DefaultCredentialsError, MalformedError
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1

load_dotenv()

LOGGER = logging.getLogger("sklarz-social-publisher.queue")

SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


class ConfigurationError(RuntimeError):
    pass


class UnsupportedPlatformError(RuntimeError):
    pass


@dataclass(frozen=True)
class Settings:
    publisher_enabled: bool
    dry_run: bool
    timezone: str
    max_posts_per_run: int
    max_backlog_minutes: int
    poll_seconds: int
    sheet_id: str
    worksheet_name: str
    google_service_account_json: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            publisher_enabled=_bool_env("PUBLISHER_ENABLED", False),
            dry_run=_bool_env("DRY_RUN", True),
            timezone=os.getenv("TIMEZONE", "America/New_York"),
            max_posts_per_run=max(1, int(os.getenv("MAX_POSTS_PER_RUN", "1"))),
            max_backlog_minutes=max(0, int(os.getenv("MAX_BACKLOG_MINUTES", "120"))),
            poll_seconds=max(30, int(os.getenv("POLL_SECONDS", "300"))),
            sheet_id=os.getenv(
                "SHEET_ID", "1DQ_2ThldqZjh_rqMSh8LkzZeUFZaCr5PtRZBgmbggbk"
            ),
            worksheet_name=os.getenv("WORKSHEET_NAME", "MAKE - Publish Queue"),
            google_service_account_json=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", ""),
        )

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)


@dataclass
class QueueRow:
    row_number: int
    values: dict[str, Any]

    def get(self, key: str) -> str:
        value = self.values.get(key, "")
        return "" if value is None else str(value).strip()

    @property
    def publish_id(self) -> str:
        return self.get("Publish ID")

    @property
    def platform(self) -> str:
        return self.get("Platform")

    @property
    def copy(self) -> str:
        return self.get("Copy")

    @property
    def asset_url(self) -> str:
        return self.get("Asset URL")

    @property
    def alt_text(self) -> str:
        return self.get("Alt Text")

    @property
    def title(self) -> str:
        return self.get("Title")

    @property
    def canonical_url(self) -> str:
        return self.get("Canonical URL")

    @property
    def post_type(self) -> str:
        return self.get("Post Type")


def _google_credentials(settings: Settings):
    """Return Google credentials without requiring a long-lived key.

    Local machines should use Application Default Credentials (ADC), ideally an
    ADC file created with service-account impersonation. A raw service-account
    JSON value is retained only as a compatibility fallback for environments
    where key creation is explicitly permitted.
    """
    raw = settings.google_service_account_json.strip()
    if raw and raw != "{}":
        try:
            service_info = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ConfigurationError(
                "GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON"
            ) from exc

        try:
            return Credentials.from_service_account_info(
                service_info, scopes=SHEETS_SCOPES
            )
        except (MalformedError, ValueError) as exc:
            raise ConfigurationError(
                f"GOOGLE_SERVICE_ACCOUNT_JSON is not a usable service-account key: {exc}"
            ) from exc

    try:
        credentials, _ = google.auth.default(scopes=SHEETS_SCOPES)
        return credentials
    except DefaultCredentialsError as exc:
        raise ConfigurationError(
            "Google credentials are not configured. For the local publisher, "
            "create Application Default Credentials with service-account "
            "impersonation instead of a service-account key."
        ) from exc


class GoogleSheetQueue:
    """Thin queue adapter for the existing MAKE - Publish Queue worksheet.

    The sheet remains the source of truth. This class never publishes content itself.
    """

    def __init__(self, settings: Settings):
        credentials = _google_credentials(settings)
        client = gspread.authorize(credentials)
        spreadsheet = client.open_by_key(settings.sheet_id)
        self.ws = spreadsheet.worksheet(settings.worksheet_name)
        self.settings = settings
        self.headers = self.ws.row_values(1)
        self.header_map = {name: idx + 1 for idx, name in enumerate(self.headers)}
        self._validate_headers()

    def _validate_headers(self) -> None:
        required = {
            "Publish ID",
            "Platform",
            "Copy",
            "Scheduled DateTime ET",
            "Approval Gate",
            "Publish Status",
            "Published URL",
            "Last Error",
            "Published At",
            "Notes",
        }
        missing = sorted(required - set(self.headers))
        if missing:
            raise ConfigurationError(f"Missing required queue columns: {', '.join(missing)}")

    def rows(self) -> list[QueueRow]:
        records = self.ws.get_all_records(default_blank="")
        return [QueueRow(index + 2, record) for index, record in enumerate(records)]

    def due_rows(
        self,
        *,
        now: datetime | None = None,
        publish_id: str | None = None,
    ) -> list[QueueRow]:
        now = now or datetime.now(self.settings.tz)
        due: list[tuple[datetime, QueueRow]] = []
        for row in self.rows():
            if publish_id and row.publish_id != publish_id:
                continue
            if row.get("Approval Gate").upper() != "APPROVED":
                continue
            if row.get("Publish Status").upper() not in {"QUEUED", "RETRY"}:
                continue
            if row.get("Published URL"):
                continue

            raw_schedule = row.get("Scheduled DateTime ET")
            scheduled = parse_queue_datetime(raw_schedule, self.settings.tz)
            if scheduled is None:
                if raw_schedule:
                    # An unparseable date is indistinguishable from "not due yet",
                    # so the row would be skipped on every run with nothing written
                    # back to the Sheet. Name it instead of failing silently.
                    LOGGER.warning(
                        "Skipping %s: could not parse 'Scheduled DateTime ET' value %r. "
                        "This row stays ineligible until the cell is corrected.",
                        row.publish_id or f"row {row.row_number}",
                        raw_schedule,
                    )
                continue
            if scheduled > now:
                continue

            age_minutes = (now - scheduled).total_seconds() / 60
            if self.settings.max_backlog_minutes and age_minutes > self.settings.max_backlog_minutes:
                continue
            due.append((scheduled, row))

        due.sort(key=lambda item: item[0])
        return [row for _, row in due[: self.settings.max_posts_per_run]]

    def update_fields(self, row_number: int, fields: dict[str, Any]) -> None:
        payload: list[dict[str, Any]] = []
        for header, value in fields.items():
            if header not in self.header_map:
                raise ConfigurationError(f"Unknown queue column: {header}")
            col = self.header_map[header]
            payload.append(
                {
                    "range": rowcol_to_a1(row_number, col),
                    "values": [["" if value is None else value]],
                }
            )
        self.ws.batch_update(payload, value_input_option="USER_ENTERED")

    def claim(self, row: QueueRow, runner_id: str) -> None:
        stamp = datetime.now(self.settings.tz).isoformat(timespec="seconds")
        self.update_fields(
            row.row_number,
            {
                "Publish Status": "PROCESSING",
                "Last Error": f"Claimed by {runner_id} at {stamp}",
            },
        )

    def mark_published(self, row: QueueRow, published_ref: str) -> None:
        stamp = datetime.now(self.settings.tz).strftime("%Y-%m-%d %H:%M")
        self.update_fields(
            row.row_number,
            {
                "Publish Status": "PUBLISHED",
                "Published URL": published_ref,
                "Published At": stamp,
                "Last Error": "",
            },
        )

    def mark_error(self, row: QueueRow, error: str) -> None:
        self.update_fields(
            row.row_number,
            {
                "Publish Status": "ERROR",
                "Last Error": error[:1000],
            },
        )

    def mark_hold(self, row: QueueRow, reason: str) -> None:
        self.update_fields(
            row.row_number,
            {
                "Publish Status": "HOLD",
                "Last Error": reason[:1000],
            },
        )


def runner_id() -> str:
    return os.getenv("RUNNER_ID", socket.gethostname() or "publisher")


def parse_queue_datetime(value: str, tz: ZoneInfo) -> datetime | None:
    if not value:
        return None
    candidates = (
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%m/%d/%Y %I:%M %p",
        "%m/%d/%Y %H:%M",
    )
    for fmt in candidates:
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=tz)
        except ValueError:
            continue
    try:
        parsed = datetime.fromisoformat(value)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=tz)
    except ValueError:
        return None


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}
