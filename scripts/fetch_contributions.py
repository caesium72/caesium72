#!/usr/bin/env python3
"""Fetch the public contribution calendar for a GitHub user; no token required."""
from __future__ import annotations
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "caesium72")
OUT = Path("data/contributions.json")
URL = f"https://github.com/users/{USERNAME}/contributions"
HEADERS = {
    "User-Agent": "caesium72-profile-art/1.0 (+https://github.com/caesium72/caesium72)",
    "Accept": "text/html",
}

def main() -> int:
    try:
        response = requests.get(URL, headers=HEADERS, timeout=(5, 20))
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Could not fetch public contribution calendar: {exc}", file=sys.stderr)
        return 1

    soup = BeautifulSoup(response.text, "html.parser")
    days = []
    for cell in soup.select("td.ContributionCalendar-day"):
        date = cell.get("data-date")
        level = cell.get("data-level")
        aria = cell.get("aria-label", "")
        match = re.search(r"(\d+) contributions?", aria)
        count = int(match.group(1)) if match else None
        if date and level is not None:
            try:
                level_int = max(0, min(4, int(level)))
            except ValueError:
                level_int = 0
            days.append({"date": date, "level": level_int, "count": count})

    if not days:
        print("No contribution cells found; GitHub may have changed its HTML. Existing SVG will not be overwritten.", file=sys.stderr)
        return 2

    payload = {
        "username": USERNAME,
        "source": URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(days)} public contribution days to {OUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
