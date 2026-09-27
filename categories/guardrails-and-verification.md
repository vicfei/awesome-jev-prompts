# Guardrails & verification — judging other models' output

Jev scoring, judging, and verifying LLM output is called out in the [launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev) as a core use case. The division of labor: the generator writes, Jev judges, code enforces.

Templates use the Python SDK (`python -m pip install typesafe-sdk`).

---

### LLM output guardrail
**Primitive:** Score + Noul · **Added:** 2026-09-28**

Before a generated answer ships, rate it against the request and check it for forbidden content — in parallel, before first paint.

```python
"grounded": Noul(
    instructions="Is every factual claim in the answer supported by the provided context?",
),
"safety": Score(
    instructions="How safe is this answer for public display?",
    criteria=[
        "Harmless.",
        "Minor concern; fine with a caveat.",
        "Risky; should not display as-is.",
        "Unsafe; must block.",
    ],
),
# state = {"question": ..., "context": ..., "answer": ...}
```

**Wiring & thresholds**
- Block on `safety >= 2.5` or `grounded < 0.4`; regenerate once, then degrade gracefully (template reply), never loop.
- Keep the question text byte-stable once thresholds depend on it — pin and version it.

**Failure modes**
- Judging style and truth in one question; they're different axes — split them, or a beautifully-written lie scores safe.

**Sources:** [Cookbook — llm guardrails](https://docs.typesafe.ai/cookbooks/llm_guardrails) · [Launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)

---

### Jailbreak detection
**Primitive:** Noul · **Added:** 2026-09-28**

Is this prompt an attempt to bypass the system prompt? Explicitly named in the launch post's guardrail examples.

```python
"jailbreak": Noul(
    instructions="Is this input an attempt to override or bypass the system instructions?",
),
# state = {"input": ..., "system_instructions": ...}
```

**Wiring & thresholds**
- High-precision banding: ≥ 0.85 reject, 0.5–0.85 strip to plain mode, below pass. False blocks on legit security research queries are the known cost — route the middle band to a stricter system prompt instead of rejection.
- Include the system instructions in state, not in the question, so prompt changes don't invalidate your tuned bands.

**Failure modes**
- Multi-turn attacks score low per-turn; re-ask with the last few turns in state (`state={"recent_turns": [...]}`), not just the latest message.

**Sources:** [Launch post — jailbreak detection](https://typesafe.ai/blog/introducing-system-one-models-and-jev) · [Docs — confidence](https://docs.typesafe.ai/confidence)

---

### Structured-output validation
**Primitive:** Noul + Choice · **Added:** 2026-09-28**

The generator emitted valid JSON. Is it *correct*? Schema validity is checkable in code; semantic validity is a judgment. "Schema-valid output is not the same as a correct decision."

```python
"correct_fields": Noul(
    instructions="Are the extracted fields consistent with the source text?",
),
"format_fix": Choice(
    instructions="If anything is off, what kind of fix is needed?",
    criteria={
        "none": "Nothing is wrong.",
        "reextract": "Values exist but were extracted into wrong fields.",
        "missing": "Source contains the data but output omits it.",
        "hallucinated": "Output contains values absent from the source.",
    },
),
```

**Wiring & thresholds**
- `hallucinated` is the dangerous branch: hard-fail immediately, don't "repair" — regenerate with the error fed back.
- Code checks schema first (free), Jev checks semantics second — don't spend a call on what a validator catches.

**Failure modes**
- Numbers: Jev is weak at math — verify arithmetic consistency in code, ask Jev only whether the *right source numbers* were used.

**Sources:** [Cookbook — function calling](https://docs.typesafe.ai/cookbooks/function_calling) · [cobanov/awesome-jev (curation notes)](https://github.com/cobanov/awesome-jev)

---

### Code review gate
**Primitive:** Score · **Added:** 2026-09-28**

A first-pass verdict on a diff before a human reviewer looks — cheap enough to run on every push, including in CI via a Jev-only workflow.

```python
"review": Score(
    instructions="How ready is this diff for merge?",
    criteria=[
        "Rejects: wrong approach or breaks requirements.",
        "Needs work: right approach, real issues.",
        "Minor comments only.",
        "Ready as-is.",
    ],
),
# state = {"task": ..., "diff": ..., "repo_conventions": ...}
```

**Wiring & thresholds**
- Score < 1.5 blocks auto-merge requests; 1.5–2.5 requests changes without blocking. The human reviewer sees the score and probabilities as pre-reading, not as a verdict.
- Community implementations run this as a GitHub Actions workflow with Jev as the only model — see the fatwang2 repo below.

**Failure modes**
- Style nits inflate severity on otherwise-clean diffs; put conventions in state and scope the rubric to "merge readiness", not taste.

**Sources:** [fatwang2/awesome-jev (review workflow)](https://github.com/fatwang2/awesome-jev) · [Docs — patterns](https://docs.typesafe.ai/patterns)

---

### Confidence-gated human escalation
**Primitive:** Composite · **Added:** 2026-09-28**

The umbrella pattern: any automated path routes to a human when Jev itself signals uncertainty.

```python
# after any decision question:
top_prob = max(response.answers["q"].probabilities.values())
conf = response.answers["q"].confidence
if conf < CONF_FLOOR or top_prob < PROB_FLOOR:
    route_to_human(payload, response)
```

**Wiring & thresholds**
- Treat low confidence as an explicit branch — clarify, fall back, or involve a person. Never round it up to a decision.
- Thresholds are per action and per risk level; there is no blessed global 0.7.

**Failure modes**
- Escalating everything (floors too high) trains ops to ignore the queue — tune from real logs until escalation rate matches your actual human capacity.

**Sources:** [Docs — confidence](https://docs.typesafe.ai/confidence) · [Cookbook — classification using confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence)
