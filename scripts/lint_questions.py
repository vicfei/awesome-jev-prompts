#!/usr/bin/env python3
"""Lint typed-decision questions against this library's own rules. Stdlib only.

Input: a JSON file holding a list of questions in SDK shape —

    [{"name": "urgent", "kind": "noul",
      "instructions": "Has the drone genuinely lost the rover?",
      "criteria": {"true": "Give up the bearing and sweep.", "false": "Keep flying."}},
     {"name": "team", "kind": "choice",
      "instructions": "Which team should handle this ticket?",
      "criteria": {"billing": "Payments and refunds.", "technical": "Software bugs.",
                   "unknown": "Not decidable from the ticket; escalate."}}]

Rules (each enforces a pattern or ecosystem fact documented in this repo):
  E1 atomicity        instructions conjoin two asks (" and ", 以及/并且/同时)
  E2 option-count     choice with more than 26 options — over the single-pass A-Z limit
  E3 rubric-size      score criteria outside 2..10 levels
  E4 empty/dup        empty or exactly duplicated option descriptions
  W1 option-load      choice with more than 8 options (reviewer cognitive load)
  W2 escape-option    choice without an explicit none/other/uncertain escape option
  W3 noul-boundary    noul without true/false criteria stating what each answer triggers

Human-readable output by default, --json for machines. Exit 1 if any E* fires;
warnings alone exit 0 (they are judgment calls, not violations).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CONJOINERS = re.compile(r"\band\b|以及|并且|同时|还是.*还是")
ESCAPE_HINTS = ("none", "other", "unknown", "uncertain", "not decidable",
                "不确定", "无法", "其他", " escalate", "escalate")
KINDS = ("noul", "choice", "score")


def lint_question(q: dict) -> list[tuple[str, str]]:
    """Return [(code, message)] for one question dict."""
    findings: list[tuple[str, str]] = []
    name = str(q.get("name", "?"))
    kind = str(q.get("kind", "")).lower()
    instructions = str(q.get("instructions", ""))
    criteria = q.get("criteria")

    if kind not in KINDS:
        findings.append((f"E0", f"{name}: unknown kind {kind!r} (expected one of {KINDS})"))
        return findings
    if not instructions.strip():
        findings.append((f"E4", f"{name}: empty instructions"))
        return findings
    if CONJOINERS.search(instructions):
        findings.append(("E1", f"{name}: instructions look like two asks joined — "
                               "split into atomic questions (one judgment per question)"))

    if kind == "choice":
        keys = list((criteria or {}).keys())
        n = len(keys)
        if n > 26:
            findings.append(("E2", f"{name}: {n} options exceeds the 26-option single-pass "
                                   "(A–Z) limit — engines knock out in groups or reject"))
        elif n > 8:
            findings.append(("W1", f"{name}: {n} options — every extra option costs the "
                                   "reviewer; consider regrouping"))
        descs = [str((criteria or {}).get(k, "")).strip() for k in keys]
        if any(not d for d in descs):
            findings.append(("E4", f"{name}: an option has an empty description"))
        if len(set(descs)) != len(descs):
            findings.append(("E4", f"{name}: duplicated option descriptions — mutual "
                                   "exclusion must be stated, not assumed"))
        blob = " ".join(keys + descs).lower()
        if n >= 3 and not any(h in blob for h in ESCAPE_HINTS):
            findings.append(("W2", f"{name}: no visible escape option (none/other/uncertain) "
                                   "— add one or say why the set is truly closed"))

    elif kind == "score":
        levels = criteria if isinstance(criteria, list) else list((criteria or {}).keys())
        n = len(levels)
        if not 2 <= n <= 10:
            findings.append(("E3", f"{name}: {n} rubric levels — score questions carry "
                                   "2 to 10 ordered levels"))
        descs = [str(d).strip() for d in (criteria if isinstance(criteria, list)
                                          else list((criteria or {}).values()))]
        if any(not d for d in descs):
            findings.append(("E4", f"{name}: a rubric level has an empty description"))
        if len(set(descs)) != len(descs):
            findings.append(("E4", f"{name}: duplicated rubric level descriptions"))

    else:  # noul
        crit = criteria or {}
        if not (crit.get("true") and crit.get("false")):
            findings.append(("W3", f"{name}: noul without true/false criteria — state what "
                                   "action each answer triggers (operational boundary)"))
    return findings


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", help="JSON file with a list of questions")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    questions = json.loads(Path(args.file).read_text(encoding="utf-8"))
    if isinstance(questions, dict):
        questions = [dict(q, name=k) for k, q in questions.items()]
    all_findings = [(i, *lint_question(q)) for i, q in enumerate(questions)]

    if args.json:
        print(json.dumps(
            [{"question": questions[i].get("name", i), "code": code, "message": msg}
             for i, code, msg in all_findings], ensure_ascii=False, indent=1))
    else:
        for i, code, msg in all_findings:
            print(f"{code}  {msg}")
        errors = sum(1 for _, c, _ in all_findings if c.startswith("E"))
        warnings = sum(1 for _, c, _ in all_findings if c.startswith("W"))
        print(f"-- {len(questions)} questions, {errors} errors, {warnings} warnings")
    sys.exit(1 if any(c.startswith("E") for _, c, _ in all_findings) else 0)


if __name__ == "__main__":
    main()
