from __future__ import annotations

import getpass
from pathlib import Path

import requests

TIMEOUT = 45
PROJECT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_DIR / ".env"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"


def _set_env_values(path: Path, updates: dict[str, str]) -> None:
    if not path.exists():
        example = PROJECT_DIR / ".env.example"
        if not example.exists():
            raise RuntimeError("Neither .env nor .env.example exists")
        path.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")

    lines = path.read_text(encoding="utf-8").splitlines()
    seen: set[str] = set()
    output: list[str] = []

    for line in lines:
        if "=" in line and not line.lstrip().startswith("#"):
            key = line.split("=", 1)[0].strip()
            if key in updates:
                output.append(f"{key}={updates[key]}")
                seen.add(key)
                continue
        output.append(line)

    for key, value in updates.items():
        if key not in seen:
            output.append(f"{key}={value}")

    path.write_text("\n".join(output) + "\n", encoding="utf-8")


def main() -> int:
    print("Sklarz Social Publisher - LinkedIn Personal setup")
    print("The access token stays on this laptop and is written only to the ignored local .env file.")
    print("Publishing will remain disabled and dry-run after setup.\n")

    token = getpass.getpass("Paste LinkedIn access token (input hidden): ").strip()
    if not token:
        print("ERROR: No token entered.")
        return 2

    response = requests.get(
        USERINFO_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=TIMEOUT,
    )
    if response.status_code != 200:
        print(f"ERROR: LinkedIn userinfo returned HTTP {response.status_code}: {response.text[:500]}")
        return 2

    try:
        profile = response.json()
    except ValueError:
        print("ERROR: LinkedIn userinfo did not return JSON.")
        return 2

    sub = str(profile.get("sub", "")).strip()
    if not sub:
        print("ERROR: LinkedIn userinfo response did not include 'sub'.")
        return 2

    name = str(profile.get("name", "LinkedIn member")).strip() or "LinkedIn member"
    person_urn = f"urn:li:person:{sub}"

    _set_env_values(
        ENV_FILE,
        {
            "PUBLISHER_ENABLED": "false",
            "DRY_RUN": "true",
            "LINKEDIN_ACCESS_TOKEN": token,
            "LINKEDIN_PERSON_URN": person_urn,
        },
    )

    print(f"Verified LinkedIn member: {name}")
    print("LinkedIn Personal credential saved locally.")
    print("PUBLISHER_ENABLED=false")
    print("DRY_RUN=true")
    print("No post was created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
