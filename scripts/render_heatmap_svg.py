#!/usr/bin/env python3
"""Render a self-contained animated contribution heatmap from fetched JSON."""
from __future__ import annotations
import html
import json
from pathlib import Path

DATA = Path("data/contributions.json")
OUT = Path("profile-art/contribution-heatmap.svg")
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

def main() -> None:
    if not DATA.exists():
        raise SystemExit("Missing data/contributions.json; run scripts/fetch_contributions.py first.")
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    days = payload.get("days", [])
    if not days:
        raise SystemExit("Contribution data is empty; refusing to render a misleading chart.")

    # Preserve the most recent 371 calendar days (53 weeks); align to weekday rows.
    days = days[-371:]
    cells = []
    for index, item in enumerate(days):
        week, weekday = divmod(index, 7)
        level = max(0, min(4, int(item.get("level", 0))))
        x, y = 24 + week * 16, 70 + weekday * 13
        date = html.escape(str(item.get("date", "")), quote=True)
        count = item.get("count")
        label = f"{count} contributions on {date}" if count is not None else f"Contribution level {level} on {date}"
        delay = min(index * 0.002, 0.8)
        cells.append(
            f'<rect x="{x}" y="{y}" width="11" height="9" rx="2" fill="{COLORS[level]}" '
            f'data-date="{date}" opacity="0">'
            f'<title>{html.escape(label)}</title>'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur=".45s" fill="freeze"/>'
            f'</rect>'
        )

    username = html.escape(str(payload.get("username", "GitHub user")))
    updated = html.escape(str(payload.get("fetched_at", "unknown")))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="190" viewBox="0 0 900 190" role="img" aria-labelledby="title desc">
<title id="title">{username} contribution activity</title>
<desc id="desc">Contribution levels from the public GitHub calendar, animated in as local SVG shapes. Fetched at {updated}.</desc>
<rect width="900" height="190" rx="12" fill="#0b1020" stroke="#2d3858"/>
<g font-family="Consolas, 'Courier New', monospace">
<text x="24" y="29" fill="#00e5ff" font-size="14">{username}@github ~ $ contributions --year rolling</text>
<text x="24" y="53" fill="#9aa8ca" font-size="10">Public calendar · refreshed {updated[:10]}</text>
{''.join(cells)}
<text x="24" y="177" fill="#9aa8ca" font-size="11">Less</text>
{''.join(f'<rect x="{58+i*16}" y="166" width="11" height="9" rx="2" fill="{color}"/>' for i, color in enumerate(COLORS))}
<text x="151" y="177" fill="#9aa8ca" font-size="11">More</text>
</g></svg>'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg + "\n", encoding="utf-8")
    print(f"Rendered {len(days)} days to {OUT}")

if __name__ == "__main__":
    main()
