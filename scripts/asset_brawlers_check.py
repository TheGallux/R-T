"""
Check that all Brawl Stars brawler assets exist in configured directories.
"""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


DIRECTORIES = [
    "/home/gallux/Documents/GitHub/R-T/assets/emojis/neutral",
    "/home/gallux/Documents/GitHub/R-T/assets/emojis/special/",

    "/home/gallux/Documents/GitHub/R-T/assets/portraits/",
]

API_URL = "https://api.brawlstars.com/v1/brawlers"

RESET = "\033[0m"
BOLD = "\033[1m"
WHITE = "\033[97m"
RED = "\033[31m"
GREEN = "\033[32m"


def get_brawler_names() -> list[str]:
    """
    Fetch and return normalized Brawl Stars brawler names from the API.
    """

    api_key = os.getenv("API_KEY_BS")
    if not api_key:
        print("ERROR: API_KEY_BS is not set.", file=sys.stderr)
        sys.exit(2)

    response = requests.get(
        API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    return [
        brawler["name"].lower().replace(" ", "_")
        for brawler in data["items"]
    ]


def check_directory(directory: str, brawlers: list[str]) -> list[str]:
    """
    Return the brawlers whose PNG asset is missing from a directory.
    """

    path = Path(directory)

    missing = []

    for brawler in brawlers:
        image = path / f"{brawler}.png"

        if not image.is_file():
            missing.append(brawler)

    return missing


def main() -> int:
    """
    Fetch brawlers and report missing assets in all configured directories.
    """

    try:
        brawlers = get_brawler_names()
    except requests.RequestException as exc:
        print(f"ERROR: Could not fetch Brawl Stars API: {exc}")
        return 2
    except (KeyError, ValueError) as exc:
        print(f"ERROR: Invalid API response: {exc}")
        return 2

    print(f"Found {len(brawlers)} brawlers.")
    print()

    any_missing = False

    for directory in DIRECTORIES:
        missing = check_directory(directory, brawlers)

        print(f"{BOLD}{WHITE}{directory}:{RESET}")

        if missing:
            any_missing = True

            for brawler in missing:
                print(
                    f"  {RED}missing{RESET} "
                    f"{BOLD}{RED}{brawler}.png{RESET}"
                )
        else:
            print(f"  {GREEN}no missing!{RESET}")

        print()

    if any_missing:
        return 1

    return 0


if __name__ == "__main__":
    load_dotenv()

    sys.exit(main())
