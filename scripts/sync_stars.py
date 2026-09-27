#!/usr/bin/env python3
"""Refresh related-list star counts and the last-checked date in README.md.

Reads data/related-lists.json, fetches live star counts from the GitHub API
(GITHUB_TOKEN if set), caches them in data/star-cache.json, and rewrites the
marked sections of README.md. Runs daily in CI; safe to run locally.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LISTS = ROOT / "data" / "related-lists.json"
CACHE = ROOT / "data" / "star-cache.json"
README = ROOT / "README.md"
START, END = "<!-- related-lists:start -->", "<!-- related-lists:end -->"
DATE_START, DATE_END = "<!-- last-checked:start -->", "<!-- last-checked:end -->"
API = "https://api.github.com/repos/{}"


def fetch_stars(repos: list[str]) -> dict[str, int]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "awesome-jev-prompts-sync",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    stars: dict[str, int] = {}
    for repo in repos:
        req = urllib.request.Request(API.format(repo), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                stars[repo] = json.load(resp)["stargazers_count"]
        except Exception as err:  # noqa: BLE001 - keep going, cache fills the gap
            print(f"warn: {repo}: {err}", file=sys.stderr)
    return stars


def replace_between(text: str, start: str, end: str, body: str) -> str:
    s = text.index(start) + len(start)
    e = text.index(end)
    return text[:s] + body + text[e:]


def main() -> int:
    entries = json.loads(LISTS.read_text(encoding="utf-8"))["repos"]
    cache: dict[str, dict] = (
        json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    )
    today = dt.date.today().isoformat()
    live = fetch_stars([e["repo"] for e in entries])
    cache.update({repo: {"stars": n, "date": today} for repo, n in live.items()})
    CACHE.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    table = ["\n| List | Focus | Stars |", "|---|---|---:|"]
    for entry in sorted(
        entries, key=lambda e: -cache.get(e["repo"], {}).get("stars", 0)
    ):
        repo = entry["repo"]
        stars = cache.get(repo, {}).get("stars")
        count = f"{stars:,}" if stars is not None else "—"
        table.append(
            f"| [{repo}](https://github.com/{repo}) | {entry['focus']} | {count} |"
        )
    table.append("")

    text = README.read_text(encoding="utf-8")
    text = replace_between(text, START, END, "\n".join(table))
    text = replace_between(text, DATE_START, DATE_END, f"\n*Last checked: {today}*\n")
    README.write_text(text, encoding="utf-8")
    print(f"updated {len(live)}/{len(entries)} star counts, last-checked {today}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
