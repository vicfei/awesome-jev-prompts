"""Tests for scripts/lint_questions.py (stdlib pytest, no network)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from lint_questions import lint_question  # noqa: E402


def noul_ok():
    return {"name": "lost", "kind": "noul",
            "instructions": "Has the drone genuinely lost the rover?",
            "criteria": {"true": "Sweep to search.", "false": "Keep the bearing."}}


def choice_ok():
    return {"name": "team", "kind": "choice",
            "instructions": "Which team should handle this ticket?",
            "criteria": {"billing": "Payments.", "technical": "Bugs.",
                         "unknown": "Not decidable; escalate."}}


def score_ok():
    return {"name": "relevance", "kind": "score",
            "instructions": "How well does this passage answer the query?",
            "criteria": ["irrelevant", "related", "partial", "answers"]}


def codes(q):
    return [c for c, _ in lint_question(q)]


def test_clean_questions_pass():
    assert codes(noul_ok()) == []
    assert codes(choice_ok()) == []
    assert codes(score_ok()) == []


def test_atomicity_error():
    q = noul_ok()
    q["instructions"] = "Is it urgent and should we notify the on-call?"
    assert "E1" in codes(q)


def test_option_count_wire_limit():
    q = choice_ok()
    q["criteria"] = {chr(65 + i): f"option {i}" for i in range(27)}  # 27 > A-Z
    assert "E2" in codes(q)
    q["criteria"] = {chr(65 + i): f"option {i}" for i in range(10)}  # 10 > 8 → load only
    assert "E2" not in codes(q) and "W1" in codes(q)


def test_rubric_size_bounds():
    q = score_ok()
    q["criteria"] = ["only"]
    assert "E3" in codes(q)
    q["criteria"] = [f"level {i}" for i in range(11)]
    assert "E3" in codes(q)


def test_empty_and_duplicate_descriptions():
    q = choice_ok()
    q["criteria"] = {"a": "", "b": "same", "c": "same", "unknown": "esc"}
    cs = codes(q)
    assert "E4" in cs


def test_escape_option_warning():
    q = choice_ok()
    q["criteria"] = {"billing": "Payments.", "technical": "Bugs.", "legal": "Contracts."}
    assert "W2" in codes(q)


def test_noul_boundary_warning():
    q = noul_ok()
    q.pop("criteria")
    assert "W3" in codes(q)


def test_unknown_kind():
    assert codes({"name": "x", "kind": "vibes", "instructions": "?"}) == ["E0"]
