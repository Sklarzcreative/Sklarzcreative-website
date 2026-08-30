from __future__ import annotations

import argparse
import logging
import sys

from .core import (
    ConfigurationError,
    GoogleSheetQueue,
    Settings,
    UnsupportedPlatformError,
    runner_id,
)
from .platforms import publish

LOGGER = logging.getLogger("sklarz-social-publisher")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Publish due Sklarz Creative social queue rows")
    parser.add_argument("--dry-run", action="store_true", help="Inspect due rows without publishing or changing the Sheet")
    parser.add_argument("--publish-id", help="Limit the run to one exact Publish ID")
    return parser


def run(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args = build_parser().parse_args(argv)
    settings = Settings.from_env()
    effective_dry_run = settings.dry_run or args.dry_run

    if not settings.publisher_enabled and not effective_dry_run:
        LOGGER.warning("Publisher disabled. Set PUBLISHER_ENABLED=true to allow live publishing.")
        return 0

    try:
        queue = GoogleSheetQueue(settings)
        due = queue.due_rows(publish_id=args.publish_id)
    except ConfigurationError as exc:
        LOGGER.error("Configuration error: %s", exc)
        return 2

    if not due:
        LOGGER.info("No eligible due rows found.")
        return 0

    LOGGER.info("Eligible rows this run: %s", ", ".join(row.publish_id for row in due))

    if effective_dry_run:
        for row in due:
            LOGGER.info(
                "DRY RUN | %s | %s | type=%s | asset=%s",
                row.publish_id,
                row.platform,
                row.post_type or "n/a",
                bool(row.asset_url),
            )
        return 0

    run_id = runner_id()
    exit_code = 0
    for row in due:
        try:
            queue.claim(row, run_id)
            published_ref = publish(row)
            queue.mark_published(row, published_ref)
            LOGGER.info("Published %s to %s: %s", row.publish_id, row.platform, published_ref)
        except UnsupportedPlatformError as exc:
            queue.mark_hold(row, str(exc))
            LOGGER.warning("Held %s: %s", row.publish_id, exc)
        except Exception as exc:  # noqa: BLE001 - queue must retain provider error text
            queue.mark_error(row, f"{type(exc).__name__}: {exc}")
            LOGGER.exception("Failed %s on %s", row.publish_id, row.platform)
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(run())
