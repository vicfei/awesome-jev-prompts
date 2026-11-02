"""Tests for scripts/leaderboard.py (stdlib pytest, no network)."""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from leaderboard import (  # noqa: E402
    cell,
    delta7,
    extract_repos,
    fmt_delta,
    preview,
    render,
    replace_between,
)


def test_extract_keeps_repos_and_issue_links():
    md = "see https://github.com/typesafe-ai/typesafe-sdk-python and " \
         "[a repo](https://github.com/virattt/ai-hedge-fund) plus " \
         "https://github.com/vicfei/minimind-jev/issues/7 thread"
    assert extract_repos(md) == {
        "typesafe-ai/typesafe-sdk-python",
        "virattt/ai-hedge-fund",
        "vicfei/minimind-jev",
    }


def test_extract_skips_site_sections_gists_and_self():
    md = (
        "https://github.com/features/actions x "
        "https://github.com/topics/jev y "
        "https://gist.github.com/o/abc123 z "
        "https://github.com/vicfei/awesome-jev-prompts self"
    )
    assert extract_repos(md) == set()


def test_extract_strips_trailing_punctuation():
    assert extract_repos("as in https://github.com/yzfly/awesome-jev-zh.") == {"yzfly/awesome-jev-zh"}


def test_delta7_uses_last_snapshot_at_least_six_days_old():
    today = dt.date(2026, 11, 2)
    hist = [["2026-10-01", 10], ["2026-10-26", 12], ["2026-10-27", 13], ["2026-10-28", 14]]
    # snapshots at least 6 days old: 10-01, 10-26 and 10-27 (== today-6) → baseline 13
    assert delta7(20, hist, today) == 7


def test_delta7_none_when_history_too_young():
    today = dt.date(2026, 11, 2)
    assert delta7(20, [["2026-10-30", 10], ["2026-11-01", 12]], today) is None
    assert delta7(20, [], today) is None


def test_render_orders_by_stars_and_ties_by_name():
    rows = [
        {"repo": "b/b", "desc": "", "stars": 5, "delta": None},
        {"repo": "a/a", "desc": "", "stars": 50, "delta": None},
        {"repo": "c/c", "desc": "", "stars": 5, "delta": None},
    ]
    out = render(rows, "2026-10-26", "2026-11-02", "en")
    assert out.index("a/a") < out.index("b/b") < out.index("c/c")
    assert "| 1 | [a/a]" in out
    assert "No weekly data yet" in out


def test_render_weekly_table_sorts_by_delta():
    rows = [
        {"repo": "x/x", "desc": "", "stars": 100, "delta": 2},
        {"repo": "y/y", "desc": "", "stars": 10, "delta": 30},
        {"repo": "z/z", "desc": "", "stars": 50, "delta": -1},
    ]
    out = render(rows, None, "2026-11-02", "en")
    week = out[out.index("## By weekly change"):]
    assert week.index("y/y") < week.index("x/x") < week.index("z/z")
    assert fmt_delta(30) == "+30" and fmt_delta(-1) == "-1" and fmt_delta(0) == "0"


def test_cell_collapses_whitespace_escapes_pipes_and_truncates():
    assert cell("a | b") == "a \\| b"
    assert cell("  multiple   spaces  ") == "multiple spaces"
    assert cell("") == "—"
    assert len(cell("x" * 200)) == 72


def test_preview_capped_at_ten_rows_sorted_by_stars():
    rows = [{"repo": f"r/{i}", "desc": "", "stars": i, "delta": None} for i in range(15)]
    out = preview(rows, "en")
    assert out.count("](https://github.com/r/") == 10
    assert "r/14" in out and "r/10" in out and "r/5" in out and "r/4" not in out
    assert out.index("r/14") < out.index("r/10")
    assert "of the 15 GitHub projects" in out


def test_replace_between_keeps_markers():
    text = "head\n<!-- leaderboard:start -->old<!-- leaderboard:end -->tail"
    out = replace_between(text, "<!-- leaderboard:start -->", "<!-- leaderboard:end -->", "NEW")
    assert out == "head\n<!-- leaderboard:start -->\nNEW\n<!-- leaderboard:end -->tail"
