# Score patterns — ordered rubric judgments

Score takes `instructions` + `criteria` as an **ordered list** defining each rubric level. The answer is a probability-weighted `score` (it can land between levels), plus `legend`, `probabilities`, and `confidence`. If your levels aren't strictly ordered by intensity or quality, you want [Choice](choice-patterns.md), not Score.

Templates use the Python SDK (`python -m pip install typesafe-sdk`).

---

### Severity rubric
**Primitive:** Score · **Added:** 2026-09-28

How bad is it? The single most reused rubric in support and ops pipelines.

```python
"severity": Score(
    instructions="How severe is this incident report?",
    criteria=[
        "Cosmetic or informational; no functional impact.",
        "Minor impairment; workaround exists.",
        "Major feature broken for some users.",
        "Outage or data loss; urgent response required.",
    ],
),
```

**Wiring & thresholds**
- Treat the returned `score` as an index into `legend` (0-based); map bands to SLAs in code — e.g. score ≥ 2.5 pages on-call, ≥ 1.5 files high priority.
- Rewrite rubric levels as full sentences a reader could rank blind — terse labels ("S1"…"S4") train nothing.

**Failure modes**
- Uneven spacing: if the jump between level 2 and 3 is much bigger than 1→2, scores pile up in the flat region. Split or re-word.

**Sources:** [Quick-start example](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [Docs — patterns](https://docs.typesafe.ai/patterns)

---

### Quality gate
**Primitive:** Score · **Added:** 2026-09-28

A pass/fix/fail verdict on generated work (code, copy, structured output) before it reaches a user or merges.

```python
"quality": Score(
    instructions="Rate this generated patch against the task requirements.",
    criteria=[
        "Wrong: does not address the task.",
        "Partial: addresses the task but with clear defects.",
        "Acceptable: meets requirements with minor issues.",
        "Excellent: meets requirements and is robust.",
    ],
),
```

**Wiring & thresholds**
- Gate on a band, not a point: < 1.5 → reject, 1.5–2.5 → one repair round, ≥ 2.5 → ship. "Schema-valid output is not the same as a correct decision" — the gate judges content, the schema only judges shape.
- Combine with a Noul "does it violate any stated constraint?" question for a second, independent vote.

**Failure modes**
- Rubric drift: silently rewording a level changes every downstream threshold — version your rubrics like code.

**Sources:** [Docs — confidence](https://docs.typesafe.ai/confidence) · [Cookbook — llm guardrails](https://docs.typesafe.ai/cookbooks/llm_guardrails)

---

### Content moderation scoring
**Primitive:** Score · **Added:** 2026-09-28

Rate user- or model-generated content against a moderation policy before display, in one 70–500 ms call suitable for real-time UX.

```python
"moderation": Score(
    instructions="How much does this content violate the stated policy?",
    criteria=[
        "No policy concern.",
        "Borderline; context could make it fine.",
        "Clearly against policy.",
        "Severe: harassment, hate, or illegal content.",
    ],
),
```

**Wiring & thresholds**
- Put the actual policy text in `state` (e.g. `state={"policy": ...}`) so you can tune policy without touching the question.
- Auto-block only at the top band; the middle band routes to review, not deletion — moderation false positives cost more than review latency.

**Failure modes**
- Policy in the question, state in the question, examples in the question — the question is frozen per threshold; everything variable belongs in `state`.

**Sources:** [Launch post — guardrails](https://typesafe.ai/blog/introducing-system-one-models-and-jev) · [Docs — state](https://docs.typesafe.ai/concepts/state)

---

### Relevance rubric (RAG)
**Primitive:** Score · **Added:** 2026-09-28

Score retrieved passages for how well they support the query before they enter the prompt — cheaper than reranking with a chat model and returns calibrated levels.

```python
"relevance": Score(
    instructions="How well does this passage answer the question?",
    criteria=[
        "Irrelevant or off-topic.",
        "Topically related but doesn't answer it.",
        "Partially answers the question.",
        "Directly and completely answers it.",
    ],
),
```

**Wiring & thresholds**
- One request per passage (parallel questions share context limits); fan out, then take score ≥ 2.5 into the prompt, sorted by score.
- Log scores per retrieval; a drifting mean is your signal the corpus or queries changed.

**Failure modes**
- Passage contains the answer keywords but for a different entity ("Paris, Texas" vs "Paris, France") — add an entity-match Noul alongside.

**Sources:** [Cookbook — classifying RAG passages](https://docs.typesafe.ai/cookbooks/classifying_rag_passages) · [Cookbook — rerank](https://docs.typesafe.ai/cookbooks/rerank_typesafe) · Community: [hotchpotch/jev-reranker](https://github.com/hotchpotch/jev-reranker), [WiktorB2004/llama-index-jev](https://github.com/WiktorB2004/llama-index-jev)

---

### Priority scoring for queues
**Primitive:** Score · **Added:** 2026-09-28

Turn unstructured requests into an ordered queue number so your scheduler stops FIFO-ing everything.

```python
"priority": Score(
    instructions="How soon does this request genuinely need action?",
    criteria=[
        "Whenever; no deadline.",
        "This week is fine.",
        "Today; blocked on us.",
        "Now; someone is waiting live.",
    ],
),
```

**Wiring & thresholds**
- Score decides *urgency*, code decides *order* — compose `score` with SLA clocks and customer tier in your scheduler, per the core rule.
- Re-score on state changes (a reply bumps the ticket) rather than caching forever.

**Failure modes**
- Rubric levels leak business rules ("VIP customers are always 3") — tier belongs in code, only the human-urgency judgment belongs in the question.

**Sources:** [Docs — patterns](https://docs.typesafe.ai/patterns) · [Docs — use-case map](https://docs.typesafe.ai/concepts/use-case-map)
