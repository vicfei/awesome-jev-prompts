#!/usr/bin/env python3
"""Check every http(s) URL in markdown files and llms.txt. Exit 1 on dead links."""

from __future__ import annotations

import re
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL_RE = re.compile(r"https?://[^\s<>\")\]`]+")
SKIP_HOSTS = ("img.shields.io",)  # badge host, not worth probing


def self_url_prefixes() -> tuple[str, ...]:
    """URL prefixes of this repo itself — self-links are structural, skip them."""
    try:
        remote = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001 - no origin (pre-launch) → nothing to skip
        return ()
    match = re.match(r"(?:https://|git@)(github\.com)[/:](.+?)(?:\.git)?$", remote)
    if not match:
        return ()
    slug = match.group(2)
    return (
        f"https://github.com/{slug}/",
        f"https://raw.githubusercontent.com/{slug}/",
    )
ALIVE_STATUSES = {401, 403, 405, 429, 501}  # bot-throttled but alive
TIMEOUT = 15


def collect_urls() -> dict[str, list[str]]:
    files = [p for p in sorted(ROOT.rglob("*.md")) if ".git" not in p.parts]
    llms = ROOT / "llms.txt"
    if llms.exists():
        files.append(llms)
    skip = self_url_prefixes()
    found: dict[str, list[str]] = {}
    for path in files:
        for url in URL_RE.findall(path.read_text(encoding="utf-8")):
            url = url.rstrip(".,;")
            if not any(url.startswith(f"https://{host}/") for host in SKIP_HOSTS) and not any(
                url.startswith(prefix) for prefix in skip
            ):
                found.setdefault(url, []).append(str(path.relative_to(ROOT)))
    return found


def check(url: str) -> tuple[str, str]:
    req = urllib.request.Request(
        url, headers={"User-Agent": "awesome-jev-prompts-link-check/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return url, f"ok ({resp.status})"
    except urllib.error.HTTPError as err:
        if err.code in ALIVE_STATUSES:
            return url, f"ok ({err.code}, throttled)"
        return url, f"DEAD ({err.code})"
    except Exception as err:  # noqa: BLE001 - any transport failure counts as dead
        return url, f"DEAD ({type(err).__name__}: {err})"


def main() -> int:
    urls = collect_urls()
    dead: list[str] = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        for url, status in pool.map(check, urls):
            print(f"{status:32} {url}")
            if status.startswith("DEAD"):
                dead.append(url)
    print(f"\n{len(urls)} URLs checked, {len(dead)} dead")
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
