from __future__ import annotations

import logging
import os
import subprocess
import sys
import time

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger("publisher-loop")


def main() -> int:
    poll_seconds = max(30, int(os.getenv("POLL_SECONDS", "300")))
    LOGGER.info("Starting Sklarz social publisher loop; poll interval=%ss", poll_seconds)
    while True:
        result = subprocess.run(
            [sys.executable, "-m", "social_publisher.main"],
            check=False,
        )
        if result.returncode not in {0, 1}:
            LOGGER.error("Publisher returned configuration/runtime code %s", result.returncode)
        time.sleep(poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
